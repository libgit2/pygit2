/*
 * Copyright 2010-2021 The pygit2 contributors
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
#include "error.h"
#include "utils.h"

extern PyTypeObject ReferenceType;
extern PyTypeObject TreeType;
extern PyTypeObject CommitType;
extern PyTypeObject BlobType;
extern PyTypeObject TagType;

/**
 * Return a *newly allocated* C string holding the string contained in the
 * 'value' argument.
 */
char *
pgit_encode(PyObject *value, const char *encoding)
{
    PyObject *tmp = NULL;

    const char *borrowed = pgit_borrow_encoding(value, encoding, NULL, &tmp);
    if (!borrowed)
        return NULL;

    char *c_str = strdup(borrowed);
    Py_DECREF(tmp);

    if (!c_str) {
        // FIXME Set exception
    }

    return c_str;
}

char*
pgit_encode_fsdefault(PyObject *value)
{
    return pgit_encode(value, Py_FileSystemDefaultEncoding);
}

/**
 * Return a pointer to the underlying C string in 'value'. The pointer is
 * guaranteed by 'tvalue', decrease its refcount when done with the string.
 */
const char*
pgit_borrow_encoding(PyObject *value, const char *encoding, const char *errors, PyObject **tvalue)
{
    PyObject *py_value = NULL;
    PyObject *py_str = NULL;

    py_value = PyOS_FSPath(value);
    if (py_value == NULL) {
        Error_type_error("unexpected %.200s", value);
        return NULL;
    }

    // Get new PyBytes reference from value
    if (PyUnicode_Check(py_value)) { // Text string
        py_str = PyUnicode_AsEncodedString(
            py_value,
            encoding ? encoding : "utf-8",
            errors ? errors : "strict"
        );

        Py_DECREF(py_value);
        if (py_str == NULL)
            return NULL;
    } else if (PyBytes_Check(py_value)) { // Byte string
        py_str = py_value;
    } else { // Type error
        Error_type_error("unexpected %.200s", value);
        Py_DECREF(py_value);
        return NULL;
    }

    // Borrow c string from the new PyBytes reference
    char *c_str = PyBytes_AsString(py_str);
    if (c_str == NULL) {
        Py_DECREF(py_str);
        return NULL;
    }

    // Return the borrowed c string and the new PyBytes reference
    *tvalue = py_str;
    return c_str;
}


/**
 * Return a borrowed c string with the representation of the given Unicode or
 * Bytes object:
 * - If value is Unicode return the UTF-8 representation
 * - If value is Bytes return the raw sttring
 * In both cases the returned string is owned by value and must not be
 * modified, nor freed.
 */
const char*
pgit_borrow(PyObject *value)
{
    if (PyUnicode_Check(value)) { // Text string
        return PyUnicode_AsUTF8(value);
    } else if (PyBytes_Check(value)) { // Byte string
        return PyBytes_AsString(value);
    }

    // Type error
    Error_type_error("unexpected %.200s", value);
    return NULL;
}


/**
 * Converts the (struct) git_strarray to a Python list
 */
/*
PyObject *
get_pylist_from_git_strarray(git_strarray *strarray)
{
    size_t index;
    PyObject *new_list;

    new_list = PyList_New(strarray->count);
    if (new_list == NULL)
        return NULL;

    for (index = 0; index < strarray->count; index++)
        PyList_SET_ITEM(new_list, index,
                        to_unicode(strarray->strings[index], NULL, NULL));

    return new_list;
}
*/

/**
 * Converts the Python list to struct git_strarray
 * returns -1 if conversion failed
 */
/*
int
get_strarraygit_from_pylist(git_strarray *array, PyObject *pylist)
{
    Py_ssize_t index, n;
    PyObject *item;
    void *ptr;
    char *str;

    if (!PyList_Check(pylist)) {
        PyErr_SetString(PyExc_TypeError, "Value must be a list");
        return -1;
    }

    n = PyList_Size(pylist);

    // allocate new git_strarray
    ptr = calloc(n, sizeof(char *));
    if (!ptr) {
        PyErr_SetNone(PyExc_MemoryError);
        return -1;
    }

    array->strings = ptr;
    array->count = n;

    for (index = 0; index < n; index++) {
        item = PyList_GetItem(pylist, index);
        str = pgit_encode(item, NULL);
        if (!str)
            goto on_error;

        array->strings[index] = str;
    }

    return 0;

on_error:
    n = index;
    for (index = 0; index < n; index++) {
        free(array->strings[index]);
    }
    free(array->strings);

    return -1;
}
*/

static git_otype
py_type_to_git_type(PyTypeObject *py_type)
{
    if (py_type == &CommitType)
        return GIT_OBJ_COMMIT;
    else if (py_type == &TreeType)
        return GIT_OBJ_TREE;
    else if (py_type == &BlobType)
        return GIT_OBJ_BLOB;
    else if (py_type == &TagType)
        return GIT_OBJ_TAG;

    PyErr_SetString(PyExc_ValueError, "invalid target type");
    return GIT_OBJ_BAD; /* -1 */
}

git_otype
py_object_to_otype(PyObject *py_type)
{
    long value;

    if (py_type == Py_None)
        return GIT_OBJ_ANY;

    if (PyLong_Check(py_type)) {
        value = PyLong_AsLong(py_type);
        if (value == -1 && PyErr_Occurred())
            return GIT_OBJ_BAD;

        /* TODO Check whether the value is a valid value */
        return (git_otype)value;
    }

    if (PyType_Check(py_type))
        return py_type_to_git_type((PyTypeObject *) py_type);

    PyErr_SetString(PyExc_ValueError, "invalid target type");
    return GIT_OBJ_BAD; /* -1 */
}
