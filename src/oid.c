/*
 * Copyright 2010-2013 The pygit2 contributors
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
#include <git2.h>
#include "utils.h"
#include "error.h"
#include "oid.h"

PyTypeObject OidType;


PyObject *
git_oid_to_python(const git_oid *oid)
{
    Oid *py_oid;

    py_oid = PyObject_New(Oid, &OidType);
    git_oid_cpy(&(py_oid->oid), oid);
    return (PyObject*)py_oid;
}

size_t
py_hex_to_git_oid(PyObject *py_oid, git_oid *oid)
{
    PyObject *py_hex;
    int err;
    char *hex;
    Py_ssize_t len;

#if PY_MAJOR_VERSION == 2
    /* Bytes (only supported in Python 2) */
    if (PyBytes_Check(py_oid)) {
        err = PyBytes_AsStringAndSize(py_oid, &hex, &len);
        if (err)
            return 0;

        err = git_oid_fromstrn(oid, hex, len);
        if (err < 0) {
            PyErr_SetObject(Error_type(err), py_oid);
            return 0;
        }

        return (size_t)len;
    }
#endif

    /* Unicode */
    if (PyUnicode_Check(py_oid)) {
        py_hex = PyUnicode_AsASCIIString(py_oid);
        if (py_hex == NULL)
            return 0;

        err = PyBytes_AsStringAndSize(py_hex, &hex, &len);
        if (err) {
            Py_DECREF(py_hex);
            return 0;
        }

        err = git_oid_fromstrn(oid, hex, len);
        Py_DECREF(py_hex);
        if (err < 0) {
            PyErr_SetObject(Error_type(err), py_oid);
            return 0;
        }

        return (size_t)len;
    }

    /* Type error */
    PyErr_SetObject(PyExc_TypeError, py_oid);
    return 0;
}

size_t
py_oid_to_git_oid(PyObject *py_oid, git_oid *oid)
{
    /* Oid */
    if (PyObject_TypeCheck(py_oid, (PyTypeObject*)&OidType)) {
        git_oid_cpy(oid, &((Oid*)py_oid)->oid);
        return GIT_OID_HEXSZ;
    }

    /* Hex */
    return py_hex_to_git_oid(py_oid, oid);
}

int
py_oid_to_git_oid_expand(git_repository *repo, PyObject *py_str, git_oid *oid)
{
    int err;
    size_t len;
    git_odb *odb = NULL;
    git_odb_object *obj = NULL;

    len = py_oid_to_git_oid(py_str, oid);
    if (len == 0)
        return -1;

    if (len == GIT_OID_HEXSZ)
        return 0;

    /* Short oid */
    err = git_repository_odb(&odb, repo);
    if (err < 0)
        goto error;

    err = git_odb_read_prefix(&obj, odb, oid, len);
    if (err < 0)
        goto error;

    git_oid_cpy(oid, git_odb_object_id(obj));
    git_odb_object_free(obj);
    git_odb_free(odb);
    return 0;

error:
    git_odb_object_free(obj);
    git_odb_free(odb);
    Error_set(err);
    return -1;
}

PyObject *
git_oid_to_py_str(const git_oid *oid)
{
    char hex[GIT_OID_HEXSZ];

    git_oid_fmt(hex, oid);

    #if PY_MAJOR_VERSION == 2
    return PyBytes_FromStringAndSize(hex, GIT_OID_HEXSZ);
    #else
    return to_unicode_n(hex, GIT_OID_HEXSZ, "utf-8", "strict");
    #endif
}


int
Oid_init(Oid *self, PyObject *args, PyObject *kw)
{
    char *keywords[] = {"raw", "hex", NULL};
    PyObject *raw = NULL, *hex = NULL;
    int err;
    char *bytes;
    Py_ssize_t len;

    if (!PyArg_ParseTupleAndKeywords(args, kw, "|OO", keywords, &raw, &hex))
        return -1;

    /* We expect one or the other, but not both. */
    if (raw == NULL && hex == NULL) {
        PyErr_SetString(PyExc_ValueError, "Expected raw or hex.");
        return -1;
    }
    if (raw != NULL && hex != NULL) {
        PyErr_SetString(PyExc_ValueError, "Expected raw or hex, not both.");
        return -1;
    }

    /* Case 1: raw */
    if (raw != NULL) {
        err = PyBytes_AsStringAndSize(raw, &bytes, &len);
        if (err)
            return -1;

        if (len > GIT_OID_RAWSZ) {
            PyErr_SetObject(PyExc_ValueError, raw);
            return -1;
        }

        memcpy(self->oid.id, (const unsigned char*)bytes, len);
        return 0;
    }

    /* Case 2: hex */
    len = py_hex_to_git_oid(hex, &self->oid);
    if (len == 0)
        return -1;

    return 0;
}


Py_hash_t
Oid_hash(PyObject *oid)
{
    /* TODO Randomize (use _Py_HashSecret) to avoid collission DoS attacks? */
    return *(Py_hash_t*) ((Oid*)oid)->oid.id;
}


PyObject *
Oid_richcompare(PyObject *o1, PyObject *o2, int op)
{
    PyObject *res;
    int cmp;

    /* Comparing to something else than an Oid is not supported. */
    if (!PyObject_TypeCheck(o2, &OidType)) {
        Py_INCREF(Py_NotImplemented);
        return Py_NotImplemented;
    }

    /* Ok go. */
    cmp = git_oid_cmp(&((Oid*)o1)->oid, &((Oid*)o2)->oid);
    switch (op) {
        case Py_LT:
            res = (cmp <= 0) ? Py_True: Py_False;
            break;
        case Py_LE:
            res = (cmp < 0) ? Py_True: Py_False;
            break;
        case Py_EQ:
            res = (cmp == 0) ? Py_True: Py_False;
            break;
        case Py_NE:
            res = (cmp != 0) ? Py_True: Py_False;
            break;
        case Py_GT:
            res = (cmp > 0) ? Py_True: Py_False;
            break;
        case Py_GE:
            res = (cmp >= 0) ? Py_True: Py_False;
            break;
        default:
            PyErr_Format(PyExc_RuntimeError, "Unexpected '%d' op", op);
            return NULL;
    }

    Py_INCREF(res);
    return res;
}


PyDoc_STRVAR(Oid_raw__doc__, "Raw oid, a 20 bytes string.");

PyObject *
Oid_raw__get__(Oid *self)
{
    return PyBytes_FromStringAndSize((const char*)self->oid.id, GIT_OID_RAWSZ);
}


PyDoc_STRVAR(Oid_hex__doc__, "Hex oid, a 40 chars long string (type str).");

PyObject *
Oid_hex__get__(Oid *self)
{
    return git_oid_to_py_str(&self->oid);
}

PyGetSetDef Oid_getseters[] = {
    GETTER(Oid, raw),
    GETTER(Oid, hex),
    {NULL},
};

PyDoc_STRVAR(Oid__doc__, "Object id.");

PyTypeObject OidType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.Oid",                             /* tp_name           */
    sizeof(Oid),                               /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    0,                                         /* tp_dealloc        */
    0,                                         /* tp_print          */
    0,                                         /* tp_getattr        */
    0,                                         /* tp_setattr        */
    0,                                         /* tp_compare        */
    0,                                         /* tp_repr           */
    0,                                         /* tp_as_number      */
    0,                                         /* tp_as_sequence    */
    0,                                         /* tp_as_mapping     */
    (hashfunc)Oid_hash,                        /* tp_hash           */
    0,                                         /* tp_call           */
    0,                                         /* tp_str            */
    0,                                         /* tp_getattro       */
    0,                                         /* tp_setattro       */
    0,                                         /* tp_as_buffer      */
    Py_TPFLAGS_DEFAULT,                        /* tp_flags          */
    Oid__doc__,                                /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    (richcmpfunc)Oid_richcompare,              /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    0,                                         /* tp_methods        */
    0,                                         /* tp_members        */
    Oid_getseters,                             /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    (initproc)Oid_init,                        /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};
