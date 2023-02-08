"""Tests for all utility functions common across services"""
import os


import funml as ml

from services.utils import (
    get_store_path,
    unit_expn,
    if_else,
    new_pipeline_of,
    to_result,
)

_ROOT_FOLDER_PATH = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)


def test_get_store_path():
    """Returns the path to the store"""
    test_data = {
        "languages": os.path.join(_ROOT_FOLDER_PATH, "languages"),
        "hymns": os.path.join(_ROOT_FOLDER_PATH, "hymns"),
        "auth": os.path.join(_ROOT_FOLDER_PATH, "auth"),
    }

    for k, v in test_data.items():
        assert get_store_path(k) == v


def test_unit_expn():
    """Unit expression returns exactly what it is passed"""
    test_data = [None, 90, 90.8, "indigo", {"y": 90}]
    for data in test_data:
        assert unit_expn(data) == data


def test_if_else():
    """if_else runs code conditionally"""
    is_even = lambda v: v % 2 == 0
    classify_num = if_else(
        check=is_even, do=lambda *args: "even", else_do=lambda *args: "odd"
    )
    test_data = [(2, "even"), (3, "odd"), (9, "odd")]
    for value, expected in test_data:
        assert classify_num(value) == expected


def test_new_pipeline_of():
    """new_pipeline_of creates a new pipeline at any point in the pipeline, especially for imperative code."""
    square = lambda v: v**2
    pipeline = lambda first, second, outputs: (
        new_pipeline_of(first)
        >> unit_expn
        >> outputs.append
        >> new_pipeline_of(second)
        >> square
        >> outputs.append
        >> ml.execute()
    )

    test_data = [
        ("hey", 9, ["hey", 81]),
        (True, 3, [True, 9]),
        ({"h": 8}, 2, [{"h": 8}, 4]),
    ]

    for arg1, arg2, expected in test_data:
        got = []
        pipeline(arg1, arg2, got)
        assert got == expected


def test_to_result():
    """to_result wraps a callable in an ml.Result such that it is ERR when error occurs"""
    div = lambda x, y: x / y
    try_div = lambda x, y: to_result(div, x, y)

    test_data = [
        (20, 4, ml.Result.OK(5)),
        (2, 0, ml.Result.ERR(ZeroDivisionError("division by zero"))),
        (
            4,
            "foo",
            ml.Result.ERR(
                TypeError("unsupported operand type(s) for /: 'int' and 'str'")
            ),
        ),
        (8.4, 2, ml.Result.OK(4.2)),
    ]

    for arg1, arg2, expected in test_data:
        assert try_div(arg1, arg2) == expected
