import time
import datetime
import asyncio


# Create class that acts as a countdown
async def countdown(seconds: float):
    # Calculate the total number of seconds
    total_seconds: float = seconds

    # While loop that checks if total_seconds reaches zero
    # If not zero, decrement total time by one second
    while total_seconds > 0:
        # Delays the program one second
        await asyncio.sleep(1)
        # Reduces total time by one second
        total_seconds -= 1

    print("Bzzzt! The countdown is at zero seconds!")


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(countdown(10))
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

# ==================================================================70
# leave a blank line below
