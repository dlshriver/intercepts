import intercepts
import pytest


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
    def increment():
        global RESULT
        RESULT = NUM + 1

    def handler():
        global RESULT
        _()
        return NUM - (RESULT - NUM)

    intercepts.register(increment, handler)

    NUM = 41
    assert increment() == 40
    assert RESULT == 42
    NUM = 42
    assert increment() == 41
    assert RESULT == 43
