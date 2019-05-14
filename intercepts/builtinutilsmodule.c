#include <Python.h>

static PyObject *addr(PyObject *self, PyObject *args)
{
    PyObject *func;
    if (!PyArg_ParseTuple(args, "O", &func))
        return NULL;
    return PyLong_FromSize_t((size_t)func);
}

static PyObject *getattr_replacement(PyObject *self, PyObject *args)
{
    return NULL;
}

static PyObject *setattr_replacement(PyObject *self, PyObject *args)
{
    return NULL;
}

static PyMethodDef Methods[] = {
    {"addr", (PyCFunction)addr, METH_VARARGS, "Return the address of a function of method."},
    {"getattr_replacement", (PyCFunction)getattr_replacement, METH_VARARGS, "A replacement for the builtin getattr."},
    {"setattr_replacement", (PyCFunction)setattr_replacement, METH_VARARGS, "A replacement for the builtin setattr."},
    {NULL, NULL, 0, NULL}};

static struct PyModuleDef builtinutilsmodule = {
    PyModuleDef_HEAD_INIT, "builtinutils", NULL, -1, Methods};

PyMODINIT_FUNC
PyInit_builtinutils(void)
{
    return PyModule_Create(&builtinutilsmodule);
}
