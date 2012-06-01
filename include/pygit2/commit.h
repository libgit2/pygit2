#ifndef INCLUDE_pygit2_commit_h
#define INCLUDE_pygit2_commit_h

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <git2.h>

PyObject* Commit_get_message_encoding(Commit *commit);
PyObject* Commit_get_message(Commit *commit);
PyObject* Commit_get_raw_message(Commit *commit);
PyObject* Commit_get_commit_time(Commit *commit);
PyObject* Commit_get_commit_time_offset(Commit *commit);
PyObject* Commit_get_committer(Commit *self);
PyObject* Commit_get_author(Commit *self);

#endif
