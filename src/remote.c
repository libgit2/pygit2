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
#include <structmember.h>
#include "error.h"
#include "utils.h"
#include "types.h"
#include "remote.h"

extern PyObject *GitError;
extern PyTypeObject RepositoryType;

PyObject *
Remote_init(Remote *self, PyObject *args, PyObject *kwds)
{
    Repository* py_repo = NULL;
    char *name = NULL;
    int err;

    if (!PyArg_ParseTuple(args, "O!s", &RepositoryType, &py_repo, &name))
        return NULL;

    self->repo = py_repo;
    Py_INCREF(self->repo);
    err = git_remote_load(&self->remote, py_repo->repo, name);

    if (err < 0)
        return Error_set(err);

    return (PyObject*) self;
}


static void
Remote_dealloc(Remote *self)
{
    Py_CLEAR(self->repo);
    git_remote_free(self->remote);
    PyObject_Del(self);
}


PyDoc_STRVAR(Remote_name__doc__, "Name of the remote refspec");

PyObject *
Remote_name__get__(Remote *self)
{
    return to_unicode(git_remote_name(self->remote), NULL, NULL);
}

int
Remote_name__set__(Remote *self, PyObject* py_name)
{
    int err;
    char* name;

    name = py_str_to_c_str(py_name, NULL);
    if (name != NULL) {
        err = git_remote_rename(self->remote, name, NULL, NULL);
        free(name);

        if (err == GIT_OK)
          return 0;

        Error_set(err);
    }

    return -1;
}


PyDoc_STRVAR(Remote_url__doc__, "Url of the remote");

PyObject *
Remote_url__get__(Remote *self)
{
    return to_unicode(git_remote_url(self->remote), NULL, NULL);
}


int
Remote_url__set__(Remote *self, PyObject* py_url)
{
    int err;
    char* url = NULL;

    url = py_str_to_c_str(py_url, NULL);
    if (url != NULL) {
        err = git_remote_set_url(self->remote, url);
        free(url);

        if (err == GIT_OK)
          return 0;

        Error_set(err);
    }

    return -1;
}


PyDoc_STRVAR(Remote_fetchspec__doc__,
  "= (source:str, destination:str)\n"
  "\n"
  "Name of the remote source and destination fetch refspecs\n");


PyObject *
Remote_fetchspec__get__(Remote *self)
{
    PyObject* py_tuple = NULL;
    const git_refspec * refspec;

    refspec = git_remote_fetchspec(self->remote);
    if  (refspec != NULL) {
        py_tuple = Py_BuildValue(
            "(ss)",
            git_refspec_src(refspec),
            git_refspec_dst(refspec)
        );

        return py_tuple;
    }

    return Error_set(GIT_ENOTFOUND);
}

int
Remote_fetchspec__set__(Remote *self, PyObject* py_tuple)
{
    int err;
    size_t length = 0;
    char* src = NULL, *dst = NULL, *buf = NULL;

    if (!PyArg_ParseTuple(py_tuple, "ss", &src, &dst))
        return -1;

    /* length is strlen('+' + src + ':' + dst) and Null-Byte */
    length = strlen(src) + strlen(dst) + 3;
    buf = (char*) calloc(length, sizeof(char));
    if (buf != NULL) {
        sprintf(buf, "+%s:%s", src, dst);
        err = git_remote_set_fetchspec(self->remote, buf);
        free(buf);

        if (err == GIT_OK)
            return 0;

        Error_set_exc(PyExc_ValueError);
    }

    return -1;
}


PyDoc_STRVAR(Remote_fetch__doc__,
  "fetch() -> {'indexed_objects': int, 'received_objects' : int,"
  "            'received_bytesa' : int}\n"
  "\n"
  "Negotiate what objects should be downloaded and download the\n"
  "packfile with those objects");

PyObject *
Remote_fetch(Remote *self, PyObject *args)
{
    PyObject* py_stats = NULL;
    const git_transfer_progress *stats;
    int err;

    err = git_remote_connect(self->remote, GIT_DIRECTION_FETCH);
    if (err == GIT_OK) {
        err = git_remote_download(self->remote, NULL, NULL);
        if (err == GIT_OK) {
            stats = git_remote_stats(self->remote);
            py_stats = Py_BuildValue("{s:I,s:I,s:n}",
                "indexed_objects", stats->indexed_objects,
                "received_objects", stats->received_objects,
                "received_bytes", stats->received_bytes);

            err = git_remote_update_tips(self->remote);
        }
        git_remote_disconnect(self->remote);
    }

    if (err < 0)
        return Error_set(err);

    return (PyObject*) py_stats;
}


PyMethodDef Remote_methods[] = {
    METHOD(Remote, fetch, METH_NOARGS),
    {NULL}
};

PyGetSetDef Remote_getseters[] = {
    GETSET(Remote, name),
    GETSET(Remote, url),
    GETSET(Remote, fetchspec),
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
    0,                                         /* tp_call           */
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
    Remote_methods,                            /* tp_methods        */
    0,                                         /* tp_members        */
    Remote_getseters,                          /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    (initproc)Remote_init,                     /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};
