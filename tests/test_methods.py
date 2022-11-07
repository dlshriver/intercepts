import intercepts


class TestClass:
    def method_no_arg(self):
        return 0

    def method_one_arg(self, arg1):
        return arg1


def handler(*args, **kwargs):
    result = _(*args, **kwargs)
    return "handled", result


def handler_0(*args, **kwargs):
    result = _(*args, **kwargs)
    return "handled_0", result


def test_register_class_function():
    t = TestClass()
    result = t.method_no_arg()
    intercepts.register(TestClass.method_no_arg, handler)
    assert t.method_no_arg() == (
        "handled",
        result,
    ), "handler function should modify output"
    t2 = TestClass()
    assert t2.method_no_arg() == (
        "handled",
        result,
    ), "handler function should modify output"


def test_register_method_no_arg():
    t = TestClass()
    result = t.method_no_arg()
    intercepts.register(t.method_no_arg, handler)
    assert t.method_no_arg() == (
        "handled",
        result,
    ), "handler function should modify output"
    t2 = TestClass()
    assert t2.method_no_arg() == (
        "handled",
        result,
    ), "handler function should modify output of other methods"


def test_register_method_one_arg():
    t = TestClass()
    t2 = TestClass()
    result = t.method_one_arg(1)
    intercepts.register(t.method_one_arg, handler)
    assert t.method_one_arg(1) == (
        "handled",
        result,
    ), "handler function should modify output"
    assert t2.method_one_arg(1) == (
        "handled",
        result,
    ), "handler function should modify output of other methods"


def test_unregister():
    t = TestClass()
    result = t.method_no_arg()
    intercepts.register(t.method_no_arg, handler)
    assert t.method_no_arg() == (
        "handled",
        result,
    ), "handler function should modify output"
    intercepts.unregister(t.method_no_arg)
    assert t.method_no_arg() == result, "method should no longer be intercepted"


def test_unregister_multiple_handlers():
    t = TestClass()
    result = t.method_no_arg()
    intercepts.register(t.method_no_arg, handler)
    intercepts.register(t.method_no_arg, handler)
    assert t.method_no_arg() == (
        "handled",
        ("handled", result),
    ), "handler function should modify output"
    intercepts.unregister(t.method_no_arg)
    assert t.method_no_arg() == result, "method should no longer be intercepted"


def test_unregister_multiple_mixed_handlers_1():
    t = TestClass()
    result = t.method_no_arg()
    intercepts.register(TestClass.method_no_arg, handler)
    intercepts.register(t.method_no_arg, handler_0)
    assert t.method_no_arg() == (
        "handled_0",
        ("handled", result),
    ), "handler function should modify output"
    intercepts.unregister(t.method_no_arg, 1)
    assert t.method_no_arg() == (
        "handled",
        result,
    ), "function should still be intercepted"


def test_unregister_multiple_mixed_handlers_2():
    t = TestClass()
    result = t.method_no_arg()
    intercepts.register(t.method_no_arg, handler_0)
    intercepts.register(TestClass.method_no_arg, handler)
    assert t.method_no_arg() == (
        "handled",
        ("handled_0", result),
    ), "handler function should modify output"
    intercepts.unregister(t.method_no_arg, 1)
    assert t.method_no_arg() == (
        "handled_0",
        result,
    ), "function should still be intercepted"


def test_unregister_multiple_mixed_handlers_3():
    t = TestClass()
    result = t.method_no_arg()
    intercepts.register(t.method_no_arg, handler_0)
    intercepts.register(TestClass.method_no_arg, handler)
    assert t.method_no_arg() == (
        "handled",
        ("handled_0", result),
    ), "handler function should modify output"
    intercepts.unregister(TestClass.method_no_arg, 1)
    assert t.method_no_arg() == (
        "handled_0",
        result,
    ), "method should still be intercepted"


def test_unregister_multiple_mixed_handlers_4():
    t = TestClass()
    result = t.method_no_arg()
    intercepts.register(TestClass.method_no_arg, handler)
    intercepts.register(t.method_no_arg, handler_0)
    assert t.method_no_arg() == (
        "handled_0",
        ("handled", result),
    ), "handler function should modify output"
    intercepts.unregister(TestClass.method_no_arg, 1)
    assert t.method_no_arg() == (
        "handled",
        result,
    ), "method should still be intercepted"


def test_unregister_multiple_handlers_depth_1():
    t = TestClass()
    result = t.method_no_arg()
    intercepts.register(t.method_no_arg, handler)
    intercepts.register(t.method_no_arg, handler)
    assert t.method_no_arg() == (
        "handled",
        ("handled", result),
    ), "handler function should modify output"
    intercepts.unregister(t.method_no_arg, depth=1)
    assert t.method_no_arg() == (
        "handled",
        result,
    ), "one handler function should modify output"


def test_unregister_all():
    t = TestClass()
    result1 = t.method_no_arg()
    result2 = t.method_one_arg(1)
    intercepts.register(t.method_no_arg, handler)
    intercepts.register(t.method_one_arg, handler)
    assert t.method_no_arg() == (
        "handled",
        result1,
    ), "handler function should modify first output"
    assert t.method_one_arg(1) == (
        "handled",
        result2,
    ), "handler function should modify second output"
    intercepts.unregister_all()
    assert (
        t.method_no_arg() == result1
    ), "first function should no longer be intercepted"
    assert (
        t.method_one_arg(1) == result2
    ), "second function should no longer be intercepted"
    assert (
        len(intercepts.registration._HANDLERS) == 0
    ), "All function intercept handlers should be unregistered."


def test_register_mixed_function_method():
    t = TestClass()
    result = t.method_no_arg()
    intercepts.register(TestClass.method_no_arg, handler)
    assert t.method_no_arg() == (
        "handled",
        result,
    ), "handler function should modify output"
    intercepts.register(t.method_no_arg, handler)
    t2 = TestClass()
    assert t2.method_no_arg() == (
        "handled",
        ("handled", result),
    ), "handler function should modify output of t2"
    assert t.method_no_arg() == (
        "handled",
        ("handled", result),
    ), "handler function should modify output of t"


def test_register_mixed_method_function():
    t = TestClass()
    result = t.method_no_arg()
    intercepts.register(t.method_no_arg, handler_0)
    assert t.method_no_arg() == (
        "handled_0",
        result,
    ), "handler function should modify output"
    intercepts.register(TestClass.method_no_arg, handler)
    t2 = TestClass()
    assert t2.method_no_arg() == (
        "handled",
        ("handled_0", result),
    ), "handler function should modify output of t2"
    assert t.method_no_arg() == (
        "handled",
        ("handled_0", result),
    ), "handler function should modify output of t"
