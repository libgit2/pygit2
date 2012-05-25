#ifndef INCLUDE_pygit2_error_h
#define INCLUDE_pygit2_error_h

#include <Python.h>
#include <git2.h>

PyObject* Error_type(int type);
PyObject* Error_set(int err);
PyObject* Error_set_str(int err, const char *str);
PyObject* Error_set_oid(int err, const git_oid *oid, size_t len);

#endif
