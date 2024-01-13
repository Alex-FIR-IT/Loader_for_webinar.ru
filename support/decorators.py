import time
from functools import wraps
from typing import Callable, AnyStr


def print_execution_time(*, action: AnyStr):
    """
    Prints execution time for a decorated function
    :param action: what a decorated function does
    :return: wrapper which additionally prints execution time
    """

    def wrapper_1(func: Callable):
        @wraps(wrapped=func)
        def wrapper_2(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()

            print(f'На {action} затрачено {end - start} секунд')

            return result

        return wrapper_2

    return wrapper_1
