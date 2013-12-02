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


PyDoc_STRVAR(Remote_get_fetch_refspecs__doc__, "Fetch refspecs");


PyObject *
Remote_get_fetch_refspecs(Remote *self)
{
    int err;
    git_strarray refspecs;
    PyObject *new_list;

    err = git_remote_get_fetch_refspecs(&refspecs, self->remote);
    if (err != GIT_OK)
        return Error_set(err);

    new_list = get_pylist_from_git_strarray(&refspecs);

    git_strarray_free(&refspecs);
    return new_list;
}


PyDoc_STRVAR(Remote_get_push_refspecs__doc__, "Push refspecs");


PyObject *
Remote_get_push_refspecs(Remote *self)
{
    int err;
    git_strarray refspecs;
    PyObject *new_list;

    err = git_remote_get_push_refspecs(&refspecs, self->remote);
    if (err != GIT_OK)
        return Error_set(err);

    new_list = get_pylist_from_git_strarray(&refspecs);

    git_strarray_free(&refspecs);
    return new_list;
}


int
get_strarraygit_from_pylist(git_strarray *array, PyObject *pylist)
{
    long index, n;
    PyObject *item;
    void *ptr;

    n = PyObject_Length(pylist);
    if (n < 0)
        return -1;

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
        array->strings[index] = py_str_to_c_str(item, NULL);
    }

    return GIT_OK;
}


PyDoc_STRVAR(Remote_set_fetch_refspecs__doc__,
    "set_fetch_refspecs([str])\n"
    "\n");


PyObject *
Remote_set_fetch_refspecs(Remote *self, PyObject *args)
{
    int err;
    PyObject *pyrefspecs;
    git_strarray fetch_refspecs;

    if (! PyArg_Parse(args, "O", &pyrefspecs))
        return NULL;

    if (get_strarraygit_from_pylist(&fetch_refspecs, pyrefspecs) != GIT_OK)
        return NULL;

    err = git_remote_set_fetch_refspecs(self->remote, &fetch_refspecs);
    git_strarray_free(&fetch_refspecs);

    if (err != GIT_OK)
        return Error_set(err);

    Py_RETURN_NONE;
}


PyDoc_STRVAR(Remote_set_push_refspecs__doc__,
    "set_push_refspecs([str])\n"
    "\n");


PyObject *
Remote_set_push_refspecs(Remote *self, PyObject *args)
{
    int err;
    PyObject *pyrefspecs;
    git_strarray push_refspecs;

    if (! PyArg_Parse(args, "O", &pyrefspecs))
        return NULL;

    if (get_strarraygit_from_pylist(&push_refspecs, pyrefspecs) != 0)
        return NULL;

    err = git_remote_set_push_refspecs(self->remote, &push_refspecs);
    git_strarray_free(&push_refspecs);

    if (err != GIT_OK)
        return Error_set(err);

    Py_RETURN_NONE;
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


PyDoc_STRVAR(Remote_refspec_count__doc__, "Number of refspecs.");

PyObject *
Remote_refspec_count__get__(Remote *self)
{
    size_t count;

    count = git_remote_refspec_count(self->remote);
    return PyLong_FromSize_t(count);
}


PyDoc_STRVAR(Remote_get_refspec__doc__,
    "get_refspec(n) -> (str, str)\n"
    "\n"
    "Return the refspec at the given position.");

PyObject *
Remote_get_refspec(Remote *self, PyObject *value)
{
    size_t n;
    const git_refspec *refspec;

    n = PyLong_AsSize_t(value);
    if (PyErr_Occurred())
        return NULL;

    refspec = git_remote_get_refspec(self->remote, n);
    if (refspec == NULL) {
        PyErr_SetObject(PyExc_IndexError, value);
        return NULL;
    }

    return Py_BuildValue("(ss)", git_refspec_src(refspec),
                                 git_refspec_dst(refspec));
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
        err = git_remote_download(self->remote);
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


PyDoc_STRVAR(Remote_save__doc__,
  "save()\n\n"
  "Save a remote to its repository configuration.");

PyObject *
Remote_save(Remote *self, PyObject *args)
{
    int err;

    err = git_remote_save(self->remote);
    if (err == GIT_OK) {
        Py_RETURN_NONE;
    }
    else {
        return Error_set(err);
    }
}


int
push_status_foreach_callback(const char *ref, const char *msg, void *data)
{
    const char **msg_dst = (const char **)data;
    if (msg != NULL && *msg_dst == NULL)
        *msg_dst = msg;
    return 0;
}

PyDoc_STRVAR(Remote_push__doc__,
    "push(refspec)\n"
    "\n"
    "Push the given refspec to the remote.  Raises ``GitError`` on error.");

PyObject *
Remote_push(Remote *self, PyObject *args)
{
    git_push *push = NULL;
    const char *refspec = NULL;
    const char *msg = NULL;
    int err;

    if (!PyArg_ParseTuple(args, "s", &refspec))
        return NULL;

    err = git_push_new(&push, self->remote);
    if (err < 0)
        return Error_set(err);

    err = git_push_add_refspec(push, refspec);
    if (err < 0)
        goto error;

    err = git_push_finish(push);
    if (err < 0)
        goto error;

    if (!git_push_unpack_ok(push)) {
        git_push_free(push);
        PyErr_SetString(GitError, "Remote failed to unpack objects");
        return NULL;
    }

    err = git_push_status_foreach(push, push_status_foreach_callback, &msg);
    if (err < 0)
        goto error;
    if (msg != NULL) {
        git_push_free(push);
        PyErr_SetString(GitError, msg);
        return NULL;
    }

    err = git_push_update_tips(push);
    if (err < 0)
        goto error;

    git_push_free(push);
    Py_RETURN_NONE;

error:
    git_push_free(push);
    return Error_set(err);
}


PyMethodDef Remote_methods[] = {
    METHOD(Remote, fetch, METH_NOARGS),
    METHOD(Remote, save, METH_NOARGS),
    METHOD(Remote, get_refspec, METH_O),
    METHOD(Remote, push, METH_VARARGS),
    METHOD(Remote, get_fetch_refspecs, METH_NOARGS),
    METHOD(Remote, set_fetch_refspecs, METH_O),
    METHOD(Remote, get_push_refspecs, METH_NOARGS),
    METHOD(Remote, set_push_refspecs, METH_O),
    {NULL}
};

PyGetSetDef Remote_getseters[] = {
    GETSET(Remote, name),
    GETSET(Remote, url),
    GETTER(Remote, refspec_count),
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
