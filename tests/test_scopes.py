import pytest

import intercepts


def test_closure():
    def increment():
        return num + 1

    def handler():
        result = _()
        return num - (result - num)

    intercepts.register(increment, handler)

    num = 41
    assert increment() == 40
    intercepts.register(increment, handler)
    assert increment() == 42
    intercepts.unregister_all()
    assert increment() == 42


def test_missing_name():
    def increment():
        return num + 1

    def handler():
        result = _()
        return num - (result - num)

    intercepts.register(increment, handler)

    with pytest.raises(NameError):
        assert increment() == 40

    num = 41
    assert increment() == 40
    num = 40
    assert increment() == 39


def test_get_global_value():
    global NUM

    def increment():
        global NUM
        return NUM + 1

    def handler():
        global NUM
        result = _()
        return NUM - (result - NUM)

    intercepts.register(increment, handler)

    NUM = 41
    assert increment() == 40
    intercepts.register(increment, handler)
    assert increment() == 42
    intercepts.unregister_all()
    assert increment() == 42


def test_set_global_value():
    global RESULT

    def increment():
        global RESULT
        RESULT = NUM + 1

    def handler():
        global RESULT
        _()
        RESULT = NUM - (RESULT - NUM)
        return RESULT

    intercepts.register(increment, handler)

    RESULT = 0
    NUM = 41
    assert increment() == 40
    assert RESULT == 40
    NUM = 42
    assert increment() == 41
    assert RESULT == 41


def test_get_global_value_handling_builtin():
    global NUM

    def handler(*args, **kwargs):
        global NUM
        result = _(*args, **kwargs)
        return NUM + 1

    NUM = 41
    assert sum([3, 8, 2]) == 13
    intercepts.register(sum, handler)
    assert sum([3, 8, 2]) == 42
    NUM = 40
    assert sum([3, 8, 2]) == 41
    intercepts.unregister_all()
    assert sum([3, 8, 2]) == 13


def test_set_global_value_handling_builtin():
    global RESULT

    def handler(*args, **kwargs):
        global RESULT
        RESULT = _(*args, **kwargs) + NUM
        return RESULT - NUM

    assert sum([1, 2, 3, 1]) == 7
    intercepts.register(sum, handler)

    NUM = 1000
    RESULT = 0
    assert RESULT == 0
    assert sum([1, 2, 3, 1]) == 7
    assert RESULT == 1007
