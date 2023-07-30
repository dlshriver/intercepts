import intercepts


def func(a, b):
    return a + b


def handler(*args, **kwargs):
    print("Preventing call.")
    return 0


def test_intercept(capsys):
    assert func(3, 5) == 8
    intercepts.register(func, handler)
    assert func(3, 5) == 0
    captured = capsys.readouterr()
    assert captured.out == "Preventing call.\n"
