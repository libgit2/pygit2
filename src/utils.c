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

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <pygit2/error.h>
#include <pygit2/utils.h>

extern PyTypeObject ReferenceType;

// py_str_to_c_str() returns a newly allocated C string holding
// the string contained in the value argument.
char * py_str_to_c_str(PyObject *value, const char *encoding)
{
    /* Case 1: byte string */
    if (PyString_Check(value))
        return strdup(PyString_AsString(value));

    /* Case 2: text string */
    if (PyUnicode_Check(value)) {
        char *c_str = NULL;

        if (encoding == NULL)
            value = PyUnicode_AsUTF8String(value);
        else
            value = PyUnicode_AsEncodedString(value, encoding, "strict");
        if (value == NULL)
            return NULL;
        c_str = strdup(PyString_AsString(value));
        Py_DECREF(value);
        return c_str;
    }

    /* Type error */
    PyErr_Format(PyExc_TypeError, "unexpected %.200s",
                 Py_TYPE(value)->tp_name);
    return NULL;
}



