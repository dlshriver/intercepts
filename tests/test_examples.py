import unittest

import intercepts


def increment(num):
    return num + 1


def handler(func, num):
    result = func(num)
    return num - (result - num)


def handler2(func, *args, **kwargs):
    return 'The answer is: %s' % func(*args, **kwargs)


class TestExamples(unittest.TestCase):
    def setUp(self):
        intercepts.unregister_all()

    def test_readme_example(self):
        self.assertEqual(increment(41), 42)
        intercepts.register(increment, handler)
        self.assertEqual(increment(41), 40)
        intercepts.unregister(increment)
        intercepts.register(increment, handler2)
        self.assertEqual(increment(41), 'The answer is: 42')
        intercepts.unregister_all()
        self.assertEqual(increment(41), 42)


if __name__ == '__main__':
    unittest.main()
