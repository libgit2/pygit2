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
#include <structmember.h>
#include "error.h"
#include "types.h"
#include "utils.h"
#include "oid.h"
#include "refspec.h"
#include "remote.h"


extern PyObject *GitError;
extern PyTypeObject RepositoryType;
extern PyTypeObject TransferProgressType;

PyObject *
wrap_transfer_progress(const git_transfer_progress *stats)
{
    TransferProgress *py_stats;

    py_stats = PyObject_New(TransferProgress, &TransferProgressType);
    if (!py_stats)
        return NULL;

    py_stats->total_objects = stats->total_objects;
    py_stats->indexed_objects = stats->indexed_objects;
    py_stats->received_objects = stats->received_objects;
    py_stats->local_objects = stats->local_objects;
    py_stats->total_deltas = stats->total_deltas;
    py_stats->indexed_deltas = stats->indexed_deltas;
    py_stats->received_bytes = stats->received_bytes;

    return (PyObject *) py_stats;
}

void
TransferProgress_dealloc(TransferProgress *self)
{
    PyObject_Del(self);
}

PyMemberDef TransferProgress_members[] = {
    RMEMBER(TransferProgress, total_objects, T_UINT, "Total number objects to download"),
    RMEMBER(TransferProgress, indexed_objects, T_UINT, "Objects which have been indexed"),
    RMEMBER(TransferProgress, received_objects, T_UINT, "Objects which have been received up to now"),
    RMEMBER(TransferProgress, local_objects, T_UINT, "Local objects which were used to fix the thin pack"),
    RMEMBER(TransferProgress, total_deltas, T_UINT, "Total number of deltas in the pack"),
    RMEMBER(TransferProgress, indexed_deltas, T_UINT, "Deltas which have been indexed"),
    /* FIXME: technically this is unsigned, but there's no value for size_t here. */
    RMEMBER(TransferProgress, received_bytes, T_PYSSIZET, "Number of bytes received up to now"),
    {NULL},
};

PyDoc_STRVAR(TransferProgress__doc__, "Progress downloading and indexing data during a fetch");

PyTypeObject TransferProgressType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.TransferProgress",                /* tp_name           */
    sizeof(TransferProgress),                            /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)TransferProgress_dealloc,      /* tp_dealloc        */
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
    TransferProgress__doc__,                            /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    0,                                         /* tp_methods        */
    TransferProgress_members,                  /* tp_members        */
    0,                                         /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    0,                                         /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};

static int
progress_cb(const char *str, int len, void *data)
{
    Remote *remote = (Remote *) data;
    PyObject *arglist, *ret;

    if (remote->progress == NULL)
        return 0;

    if (!PyCallable_Check(remote->progress)) {
        PyErr_SetString(PyExc_TypeError, "progress callback is not callable");
        return -1;
    }

    arglist = Py_BuildValue("(s#)", str, len);
    ret = PyObject_CallObject(remote->progress, arglist);
    Py_DECREF(arglist);

    if (!ret)
        return -1;

    Py_DECREF(ret);

    return 0;
}

static int
transfer_progress_cb(const git_transfer_progress *stats, void *data)
{
    Remote *remote = (Remote *) data;
    PyObject *py_stats, *ret;

    if (remote->transfer_progress == NULL)
        return 0;

    if (!PyCallable_Check(remote->transfer_progress)) {
        PyErr_SetString(PyExc_TypeError, "transfer progress callback is not callable");
        return -1;
    }

    py_stats = wrap_transfer_progress(stats);
    if (!py_stats)
        return -1;

    ret = PyObject_CallFunctionObjArgs(remote->transfer_progress, py_stats, NULL);
    if (!ret)
        return -1;

    Py_DECREF(ret);

    return 0;
}

static int
update_tips_cb(const char *refname, const git_oid *a, const git_oid *b, void *data)
{
    Remote *remote = (Remote *) data;
    PyObject *ret;
    PyObject *old, *new;

    if (remote->update_tips == NULL)
        return 0;

    if (!PyCallable_Check(remote->update_tips)) {
        PyErr_SetString(PyExc_TypeError, "update tips callback is not callable");
        return -1;
    }

    old = git_oid_to_python(a);
    new = git_oid_to_python(b);

    ret = PyObject_CallFunction(remote->update_tips, "(s,O,O)", refname, old ,new);

    Py_DECREF(old);
    Py_DECREF(new);

    if (!ret)
        return -1;

    Py_DECREF(ret);

    return 0;
}

static void
Remote_dealloc(Remote *self)
{
    Py_CLEAR(self->repo);
    Py_CLEAR(self->progress);
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
    const char* name;
    PyObject *tname;

    name = py_str_borrow_c_str(&tname, py_name, NULL);
    if (name != NULL) {
        err = git_remote_rename(self->remote, name, NULL, NULL);
	Py_DECREF(tname);

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

int
get_strarraygit_from_pylist(git_strarray *array, PyObject *pylist)
{
    Py_ssize_t index, n;
    PyObject *item;
    void *ptr;

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
        char *str = py_str_to_c_str(item, NULL);
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

PyDoc_STRVAR(Remote_fetch_refspecs__doc__, "Fetch refspecs");

PyObject *
Remote_fetch_refspecs__get__(Remote *self)
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

int
Remote_fetch_refspecs__set__(Remote *self, PyObject *py_list)
{
    int err;
    git_strarray fetch_refspecs;

    if (get_strarraygit_from_pylist(&fetch_refspecs, py_list) < 0)
        return -1;

    err = git_remote_set_fetch_refspecs(self->remote, &fetch_refspecs);
    git_strarray_free(&fetch_refspecs);

    if (err < 0) {
        Error_set(err);
        return -1;
    }

    return 0;
}

PyDoc_STRVAR(Remote_push_refspecs__doc__, "Push refspecs");

PyObject *
Remote_push_refspecs__get__(Remote *self)
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
Remote_push_refspecs__set__(Remote *self, PyObject *py_list)
{
    int err;
    git_strarray push_refspecs;

    if (get_strarraygit_from_pylist(&push_refspecs, py_list) != 0)
        return -1;

    err = git_remote_set_push_refspecs(self->remote, &push_refspecs);
    git_strarray_free(&push_refspecs);

    if (err < 0) {
        Error_set(err);
        return -1;
    }

    return 0;
}


PyDoc_STRVAR(Remote_url__doc__, "Url of the remote");


PyObject *
Remote_url__get__(Remote *self)
{
    const char *url;

    url = git_remote_url(self->remote);
    if (!url)
        Py_RETURN_NONE;

    return to_unicode(url, NULL, NULL);
}


int
Remote_url__set__(Remote *self, PyObject* py_url)
{
    int err;
    const char* url = NULL;
    PyObject *turl;

    url = py_str_borrow_c_str(&turl, py_url, NULL);
    if (url != NULL) {
        err = git_remote_set_url(self->remote, url);
	Py_DECREF(turl);

        if (err == GIT_OK)
            return 0;

        Error_set(err);
    }

    return -1;
}

PyDoc_STRVAR(Remote_push_url__doc__, "Push url of the remote");


PyObject *
Remote_push_url__get__(Remote *self)
{
    const char *url;

    url = git_remote_pushurl(self->remote);
    if (!url)
        Py_RETURN_NONE;

    return to_unicode(url, NULL, NULL);
}


int
Remote_push_url__set__(Remote *self, PyObject* py_url)
{
    int err;
    const char* url = NULL;
    PyObject *turl;

    url = py_str_borrow_c_str(&turl, py_url, NULL);
    if (url != NULL) {
        err = git_remote_set_pushurl(self->remote, url);
	Py_DECREF(turl);

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

    return (PyObject*) wrap_refspec(self, refspec);
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

    PyErr_Clear();
    err = git_remote_fetch(self->remote);
    /*
     * XXX: We should be checking for GIT_EUSER, but on v0.20, this does not
     * make it all the way to us for update_tips
     */
    if (err < 0 && PyErr_Occurred())
        return NULL;
    if (err < 0)
        return Error_set(err);

    stats = git_remote_stats(self->remote);
    py_stats = Py_BuildValue("{s:I,s:I,s:n}",
        "indexed_objects", stats->indexed_objects,
        "received_objects", stats->received_objects,
        "received_bytes", stats->received_bytes);

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


PyDoc_STRVAR(Remote_add_push__doc__,
    "add_push(refspec)\n"
    "\n"
    "Add a push refspec to the remote.");

PyObject *
Remote_add_push(Remote *self, PyObject *args)
{
    git_remote *remote;
    char *refspec = NULL;
    int err = 0;

    if (!PyArg_ParseTuple(args, "s", &refspec))
        return NULL;

    remote = self->remote;
    err = git_remote_add_push(remote, refspec);
    if (err < 0)
        return Error_set(err);

    Py_RETURN_NONE;
}


PyDoc_STRVAR(Remote_add_fetch__doc__,
    "add_fetch(refspec)\n"
    "\n"
    "Add a fetch refspec to the remote.");

PyObject *
Remote_add_fetch(Remote *self, PyObject *args)
{
    git_remote *remote;
    char *refspec = NULL;
    int err = 0;

    if (!PyArg_ParseTuple(args, "s", &refspec))
        return NULL;

    remote = self->remote;
    err = git_remote_add_fetch(remote, refspec);
    if (err < 0)
        return Error_set(err);

    Py_RETURN_NONE;
}

PyMethodDef Remote_methods[] = {
    METHOD(Remote, fetch, METH_NOARGS),
    METHOD(Remote, save, METH_NOARGS),
    METHOD(Remote, get_refspec, METH_O),
    METHOD(Remote, push, METH_VARARGS),
    METHOD(Remote, add_push, METH_VARARGS),
    METHOD(Remote, add_fetch, METH_VARARGS),
    {NULL}
};

PyGetSetDef Remote_getseters[] = {
    GETSET(Remote, name),
    GETSET(Remote, url),
    GETSET(Remote, push_url),
    GETTER(Remote, refspec_count),
    GETSET(Remote, fetch_refspecs),
    GETSET(Remote, push_refspecs),
    {NULL}
};

PyMemberDef Remote_members[] = {
    MEMBER(Remote, progress, T_OBJECT_EX, "Progress output callback"),
    MEMBER(Remote, transfer_progress, T_OBJECT_EX, "Transfer progress callback"),
    MEMBER(Remote, update_tips, T_OBJECT_EX, "update tips callback"),
    {NULL},
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
    Remote_members,                            /* tp_members        */
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

PyObject *
wrap_remote(git_remote *c_remote, Repository *repo)
{
    Remote *py_remote = NULL;
    git_remote_callbacks callbacks = GIT_REMOTE_CALLBACKS_INIT;

    py_remote = PyObject_New(Remote, &RemoteType);
    if (py_remote) {
        Py_INCREF(repo);
        py_remote->repo = repo;
        py_remote->remote = c_remote;
        py_remote->progress = NULL;
        py_remote->transfer_progress = NULL;
        py_remote->update_tips = NULL;

        callbacks.progress = progress_cb;
        callbacks.transfer_progress = transfer_progress_cb;
        callbacks.update_tips = update_tips_cb;
        callbacks.payload = py_remote;
        git_remote_set_callbacks(c_remote, &callbacks);
    }

    return (PyObject *)py_remote;
}
