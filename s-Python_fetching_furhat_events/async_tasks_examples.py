import asyncio
import time

async def background_worker(delay, name):
    """A worker that simulates a long-running I/O operation."""
    print(f"[{name}] Task started at {time.strftime('%X')}")
    
    # This is the non-blocking wait. Control yields here.
    await asyncio.sleep(delay)
    
    print(f"[{name}] Task finished after {delay} seconds.")

async def app_entry_point():
    print(f"App Event Loop started at {time.strftime('%X')}")
    
    # 1. Schedule Task A (Starts and runs in the background)
    # create_task does NOT block. It returns a Task object.
    task_a = asyncio.create_task(background_worker(5, "Task A: Serial Port Write"))
    
    print("Main loop continues immediately after scheduling Task A.")
    
    # 2. Wait 2 seconds (simulating other work or user interaction)
    await asyncio.sleep(2)
    
    # 3. Schedule Task B (Starts and runs concurrently with Task A)
    task_b = asyncio.create_task(background_worker(3, "Task B: Network Log"))
    
    print("Main loop continues immediately after scheduling Task B.")

    # We can now wait for them to finish, or just let them complete on their own.
    # We use asyncio.gather to block ONLY if we need to wait for ALL of them.
    await asyncio.gather(task_a, task_b) 
    
    print(f"All tasks completed at {time.strftime('%X')}")

# Running this will show that A and B start close to time=0, 
# and the total execution time is ~5 seconds (the duration of the longest task).
asyncio.run(app_entry_point())