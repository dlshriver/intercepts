#include <Python.h>

static PyObject *intercept_handler(PyObject *self, PyObject *args, PyObject *kwargs)
{
    if (self == NULL)
    {
        printf("null self\n");
        Py_RETURN_NONE;
    }
    char *ptr;
    size_t func_addr = strtoul(PyModule_GetName(self), &ptr, 10);

    PyObject *module_dict = PyImport_GetModuleDict();
    PyObject *intercepts_module = PyDict_GetItemString(module_dict, "intercepts.registration");
    if (PyErr_Occurred())
        return NULL;
    PyObject *intercept_handler = PyObject_GetAttrString(intercepts_module, "_intercept_handler");
    if (PyErr_Occurred())
    {
        return NULL;
    }
    Py_INCREF(intercept_handler);

    PyTupleObject *co_consts = (PyTupleObject *)(((PyCodeObject *)(((PyFunctionObject *)intercept_handler)->func_code))->co_consts);
    Py_ssize_t size_co_consts = PyTuple_Size((PyObject *)co_consts);

    PyTupleObject *new_co_consts = (PyTupleObject *)PyTuple_New(size_co_consts + 1);
    for (int i = 0; i < size_co_consts; i++)
    {
        PyTuple_SetItem(
            (PyObject *)new_co_consts,
            i,
            PyTuple_GetItem((PyObject *)co_consts, i));
    }
    PyObject *func_id = Py_BuildValue("K", func_addr);
    PyTuple_SetItem(
        (PyObject *)new_co_consts,
        size_co_consts,
        func_id);

    ((PyCodeObject *)(((PyFunctionObject *)intercept_handler)->func_code))->co_consts = (PyObject *)new_co_consts;
    PyObject *result = PyEval_CallObjectWithKeywords(
        (PyObject *)intercept_handler,
        args,
        kwargs);
    ((PyCodeObject *)(((PyFunctionObject *)intercept_handler)->func_code))->co_consts = (PyObject *)co_consts;
    Py_DECREF(intercept_handler);

    return result;
}

static PyObject *get_handler(PyObject *self, PyObject *args, PyObject *kwargs)
{
    size_t func_id;
    if (!PyArg_ParseTuple(args, "K", &func_id))
        return NULL;

    const char *func_name = ((PyCFunctionObject *)func_id)->m_ml->ml_name;
    const char *func_doc = ((PyCFunctionObject *)func_id)->m_ml->ml_doc;

    static PyMethodDef handler_def;
    handler_def.ml_name = func_name;
    handler_def.ml_meth = (PyCFunction)intercept_handler;
    handler_def.ml_flags = METH_VARARGS | METH_KEYWORDS;
    handler_def.ml_doc = func_doc;

    char func_id_str[32];
    sprintf(func_id_str, "%lu", func_id);
    PyObject *new_module = PyModule_New((const char *)func_id_str);
    PyObject *fn = PyCFunction_NewEx(
        &handler_def,
        (PyObject *)new_module,
        NULL);
    Py_DECREF(new_module);
    return fn;
}

static PyMethodDef Methods[] = {
    {"intercept_handler", (PyCFunction)intercept_handler, METH_VARARGS | METH_KEYWORDS, "Handle a builtin function or method."},
    {"get_handler", (PyCFunction)get_handler, METH_VARARGS | METH_KEYWORDS, "Get a new function handler."},
    {NULL, NULL, 0, NULL}};

static struct PyModuleDef builtinhandlermodule = {
    PyModuleDef_HEAD_INIT, "builtinhandler", NULL, -1, Methods};

PyMODINIT_FUNC
PyInit_builtinhandler(void)
{
    return PyModule_Create(&builtinhandlermodule);
}
