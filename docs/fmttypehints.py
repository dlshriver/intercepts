import inspect
import types
import typing
from typing import Union

from sphinx.application import Sphinx
from sphinx.ext.autodoc import Options


def format_type(type_hint) -> str:
    if type_hint is None:
        return "None"
    elif type_hint is typing.Callable:
        return "{}`~{}.{}`".format(":py:data:", "typing", "Callable")
    elif hasattr(type_hint, "__origin__") and type_hint.__origin__ is typing.Union:
        params = type_hint.__args__
        return " or ".join(format_type(param) for param in params)
    if type_hint not in set([int, str]):
        print("Unknow type_hint: %s" % type_hint)
    return type_hint.__qualname__


def process_docstring(
    app: Sphinx, what: str, name: str, obj, options: Options, lines: list
):
    assert what == "function", "currently, we only handle functions"
    for name, type_hint in obj.__annotations__.items():
        type_str = format_type(type_hint)
        # type_str = str(type_hint)
        if name == "return":
            if type_hint is not None:
                lines.append(":rtype: %s" % type_str)
        else:
            param = ":param %s:" % name
            index = [i for i, line in enumerate(lines) if param in line][0]
            lines.insert(index, ":type %s: %s" % (name, type_str))


def process_signature(
    app: Sphinx,
    what: str,
    name: str,
    obj,
    options: Options,
    signature: str,
    return_annotation: Union[str, None],
):
    assert what == "function", "currently, we only handle functions"
    s = inspect.signature(obj)
    parameters = [
        param.replace(annotation=inspect.Parameter.empty)
        for param in s.parameters.values()
    ]
    new_signature = str(
        s.replace(parameters=parameters, return_annotation=inspect.Parameter.empty)
    )
    return (new_signature, return_annotation)


def setup(app: Sphinx):
    app.connect("autodoc-process-docstring", process_docstring)
    app.connect("autodoc-process-signature", process_signature)
