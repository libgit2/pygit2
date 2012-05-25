#ifndef INCLUDE_pygit2_signature_h
#define INCLUDE_pygit2_signature_h

#include <Python.h>
#include <git2.h>
#include <pygit2/types.h>

PyObject* Signature_get_encoding(Signature *self);
PyObject* Signature_get_raw_name(Signature *self);
PyObject* Signature_get_raw_email(Signature *self);
PyObject* Signature_get_name(Signature *self);
PyObject* Signature_get_email(Signature *self);
PyObject* Signature_get_time(Signature *self);
PyObject* Signature_get_offset(Signature *self);
PyObject* build_signature(Object *obj, const git_signature *signature, const char *encoding);

#endif
