#ifndef INCLUDE_pygit2_reference_h
#define INCLUDE_pygit2_reference_h

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <git2.h>

PyObject* Reference_delete(Reference *self, PyObject *args);
PyObject* Reference_rename(Reference *self, PyObject *py_name);
PyObject* Reference_reload(Reference *self);
PyObject* Reference_resolve(Reference *self, PyObject *args);
PyObject* Reference_get_target(Reference *self);
PyObject* Reference_get_name(Reference *self);
PyObject* Reference_get_oid(Reference *self);
PyObject* Reference_get_hex(Reference *self);
PyObject* Reference_get_type(Reference *self);
PyObject* wrap_reference(git_reference * c_reference);

#endif
