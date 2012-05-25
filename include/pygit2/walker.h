#ifndef INCLUDE_pygit2_walker_h
#define INCLUDE_pygit2_walker_h

#include <Python.h>
#include <git2.h>
#include <pygit2/types.h>

void Walker_dealloc(Walker *self);
PyObject* Walker_hide(Walker *self, PyObject *py_hex);
PyObject* Walker_push(Walker *self, PyObject *py_hex);
PyObject* Walker_sort(Walker *self, PyObject *py_sort_mode);
PyObject* Walker_reset(Walker *self);
PyObject* Walker_iter(Walker *self);
PyObject* Walker_iternext(Walker *self);

#endif
