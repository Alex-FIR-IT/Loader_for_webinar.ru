import time
from functools import wraps
from typing import Callable, AnyStr, Union
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


def retry_execution_if_exception_is_raised(*, retries: int, delay: Union[int, AnyStr]):
    def wrapper_1(func: Callable):
        @wraps(wrapped=func)
        def wrapper_2(*args, **kwargs):
            successfully = error = result = False

            for retry in range(retries):
                try:
                    result = func(*args, **kwargs)
                    successfully = True
                    break
                except Exception as error:
                    print(f"Попытка {retry + 1} провалилась! \n"
                          f"Возникло исключение - {error}\n"
                          )
                    chime.warning()
                    time.sleep(secs=delay)

            if not successfully:
                print('Не удалось выполнить операцию!')
                raise Exception(error)

            return result

        return wrapper_2

    return wrapper_1
