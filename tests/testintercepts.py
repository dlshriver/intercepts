import unittest

import intercepts


def func():
    return 'func'


def func_no_args():
    return 'func_no_args'


def func_no_return():
    pass


def func_one_arg(arg1):
    return 'func_one_arg', arg1


def func_two_args(arg1, arg2):
    return 'func_two_args', arg1, arg2


def func_one_kwarg(kwarg1='kwarg1'):
    return 'func_one_kwarg', kwarg1


def handler(func, *args, **kwargs):
    result = func(*args, **kwargs)
    return 'handled', result


class TestRegisterFunctionHandler(unittest.TestCase):
    def setUp(self):
        intercepts.unregister_all()

    def test_resister_func(self):
        self.assertIsNone(intercepts.register(func, handler),
                          'intercepts.register should return None')

    def test_resister_func_no_args(self):
        result = func_no_args()
        intercepts.register(func_no_args, handler)
        self.assertEqual(func_no_args(), ('handled', result),
                         'handler function should modify output')

    def test_register_func_no_return(self):
        intercepts.register(func_no_return, handler)
        self.assertEqual(func_no_return(), ('handled', None),
                         'handler function should modify output')

    def test_register_func_one_arg(self):
        arg1 = 1
        result = func_one_arg(arg1)
        intercepts.register(func_one_arg, handler)
        self.assertEqual(func_one_arg(arg1), ('handled', result),
                         'handler function should modify output')

    def test_register_func_two_args(self):
        arg1, arg2 = 1, 2
        result = func_two_args(arg1, arg2)
        intercepts.register(func_two_args, handler)
        self.assertEqual(func_two_args(arg1, arg2), ('handled', result),
                         'handler function should modify output')

    def test_register_func_one_kwarg_1(self):
        kwarg1 = 1
        result = func_one_kwarg()
        intercepts.register(func_one_kwarg, handler)
        self.assertEqual(func_one_kwarg(), ('handled', result),
                         'handler function should modify output')

    def test_register_func_one_kwarg_2(self):
        kwarg1 = 1
        result = func_one_kwarg(kwarg1)
        intercepts.register(func_one_kwarg, handler)
        self.assertEqual(func_one_kwarg(kwarg1), ('handled', result),
                         'handler function should modify output')

    def test_handle_handler(self):
        with self.assertRaises(ValueError):
            intercepts.register(handler, handler)
            handler(func)

    def test_unregister_all(self):
        result = func_no_args()
        intercepts.register(func_no_args, handler)
        intercepts.register(func_no_return, handler)
        self.assertEqual(func_no_args(), ('handled', result),
                         'handler function should '
                         'modify first output')
        self.assertEqual(func_no_return(), ('handled', None),
                         'handler function should '
                         'modify second output')
        intercepts.unregister_all()
        self.assertEqual(func_no_args(), result,
                         'first function should '
                         'no longer be intercepted')
        self.assertIsNone(func_no_return(),
                          'second function should '
                          'no longer be intercepted')

    def test_unregister(self):
        result = func_no_args()
        intercepts.register(func_no_args, handler)
        self.assertEqual(func_no_args(), ('handled', result),
                         'handler function should modify output')
        intercepts.unregister(func_no_args)
        self.assertEqual(func_no_args(), result,
                         'function should no longer be intercepted')

    def test_unregister_multiple_handlers(self):
        result = func_no_args()
        intercepts.register(func_no_args, handler)
        intercepts.register(func_no_args, handler)
        self.assertEqual(func_no_args(),
                         ('handled', ('handled', result)),
                         'handler functions should modify output')
        intercepts.unregister(func_no_args)
        self.assertEqual(func_no_args(), result,
                         'function should no longer be intercepted')

    def test_unregister_multiple_handlers_depth_1(self):
        result = func_no_args()
        intercepts.register(func_no_args, handler)
        intercepts.register(func_no_args, handler)
        self.assertEqual(func_no_args(),
                         ('handled', ('handled', result)),
                         'handler functions should modify output')
        intercepts.unregister(func_no_args, depth=1)
        self.assertEqual(func_no_args(), ('handled', result),
                         'one handler function should modify output')


if __name__ == '__main__':
    unittest.main()
