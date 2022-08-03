from threading import Thread, current_thread
from ctypes import c_ulong, pythonapi, py_object
from typing import Any, Awaitable, Callable
import asyncio

# Decorators to use a sync function as async, allowing task cancellation.
# Cancelling is done as in asyncio.Task.cancel(), by sending a asyncio.CancelledError
# to the inside of the function.


def async_t(func) -> Awaitable:
    """Decorate a sync function to be used as async. Supports task cancelling.
    This version is based on Thread().start()
    """

    async def run_cancellable(*args, **kwargs) -> Any:
        def worker() -> None:
            try:
                context["result"] = func(*args, **kwargs)
            except BaseException as e:
                context["exception"] = e

        context: dict = {"exception": None, "result": None}
        worker_thread: Thread = Thread(target=worker)
        worker_thread.start()

        while worker_thread.is_alive():
            try:
                await asyncio.sleep(0.001)
            except asyncio.CancelledError:
                if worker_thread.is_alive():
                    thread_id: c_ulong = c_ulong(worker_thread.ident)
                    exception: c_ulong = py_object(asyncio.CancelledError)
                    ret = pythonapi.PyThreadState_SetAsyncExc(thread_id, exception)
                    if ret > 1:  # This should NEVER happen, but shit happens
                        pythonapi.PyThreadState_SetAsyncExc(thread_id, None)

        if context["exception"]:
            raise context["exception"]

        return context["result"]

    return run_cancellable


# Based on run_in_executor
def async_e(func: Callable) -> Awaitable:
    """Decorate a sync function to be used as async. Supports task cancelling.
    This version is based on loop.run_in_executor()
    """

    async def run_cancellable(*args, **kwargs) -> Any:
        def worker() -> Any:
            context["thread"] = current_thread().ident
            return func(*args, **kwargs)

        context: dict = {"thread": None}
        loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
        future: asyncio.Future = asyncio.ensure_future(loop.run_in_executor(None, worker))
        while not future.done():
            try:
                await asyncio.wait([future])
            except asyncio.CancelledError:
                thread_id: c_ulong = c_ulong(context["thread"])
                exception: py_object = py_object(asyncio.CancelledError)
                ret: int = pythonapi.PyThreadState_SetAsyncExc(thread_id, exception)
                if ret > 1:  # This should NEVER happen, but shit happens
                    pythonapi.PyThreadState_SetAsyncExc(thread_id, None)
        return future.result()

    return run_cancellable
