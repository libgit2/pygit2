#ifndef INCLUDE_pygit2_diff_h
#define INCLUDE_pygit2_diff_h

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <git2.h>
#include <pygit2/types.h>

#define DIFF_CHECK_TYPES(_x, _y, _type_x, _type_y) \
                  PyObject_TypeCheck(_x, _type_x) && \
                  PyObject_TypeCheck(_y, _type_y)


PyObject* Diff_changes(Diff *self);
PyObject* Diff_patch(Diff *self);

#endif
