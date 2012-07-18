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
#include <pygit2/types.h>
#include <pygit2/utils.h>
#include <pygit2/oid.h>
#include <pygit2/signature.h>

int
Signature_init(Signature *self, PyObject *args, PyObject *kwds)
{
    PyObject *py_name;
    char *name, *email, *encoding = NULL;
    long long time;
    int offset;
    int err;
    git_signature *signature;

    if (kwds) {
        PyErr_SetString(PyExc_TypeError,
                        "Signature takes no keyword arguments");
        return -1;
    }

    if (!PyArg_ParseTuple(args, "OsLi|s",
                          &py_name, &email, &time, &offset, &encoding))
        return -1;

    name = py_str_to_c_str(py_name, encoding);
    if (name == NULL)
        return -1;

    err = git_signature_new(&signature, name, email, time, offset);
    free(name);
    if (err < 0) {
        Error_set(err);
        return -1;
    }

    self->obj = NULL;
    self->signature = signature;

    if (encoding) {
        self->encoding = strdup(encoding);
        if (self->encoding == NULL) {
            PyErr_NoMemory();
            return -1;
        }
    }

    return 0;
}

void
Signature_dealloc(Signature *self)
{
    if (self->obj)
        Py_DECREF(self->obj);
    else {
        git_signature_free((git_signature*)self->signature);
        free((void*)self->encoding);
    }
    Py_TYPE(self)->tp_free((PyObject*)self);
}

PyObject *
Signature_get_encoding(Signature *self)
{
    const char *encoding;

    encoding = self->encoding;
    if (encoding == NULL)
        encoding = "utf-8";

    return to_encoding(encoding);
}

PyObject *
Signature_get_raw_name(Signature *self)
{
    return to_bytes(self->signature->name);
}

PyObject *
Signature_get_raw_email(Signature *self)
{
    return to_bytes(self->signature->email);
}

PyObject *
Signature_get_name(Signature *self)
{
    return to_unicode(self->signature->name, self->encoding, "strict");
}

PyObject *
Signature_get_email(Signature *self)
{
    return to_unicode(self->signature->email, self->encoding, "strict");
}

PyObject *
Signature_get_time(Signature *self)
{
    return PyInt_FromLong(self->signature->when.time);
}

PyObject *
Signature_get_offset(Signature *self)
{
    return PyInt_FromLong(self->signature->when.offset);
}

PyGetSetDef Signature_getseters[] = {
    {"_encoding", (getter)Signature_get_encoding, NULL, "encoding", NULL},
    {"_name", (getter)Signature_get_raw_name, NULL, "Name (bytes)", NULL},
    {"_email", (getter)Signature_get_raw_email, NULL, "Email (bytes)", NULL},
    {"name", (getter)Signature_get_name, NULL, "Name", NULL},
    {"email", (getter)Signature_get_email, NULL, "Email", NULL},
    {"time", (getter)Signature_get_time, NULL, "Time", NULL},
    {"offset", (getter)Signature_get_offset, NULL, "Offset", NULL},
    {NULL}
};

PyTypeObject SignatureType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.Signature",                        /* tp_name           */
    sizeof(Signature),                         /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)Signature_dealloc,             /* tp_dealloc        */
    0,                                         /* tp_print          */
    0,                                         /* tp_getattr        */
    0,                                         /* tp_setattr        */
    0,                                         /* tp_compare        */
    0,                                         /* tp_repr           */
    0,                                         /* tp_as_number      */
    0,                                         /* tp_as_sequence    */
    0,                                         /* tp_as_mapping     */
    0,                                         /* tp_hash           */
    0,                                         /* tp_call           */
    0,                                         /* tp_str            */
    0,                                         /* tp_getattro       */
    0,                                         /* tp_setattro       */
    0,                                         /* tp_as_buffer      */
    Py_TPFLAGS_DEFAULT,                        /* tp_flags          */
    "Signature",                               /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    0,                                         /* tp_methods        */
    0,                                         /* tp_members        */
    Signature_getseters,                       /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    (initproc)Signature_init,                  /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};

PyObject *
build_signature(Object *obj, const git_signature *signature,
                const char *encoding)
{
    Signature *py_signature;

    py_signature = PyObject_New(Signature, &SignatureType);
    if (py_signature) {
        Py_INCREF(obj);
        py_signature->obj = obj;
        py_signature->signature = signature;
        py_signature->encoding = encoding;
    }
    return (PyObject*)py_signature;
}
