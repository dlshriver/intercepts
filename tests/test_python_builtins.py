import sys
import unittest

import intercepts

_REAL_STDOUT = sys.stdout


def handler(func, *args, **kwargs):
    apples = 12
    result = func(*args, **kwargs)
    return "handled", result


class MockStdout:
    def __init__(self):
        self.out = []

    def write(self, value):
        self.out.append(str(value))

    def flush(self):
        pass


class MockStdin:
    def __init__(self, lines=[]):
        self.lines = lines

    def readline(self):
        line = self.lines[0]
        if len(self.lines) > 1:
            self.lines = self.lines[1:]
        return line


class TestAttribute:
    def __delete__(self, obj):
        print("deleting %r from %r" % (self, obj))

    def __set__(self, obj, value):
        print("setting %r from %r" % (self, obj))


class TestObject:
    test_attr = TestAttribute()


def _printerr(*args):
    sys.stderr.write(" ".join([str(x) for x in args]))
    sys.stderr.write("\n")
    sys.stderr.flush()


def get_stdout():
    stdout = sys.stdout
    if isinstance(stdout, MockStdout):
        output = "".join(stdout.out)
        stdout.out = []
        return output
    else:
        raise ValueError("Can't get stdout from type: %s" % type(stdout))


class TestPythonBuiltinHandler(unittest.TestCase):
    def setUp(self):
        intercepts.unregister_all()
        sys.stdout = MockStdout()
        sys.stdin = MockStdin()

    def run_test(self, builtin_func, *args, **kwargs):
        result = builtin_func(*args, **kwargs)
        stdout = get_stdout()
        intercepts.register(builtin_func, handler)
        handled_result = builtin_func(*args, **kwargs)
        handled_stdout = get_stdout()
        intercepts.unregister(builtin_func)
        self.assertEqual(
            handled_result, ("handled", result), "handler function should modify output"
        )
        self.assertEqual(stdout, handled_stdout, "stdout should not change")
        unhandled_result = builtin_func(*args, **kwargs)
        unhandled_stdout = get_stdout()
        self.assertEqual(
            unhandled_result, result, "function should no longer be intercepted"
        )
        self.assertEqual(stdout, unhandled_stdout, "stdout should not change")

    def run_local_isolated_test(self, builtin_func, *args, **kwargs):
        # run the function in local isolation to prevent changes due to changing local environment
        def isolated_func(func, *args, **kwargs):
            a = 0
            b = 1
            c = []
            return func(*args, **kwargs)

        result = isolated_func(builtin_func, *args, **kwargs)
        stdout = get_stdout()
        intercepts.register(builtin_func, handler)
        handled_result = isolated_func(builtin_func, *args, **kwargs)
        handled_stdout = get_stdout()
        self.assertEqual(
            handled_result, ("handled", result), "handler function should modify output"
        )
        self.assertEqual(stdout, handled_stdout, "stdout should not change")
        intercepts.unregister(builtin_func)
        unhandled_result = isolated_func(builtin_func, *args, **kwargs)
        unhandled_stdout = get_stdout()
        self.assertEqual(
            unhandled_result, result, "function should no longer be intercepted"
        )
        self.assertEqual(stdout, unhandled_stdout, "stdout should not change")

    def test_abs(self):
        self.run_test(abs, 3)
        self.run_test(abs, 3002)
        self.run_test(abs, -3)
        self.run_test(abs, -10001919)
        self.run_test(abs, 0)

    def test_all(self):
        self.run_test(all, [True, True, True, True, True])
        self.run_test(all, [True, False])
        self.run_test(all, [False, False, False])
        self.run_test(all, [])
        self.run_test(all, [2, 3, 4, 5])
        self.run_test(all, ["apple", "banana", "orange"])

    def test_any(self):
        self.run_test(any, [True, True, True, True, True])
        self.run_test(any, [True, False])
        self.run_test(any, [False, False, False])
        self.run_test(any, [])
        self.run_test(any, [2, 3, 4, 5])
        self.run_test(any, ["apple", "banana", "orange"])

    def test_ascii(self):
        self.run_test(ascii, "this is a test")
        self.run_test(ascii, sys.stdout)
        self.run_test(ascii, "\n\x00\x1111\u1010this is a test")

    def test_bin(self):
        self.run_test(bin, 5)
        self.run_test(bin, 5012)
        self.run_test(bin, -10003)
        self.run_test(bin, -2)
        self.run_test(bin, 0)

    @unittest.skip("<class 'type'> not yet supported")
    def test_bool(self):
        self.run_test(bool)
        self.run_test(bool, 0)
        self.run_test(bool, 5)
        self.run_test(bool, 10900)
        self.run_test(bool, -184)
        self.run_test(bool, [0])
        self.run_test(bool, [19])

    @unittest.skip("method is python3.7 only")
    def test_breakpoint(self):
        self.run_test(breakpoint)

    @unittest.skip("<class 'type'> not yet supported")
    def test_bytearray(self):
        # TODO : add more tests after implementing type intercepts
        self.run_test(bytearray, 0)

    @unittest.skip("<class 'type'> not yet supported")
    def test_bytes(self):
        # TODO : add more tests after implementing type intercepts
        self.run_test(bytes, 0)

    def test_callable(self):
        self.run_test(callable, int)
        self.run_test(callable, lambda x: x)
        self.run_test(callable, 0)
        self.run_test(callable, "not callable")
        self.run_test(callable, MockStdout)
        self.run_test(callable, handler)

    def test_chr(self):
        self.run_test(chr, 100)
        self.run_test(chr, 0)
        self.run_test(chr, 21010)

    @unittest.skip("<class 'type'> not yet supported")
    def test_classmethod(self):
        # TODO : add more tests after implementing type intercepts
        self.run_test(classmethod, TestPythonBuiltinHandler.test_classmethod)

    def test_compile(self):
        self.run_test(compile, "print('hello world')", "<test>", "exec")
        self.run_test(compile, "print('hello world')", "<test>", "eval")
        self.run_test(compile, "print('hello world')", "<test>", "single")

    @unittest.skip("<class 'type'> not yet supported")
    def test_complex(self):
        # TODO : add more tests after implementing type intercepts
        self.run_test(complex)

    def test_delattr(self):
        self.run_test(delattr, TestObject(), "test_attr")

    @unittest.skip("<class 'type'> not yet supported")
    def test_dict(self):
        # TODO : add more tests after implementing type intercepts
        self.run_test(dict)

    @unittest.skip(
        "dir does not work without arguments. Need to forward local variables to handler."
    )
    def test_dir(self):
        self.run_test(dir, self)
        self.run_test(dir, handler)
        self.run_test(dir, "string test")
        self.run_test(dir, int)
        self.run_test(dir, 10124)
        self.run_local_isolated_test(dir)

    def test_divmod(self):
        self.run_test(divmod, 45, 9)
        self.run_test(divmod, -45, 9)
        self.run_test(divmod, 45, -9)
        self.run_test(divmod, 0, 77)
        self.run_test(divmod, 99999, 421)

    @unittest.skip("<class 'type'> not yet supported")
    def test_enumerate(self):
        # TODO : add more tests after implementing type intercepts
        self.run_test(enumerate, [])

    def test_eval(self):
        self.run_test(eval, "print('hello world')")
        self.run_test(eval, "[0, 1, 2, 3, 4]")
        self.run_test(eval, "range(100)")

    def test_exec(self):
        self.run_test(exec, "print('hello world')")
        self.run_test(exec, "[0, 1, 2, 3, 4]")
        self.run_test(exec, "range(100)")
        self.run_test(exec, compile("print('hello world')", "<test>", "exec"))

    @unittest.skip("<class 'type'> not yet supported")
    def test_filter(self):
        # TODO : add more tests after implementing type intercepts
        self.run_test(filter, lambda x: True, range(10))

    @unittest.skip("<class 'type'> not yet supported")
    def test_float(self):
        # TODO : add more tests after implementing type intercepts
        self.run_test(float)

    def test_format(self):
        self.run_test(format, "test")
        self.run_test(format, 0.0)
        self.run_test(format, 0.0, "f")
        self.run_test(format, 0.0, ".8f")
        self.run_test(format, TestObject(), "")

    @unittest.skip("<class 'type'> not yet supported")
    def test_frozenset(self):
        # TODO : add more tests after implementing type intercepts
        self.run_test(frozenset)

    def test_getattr(self):
        self.run_test(getattr, TestObject(), "test_attr")
        self.run_test(getattr, sys.stdout, "write")
        self.run_test(getattr, self, "test_getattr")
        self.run_test(getattr, [], "append")
        self.run_test(getattr, 0, "__add__")

    def test_globals(self):
        self.run_test(globals)

    def test_hasattr(self):
        self.run_test(hasattr, TestObject(), "test_attr")
        self.run_test(hasattr, TestObject, "test_attr")
        self.run_test(hasattr, [], "append")

    def test_hash(self):
        self.run_test(hash, 0)
        self.run_test(hash, "test")
        self.run_test(hash, TestObject())

    @unittest.skip("need way to test interactive functions")
    def test_help(self):
        # TODO : add more tests
        self.run_test(help)

    def test_hex(self):
        self.run_test(hex, 7)
        self.run_test(hex, 7239)
        self.run_test(hex, -2993)
        self.run_test(hex, -3)
        self.run_test(hex, 0)

    def test_id(self):
        self.run_test(id, 0)
        self.run_test(id, id)
        self.run_test(id, lambda x: x)
        self.run_test(id, TestObject())
        self.run_test(id, TestObject)
        self.run_test(id, "test string")

    def test_input(self):
        sys.stdin.lines = ["test"]
        self.run_test(input)
        self.run_test(input, "Input: ")

    @unittest.skip("<class 'type'> not yet supported")
    def test_int(self):
        # TODO : add more tests after implementing type intercepts
        self.run_test(int)

    def test_isinstance(self):
        self.run_test(isinstance, 0, int)
        self.run_test(isinstance, 100.9, int)
        self.run_test(isinstance, TestObject(), object)
        self.run_test(isinstance, TestObject(), TestObject)
        self.run_test(isinstance, "test object", TestObject)
        self.run_test(isinstance, TestObject, type)
        self.run_test(isinstance, handler, type(handler))

    def test_issubclass(self):
        self.run_test(issubclass, TestObject, TestObject)
        self.run_test(issubclass, object, TestObject)
        self.run_test(issubclass, TestObject, object)

    def _test_iter_helper(self, *args, **kwargs):
        builtin_func = iter
        result = list(builtin_func(*args, **kwargs))
        stdout = get_stdout()
        intercepts.register(builtin_func, handler)
        handled_result = builtin_func(*args, **kwargs)
        handled_stdout = get_stdout()
        intercepts.unregister(builtin_func)
        self.assertTrue(isinstance(handled_result, tuple))
        self.assertEqual(handled_result[0], "handled")
        self.assertEqual(list(handled_result[1]), result)
        self.assertEqual(stdout, handled_stdout, "stdout should not change")
        unhandled_result = list(builtin_func(*args, **kwargs))
        unhandled_stdout = get_stdout()
        self.assertEqual(
            unhandled_result, result, "function should no longer be intercepted"
        )
        self.assertEqual(stdout, unhandled_stdout, "stdout should not change")

    def test_iter(self):
        self._test_iter_helper([])
        self._test_iter_helper((1, 2, 3, 4, 5))
        self._test_iter_helper(range(1000))
        self._test_iter_helper(
            lambda x=[]: [len(x), x.append(len(x)) if len(x) < 10 else x.clear()][0], 10
        )

    def test_len(self):
        self.run_test(len, [])
        self.run_test(len, ())
        self.run_test(len, "test")

    @unittest.skip("<class 'type'> not yet supported")
    def test_list(self):
        # TODO : add more tests after implementing type intercepts
        self.run_test(list)

    @unittest.skip("locals does not work. Need to forward local variables to handler.")
    def test_locals(self):
        self.run_local_isolated_test(locals)

    @unittest.skip("<class 'type'> not yet supported")
    def test_map(self):
        self.run_test(map, lambda x: x, [])
        self.run_test(map, lambda x: x, [1, 2, 3, 4])
        self.run_test(map, lambda x: x + 1, range(100))

    def test_max(self):
        self.run_test(max, range(10))
        self.run_test(max, "a", "b", "c", "d")
        self.run_test(max, 1, 2, 3, 4, 9)
        self.run_test(max, [], default=None)
        self.run_test(max, [(0, 0), (0, 1), (2, -1)], key=lambda s: s[1])

    @unittest.skip("<class 'type'> not yet supported")
    def test_memoryview(self):
        # TODO : add more tests after implementing type intercepts
        self.run_test(memoryview, b"test bytes")

    def test_min(self):
        self.run_test(min, range(10))
        self.run_test(min, "a", "b", "c", "d")
        self.run_test(min, 1, 2, 3, 4, 9)
        self.run_test(min, [], default=None)
        self.run_test(min, [(0, 0), (0, 1), (2, -1)], key=lambda s: s[1])

    def test_next(self):
        self.run_test(next, (0 for i in range(10)))
        self.run_test(next, (0 for i in range(0)), -1)

    @unittest.skip("<class 'type'> not yet supported")
    def test_object(self):
        # TODO : add more tests after implementing type intercepts
        self.run_test(object)

    def test_oct(self):
        self.run_test(oct, 12)
        self.run_test(oct, 219836)
        self.run_test(oct, -1240)
        self.run_test(oct, -1)
        self.run_test(oct, 0)

    def _test_open_helper(self, *args, **kwargs):
        from io import TextIOBase

        builtin_func = open
        result = builtin_func(*args, **kwargs)
        stdout = get_stdout()
        intercepts.register(builtin_func, handler)
        handled_str, handled_result = builtin_func(*args, **kwargs)
        handled_stdout = get_stdout()
        self.assertEqual(handled_str, "handled")
        self.assertEqual(result.name, handled_result.name)
        self.assertEqual(type(result), type(handled_result))
        if isinstance(result, TextIOBase):
            self.assertEqual(result.mode, handled_result.mode)
            self.assertEqual(result.encoding, handled_result.encoding)
        self.assertEqual(stdout, handled_stdout, "stdout should not change")
        intercepts.unregister(builtin_func)
        unhandled_result = builtin_func(*args, **kwargs)
        unhandled_stdout = get_stdout()
        self.assertEqual(
            unhandled_result.name,
            result.name,
            "function should no longer be intercepted",
        )
        self.assertEqual(type(result), type(unhandled_result))
        if isinstance(result, TextIOBase):
            self.assertEqual(result.mode, unhandled_result.mode)
            self.assertEqual(result.encoding, unhandled_result.encoding)
        self.assertEqual(stdout, unhandled_stdout, "stdout should not change")
        result.close()
        handled_result.close()
        unhandled_result.close()

    def test_open(self):
        self._test_open_helper("/tmp/test_text_file", "w+")
        self._test_open_helper("/tmp/test_text_file", "w")
        self._test_open_helper("/tmp/test_text_file", "r")
        self._test_open_helper("/tmp/test_text_file", "a")
        self._test_open_helper("/tmp/test_file", "wb+")
        self._test_open_helper("/tmp/test_file", "wb")
        self._test_open_helper("/tmp/test_file", "rb")
        self._test_open_helper("/tmp/test_file", "ab")

    def test_ord(self):
        self.run_test(ord, "a")
        self.run_test(ord, "\x41")
        self.run_test(ord, "\u1000")

    def test_pow(self):
        self.run_test(pow, 1, 1)
        self.run_test(pow, 1, 0)
        self.run_test(pow, 2, 10)
        self.run_test(pow, -3, 3)
        self.run_test(pow, 10, 12)
        self.run_test(pow, 1000, -2)
        self.run_test(pow, 7, 4, 3)

    def test_print(self):
        self.run_test(print, "TEST")
        self.run_test(print, "hello", "world")
        self.run_test(print, "test", "3", sep=":")
        self.run_test(print, "test", "4", end=".")

    @unittest.skip("<class 'type'> not yet supported")
    def test_property(self):
        # TODO : add more tests after implementing type intercepts
        self.run_test(property)

    @unittest.skip("<class 'type'> not yet supported")
    def test_range(self):
        # TODO : add more tests after implementing type intercepts
        self.run_test(range, 10)

    def test_repr(self):
        self.run_test(repr, 0)
        self.run_test(repr, "string")
        self.run_test(repr, TestObject())
        self.run_test(repr, TestObject)
        self.run_test(repr, TestObject().test_attr)

    @unittest.skip("<class 'type'> not yet supported")
    def test_reversed(self):
        # TODO : add more tests after implementing type intercepts
        self.run_test(reversed, [])

    def test_round(self):
        self.run_test(round, 0)
        self.run_test(round, 0.0)
        self.run_test(round, 0.11111)
        self.run_test(round, 0.124125151)
        self.run_test(round, 22351.121151)
        self.run_test(round, 0.0, 0)
        self.run_test(round, 3.3, 0)
        self.run_test(round, 32457.1178, 1)
        self.run_test(round, 54124.08912748, 4)

    @unittest.skip("<class 'type'> not yet supported")
    def test_set(self):
        # TODO : add more tests after implementing type intercepts
        self.run_test(set)

    def test_setattr(self):
        self.run_test(setattr, TestObject(), "test_attr", 0)
        self.run_test(setattr, TestObject(), "name", None)

    @unittest.skip("<class 'type'> not yet supported")
    def test_slice(self):
        # TODO : add more tests after implementing type intercepts
        self.run_test(slice, 10)

    def test_sorted(self):
        self.run_test(sorted, [])
        self.run_test(sorted, range(100))
        self.run_test(sorted, [3, 5, 9, 2, 4, 1])
        self.run_test(sorted, ["a", "c", "orange", "banana", "grape"])
        self.run_test(sorted, [3, 5, 9, 2, 4, 1], reverse=True)
        self.run_test(sorted, [(0, 0), (1, -1), (2, 3), (3, -2)], key=lambda x: x[1])

    @unittest.skip("<class 'type'> not yet supported")
    def test_staticmethod(self):
        # TODO : add more tests after implementing type intercepts
        self.run_test(staticmethod, TestPythonBuiltinHandler.test_staticmethod)

    @unittest.skip("<class 'type'> not yet supported")
    def test_str(self):
        # TODO : add more tests after implementing type intercepts
        self.run_test(str)

    def test_sum(self):
        self.run_test(sum, [])
        self.run_test(sum, [], 100)
        self.run_test(sum, [3, 5, 6, 1, 6, 1, 4, 3, 7])

    @unittest.skip("<class 'type'> not yet supported")
    def test_super(self):
        self.run_test(super, TestPythonBuiltinHandler, self)
        self.run_test(super)

    @unittest.skip("<class 'type'> not yet supported")
    def test_tuple(self):
        # TODO : add more tests after implementing type intercepts
        self.run_test(tuple)

    @unittest.skip("<class 'type'> not yet supported")
    def test_type(self):
        # TODO : add more tests after implementing type intercepts
        self.run_test(type, self)

    @unittest.skip("vars does not work. Need to forward local variables to handler.")
    def test_vars(self):
        # TODO : add more tests after implementing type intercepts
        self.run_local_isolated_test(vars)

    @unittest.skip("<class 'type'> not yet supported")
    def test_zip(self):
        # TODO : add more tests after implementing type intercepts
        self.run_test(zip)

    def test___import__(self):
        self.run_test(__import__, "builtins")
        self.run_test(__import__, "os")
        self.run_test(__import__, "sys")


if __name__ == "__main__":
    unittest.main()
