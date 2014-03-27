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
#include "diff.h"
#include "error.h"
#include "utils.h"
#include "object.h"
#include "blob.h"

extern PyObject *GitError;

extern PyTypeObject BlobType;

PyDoc_STRVAR(Blob_diff__doc__,
  "diff([blob, flag, old_as_path, new_as_path] -> Patch\n"
  "\n"
  "Directly generate a :py:class:`pygit2.Patch` from the difference\n"
  "  between two blobs.\n"
  "\n"
  "Arguments:\n"
  "\n"
  "blob: the :py:class:`~pygit2.Blob` to diff.\n"
  "\n"
  "flag: a GIT_DIFF_* constant.\n"
  "\n"
  "old_as_path: treat old blob as if it had this filename.\n"
  "\n"
  "new_as_path: treat new blob as if it had this filename.\n");

PyObject *
Blob_diff(Blob *self, PyObject *args, PyObject *kwds)
{
    git_diff_options opts = GIT_DIFF_OPTIONS_INIT;
    git_patch *patch;
    char *old_as_path = NULL, *new_as_path = NULL;
    Blob *py_blob = NULL;
    int err;
    char *keywords[] = {"blob", "flag", "old_as_path", "new_as_path", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|O!ssI", keywords,
                                     &BlobType, &py_blob, &opts.flags,
                                     &old_as_path, &new_as_path))
        return NULL;

    err = git_patch_from_blobs(&patch, self->blob, old_as_path,
                               py_blob ? py_blob->blob : NULL, new_as_path,
                               &opts);
    if (err < 0)
        return Error_set(err);

    return wrap_patch(patch);
}


PyDoc_STRVAR(Blob_diff_to_buffer__doc__,
  "diff_to_buffer([buffer, flag, old_as_path, buffer_as_path] -> Patch\n"
  "\n"
  "Directly generate a :py:class:`~pygit2.Patch` from the difference\n"
  "  between a blob and a buffer.\n"
  "\n"
  "Arguments:\n"
  "\n"
  "buffer: Raw data for new side of diff.\n"
  "\n"
  "flag: a GIT_DIFF_* constant.\n"
  "\n"
  "old_as_path: treat old blob as if it had this filename.\n"
  "\n"
  "buffer_as_path: treat buffer as if it had this filename.\n");

PyObject *
Blob_diff_to_buffer(Blob *self, PyObject *args, PyObject *kwds)
{
    git_diff_options opts = GIT_DIFF_OPTIONS_INIT;
    git_patch *patch;
    char *old_as_path = NULL, *buffer_as_path = NULL;
    const char *buffer = NULL;
    Py_ssize_t buffer_len;
    int err;
    char *keywords[] = {"buffer", "flag", "old_as_path", "buffer_as_path",
                        NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|s#ssI", keywords,
                                     &buffer, &buffer_len, &opts.flags,
                                     &old_as_path, &buffer_as_path))
        return NULL;

    err = git_patch_from_blob_and_buffer(&patch, self->blob, old_as_path,
                                         buffer, buffer_len, buffer_as_path,
                                         &opts);
    if (err < 0)
        return Error_set(err);

    return wrap_patch(patch);
}

static PyMethodDef Blob_methods[] = {
    METHOD(Blob, diff, METH_VARARGS | METH_KEYWORDS),
    METHOD(Blob, diff_to_buffer, METH_VARARGS | METH_KEYWORDS),
    {NULL}
};


PyDoc_STRVAR(Blob_size__doc__, "Size.");

PyObject *
Blob_size__get__(Blob *self)
{
    return PyLong_FromLongLong(git_blob_rawsize(self->blob));
}


PyDoc_STRVAR(Blob_is_binary__doc__, "True if binary data, False if not.");

PyObject *
Blob_is_binary__get__(Blob *self)
{
    if (git_blob_is_binary(self->blob))
        Py_RETURN_TRUE;
    Py_RETURN_FALSE;
}


PyDoc_STRVAR(Blob_data__doc__,
  "The contents of the blob, a bytes string. This is the same as\n"
  "Blob.read_raw()");

PyGetSetDef Blob_getseters[] = {
    GETTER(Blob, size),
    GETTER(Blob, is_binary),
    {"data", (getter)Object_read_raw, NULL, Blob_data__doc__, NULL},
    {NULL}
};


PyDoc_STRVAR(Blob__doc__, "Blob objects.");

PyTypeObject BlobType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.Blob",                            /* tp_name           */
    sizeof(Blob),                              /* tp_basicsize      */
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
    0,                                         /* tp_hash           */
    0,                                         /* tp_call           */
    0,                                         /* tp_str            */
    0,                                         /* tp_getattro       */
    0,                                         /* tp_setattro       */
    0,                                         /* tp_as_buffer      */
    Py_TPFLAGS_DEFAULT,                        /* tp_flags          */
    Blob__doc__,                               /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    Blob_methods,                              /* tp_methods        */
    0,                                         /* tp_members        */
    Blob_getseters,                            /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    0,                                         /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};
