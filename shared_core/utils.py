import functools
import datetime
from typing import TypeVar, Callable, cast

TCallable = TypeVar("TCallable", bound=Callable)


def continuously_ask_user_yn(question: str = "", return_bool: bool = False) -> bool or str:
    """
    Continuously ask the user for a valid answer until one is given.
    """
    question = question + " [y/n]: "
    while True:
        answer = input(question)
        answer = answer.lower()
        if answer in ["y", "n"]:
            if return_bool:
                if answer == "y":
                    return True
                else:
                    return False
            else:
                return answer
        else:
            print("Invalid answer, please try again")


def execution_time(func: TCallable) -> TCallable:
    """
    Decorator to measure the execution time of a function.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = datetime.datetime.now()
        result = func(*args, **kwargs)
        print("Total run time: ", str(datetime.datetime.now() - start))
        return result
    return cast(TCallable, wrapper)
