#ifndef INCLUDE_pygit2_object_h
#define INCLUDE_pygit2_object_h

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <git2.h>
#include <pygit2/types.h>

PyObject* Object_get_oid(Object *self);
PyObject* Object_get_hex(Object *self);
PyObject* Object_get_type(Object *self);
PyObject* Object_read_raw(Object *self);

#endif
