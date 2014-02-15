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
#include "diff.h"
#include "error.h"
#include "patch.h"
#include "types.h"
#include "utils.h"

extern PyObject *GitError;

extern PyTypeObject BlobType;
extern PyTypeObject DiffType;
extern PyTypeObject DiffHunkType;
extern PyTypeObject IndexType;
extern PyTypeObject PatchType;
extern PyTypeObject TreeType;

PyObject *
wrap_patch(git_patch *patch)
{
    Patch *py_patch;

    if (!patch)
        Py_RETURN_NONE;

    py_patch = PyObject_New(Patch, &PatchType);
    if (py_patch) {
        py_patch->patch = patch;
    }

    return (PyObject*) py_patch;
}

PyObject *
patch_get_hunk_byindex(Patch *self, size_t idx)
{
    const git_diff_hunk *hunk = NULL;
    int err;

    err = git_patch_get_hunk(&hunk, NULL, self->patch, idx);
    if (err < 0)
        return Error_set(err);

    return (PyObject*) wrap_diff_hunk(hunk, idx, self);
}

PyObject *
PatchIter_iternext(PatchIter *self)
{
    if (self->i < self->n)
        return patch_get_hunk_byindex(self->patch, self->i++);

    PyErr_SetNone(PyExc_StopIteration);
    return NULL;
}

static void
PatchIter_dealloc(PatchIter *self)
{
    Py_CLEAR(self->patch);
    PyObject_Del(self);
}


PyDoc_STRVAR(PatchIter__doc__, "Patch iterator object.");

PyTypeObject PatchIterType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.PatchIter",                       /* tp_name           */
    sizeof(PatchIter),                         /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)PatchIter_dealloc,             /* tp_dealloc        */
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
    PatchIter__doc__,                          /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    PyObject_SelfIter,                         /* tp_iter           */
    (iternextfunc) PatchIter_iternext,         /* tp_iternext       */
};


PyObject *
Patch_iter(Patch *self)
{
    PatchIter *iter;

    iter = PyObject_New(PatchIter, &PatchIterType);
    if (iter != NULL) {
        Py_INCREF(self);
        iter->patch = self;
        iter->i = 0;
        iter->n = git_patch_num_hunks(self->patch);
    }
    return (PyObject*)iter;
}

Py_ssize_t
Patch_len(Patch *self)
{
    assert(self->patch);
    return (Py_ssize_t)git_patch_num_hunks(self->patch);
}

PyObject *
Patch_getitem(Patch *self, PyObject *value)
{
    size_t i;

    if (PyLong_Check(value) < 0) {
        PyErr_SetObject(PyExc_IndexError, value);
        return NULL;
    }

    i = PyLong_AsUnsignedLong(value);
    if (PyErr_Occurred()) {
        PyErr_SetObject(PyExc_IndexError, value);
        return NULL;
    }

    return patch_get_hunk_byindex(self, i);
}

PyObject *
Patch__str__(Patch *self)
{
    git_buf buf = {NULL};
    int err;
    PyObject *py_str;

    err = git_patch_to_buf(&buf, self->patch);
    if (err < 0)
        goto cleanup;

    py_str = to_unicode(buf.ptr, NULL, NULL);

cleanup:
    git_buf_free(&buf);
    return (err < 0) ? Error_set(err) : py_str;
}

PyDoc_STRVAR(Patch_from_blob_and_buffer__doc__,
  "from_blob_and_buffer([old_blob, old_as_path, buffer, buffer_as_path,\n"
  "                      flags] -> Patch\n"
  "\n"
  "Directly generate a :py:class:`~pygit2.Patch` from the difference\n"
  "between a blob and a buffer.\n"
  "\n"
  ":param Blob old_blob: the :py:class:`~pygit2.Blob` for old side of diff.\n"
  "\n"
  ":param str old_as_path: treat old blob as if it had this filename.\n"
  "\n"
  ":param Blob buffer: Raw data for new side of diff.\n"
  "\n"
  ":param str buffer_as_path: treat buffer as if it had this filename.\n"
  "\n"
  ":param flag: a GIT_DIFF_* constant.\n"
  "\n"
  ":rtype: Patch\n");

PyObject *
Patch_from_blob_and_buffer(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    git_diff_options opts = GIT_DIFF_OPTIONS_INIT;
    git_patch *patch;
    char *old_as_path = NULL, *buffer_as_path = NULL;
    const char *buffer = NULL;
    Py_ssize_t buffer_len;
    Blob *py_old_blob = NULL;
    int err;
    char *keywords[] = {"old_blob", "old_as_path", "buffer", "buffer_as_path",
                        "flags", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|O!ss#sI", keywords,
                                     &BlobType, &py_old_blob, &old_as_path,
                                     &buffer, &buffer_len, &buffer_as_path,
                                     &opts.flags))
        return NULL;

    err = git_patch_from_blob_and_buffer(&patch,
                                         py_old_blob ? py_old_blob->blob : NULL,
                                         old_as_path,
                                         buffer,
                                         buffer_len,
                                         buffer_as_path,
                                         &opts);
    if (err < 0)
        return Error_set(err);

    return wrap_patch(patch);
}


PyDoc_STRVAR(Patch_from_blobs__doc__,
  "from_blobs([old_blob, old_as_path, new_blob, new_as_path, flags] -> Patch\n"
  "\n"
  "Directly generate a :py:class:`pygit2.Patch` from the difference\n"
  "between two blobs.\n"
  "\n"
  ":param Blob old_blob: the :py:class:`~pygit2.Blob` for old side of diff.\n"
  "\n"
  ":param str old_as_path: treat old blob as if it had this filename.\n"
  "\n"
  ":param Blob new_blob: the :py:class:`~pygit2.Blob` for new side of diff.\n"
  "\n"
  ":param str new_as_path: treat new blob as if it had this filename.\n"
  "\n"
  ":param flag: a GIT_DIFF_* constant.\n"
  "\n"
  ":rtype: Patch\n");

PyObject *
Patch_from_blobs(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    git_diff_options opts = GIT_DIFF_OPTIONS_INIT;
    git_patch *patch;
    char *old_as_path = NULL, *new_as_path = NULL;
    Blob *py_new_blob = NULL, *py_old_blob = NULL;
    int err;
    char *keywords[] = {"old_blob", "old_as_path", "new_blob",  "new_as_path",
                        "flags", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|O!sO!sI", keywords,
                                     &BlobType, &py_old_blob, &old_as_path,
                                     &BlobType, &py_new_blob, &new_as_path,
                                     &opts.flags))
        return NULL;

    err = git_patch_from_blobs(&patch,
                               py_old_blob ? py_old_blob->blob : NULL,
                               old_as_path,
                               py_new_blob ? py_new_blob->blob : NULL,
                               new_as_path,
                               &opts);
    if (err < 0)
        return Error_set(err);

    return wrap_patch(patch);
}


PyDoc_STRVAR(Patch_from_diff__doc__,
  "from_diff(diff, idx) -> Patch\n"
  "\n"
  "Return the :py:class:`pygit2.Patch` for an entry in the diff list.\n"
  "\n"
  "Arguments:\n"
  "\n"
  "diff: the :py:class:`~pygit2.Diff` list object.\n"
  "\n"
  "idx: index into diff list.\n");

PyObject *
Patch_from_diff(PyTypeObject *type, PyObject *args)
{
    git_patch *patch;
    Diff *py_diff;
    Py_ssize_t idx;
    int err;

    if (!PyArg_ParseTuple(args, "O!n", &DiffType, &py_diff, &idx))
        return NULL;

    err = git_patch_from_diff(&patch, py_diff->diff, idx);
    if (err < 0)
        return Error_set(err);

    return wrap_patch(patch);
}


PyDoc_STRVAR(Patch_size__doc__,
  "size([include_context, include_hunk_headers, include_file_headers]) -> size\n"
  "\n"
  "Look up size of patch diff data in bytes.\n"
  "\n"
  "Arguments:\n"
  "\n"
  "include_context: include context lines in size if non-zero.\n"
  "\n"
  "include_hunk_headers: include hunk header lines if non-zero.\n"
  "\n"
  "include_file_headers: include file header lines if non-zero.");

PyObject *
Patch_size(Patch *self, PyObject *args, PyObject *kwds)
{
    int context = 0, hunk_headers = 0, file_headers = 0;
    PyObject *py_context = NULL;
    PyObject *py_hunk_headers = NULL;
    PyObject *py_file_headers = NULL;
    char *keywords[] = {"include_context", "include_hunk_headers",
                        "include_file_headers", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|O!O!O!", keywords,
                                     &PyBool_Type, &py_context,
                                     &PyBool_Type, &py_hunk_headers,
                                     &PyBool_Type, &py_file_headers))
        return NULL;

    if (py_context)
        context = PyObject_IsTrue(py_context);
    if (py_hunk_headers)
        hunk_headers = PyObject_IsTrue(py_hunk_headers);
    if (py_file_headers)
        file_headers = PyObject_IsTrue(py_file_headers);

    return PyLong_FromSize_t(git_patch_size(self->patch,
                context, hunk_headers, file_headers));
}


PyDoc_STRVAR(Patch_delta__doc__, "Get the delta associated with a patch.");

PyObject *
Patch_delta__get__(Patch *self)
{
    if (!self->patch)
        Py_RETURN_NONE;

    return wrap_diff_delta(git_patch_get_delta(self->patch)); 
}

PyDoc_STRVAR(Patch_line_stats__doc__, "Get line counts of each type in a patch.");

PyObject *
Patch_line_stats__get__(Patch *self)
{
    size_t context, additions, deletions;
    int err;

    if (!self->patch)
        Py_RETURN_NONE;

    err = git_patch_line_stats(&context, &additions, &deletions,
                               self->patch);
    if (err < 0)
        return Error_set(err);

    return Py_BuildValue("III", context, additions, deletions);
}

void
Patch_dealloc(Patch *self)
{
    git_patch_free(self->patch);
    PyObject_Del(self);
}

PyMappingMethods Patch_as_mapping = {
    (lenfunc)Patch_len,           /* mp_length */
    (binaryfunc)Patch_getitem,    /* mp_subscript */
    0,                            /* mp_ass_subscript */
};

PyMethodDef Patch_methods[] = {
    METHOD(Patch, from_blob_and_buffer, METH_VARARGS | METH_KEYWORDS | METH_CLASS),
    METHOD(Patch, from_blobs, METH_VARARGS | METH_KEYWORDS | METH_CLASS),
    METHOD(Patch, from_diff, METH_VARARGS | METH_KEYWORDS | METH_CLASS),
    METHOD(Patch, size, METH_VARARGS | METH_KEYWORDS),
    {NULL}
};

PyGetSetDef Patch_getseters[] = {
    GETTER(Patch, delta),
    GETTER(Patch, line_stats),
    {NULL}
};

PyDoc_STRVAR(Patch__doc__, "Patch object.");

PyTypeObject PatchType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.Patch",                           /* tp_name           */
    sizeof(Patch),                             /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)Patch_dealloc,                 /* tp_dealloc        */
    0,                                         /* tp_print          */
    0,                                         /* tp_getattr        */
    0,                                         /* tp_setattr        */
    0,                                         /* tp_compare        */
    0,                                         /* tp_repr           */
    0,                                         /* tp_as_number      */
    0,                                         /* tp_as_sequence    */
    &Patch_as_mapping,                         /* tp_as_mapping     */
    0,                                         /* tp_hash           */
    0,                                         /* tp_call           */
    (reprfunc)Patch__str__,                    /* tp_str            */
    0,                                         /* tp_getattro       */
    0,                                         /* tp_setattro       */
    0,                                         /* tp_as_buffer      */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,  /* tp_flags          */
    Patch__doc__,                              /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    (getiterfunc)Patch_iter,                   /* tp_iter           */
    0,                                         /* tp_iternext       */
    Patch_methods,                             /* tp_methods        */
    0,                                         /* tp_members        */
    Patch_getseters,                           /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    0,                                         /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};
