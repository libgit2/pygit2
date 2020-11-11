/*
 * Copyright 2010-2020 The pygit2 contributors
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

#include <Python.h>
#include "error.h"
#include "types.h"
#include "utils.h"

extern PyTypeObject RepositoryType;

/* forward-declaration for PackBuilder._from_c() */
PyTypeObject PackBuilderType;

PyObject *
wrap_packbuilder(git_packbuilder *c_packbuilder, Repository *repo)
{
    PackBuilder *py_packbuilder = PyObject_GC_New(PackBuilder, &PackBuilderType);

    if (py_packbuilder) {
        py_packbuilder->packbuilder = c_packbuilder;
        py_packbuilder->owned = 1;
        py_packbuilder->repo = repo;
    }

    return (PyObject *)py_packbuilder;
}

int
PackBuilder_init(PackBuilder *self, PyObject *args, PyObject *kwds)
{
    Repository *repo = NULL;

    if (kwds && PyDict_Size(kwds) > 0) {
        PyErr_SetString(PyExc_TypeError,
                        "PackBuilder takes no keyword arguments");
        return -1;
    }
    if (!PyArg_ParseTuple(args, "O!", &RepositoryType, &repo)) {
        return -1;
    }
        /* Create packbuilder */
    int err = git_packbuilder_new(&self->packbuilder, repo->repo);
    if (err != 0) {
        Error_set(err);
        return -1;
    }
    self->owned = 1;
    self->repo = repo;
    return 0;
}

PyDoc_STRVAR(PackBuilder__from_c__doc__, "Init a PackBuilder from a pointer. For internal use only.");
PyObject *
PackBuilder__from_c(PackBuilder *py_packbuilder, PyObject *args)
{
    PyObject *py_pointer, *py_free;
    char *buffer;
    Py_ssize_t len;
    int err;

    py_packbuilder->packbuilder = NULL;
    Repository *repo = NULL;

    if (!PyArg_ParseTuple(args, "OO!", &py_pointer, &RepositoryType, &repo))
        return NULL;

    err = PyBytes_AsStringAndSize(py_pointer, &buffer, &len);
    if (err < 0)
        return NULL;

    if (len != sizeof(git_packbuilder *)) {
        PyErr_SetString(PyExc_TypeError, "invalid pointer length");
        return NULL;
    }

    py_packbuilder->packbuilder = *((git_packbuilder **) buffer);
    py_packbuilder->owned = py_free == Py_True;
    py_packbuilder->repo = repo;

    Py_RETURN_NONE;
}

PyDoc_STRVAR(PackBuilder__disown__doc__, "Mark the object as not-owned by us. For internal use only.");
PyObject *
PackBuilder__disown(PackBuilder *py_packbuilder)
{
    py_packbuilder->owned = 0;
    Py_RETURN_NONE;
}

void
PackBuilder_dealloc(PackBuilder *self)
{
    PyObject_GC_UnTrack(self);

    if (self->owned)
        git_packbuilder_free(self->packbuilder);

    Py_TYPE(self)->tp_free(self);
}

int
PackBuilder_traverse(PackBuilder *self, visitproc visit, void *arg)
{
    return 0;
}

int
PackBuilder_clear(PackBuilder *self)
{
    return 0;
}


PyDoc_STRVAR(PackBuilder__pointer__doc__, "Get the packbuilder's pointer. For internal use only.");
PyObject *
PackBuilder__pointer__get__(PackBuilder *self)
{
    /* Bytes means a raw buffer */
    return PyBytes_FromStringAndSize((char *) &self->packbuilder, sizeof(git_packbuilder *));
}

PyDoc_STRVAR(PackBuilder__repo__doc__, "Get the packbuilder's repository pointer. For internal use only.");
PyObject *
PackBuilder__repo__get__(PackBuilder *self)
{
    /* Bytes means a raw buffer */
    return PyBytes_FromStringAndSize((char *) &self->repo, sizeof(Repository *));
}



PyMethodDef PackBuilder_methods[] = {
    METHOD(PackBuilder, _disown, METH_NOARGS),
    METHOD(PackBuilder, _from_c, METH_VARARGS),
    {NULL}
};

PyGetSetDef PackBuilder_getseters[] = {
    GETTER(PackBuilder, _pointer),
    GETTER(PackBuilder, _repo),
    {NULL}
};


PyDoc_STRVAR(PackBuilder__doc__,
  "PackBuilder(backend) -> PackBuilder\n"
  "\n"
  "Git packbuilder.");

PyTypeObject PackBuilderType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.PackBuilder",                      /* tp_name           */
    sizeof(PackBuilder),                        /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)PackBuilder_dealloc,            /* tp_dealloc        */
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
    Py_TPFLAGS_DEFAULT |
    Py_TPFLAGS_BASETYPE |
    Py_TPFLAGS_HAVE_GC,                        /* tp_flags          */
    PackBuilder__doc__,                         /* tp_doc            */
    (traverseproc)PackBuilder_traverse,         /* tp_traverse       */
    (inquiry)PackBuilder_clear,                 /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    PackBuilder_methods,                        /* tp_methods        */
    0,                                         /* tp_members        */
    PackBuilder_getseters,                      /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    (initproc)PackBuilder_init,                 /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};
