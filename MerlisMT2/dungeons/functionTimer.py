import multiprocessing
import time

class TimeoutException(Exception):
    pass

# Move the wrapper function outside
def wrapper(func, result_container, args, kwargs):
    try:
        result = func(*args, **kwargs)
        result_container.put(result)  # Store the result in the queue
    except Exception as e:
        result_container.put(e)  # Store any exception raised by the function

def call_with_timeout(func, args=(), kwargs={}, timeout=5):
    # Result container to store the function result or exception
    result_container = multiprocessing.Queue()

    # Start the function in a separate process, passing arguments to the global wrapper
    process = multiprocessing.Process(target=wrapper, args=(func, result_container, args, kwargs))
    process.start()

    # Wait for the function to complete or timeout
    process.join(timeout)

    if process.is_alive():
        process.terminate()  # Kill the process if it's still running after the timeout
        raise TimeoutException(f"Function call timed out after {timeout} seconds")

    # If the function completed, return the result
    if not result_container.empty():
        result = result_container.get()
        if isinstance(result, Exception):
            raise result  # Re-raise the function's exception
        return result
    else:
        return None  # In case no result was captured