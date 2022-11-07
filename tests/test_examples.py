import intercepts


def test_readme_example():
    def increment(num):
        return num + 1

    def handler(num):
        result = _(num)
        return num - (result - num)

    def handler2(*args, **kwargs):
        result = _(*args, **kwargs)
        return f"The answer is: {result}"

    assert increment(41) == 42
    intercepts.register(increment, handler)
    assert increment(41) == 40
    intercepts.unregister(increment)
    intercepts.register(increment, handler2)
    assert increment(41) == "The answer is: 42"
    intercepts.unregister_all()
    assert increment(41) == 42


def test_quickstart_example_1():
    def handler(*args, **kwargs):
        return _(*args, **kwargs) * 2

    intercepts.register(sum, handler)
    assert sum([2, 2]) == 8
    assert sum([1, 2, 3, 4, 5, 6]) == 42


def test_quickstart_example_2(capsys):
    def pre_handler(*args, **kwargs):
        print("Executing function:", _.__name__)
        return _(*args, **kwargs)

    def post_handler(*args, **kwargs):
        result = _(*args, **kwargs)
        print("Executed function:", _.__name__)
        return result

    intercepts.register(sum, pre_handler)
    intercepts.register(sum, post_handler)

    assert sum([1, 2, 3, 4, 5, 6]) == 21
    captured = capsys.readouterr()
    assert captured.out == ("Executing function: sum\nExecuted function: sum\n")


def test_quickstart_example_3(capsys):
    def handler_0(*args, **kwargs):
        print("handler 0")
        return _(*args, **kwargs)

    def handler_1(*args, **kwargs):
        print("handler 1")
        return _(*args, **kwargs)

    intercepts.register(abs, handler_0)
    intercepts.register(abs, handler_1)

    assert abs(33) == 33
    captured = capsys.readouterr()
    assert captured.out == "handler 1\nhandler 0\n"

    assert abs(-6) == 6
    captured = capsys.readouterr()
    assert captured.out == "handler 1\nhandler 0\n"
