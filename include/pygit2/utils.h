/*
 * Copyright 2010-2012 The pygit2 contributors
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
#include <pygit2/types.h>


/* Python 3 support */
#if PY_MAJOR_VERSION >= 3
  #define PyInt_AsLong PyLong_AsLong
  #define PyInt_Check PyLong_Check
  #define PyInt_FromLong PyLong_FromLong
  #define PyString_AS_STRING PyBytes_AS_STRING
  #define PyString_AsString PyBytes_AsString
  #define PyString_AsStringAndSize PyBytes_AsStringAndSize
  #define PyString_Check PyBytes_Check
  #define PyString_FromString PyBytes_FromString
  #define PyString_FromStringAndSize PyBytes_FromStringAndSize
  #define PyString_Size PyBytes_Size
#endif

#if PY_MAJOR_VERSION == 2
  #define to_path(x) to_bytes(x)
  #define to_encoding(x) to_bytes(x)
#else
  #define to_path(x) to_unicode(x, Py_FileSystemDefaultEncoding, "strict")
  #define to_encoding(x) PyUnicode_DecodeASCII(x, strlen(x), "strict")
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
Py_LOCAL_INLINE(PyObject*)
to_unicode(const char *value, const char *encoding, const char *errors)
{
    if (encoding == NULL) {
        /* If the encoding is not explicit, it may not be UTF-8, so it
         * is not safe to decode it strictly.  This is rare in the
         * wild, but does occur in old commits to git itself
         * (e.g. c31820c2). */
        encoding = "utf-8";
        errors = "replace";
    }
    return PyUnicode_Decode(value, strlen(value), encoding, errors);
}

Py_LOCAL_INLINE(PyObject*)
to_bytes(const char * value)
{
    return PyString_FromString(value);
}

char * py_str_to_c_str(PyObject *value, const char *encoding);

#define py_path_to_c_str(py_path) \
        py_str_to_c_str(py_path, Py_FileSystemDefaultEncoding)

#endif
