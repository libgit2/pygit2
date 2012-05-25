#ifndef INCLUDE_pygit2_diff_h
#define INCLUDE_pygit2_diff_h

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <git2.h>
#include <pygit2/types.h>

PyObject* Diff_changes(Diff *self);
PyObject* Diff_patch(Diff *self);

#endif
