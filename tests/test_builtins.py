import types

import intercepts


def handler(*args, **kwargs):
    result = _(*args, **kwargs)
    return "handled", result


def test_register_import(capsys):
    result = __import__("os", globals(), locals(), level=0)
    intercepts.register(
        __import__,
        lambda *args, **kwargs: [print(args[0]), _(*args, **kwargs)][-1],
    )
    result_ = __import__("os", globals(), locals(), level=0)
    assert result_ == result, "handler function should not modify output"
    captured = capsys.readouterr()
    assert (
        captured.out == "os\n"
    ), "handler function should print the name of the imported module"


def test_resister_print():
    assert (
        intercepts.register(print, handler) == print
    ), "intercepts.register should return the handled function"
    assert isinstance(print, types.BuiltinFunctionType)


def test_resister_print_call(capsys):
    args = ("test message",)
    result = print(*args)
    captured = capsys.readouterr()
    assert captured.out == " ".join(args) + "\n"
    intercepts.register(print, handler)
    assert print(*args) == ("handled", result), "handler function should modify output"
    captured = capsys.readouterr()
    assert captured.out == " ".join(args) + "\n"


def test_register_sorted():
    args = ([1, 4, 6, 2, 9, 5, 10, 11, 11, 3, -18],)
    result = sorted(*args)
    intercepts.register(sorted, handler)
    assert sorted(*args) == ("handled", result), "handler function should modify output"


def test_register_sum():
    args = ([1, 4, 6, 2, 9, 5, 10, 11, 11, 3, -18],)
    result = sum(*args)
    intercepts.register(sum, handler)
    assert sum(*args) == ("handled", result), "handler function should modify output"


def test_register_sorted_rev():
    args = ([1, 4, 6, 2, 9, 5, 10, 11, 11, 3, -18],)
    result = sorted(*args)

    def handler_rev(*args, **kwargs):
        return ("handled", list(reversed(_(*args, **kwargs))))

    intercepts.register(sorted, handler_rev)
    assert sorted(*args) == (
        "handled",
        list(reversed(result)),
    ), "handler function should modify output"


def test_unregister():
    args = (5, 11)
    result = pow(*args)
    intercepts.register(pow, handler)
    assert pow(*args) == ("handled", result), "handler function should modify output"
    intercepts.unregister(pow)
    assert pow(*args) == result, "function should no longer be intercepted"


def test_unregister_multiple_handlers():
    args = (type,)
    result = repr(*args)
    intercepts.register(repr, handler)
    intercepts.register(repr, handler)
    assert repr(*args) == (
        "handled",
        ("handled", result),
    ), "handler functions should modify output"
    intercepts.unregister(repr)
    assert repr(*args) == result, "function should no longer be intercepted"


def test_unregister_multiple_handlers_depth_1():
    func = round
    args = (3.14159265358979, 2)
    result = func(*args)
    intercepts.register(func, handler)
    intercepts.register(func, handler)
    assert func(*args) == (
        "handled",
        ("handled", result),
    ), "handler functions should modify output"
    intercepts.unregister(func, depth=1)
    assert func(*args) == (
        "handled",
        result,
    ), "one handler function should modify output"
