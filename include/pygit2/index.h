#ifndef INCLUDE_pygit2_index_h
#define INCLUDE_pygit2_index_h

#include <Python.h>
#include <git2.h>

PyObject* Index_add(Index *self, PyObject *args);
PyObject* Index_clear(Index *self);
PyObject* Index_find(Index *self, PyObject *py_path);
PyObject* Index_read(Index *self);
PyObject* Index_write(Index *self);
PyObject* Index_iter(Index *self);
PyObject* Index_getitem(Index *self, PyObject *value);
PyObject* Index_read_tree(Index *self, PyObject *value);
PyObject* Index_write_tree(Index *self);
Py_ssize_t Index_len(Index *self);
int Index_setitem(Index *self, PyObject *key, PyObject *value);

#endif
