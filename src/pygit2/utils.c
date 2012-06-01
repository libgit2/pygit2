#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <pygit2/error.h>
#include <pygit2/utils.h>

extern PyTypeObject ReferenceType;

// py_str_to_c_str() returns a newly allocated C string holding
// the string contained in the value argument.
char * py_str_to_c_str(PyObject *value, const char *encoding)
{
    /* Case 1: byte string */
    if (PyString_Check(value))
        return strdup(PyString_AsString(value));

    /* Case 2: text string */
    if (PyUnicode_Check(value)) {
        char *c_str = NULL;

        if (encoding == NULL)
            value = PyUnicode_AsUTF8String(value);
        else
            value = PyUnicode_AsEncodedString(value, encoding, "strict");
        if (value == NULL)
            return NULL;
        c_str = strdup(PyString_AsString(value));
        Py_DECREF(value);
        return c_str;
    }

    /* Type error */
    PyErr_Format(PyExc_TypeError, "unexpected %.200s",
                 Py_TYPE(value)->tp_name);
    return NULL;
}



