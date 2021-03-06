import unittest

import intercepts
import intercepts.registration


class TestClass:
    def method_no_arg(self):
        return 0

    def method_one_arg(self, arg1):
        return arg1


def handler(func, *args, **kwargs):
    result = func(*args, **kwargs)
    return "handled", result


def handler_0(func, *args, **kwargs):
    result = func(*args, **kwargs)
    return "handled_0", result


class TestRegisterMethodHandler(unittest.TestCase):
    def setUp(self):
        intercepts.unregister_all()

    def test_register_class_function(self):
        t = TestClass()
        result = t.method_no_arg()
        intercepts.register(TestClass.method_no_arg, handler)
        self.assertEqual(
            t.method_no_arg(),
            ("handled", result),
            "handler function should modify output",
        )
        t2 = TestClass()
        self.assertEqual(
            t2.method_no_arg(),
            ("handled", result),
            "handler function should modify output",
        )

    def test_register_method_no_arg(self):
        t = TestClass()
        result = t.method_no_arg()
        intercepts.register(t.method_no_arg, handler)
        self.assertEqual(
            t.method_no_arg(),
            ("handled", result),
            "handler function should modify output",
        )
        t2 = TestClass()
        self.assertEqual(
            t2.method_no_arg(),
            ("handled", result),
            "handler function should modify output of other methods",
        )

    def test_register_method_one_arg(self):
        t = TestClass()
        t2 = TestClass()
        result = t.method_one_arg(1)
        intercepts.register(t.method_one_arg, handler)
        self.assertEqual(
            t.method_one_arg(1),
            ("handled", result),
            "handler function should modify output",
        )
        self.assertEqual(
            t2.method_one_arg(1),
            ("handled", result),
            "handler function should modify output of other methods",
        )

    def test_unregister(self):
        t = TestClass()
        result = t.method_no_arg()
        intercepts.register(t.method_no_arg, handler)
        self.assertEqual(
            t.method_no_arg(),
            ("handled", result),
            "handler function should modify output",
        )
        intercepts.unregister(t.method_no_arg)
        self.assertEqual(
            t.method_no_arg(), result, "method should no longer be intercepted"
        )

    def test_unregister_multiple_handlers(self):
        t = TestClass()
        result = t.method_no_arg()
        intercepts.register(t.method_no_arg, handler)
        intercepts.register(t.method_no_arg, handler)
        self.assertEqual(
            t.method_no_arg(),
            ("handled", ("handled", result)),
            "handler function should modify output",
        )
        intercepts.unregister(t.method_no_arg)
        self.assertEqual(
            t.method_no_arg(), result, "method should no longer be intercepted"
        )

    def test_unregister_multiple_mixed_handlers_1(self):
        t = TestClass()
        result = t.method_no_arg()
        intercepts.register(TestClass.method_no_arg, handler)
        intercepts.register(t.method_no_arg, handler_0)
        self.assertEqual(
            t.method_no_arg(),
            ("handled_0", ("handled", result)),
            "handler function should modify output",
        )
        intercepts.unregister(t.method_no_arg, 1)
        self.assertEqual(
            t.method_no_arg(),
            ("handled", result),
            "function should still be intercepted",
        )

    def test_unregister_multiple_mixed_handlers_2(self):
        t = TestClass()
        result = t.method_no_arg()
        intercepts.register(t.method_no_arg, handler_0)
        intercepts.register(TestClass.method_no_arg, handler)
        self.assertEqual(
            t.method_no_arg(),
            ("handled", ("handled_0", result)),
            "handler function should modify output",
        )
        intercepts.unregister(t.method_no_arg, 1)
        self.assertEqual(
            t.method_no_arg(),
            ("handled_0", result),
            "function should still be intercepted",
        )

    def test_unregister_multiple_mixed_handlers_3(self):
        t = TestClass()
        result = t.method_no_arg()
        intercepts.register(t.method_no_arg, handler_0)
        intercepts.register(TestClass.method_no_arg, handler)
        self.assertEqual(
            t.method_no_arg(),
            ("handled", ("handled_0", result)),
            "handler function should modify output",
        )
        intercepts.unregister(TestClass.method_no_arg, 1)
        self.assertEqual(
            t.method_no_arg(),
            ("handled_0", result),
            "method should still be intercepted",
        )

    def test_unregister_multiple_mixed_handlers_4(self):
        t = TestClass()
        result = t.method_no_arg()
        intercepts.register(TestClass.method_no_arg, handler)
        intercepts.register(t.method_no_arg, handler_0)
        self.assertEqual(
            t.method_no_arg(),
            ("handled_0", ("handled", result)),
            "handler function should modify output",
        )
        intercepts.unregister(TestClass.method_no_arg, 1)
        self.assertEqual(
            t.method_no_arg(), ("handled", result), "method should still be intercepted"
        )

    def test_unregister_multiple_handlers_depth_1(self):
        t = TestClass()
        result = t.method_no_arg()
        intercepts.register(t.method_no_arg, handler)
        intercepts.register(t.method_no_arg, handler)
        self.assertEqual(
            t.method_no_arg(),
            ("handled", ("handled", result)),
            "handler function should modify output",
        )
        intercepts.unregister(t.method_no_arg, depth=1)
        self.assertEqual(
            t.method_no_arg(),
            ("handled", result),
            "one handler function should modify output",
        )

    def test_unregister_all(self):
        t = TestClass()
        result1 = t.method_no_arg()
        result2 = t.method_one_arg(1)
        intercepts.register(t.method_no_arg, handler)
        intercepts.register(t.method_one_arg, handler)
        self.assertEqual(
            t.method_no_arg(),
            ("handled", result1),
            "handler function should modify first output",
        )
        self.assertEqual(
            t.method_one_arg(1),
            ("handled", result2),
            "handler function should modify second output",
        )
        intercepts.unregister_all()
        self.assertEqual(
            t.method_no_arg(), result1, "first function should no longer be intercepted"
        )
        self.assertEqual(
            t.method_one_arg(1),
            result2,
            "second function should no longer be intercepted",
        )
        self.assertEqual(
            intercepts.registration._HANDLERS,
            {},
            "All function intercept handlers should be unregistered.",
        )

    def test_register_mixed_function_method(self):
        t = TestClass()
        result = t.method_no_arg()
        intercepts.register(TestClass.method_no_arg, handler)
        self.assertEqual(
            t.method_no_arg(),
            ("handled", result),
            "handler function should modify output",
        )
        intercepts.register(t.method_no_arg, handler)
        t2 = TestClass()
        self.assertEqual(
            t2.method_no_arg(),
            ("handled", ("handled", result)),
            "handler function should modify output of t2",
        )
        self.assertEqual(
            t.method_no_arg(),
            ("handled", ("handled", result)),
            "handler function should modify output of t",
        )

    def test_register_mixed_method_function(self):
        t = TestClass()
        result = t.method_no_arg()
        intercepts.register(t.method_no_arg, handler_0)
        self.assertEqual(
            t.method_no_arg(),
            ("handled_0", result),
            "handler function should modify output",
        )
        intercepts.register(TestClass.method_no_arg, handler)
        t2 = TestClass()
        self.assertEqual(
            t2.method_no_arg(),
            ("handled", ("handled_0", result)),
            "handler function should modify output of t2",
        )
        self.assertEqual(
            t.method_no_arg(),
            ("handled", ("handled_0", result)),
            "handler function should modify output of t",
        )


if __name__ == "__main__":
    unittest.main()
