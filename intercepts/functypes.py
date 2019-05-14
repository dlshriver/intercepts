import ctypes

Py_ssize_t = ctypes.c_int64 if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_int32


class PyObject(ctypes.Structure):
    def incref(self):
        self.ob_refcnt += 1

    def decref(self):
        self.ob_refcnt -= 1


class PyTypeObject(ctypes.Structure):
    pass


PyTypeObject_p = ctypes.POINTER(PyTypeObject)


PyObject._fields_ = [("ob_refcnt", Py_ssize_t), ("ob_type", PyTypeObject_p)]
PyTypeObject._fields_ = [
    ("ob_base", PyObject),
    ("ob_size", Py_ssize_t),
    ("tp_name", ctypes.c_char_p),
]


class PyMethodDef(ctypes.Structure):
    _fields_ = [
        ("ml_name", ctypes.c_char_p),
        (
            "ml_meth",
            ctypes.CFUNCTYPE(
                ctypes.py_object, ctypes.POINTER(PyObject), ctypes.POINTER(PyObject)
            ),
        ),
        ("ml_flags", ctypes.c_int),
        ("ml_doc", ctypes.c_char_p),
    ]


class PyCFunctionObject(ctypes.Structure):
    _fields_ = [
        ("ob_base", PyObject),
        ("m_ml", ctypes.POINTER(PyMethodDef)),
        ("m_self", ctypes.POINTER(PyObject)),
        ("m_module", ctypes.POINTER(PyObject)),
        ("m_weakreflist", ctypes.POINTER(PyObject)),
    ]
