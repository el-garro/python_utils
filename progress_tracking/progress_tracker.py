from functools import partial
from time import time

# Progress tracking with custom refresh interval, can be made async easily
# by eitin
def progress_tracker(refresh_interval: int, progress_message):
    context = {"start_time": time(), "refresh_interval": refresh_interval}

    def progress_callback(pos: int, total: int):
        now = time()
        if not "last_update" in context:
            context["last_update"] = context["start_time"]

        # Only update after refresh_interval
        if now - context["last_update"] < context["refresh_interval"]:
            if pos != total:
                if context["last_update"] != context["start_time"]:
                    return
        context["last_update"] = now

        # Get percent
        try:
            percent = 100 * pos / total
        except:
            percent = 0

        # Get average speed
        try:
            avg_speed = pos / (now - context["start_time"])
        except:
            avg_speed = 0

        # Get ETA in seconds
        try:
            eta = (total - pos) / avg_speed
        except:
            eta = 0

        # Show the result (this part changes depending of the project)
        # Maybe do something with progress_message??
        print(
            f"Progress: {pos}/{total}",
            f"Percent: {round(percent,2)}",
            f"Speed: {round(avg_speed)}B/s",
            f"ETA: {round(eta)}",
        )

    return progress_callback


if __name__ == "__main__":
    # Example Usage
    from random import randint
    from time import sleep

    def sample_progressive_task(progress_callback=None):
        total = randint(1000, 2000)
        step = randint(int(total / 20), int(total / 10))
        print(f"Simulating {total} B at {step}B/s")

        pos = 0
        while pos < total:
            pos += step
            if pos > total:
                pos = total
            sleep(1)
            progress_callback(pos, total)

    def main():
        msg = object()  # Some object, like a message to edit
        sample_progressive_task(progress_tracker(3, msg))

    main()
