import inspect
from typing import Callable, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed


def decorator(f: Optional[Callable] = None, *args, **kwargs):
    if f is None:
        return decorator
    # Get the signature of the function
    sig = inspect.signature(f)

    def wrapped(*args, **kwargs):
        # Filter the kwargs based on the function signature
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
        return f(*args, **filtered_kwargs)

    def call(*args, **kwargs):
        # Filter the kwargs based on the function signature
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
        return f(*args, **filtered_kwargs)

    def map_call(iterable, order_outputs=False, kwargs=None):
        if kwargs is None:
            kwargs = {}

        with ThreadPoolExecutor(max_workers=5) as executor:
            # Prepare a list to hold the futures
            futures = []

            for args in iterable:
                # Filter the kwargs based on the function signature for each call
                filtered_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}

                if isinstance(args, list):
                    future = executor.submit(f, *args, **filtered_kwargs)
                else:
                    future = executor.submit(f, args, **filtered_kwargs)

                futures.append(future)

            # If order_outputs is True, then the results are returned in the order that they were started.
            # Otherwise, they're returned as they finish.
            if order_outputs:
                results = [future.result() for future in futures]
            else:
                results = [future.result() for future in as_completed(futures)]

            return results

    wrapped.call = call
    wrapped.map = map_call

    return wrapped

