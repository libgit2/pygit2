/*
 * Copyright 2010-2014 The pygit2 contributors
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

/**
 * py_str_to_c_str() returns a newly allocated C string holding the string
 * contained in the 'value' argument.
 */
char *
py_str_to_c_str(PyObject *value, const char *encoding)
{
    const char *borrowed;
    char *c_str = NULL;
    PyObject *tmp = NULL;

    borrowed = py_str_borrow_c_str(&tmp, value, encoding);
    if (!borrowed)
        return NULL;

    c_str = strdup(borrowed);

    Py_DECREF(tmp);
    return c_str;
}

/**
 * Return a pointer to the underlying C string in 'value'. The pointer is
 * guaranteed by 'tvalue'. Decrease its refcount when done with the string.
 */
const char *
py_str_borrow_c_str(PyObject **tvalue, PyObject *value, const char *encoding)
{
    /* Case 1: byte string */
    if (PyBytes_Check(value)) {
        Py_INCREF(value);
        *tvalue = value;
        return PyBytes_AsString(value);
    }

    /* Case 2: text string */
    if (PyUnicode_Check(value)) {
        if (encoding == NULL)
            *tvalue = PyUnicode_AsUTF8String(value);
        else
            *tvalue = PyUnicode_AsEncodedString(value, encoding, "strict");
        if (*tvalue == NULL)
            return NULL;
        return PyBytes_AsString(*tvalue);
    }

    /* Type error */
    PyErr_Format(PyExc_TypeError, "unexpected %.200s",
                 Py_TYPE(value)->tp_name);
    return NULL;
}

/**
 * Converts the (struct) git_strarray to a Python list
 */
PyObject *
get_pylist_from_git_strarray(git_strarray *strarray)
{
    int index;
    PyObject *new_list;

    new_list = PyList_New(strarray->count);
    if (new_list == NULL)
        return NULL;

    for (index = 0; index < strarray->count; index++)
        PyList_SET_ITEM(new_list, index,
                        to_unicode(strarray->strings[index], NULL, NULL));

    return new_list;
}

/**
 * Converts the Python list to struct git_strarray
 * returns -1 if conversion failed
 */
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

    /* allocate new git_strarray */
    ptr = calloc(n, sizeof(char *));
    if (!ptr) {
        PyErr_SetNone(PyExc_MemoryError);
        return -1;
    }

    array->strings = ptr;
    array->count = n;

    for (index = 0; index < n; index++) {
        item = PyList_GetItem(pylist, index);
        str = py_str_to_c_str(item, NULL);
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

static int
py_cred_to_git_cred(git_cred **out, PyObject *py_cred, unsigned int allowed)
{
    PyObject *py_type, *py_tuple;
    long type;
    int err = -1;

    py_type = PyObject_GetAttrString(py_cred, "credential_type");
    py_tuple = PyObject_GetAttrString(py_cred, "credential_tuple");

    if (!py_type || !py_tuple) {
        printf("py_type %p, py_tuple %p\n", py_type, py_tuple);
        PyErr_SetString(PyExc_TypeError, "credential doesn't implement the interface");
        goto cleanup;
    }

    if (!PyLong_Check(py_type)) {
        PyErr_SetString(PyExc_TypeError, "credential type is not a long");
        goto cleanup;
    }

    type = PyLong_AsLong(py_type);

    /* Sanity check, make sure we're given credentials we can use */
    if (!(allowed & type)) {
        PyErr_SetString(PyExc_TypeError, "invalid credential type");
        goto cleanup;
    }

    switch (type) {
    case GIT_CREDTYPE_USERPASS_PLAINTEXT:
    {
        const char *username, *password;

        if (!PyArg_ParseTuple(py_tuple, "ss", &username, &password))
            goto cleanup;

        err = git_cred_userpass_plaintext_new(out, username, password);
        break;
    }
    case GIT_CREDTYPE_SSH_KEY:
    {
        const char *username, *pubkey, *privkey, *passphrase;

        if (!PyArg_ParseTuple(py_tuple, "ssss", &username, &pubkey, &privkey, &passphrase))
            goto cleanup;

        err = git_cred_ssh_key_new(out, username, pubkey, privkey, passphrase);
        break;
    }
    default:
        PyErr_SetString(PyExc_TypeError, "unsupported credential type");
        break;
    }

cleanup:
    Py_XDECREF(py_type);
    Py_XDECREF(py_tuple);

    return err;
}

int
callable_to_credentials(git_cred **out, const char *url, const char *username_from_url, unsigned int allowed_types, PyObject *credentials)
{
    int err;
    PyObject *py_cred = NULL, *arglist = NULL;

    if (credentials == NULL || credentials == Py_None)
        return 0;

    if (!PyCallable_Check(credentials)) {
        PyErr_SetString(PyExc_TypeError, "credentials callback is not callable");
        return -1;
    }

    arglist = Py_BuildValue("(szI)", url, username_from_url, allowed_types);
    py_cred = PyObject_CallObject(credentials, arglist);
    Py_DECREF(arglist);

    if (!py_cred)
        return -1;

    err = py_cred_to_git_cred(out, py_cred, allowed_types);
    Py_DECREF(py_cred);

    return err;
}
