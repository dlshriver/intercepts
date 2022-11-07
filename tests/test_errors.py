import pytest

import intercepts


def test_non_function_handler():
    with pytest.raises(ValueError):
        intercepts.register(sum, print)


def test_handle_handler():
    handler = lambda x: x
    with pytest.raises(ValueError):
        intercepts.register(handler, handler)


def test_register_unsupported():
    handler = lambda x: x
    with pytest.raises(NotImplementedError):
        intercepts.register(int, handler)


def test_unregister_unsupported():
    with pytest.raises(NotImplementedError):
        intercepts.unregister(int)
