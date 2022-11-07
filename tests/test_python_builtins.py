import io

import pytest

import intercepts


def handler(*args, **kwargs):
    apples = 12
    result = _(*args, **kwargs)
    return "handled", result


class TestAttribute:
    def __delete__(self, obj):
        print("deleting %r from %r" % (self, obj))

    def __set__(self, obj, value):
        print("setting %r from %r" % (self, obj))


class TestObject:
    test_attr = TestAttribute()


@pytest.mark.parametrize(
    "builtin_func,args,kwargs",
    [
        (abs, (3,), {}),
        (abs, (3002,), {}),
        (abs, (-3,), {}),
        (abs, (-10001919,), {}),
        (abs, (0,), {}),
        (all, ([True, True, True, True, True],), {}),
        (all, ([True, False],), {}),
        (all, ([False, False, False],), {}),
        (all, ([],), {}),
        (all, ([2, 3, 4, 5],), {}),
        (all, (["apple", "banana", "orange"],), {}),
        (any, ([True, True, True, True, True],), {}),
        (any, ([True, False],), {}),
        (any, ([False, False, False],), {}),
        (any, ([],), {}),
        (any, ([2, 3, 4, 5],), {}),
        (any, (["apple", "banana", "orange"],), {}),
        (ascii, ("this is a test",), {}),
        (ascii, (ascii,), {}),
        (ascii, ("\n\x00\x1111\u1010this is a test",), {}),
        (bin, (5,), {}),
        (bin, (5012,), {}),
        (bin, (-10003,), {}),
        (bin, (-2,), {}),
        (bin, (0,), {}),
        pytest.param(
            bool,
            (),
            {},
            marks=pytest.mark.xfail(reason="Unsupported type: <class 'type'>"),
        ),
        pytest.param(
            bytearray,
            (),
            {},
            marks=pytest.mark.xfail(reason="Unsupported type: <class 'type'>"),
        ),
        pytest.param(
            bytes,
            (),
            {},
            marks=pytest.mark.xfail(reason="Unsupported type: <class 'type'>"),
        ),
        (callable, (int,), {}),
        (callable, (lambda x: x,), {}),
        (callable, (0,), {}),
        (callable, ("not callable",), {}),
        (callable, (handler,), {}),
        (callable, (TestAttribute,), {}),
        (chr, (100,), {}),
        (chr, (0,), {}),
        (chr, (21010,), {}),
        pytest.param(
            classmethod,
            (),
            {},
            marks=pytest.mark.xfail(reason="Unsupported type: <class 'type'>"),
        ),
        (compile, ("print('hello world')", "<test>", "exec"), {}),
        (compile, ("print('hello world')", "<test>", "eval"), {}),
        (compile, ("print('hello world')", "<test>", "single"), {}),
        pytest.param(
            complex,
            (),
            {},
            marks=pytest.mark.xfail(reason="Unsupported type: <class 'type'>"),
        ),
        (delattr, (TestObject(), "test_attr"), {}),
        pytest.param(
            dict,
            (),
            {},
            marks=pytest.mark.xfail(reason="Unsupported type: <class 'type'>"),
        ),
        (dir, (TestObject(),), {}),
        (dir, (handler,), {}),
        (dir, ("string test",), {}),
        (dir, (int,), {}),
        (dir, (10124,), {}),
        pytest.param(
            dir,
            (),
            {},
            marks=pytest.mark.xfail(
                reason="result of 'dir' without arguments is context dependent"
            ),
        ),
        (divmod, (45, 9), {}),
        (divmod, (-45, 9), {}),
        (divmod, (45, -9), {}),
        (divmod, (0, 77), {}),
        (divmod, (99999, 421), {}),
        pytest.param(
            enumerate,
            ((),),
            {},
            marks=pytest.mark.xfail(reason="Unsupported type: <class 'type'>"),
        ),
        (eval, ("print('hello world')",), {}),
        (eval, ("[0, 1, 2, 3, 4]",), {}),
        (eval, ("range(100)",), {}),
        (exec, ("print('hello world')",), {}),
        (exec, ("[0, 1, 2, 3, 4]",), {}),
        (exec, ("range(100)",), {}),
        (exec, (compile("print('hello world')", "<test>", "exec"),), {}),
        pytest.param(
            filter,
            (lambda x: x),
            {},
            marks=pytest.mark.xfail(reason="Unsupported type: <class 'type'>"),
        ),
        pytest.param(
            float,
            (),
            {},
            marks=pytest.mark.xfail(reason="Unsupported type: <class 'type'>"),
        ),
        (format, ("test",), {}),
        (format, (0.0,), {}),
        (format, (0.0, "f"), {}),
        (format, (0.0, ".8f"), {}),
        (format, (TestObject(), ""), {}),
        pytest.param(
            frozenset,
            (),
            {},
            marks=pytest.mark.xfail(reason="Unsupported type: <class 'type'>"),
        ),
        (getattr, (TestObject(), "test_attr"), {}),
        (getattr, ([], "append"), {}),
        (getattr, (0, "__add__"), {}),
        (hasattr, (TestObject(), "test_attr"), {}),
        (hasattr, (TestObject, "test_attr"), {}),
        (hasattr, ([], "append"), {}),
        (hash, (0,), {}),
        (hash, ("test",), {}),
        (hash, (TestObject(),), {}),
        (hex, (7,), {}),
        (hex, (7239,), {}),
        (hex, (-2993,), {}),
        (hex, (-3,), {}),
        (hex, (0,), {}),
        (id, (0,), {}),
        (id, (id,), {}),
        pytest.param(
            int,
            (),
            {},
            marks=pytest.mark.xfail(reason="Unsupported type: <class 'type'>"),
        ),
        (isinstance, (0, int), {}),
        (isinstance, (100.9, int), {}),
        (isinstance, (handler, type(handler)), {}),
        (issubclass, (TestObject, TestObject), {}),
        (issubclass, (object, TestObject), {}),
        (len, ([],), {}),
        (len, ("test",), {}),
        pytest.param(
            list,
            (),
            {},
            marks=pytest.mark.xfail(reason="Unsupported type: <class 'type'>"),
        ),
        pytest.param(
            locals,
            (),
            {},
            marks=pytest.mark.xfail(reason="result of 'locals' is context dependent"),
        ),
        pytest.param(
            map,
            (lambda x: x, []),
            {},
            marks=pytest.mark.xfail(reason="Unsupported type: <class 'type'>"),
        ),
        pytest.param(
            map,
            (lambda x: x + 1, range(100)),
            {},
            marks=pytest.mark.xfail(reason="Unsupported type: <class 'type'>"),
        ),
        (max, (range(10),), {}),
        (max, (1, 2, 3, 4, 9), {}),
        (max, ([],), {"default": None}),
        (max, ([(0, 0), (0, 1), (2, -1)],), {"key": lambda s: s[1]}),
        pytest.param(
            memoryview,
            (b"test",),
            {},
            marks=pytest.mark.xfail(reason="Unsupported type: <class 'type'>"),
        ),
        (min, (range(10),), {}),
        (min, (1, 2, 3, 4, 9), {}),
        (min, ([],), {"default": None}),
        (min, ([(0, 0), (0, 1), (2, -1)],), {"key": lambda s: s[1]}),
        (next, ((0 for i in range(10)),), {}),
        (next, ((0 for i in range(0)), -1), {}),
        pytest.param(
            object,
            (),
            {},
            marks=pytest.mark.xfail(reason="Unsupported type: <class 'type'>"),
        ),
        (oct, (12,), {}),
        (oct, (-1,), {}),
        (oct, (0,), {}),
        (ord, ("a",), {}),
        (ord, ("\x41",), {}),
        (ord, ("\u1000",), {}),
        (pow, (1, 1), {}),
        (pow, (2, 10), {}),
        (pow, (1000, -2), {}),
        (pow, (7, 4, 3), {}),
        (print, ("TEST",), {}),
        (print, ("hello", "world"), {}),
        (print, ("test", "3"), {"sep": ":"}),
        (print, ("test", "4"), {"end": "."}),
        pytest.param(
            property,
            (),
            {},
            marks=pytest.mark.xfail(reason="Unsupported type: <class 'type'>"),
        ),
        pytest.param(
            range,
            (10,),
            {},
            marks=pytest.mark.xfail(reason="Unsupported type: <class 'type'>"),
        ),
        (repr, (0,), {}),
        (repr, (TestObject,), {}),
        (repr, (TestObject(),), {}),
        pytest.param(
            reversed,
            ([],),
            {},
            marks=pytest.mark.xfail(reason="Unsupported type: <class 'type'>"),
        ),
        (round, (0,), {}),
        (round, (0.124125151,), {}),
        (round, (54124.08912748, 4), {}),
        pytest.param(
            set,
            (),
            {},
            marks=pytest.mark.xfail(reason="Unsupported type: <class 'type'>"),
        ),
        (setattr, (TestObject(), "test_attr", 0), {}),
        pytest.param(
            slice,
            (10,),
            {},
            marks=pytest.mark.xfail(reason="Unsupported type: <class 'type'>"),
        ),
        (sorted, ([],), {}),
        (sorted, (range(100),), {"reverse": True}),
        (sorted, ([(0, 0), (1, -1), (2, 3), (3, -2)],), {"key": lambda x: x[1]}),
        pytest.param(
            staticmethod,
            (TestObject.test_attr,),
            {},
            marks=pytest.mark.xfail(reason="Unsupported type: <class 'type'>"),
        ),
        pytest.param(
            str,
            (),
            {},
            marks=pytest.mark.xfail(reason="Unsupported type: <class 'type'>"),
        ),
        (sum, ([],), {}),
        (sum, ([], 100), {}),
        (sum, ([3, 5, 6, 1, 6, 1, 4, 3, 7],), {}),
        pytest.param(
            super,
            (),
            {},
            marks=pytest.mark.xfail(reason="Unsupported type: <class 'type'>"),
        ),
        pytest.param(
            tuple,
            (),
            {},
            marks=pytest.mark.xfail(reason="Unsupported type: <class 'type'>"),
        ),
        pytest.param(
            type,
            (),
            {},
            marks=pytest.mark.xfail(reason="Unsupported type: <class 'type'>"),
        ),
        (vars, (TestObject(),), {}),
        pytest.param(
            vars,
            (),
            {},
            marks=pytest.mark.xfail(reason="result of 'vars' is context dependent"),
        ),
        pytest.param(
            zip,
            (),
            {},
            marks=pytest.mark.xfail(reason="Unsupported type: <class 'type'>"),
        ),
        (__import__, ("builtins",), {}),
    ],
)
def test_builtin(capsys, builtin_func, args, kwargs):
    result = builtin_func(*args, **kwargs)
    captured_0 = capsys.readouterr()
    intercepts.register(builtin_func, handler)
    handled_result = builtin_func(*args, **kwargs)
    captured_1 = capsys.readouterr()
    intercepts.unregister(builtin_func)
    assert handled_result == (
        "handled",
        result,
    ), "handler function should modify output"
    assert captured_0.out == captured_1.out, "stdout should not change"
    unhandled_result = builtin_func(*args, **kwargs)
    captured_2 = capsys.readouterr()
    assert unhandled_result == result, "handler function should modify output"
    assert captured_0.out == captured_2.out, "stdout should not change"


@pytest.mark.skip(reason="opens pdb, need to figure out how to stop it")
def test_breakpoint(capsys):
    test_builtin(capsys, breakpoint, (), {})


@pytest.mark.skip(reason="segfaults, must fix")
def test_globals(capsys):
    test_builtin(capsys, globals, (), {})


@pytest.mark.xfail(reason="Unsupported type: <class '_sitebuiltins._Helper'>")
def test_help(capsys, monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO("\n"))
    test_builtin(capsys, help, (), {})


def test_input(capsys, monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO("test\n" * 100))
    test_builtin(capsys, input, (), {})
    test_builtin(capsys, input, ("Input: ",), {})


@pytest.mark.xfail(reason="crashes program, must fix")
@pytest.mark.parametrize(
    "args",
    [
        ([],),
        ((1, 2, 3, 4, 5),),
        (range(1000),),
        (lambda x=[]: [len(x), x.append(len(x)) if len(x) < 10 else x.clear()][0], 10),
    ],
)
def test_iter(capsys, args):
    builtin_func = iter
    result = list(builtin_func(*args))
    captured_0 = capsys.readouterr()
    intercepts.register(builtin_func, handler)
    handled_result = builtin_func(*args)
    captured_1 = capsys.readouterr()
    intercepts.unregister(builtin_func)
    assert isinstance(handled_result, tuple)
    assert handled_result[0] == "handled"
    assert list(handled_result[1]) == result
    assert captured_0.out == captured_1.out, "stdout should not change"
    unhandled_result = list(builtin_func(*args))
    captured_2 = capsys.readouterr()
    assert unhandled_result == result, "function should no longer be intercepted"
    assert captured_0.out == captured_2.out, "stdout should not change"


@pytest.mark.parametrize(
    "mode",
    ["w+", "w", "r", "a", "wb+", "wb", "rb", "ab"],
)
def test_open(tmp_path, mode):
    def handler(*args, **kwargs):
        result = _(*args, **kwargs)
        result.handled = True
        return result

    tmp_file = tmp_path / "file.txt"
    tmp_file.write_text("test\n")
    builtin_func = open
    result = builtin_func(tmp_file, mode)
    intercepts.register(builtin_func, handler)
    handled_result = builtin_func(tmp_file, mode)
    assert handled_result.handled
    assert result.name == handled_result.name
    assert type(result) == type(handled_result)
    assert result.mode == handled_result.mode
    intercepts.unregister(builtin_func)
    unhandled_result = builtin_func(tmp_file, mode)
    assert not getattr(
        unhandled_result, "handled", False
    ), "function should no longer be intercepted"
    assert type(unhandled_result) == type(result)
    assert unhandled_result.name == result.name
    assert unhandled_result.mode == result.mode
