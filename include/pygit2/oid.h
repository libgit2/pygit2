#ifndef INCLUDE_pygit2_oid_h
#define INCLUDE_pygit2_oid_h

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <git2.h>

int py_str_to_git_oid(PyObject *py_str, git_oid *oid);
int py_str_to_git_oid_expand(git_repository *repo, PyObject *py_str,
                              git_oid *oid);
PyObject* git_oid_to_py_str(const git_oid *oid);

#define git_oid_to_python(id) \
        PyString_FromStringAndSize((const char*)id, GIT_OID_RAWSZ)

#endif
