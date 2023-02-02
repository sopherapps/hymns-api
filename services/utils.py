"""Contains the utility functions shared across services"""
from collections import Awaitable
from os import path
from typing import Callable, Any

import funml as ml


"""
Main Expressions
"""
get_store_path = lambda name: path.join(
    _ROOT_FOLDER, name
)  # type: Callable[[str], str]
"""Gets the path to the store"""


unit_expn = ml.val(lambda v: v)  # type: Callable[[Any], Any]
"""An expression that just echoes its inputs"""

await_output = lambda v: await v  # type: Callable[[Awaitable], Any]
"""Awaits an awaitable"""

if_else = lambda check=unit_expn, do=unit_expn, else_do=unit_expn: ml.val(
    lambda *args, **kwargs: (
        ml.match(check(*args, **kwargs))
        .case(True, do=lambda: do(*args, **kwargs))
        .case(False, do=lambda: else_do(*args, **kwargs))
    )()
)  # type: Callable[..., ml.types.Expression]
"""A short cut to creating a conditional expression with only two branches"""


new_pipeline_of = lambda data: ml.val(
    lambda *args: data
)  # type: Callable[[Any], ml.types.Expression]
"""Initializes a new pseudo pipeline for the passed data, discarding the data produced from any previous pipeline.

This is especially useful when doing naturally-imperative work, but trying to maintain the
declarative nature of FunML
"""


def to_result(
    func: Callable, *args: Any, **kwargs: Any
) -> ml.Result | Awaitable[ml.Result]:
    """Wraps a callable in an ml.Result

    Args:
        func: the callable to call
        args: the args to pass to `func`
        kwargs: the key-word args to pass to `func`

    Returns:
        an ml.Result.OK with the output of the `func` call if no error occurred
        else ml.Result.ERR with the exception raised.
    """
    try:
        res = func(*args, **kwargs)

        # in case it is already a result, just return it
        if isinstance(res, ml.Result):
            return res

        return ml.Result.OK(res)
    except Exception as exp:
        return ml.Result.ERR(exp)


"""
Primitive Expressions
"""


"""
Data
"""
_ROOT_FOLDER = path.dirname(path.dirname(path.abspath(__file__)))
