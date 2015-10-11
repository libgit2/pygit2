/*
 * Copyright 2010-2015 The pygit2 contributors
 *
 * This file is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License, version 2,
 * as published by the Free Software Foundation.
 *
 * In addition to the permissions in the GNU General Public License,
 * the authors give you unlimited permission to link the compiled
 * version of this file into combinations with other programs,
 * and to distribute those combinations without any restriction
 * coming from the use of this file.  (The General Public License
 * restrictions do apply in other respects; for example, they cover
 * modification of the file, and distribution when not linked into
 * a combined executable.)
 *
 * This file is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; see the file COPYING.  If not, write to
 * the Free Software Foundation, 51 Franklin Street, Fifth Floor,
 * Boston, MA 02110-1301, USA.
 */

#ifndef INCLUDE_pygit2_utils_h
#define INCLUDE_pygit2_utils_h

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <git2.h>
#include "types.h"

#ifdef __GNUC__
#  define PYGIT2_FN_UNUSED __attribute__((unused))
#else
#  define PYGIT2_FN_UNUSED
#endif

/* Python 2 support */
#if PY_MAJOR_VERSION == 2
  #define PyLong_FromSize_t PyInt_FromSize_t
  #define PyLong_AsSize_t (size_t)PyInt_AsSsize_t
  #define PyLong_AsLong PyInt_AsLong
  #undef PyLong_Check
  #define PyLong_Check PyInt_Check
  #define PyLong_FromLong PyInt_FromLong
  #define PyInteger_Type PyInt_Type
  #define PyBytes_AS_STRING PyString_AS_STRING
  #define PyBytes_AsString PyString_AsString
  #define PyBytes_AsStringAndSize PyString_AsStringAndSize
  #define PyBytes_Check PyString_Check
  #define PyBytes_FromString PyString_FromString
  #define PyBytes_FromStringAndSize PyString_FromStringAndSize
  #define PyBytes_Size PyString_Size
  #define to_path(x) to_bytes(x)
  #define to_encoding(x) to_bytes(x)
#else
  #define PyInteger_Type PyLong_Type
  #define to_path(x) to_unicode(x, Py_FileSystemDefaultEncoding, "strict")
  #define to_encoding(x) PyUnicode_DecodeASCII(x, strlen(x), "strict")
  #define PyString_FromFormat(s, ...) PyUnicode_FromFormat(s, __VA_ARGS__)
#endif

#ifdef PYPY_VERSION
  #define PyLong_AsSize_t (size_t)PyLong_AsUnsignedLong
#endif

#ifndef Py_hash_t
  #define Py_hash_t long
#endif


#define CHECK_REFERENCE(self)\
    if (self->reference == NULL) {\
        PyErr_SetString(GitError, "deleted reference");\
        return NULL;\
    }

#define CHECK_REFERENCE_INT(self)\
    if (self->reference == NULL) {\
        PyErr_SetString(GitError, "deleted reference");\
        return -1;\
    }


/* Utilities */
#define to_unicode(x, encoding, errors)\
        to_unicode_n(x, strlen(x), encoding, errors)

PYGIT2_FN_UNUSED
Py_LOCAL_INLINE(PyObject*)
to_unicode_n(const char *value, size_t len, const char *encoding,
             const char *errors)
{
    if (encoding == NULL) {
        /* If the encoding is not explicit, it may not be UTF-8, so it
         * is not safe to decode it strictly.  This is rare in the
         * wild, but does occur in old commits to git itself
         * (e.g. c31820c2). */
        encoding = "utf-8";
        errors = "replace";
    }

    return PyUnicode_Decode(value, len, encoding, errors);
}

PYGIT2_FN_UNUSED
Py_LOCAL_INLINE(PyObject*)
to_bytes(const char * value)
{
    return PyBytes_FromString(value);
}

char * py_str_to_c_str(PyObject *value, const char *encoding);
const char *py_str_borrow_c_str(PyObject **tvaue, PyObject *value, const char *encoding);

PyObject * get_pylist_from_git_strarray(git_strarray *strarray);
int get_strarraygit_from_pylist(git_strarray *array, PyObject *pylist);

int py_object_to_object_type(PyObject *py_type);

#define py_path_to_c_str(py_path) \
        py_str_to_c_str(py_path, Py_FileSystemDefaultEncoding)

/* Helpers to make shorter PyMethodDef and PyGetSetDef blocks */
#define METHOD(type, name, args)\
  {#name, (PyCFunction) type ## _ ## name, args, type ## _ ## name ## __doc__}

#define GETTER(type, attr)\
  {         #attr,\
   (getter) type ## _ ## attr ## __get__,\
            NULL,\
            type ## _ ## attr ## __doc__,\
            NULL}

#define GETSET(type, attr)\
  {         #attr,\
   (getter) type ## _ ## attr ## __get__,\
   (setter) type ## _ ## attr ## __set__,\
            type ## _ ## attr ## __doc__,\
            NULL}

#define MEMBER(type, attr, attr_type, docstr)\
  {#attr, attr_type, offsetof(type, attr), 0, PyDoc_STR(docstr)}

#define RMEMBER(type, attr, attr_type, docstr)\
  {#attr, attr_type, offsetof(type, attr), READONLY, PyDoc_STR(docstr)}


/* Helpers for memory allocation */
#define CALLOC(ptr, num, size, label) \
        ptr = calloc((num), size);\
        if (ptr == NULL) {\
            err = GIT_ERROR;\
            giterr_set_oom();\
            goto label;\
        }

#define MALLOC(ptr, size, label) \
        ptr = malloc(size);\
        if (ptr == NULL) {\
            err = GIT_ERROR;\
            giterr_set_oom();\
            goto label;\
        }

/* Helpers to make type init shorter. */
#define INIT_TYPE(type, base, new) \
    type.tp_base = base; \
    type.tp_new = new; \
    if (PyType_Ready(&type) < 0) return NULL;

#define ADD_TYPE(module, type) \
    Py_INCREF(& type ## Type);\
    if (PyModule_AddObject(module, #type, (PyObject*) & type ## Type) == -1)\
        return NULL;

#define ADD_CONSTANT_INT(m, name) \
    if (PyModule_AddIntConstant(m, #name, name) == -1) return NULL;

#define ADD_CONSTANT_STR(m, name) \
    if (PyModule_AddStringConstant(m, #name, name) == -1) return NULL;


#endif
