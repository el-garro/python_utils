from multiprocessing import Queue, Process
import asyncio
from typing import Any, Callable


def _mp_worker(queue: Queue, func, *args, **kwargs) -> None:
    try:
        queue.put(func(*args, **kwargs))
    except BaseException as e:
        queue.put(e)


async def run_in_process(func: Callable, *args, **kwargs) -> Any:
    """Run a sync function as async using a separate process. The function
    must be picklable and __name__ protection is advised.

    Args:
        func (Callable): Function to be called in a new process. MUST BE PICKLABLE
        *args (Any): Positional arguments of the function
        **kwargs (Any): Named arguments of the function

    Raises:
        BaseException: Any Exception raised by the function

    Returns:
        Any: Return of the function
    """
    try:
        mp_queue: Queue = Queue()
        new_process: Process = Process(target=_mp_worker, args=(mp_queue, func, *args), kwargs=kwargs)
        new_process.start()

        while new_process.is_alive():
            await asyncio.sleep(0.001)

        result = mp_queue.get()
        new_process.join()  # Avoid Zombie processes on Linux

        if isinstance(result, BaseException):
            raise result

        return result
    except asyncio.CancelledError as e:
        new_process.kill()
        raise e
