import pytest

import intercepts


def func():
    return "func"


def func_no_args():
    return "func_no_args"


def func_no_return():
    pass


def func_one_arg(arg1):
    return "func_one_arg", arg1


def func_two_args(arg1, arg2):
    return "func_two_args", arg1, arg2


def func_one_kwarg(kwarg1="kwarg1"):
    return "func_one_kwarg", kwarg1


def handler(*args, **kwargs):
    result = _(*args, **kwargs)
    return "handled", result


def test_register_func():
    assert (
        intercepts.register(func, handler) == func
    ), "intercepts.register should return the function to be handled"


def test_register_func_no_args():
    result = func_no_args()
    intercepts.register(func_no_args, handler)
    assert func_no_args() == (
        "handled",
        result,
    ), "handler function should modify output"


def test_register_func_no_return():
    intercepts.register(func_no_return, handler)
    assert func_no_return() == (
        "handled",
        None,
    ), "handler function should modify output"


def test_register_func_one_arg():
    arg1 = 1
    result = func_one_arg(arg1)
    intercepts.register(func_one_arg, handler)
    assert func_one_arg(arg1) == (
        "handled",
        result,
    ), "handler function should modify output"


def test_register_func_two_args():
    arg1, arg2 = 1, 2
    result = func_two_args(arg1, arg2)
    intercepts.register(func_two_args, handler)
    assert func_two_args(arg1, arg2) == (
        "handled",
        result,
    ), "handler function should modify output"


def test_register_func_one_kwarg_1():
    result = func_one_kwarg()
    intercepts.register(func_one_kwarg, handler)
    assert func_one_kwarg() == (
        "handled",
        result,
    ), "handler function should modify output"


def test_register_func_one_kwarg_2():
    kwarg1 = 1
    result = func_one_kwarg(kwarg1)
    intercepts.register(func_one_kwarg, handler)
    assert func_one_kwarg(kwarg1) == (
        "handled",
        result,
    ), "handler function should modify output"


def test_handle_handler():
    with pytest.raises(ValueError):
        intercepts.register(handler, handler)
        handler(func)


def test_unregister_all():
    result = func_no_args()
    intercepts.register(func_no_args, handler)
    intercepts.register(func_no_return, handler)
    assert func_no_args() == (
        "handled",
        result,
    ), "handler function should modify first output"
    assert func_no_return() == (
        "handled",
        None,
    ), "handler function should modify second output"
    intercepts.unregister_all()
    assert func_no_args() == result, "first function should no longer be intercepted"
    assert func_no_return() is None, "second function should no longer be intercepted"
    assert (
        len(intercepts.registration._HANDLERS) == 0
    ), "All function intercept handlers should be unregistered."


def test_unregister():
    result = func_no_args()
    intercepts.register(func_no_args, handler)
    assert func_no_args() == (
        "handled",
        result,
    ), "handler function should modify output"
    intercepts.unregister(func_no_args)
    assert func_no_args() == result, "function should no longer be intercepted"


def test_unregister_multiple_handlers():
    result = func_no_args()
    intercepts.register(func_no_args, handler)
    intercepts.register(func_no_args, handler)
    assert func_no_args() == (
        "handled",
        ("handled", result),
    ), "handler functions should modify output"
    intercepts.unregister(func_no_args)
    assert func_no_args() == result, "function should no longer be intercepted"


def test_unregister_multiple_handlers_depth_1():
    result = func_no_args()
    intercepts.register(func_no_args, handler)
    intercepts.register(func_no_args, handler)
    assert func_no_args() == (
        "handled",
        ("handled", result),
    ), "handler functions should modify output"
    intercepts.unregister(func_no_args, depth=1)
    assert func_no_args() == (
        "handled",
        result,
    ), "one handler function should modify output"
