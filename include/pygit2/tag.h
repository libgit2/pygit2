#ifndef INCLUDE_pygit2_tag_h
#define INCLUDE_pygit2_tag_h

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <git2.h>
#include <pygit2/types.h>

PyObject* Tag_get_target(Tag *self);
PyObject* Tag_get_name(Tag *self);
PyObject* Tag_get_tagger(Tag *self);
PyObject* Tag_get_message(Tag *self);
PyObject* Tag_get_raw_message(Tag *self);

#endif
