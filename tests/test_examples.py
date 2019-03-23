import sys
import unittest

import intercepts

_REAL_STDOUT = sys.stdout


class MockStdout:
    def __init__(self):
        self.out = []

    def write(self, value):
        self.out.append(str(value))

    def flush(self):
        pass


def increment(num):
    return num + 1


def handler(func, num):
    result = func(num)
    return num - (result - num)


def handler2(func, *args, **kwargs):
    return "The answer is: %s" % func(*args, **kwargs)


@unittest.skip("Builtins known to currently be broken.")
class TestExamples(unittest.TestCase):
    def setUp(self):
        intercepts.unregister_all()
        sys.stdout = MockStdout()

    def test_readme_example(self):
        self.assertEqual(increment(41), 42)
        intercepts.register(increment, handler)
        self.assertEqual(increment(41), 40)
        intercepts.unregister(increment)
        intercepts.register(increment, handler2)
        self.assertEqual(increment(41), "The answer is: 42")
        intercepts.unregister_all()
        self.assertEqual(increment(41), 42)

    def test_quickstart_example_1(self):
        def handler(func, *args, **kwargs):
            return func(*args, **kwargs) * 2

        intercepts.register(sum, handler)
        self.assertEqual(sum([2, 2]), 8)
        self.assertEqual(sum([1, 2, 3, 4, 5, 6]), 42)

    def test_quickstart_example_2(self):
        def pre_handler(func, *args, **kwargs):
            print("Executing function:", func.__name__)
            return func(*args, **kwargs)

        def post_handler(func, *args, **kwargs):
            result = func(*args, **kwargs)
            print("Executed function:", func.__name__)
            return result

        intercepts.register(sum, pre_handler)
        intercepts.register(sum, post_handler)

        self.assertEqual(sum([1, 2, 3, 4, 5, 6]), 21)
        self.assertEqual(
            sys.stdout.out,
            [
                "Executing function:",
                " ",
                "sum",
                "\n",
                "Executed function:",
                " ",
                "sum",
                "\n",
            ],
        )

    def test_quickstart_example_3(self):
        def handler_0(func, *args, **kwargs):
            print("handler 0")
            return func(*args, **kwargs)

        def handler_1(func, *args, **kwargs):
            print("handler 1")
            return func(*args, **kwargs)

        intercepts.register(abs, handler_0)
        intercepts.register(abs, handler_1)

        self.assertEqual(abs(33), 33)
        self.assertEqual(sys.stdout.out, ["handler 1", "\n", "handler 0", "\n"])

        sys.stdout.out = []
        self.assertEqual(abs(-6), 6)
        self.assertEqual(sys.stdout.out, ["handler 1", "\n", "handler 0", "\n"])


if __name__ == "__main__":
    unittest.main()
