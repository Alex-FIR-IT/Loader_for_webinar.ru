import time
from functools import wraps
from typing import Callable, AnyStr
import chime


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


def chime_when_is_done(*, chime_level: AnyStr):
    """
    Chime after function is accomplished
    :param chime_level: 'success' or 'info' or 'warning' or 'error'
    :return: wrapper which additionally chime after function is accomplished
    """
    def wrapper_1(func: Callable):
        @wraps(wrapped=func)
        def wrapper_2(*args, **kwargs):

            result = func(*args, **kwargs)

            if chime_level == 'success':
                chime.success()
            elif chime_level == 'info':
                chime.info()
            elif chime_level == 'warning':
                chime.warning()
            else:
                chime.error()

            return result

        return wrapper_2

    return wrapper_1
