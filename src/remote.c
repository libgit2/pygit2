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
#include <structmember.h>
#include <pygit2/error.h>
#include <pygit2/utils.h>
#include <pygit2/types.h>

extern PyObject *GitError;
extern PyTypeObject RepositoryType;

PyObject *
Remote_call(Remote *self, PyObject *args, PyObject *kwds)
{
    Repository* py_repo = NULL;
    char *name = NULL;
    int err;

    if (!PyArg_ParseTuple(args, "O!s", &RepositoryType, &py_repo, &name))
        return NULL;

    self->repo = py_repo;
    err = git_remote_load(&self->remote, py_repo->repo, name);

    if (err < 0)
        return Error_set(err);

    return (PyObject*) self;
}


static void
Remote_dealloc(Remote *self)
{
    git_remote_free(self->remote);
    PyObject_Del(self);
}


PyDoc_STRVAR(Remote_name__doc__, "Name of the remote refspec");

PyObject *
Remote_name__get__(Remote *self)
{
    return PyUnicode_FromString(git_remote_name(self->remote));
}


PyDoc_STRVAR(Remote_url__doc__, "Url of the remote refspec");

PyObject *
Remote_url__get__(Remote *self)
{
    return PyUnicode_FromString(git_remote_url(self->remote));
}


PyGetSetDef Remote_getseters[] = {
    GETTER(Remote, name),
    GETTER(Remote, url),
    {NULL}
};

PyDoc_STRVAR(Remote__doc__, "Remote object.");

PyTypeObject RemoteType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.Remote",                          /* tp_name           */
    sizeof(Remote),                            /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)Remote_dealloc,                /* tp_dealloc        */
    0,                                         /* tp_print          */
    0,                                         /* tp_getattr        */
    0,                                         /* tp_setattr        */
    0,                                         /* tp_compare        */
    0,                                         /* tp_repr           */
    0,                                         /* tp_as_number      */
    0,                                         /* tp_as_sequence    */
    0,                                         /* tp_as_mapping     */
    0,                                         /* tp_hash           */
    (ternaryfunc) Remote_call,                               /* tp_call           */
    0,                                         /* tp_str            */
    0,                                         /* tp_getattro       */
    0,                                         /* tp_setattro       */
    0,                                         /* tp_as_buffer      */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,  /* tp_flags          */
    Remote__doc__,                             /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    0,                                         /* tp_methods        */
    0,                                         /* tp_members        */
    Remote_getseters,                          /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    0,                                         /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};
