import sys
import types
import unittest

import intercepts

_REAL_STDOUT = sys.stdout


def handler(func, *args, **kwargs):
    result = func(*args, **kwargs)
    return "handled", result


class MockStdout:
    def __init__(self):
        self.out = []

    def write(self, value):
        self.out.append(str(value))

    def flush(self):
        pass


class TestRegisterBuiltinHandler(unittest.TestCase):
    def setUp(self):
        intercepts.unregister_all()
        sys.stdout = MockStdout()

    def test_register_import(self):
        result = __import__("os", globals(), locals(), level=0)
        intercepts.register(
            __import__,
            lambda func, *args, **kwargs: [print(args[0]), func(*args, **kwargs)][-1],
        )
        result_ = __import__("os", globals(), locals(), level=0)
        self.assertEqual(result_, result, "handler function should not modify output")
        self.assertEqual(
            sys.stdout.out,
            ["os", "\n"],
            "handler function should print the name of the imported module",
        )

    def test_resister_print(self):
        self.assertEqual(
            intercepts.register(print, handler),
            print,
            "intercepts.register should return the handled function",
        )
        self.assertTrue(isinstance(print, types.BuiltinFunctionType))

    def test_resister_print_call(self):
        args = ("test message",)
        result = print(*args)
        self.assertEqual(sys.stdout.out, [" ".join(args), "\n"])
        intercepts.register(print, handler)
        self.assertEqual(
            print(*args), ("handled", result), "handler function should modify output"
        )
        self.assertEqual(sys.stdout.out, [" ".join(args), "\n"] * 2)

    def test_register_sorted(self):
        args = ([1, 4, 6, 2, 9, 5, 10, 11, 11, 3, -18],)
        result = sorted(*args)
        intercepts.register(sorted, handler)
        self.assertEqual(
            sorted(*args), ("handled", result), "handler function should modify output"
        )

    def test_register_sum(self):
        args = ([1, 4, 6, 2, 9, 5, 10, 11, 11, 3, -18],)
        result = sum(*args)
        intercepts.register(sum, handler)
        self.assertEqual(
            sum(*args), ("handled", result), "handler function should modify output"
        )

    def test_register_sorted_rev(self):
        args = ([1, 4, 6, 2, 9, 5, 10, 11, 11, 3, -18],)
        result = sorted(*args)

        def handler_rev(func, *args, **kwargs):
            return ("handled", list(reversed(func(*args, **kwargs))))

        intercepts.register(sorted, handler_rev)
        self.assertEqual(
            sorted(*args),
            ("handled", list(reversed(result))),
            "handler function should modify output",
        )

    def test_unregister(self):
        args = (5, 11)
        result = pow(*args)
        intercepts.register(pow, handler)
        self.assertEqual(
            pow(*args), ("handled", result), "handler function should modify output"
        )
        intercepts.unregister(pow)
        self.assertEqual(pow(*args), result, "function should no longer be intercepted")

    def test_unregister_multiple_handlers(self):
        args = (self,)
        result = repr(*args)
        intercepts.register(repr, handler)
        intercepts.register(repr, handler)
        self.assertEqual(
            repr(*args),
            ("handled", ("handled", result)),
            "handler functions should modify output",
        )
        intercepts.unregister(repr)
        self.assertEqual(
            repr(*args), result, "function should no longer be intercepted"
        )

    def test_unregister_multiple_handlers_depth_1(self):
        func = round
        args = (3.14159265358979, 2)
        result = func(*args)
        intercepts.register(func, handler)
        intercepts.register(func, handler)
        self.assertEqual(
            func(*args),
            ("handled", ("handled", result)),
            "handler functions should modify output",
        )
        intercepts.unregister(func, depth=1)
        self.assertEqual(
            func(*args),
            ("handled", result),
            "one handler function should modify output",
        )


if __name__ == "__main__":
    unittest.main()
