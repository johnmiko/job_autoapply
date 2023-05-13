from selenium.common.exceptions import TimeoutException


# https://stackoverflow.com/questions/15572288/general-decorator-to-wrap-try-except-in-python
def passTimeoutException(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except TimeoutException:
            return
        return result

    return wrapper

from contextlib import contextmanager

@contextmanager
def ignoring(*exceptions, action=print):
    try:
        yield
    except exceptions or Exception as e:
        callable(action) and action(e)