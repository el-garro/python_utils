from inspect import iscoroutinefunction
from time import time

# Decorator to make a function callable only each x seconds
def slow(interval: int):
    def dec(func):
        last_update = [time()]  # It needs to be mutable from the wrapper, hence the list

        # Sync wrapper
        def wrap_sync(*args, **kwargs):
            now = time()
            if now - last_update[0] < interval:
                return
            last_update[0] = now
            return func(*args, **kwargs)

        # Async wrapper
        async def wrap_async(*args, **kwargs):
            now = time()
            if now - last_update[0] < interval:
                return
            last_update[0] = now
            return await func(*args, **kwargs)

        if iscoroutinefunction(func):
            return wrap_async
        else:
            return wrap_sync

    return dec


if __name__ == "__main__":
    # Example Usage
    @slow(3)
    def function1(message: str):
        print(message, time())

    @slow(1)
    def function2(message: str):
        print(message, time())

    while True:
        function1("Message from function1")
        function2("Message from function2")
