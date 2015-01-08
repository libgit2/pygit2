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
#include "diff.h"

extern PyObject *GitError;

extern PyTypeObject TreeType;
extern PyTypeObject IndexType;
extern PyTypeObject DiffType;
extern PyTypeObject HunkType;
extern PyTypeObject RepositoryType;

PyTypeObject PatchType;

PyObject *
wrap_diff(git_diff *diff, Repository *repo)
{
    Diff *py_diff;

    py_diff = PyObject_New(Diff, &DiffType);
    if (py_diff) {
        Py_INCREF(repo);
        py_diff->repo = repo;
        py_diff->diff = diff;
    }

    return (PyObject*) py_diff;
}

PyObject *
wrap_patch(git_patch *patch)
{
    Patch *py_patch;

    if (!patch)
        Py_RETURN_NONE;

    py_patch = PyObject_New(Patch, &PatchType);
    if (py_patch) {
        size_t i, j, hunk_amounts, lines_in_hunk, additions, deletions;
        const git_diff_delta *delta;
        const git_diff_hunk *hunk;
        const git_diff_line *line;
        int err;

        delta = git_patch_get_delta(patch);

        py_patch->old_file_path = strdup(delta->old_file.path);
        py_patch->new_file_path = strdup(delta->new_file.path);
        py_patch->status = git_diff_status_char(delta->status);
        py_patch->similarity = delta->similarity;
        py_patch->flags = delta->flags;
        py_patch->old_id = git_oid_to_python(&delta->old_file.id);
        py_patch->new_id = git_oid_to_python(&delta->new_file.id);

        git_patch_line_stats(NULL, &additions, &deletions, patch);
        py_patch->additions = additions;
        py_patch->deletions = deletions;

        hunk_amounts = git_patch_num_hunks(patch);
        py_patch->hunks = PyList_New(hunk_amounts);
        for (i = 0; i < hunk_amounts; ++i) {
            Hunk *py_hunk = NULL;

            err = git_patch_get_hunk(&hunk, &lines_in_hunk, patch, i);
            if (err < 0)
                return Error_set(err);

            py_hunk = PyObject_New(Hunk, &HunkType);
            if (py_hunk != NULL) {
                py_hunk->old_start = hunk->old_start;
                py_hunk->old_lines = hunk->old_lines;
                py_hunk->new_start = hunk->new_start;
                py_hunk->new_lines = hunk->new_lines;

                py_hunk->lines = PyList_New(lines_in_hunk);
                for (j = 0; j < lines_in_hunk; ++j) {
                    PyObject *py_line_origin = NULL, *py_line = NULL;

                    err = git_patch_get_line_in_hunk(&line, patch, i, j);
                    if (err < 0)
                        return Error_set(err);

                    py_line_origin = to_unicode_n(&line->origin, 1,
                        NULL, NULL);
                    py_line = to_unicode_n(line->content, line->content_len,
                        NULL, NULL);
                    PyList_SetItem(py_hunk->lines, j,
                        Py_BuildValue("OO", py_line_origin, py_line));

                    Py_DECREF(py_line_origin);
                    Py_DECREF(py_line);
                }

                PyList_SetItem((PyObject*) py_patch->hunks, i,
                    (PyObject*) py_hunk);
            }
        }
    }
    git_patch_free(patch);

    return (PyObject*) py_patch;
}

PyObject *
diff_get_patch_byindex(git_diff *diff, size_t idx)
{
    git_patch *patch = NULL;
    int err;

    err = git_patch_from_diff(&patch, diff, idx);
    if (err < 0)
        return Error_set(err);

    return (PyObject*) wrap_patch(patch);
}

static void
Patch_dealloc(Patch *self)
{
    Py_CLEAR(self->hunks);
    Py_CLEAR(self->old_id);
    Py_CLEAR(self->new_id);
    free(self->old_file_path);
    free(self->new_file_path);
    PyObject_Del(self);
}

PyMemberDef Patch_members[] = {
    MEMBER(Patch, old_file_path, T_STRING, "old file path"),
    MEMBER(Patch, new_file_path, T_STRING, "new file path"),
    MEMBER(Patch, old_id, T_OBJECT, "old oid"),
    MEMBER(Patch, new_id, T_OBJECT, "new oid"),
    MEMBER(Patch, status, T_CHAR, "status"),
    MEMBER(Patch, similarity, T_INT, "similarity"),
    MEMBER(Patch, hunks, T_OBJECT, "hunks"),
    MEMBER(Patch, additions, T_INT, "additions"),
    MEMBER(Patch, deletions, T_INT, "deletions"),
    {NULL}
};

PyDoc_STRVAR(Patch_is_binary__doc__, "True if binary data, False if not.");

PyObject *
Patch_is_binary__get__(Patch *self)
{
    if (!(self->flags & GIT_DIFF_FLAG_NOT_BINARY) &&
            (self->flags & GIT_DIFF_FLAG_BINARY))
        Py_RETURN_TRUE;
    Py_RETURN_FALSE;
}

PyGetSetDef Patch_getseters[] = {
    GETTER(Patch, is_binary),
    {NULL}
};

PyDoc_STRVAR(Patch__doc__, "Diff patch object.");

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
    0,                                         /* tp_as_mapping     */
    0,                                         /* tp_hash           */
    0,                                         /* tp_call           */
    0,                                         /* tp_str            */
    0,                                         /* tp_getattro       */
    0,                                         /* tp_setattro       */
    0,                                         /* tp_as_buffer      */
    Py_TPFLAGS_DEFAULT,                        /* tp_flags          */
    Patch__doc__,                              /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    0,                                         /* tp_methods        */
    Patch_members,                             /* tp_members        */
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


PyObject *
DiffIter_iternext(DiffIter *self)
{
    if (self->i < self->n)
        return diff_get_patch_byindex(self->diff->diff, self->i++);

    PyErr_SetNone(PyExc_StopIteration);
    return NULL;
}

void
DiffIter_dealloc(DiffIter *self)
{
    Py_CLEAR(self->diff);
    PyObject_Del(self);
}


PyDoc_STRVAR(DiffIter__doc__, "Diff iterator object.");

PyTypeObject DiffIterType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.DiffIter",                        /* tp_name           */
    sizeof(DiffIter),                          /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)DiffIter_dealloc,              /* tp_dealloc        */
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
    DiffIter__doc__,                           /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    PyObject_SelfIter,                         /* tp_iter           */
    (iternextfunc) DiffIter_iternext,          /* tp_iternext       */
};

Py_ssize_t
Diff_len(Diff *self)
{
    assert(self->diff);
    return (Py_ssize_t)git_diff_num_deltas(self->diff);
}

PyDoc_STRVAR(Diff_patch__doc__, "Patch diff string.");

PyObject *
Diff_patch__get__(Diff *self)
{
    git_patch* patch;
    git_buf buf = {NULL};
    int err = GIT_ERROR;
    size_t i, len, num;
    PyObject *py_patch = NULL;

    num = git_diff_num_deltas(self->diff);
    if (num == 0)
        Py_RETURN_NONE;

    for (i = 0, len = 1; i < num ; ++i) {
        err = git_patch_from_diff(&patch, self->diff, i);
        if (err < 0)
            goto cleanup;

        /* This appends to the current buf, so we can simply keep passing it */
        err = git_patch_to_buf(&buf, patch);
        if (err < 0)
            goto cleanup;

        git_patch_free(patch);
    }

    py_patch = to_unicode(buf.ptr, NULL, NULL);
    git_buf_free(&buf);

cleanup:
    git_buf_free(&buf);
    return (err < 0) ? Error_set(err) : py_patch;
}


static void
Hunk_dealloc(Hunk *self)
{
    Py_CLEAR(self->lines);
    PyObject_Del(self);
}

PyMemberDef Hunk_members[] = {
    MEMBER(Hunk, old_start, T_INT, "Old start."),
    MEMBER(Hunk, old_lines, T_INT, "Old lines."),
    MEMBER(Hunk, new_start, T_INT, "New start."),
    MEMBER(Hunk, new_lines, T_INT, "New lines."),
    MEMBER(Hunk, lines, T_OBJECT, "Lines."),
    {NULL}
};


PyDoc_STRVAR(Hunk__doc__, "Hunk object.");

PyTypeObject HunkType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.Hunk",                            /* tp_name           */
    sizeof(Hunk),                              /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)Hunk_dealloc,                  /* tp_dealloc        */
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
    Hunk__doc__,                               /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    0,                                         /* tp_methods        */
    Hunk_members,                              /* tp_members        */
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

PyDoc_STRVAR(Diff_from_c__doc__, "Method exposed for Index to hook into");

PyObject *
Diff_from_c(Diff *dummy, PyObject *args)
{
    PyObject *py_diff, *py_repository;
    git_diff *diff;
    char *buffer;
    Py_ssize_t length;

    if (!PyArg_ParseTuple(args, "OO!", &py_diff, &RepositoryType, &py_repository))
        return NULL;

    /* Here we need to do the opposite conversion from the _pointer getters */
    if (PyBytes_AsStringAndSize(py_diff, &buffer, &length))
        return NULL;

    if (length != sizeof(git_diff *)) {
        PyErr_SetString(PyExc_TypeError, "passed value is not a pointer");
        return NULL;
    }

    /* the "buffer" contains the pointer */
    diff = *((git_diff **) buffer);

    return wrap_diff(diff, (Repository *) py_repository);
}

PyDoc_STRVAR(Diff_merge__doc__,
  "merge(diff)\n"
  "\n"
  "Merge one diff into another.");

PyObject *
Diff_merge(Diff *self, PyObject *args)
{
    Diff *py_diff;
    int err;

    if (!PyArg_ParseTuple(args, "O!", &DiffType, &py_diff))
        return NULL;

    if (py_diff->repo->repo != self->repo->repo)
        return Error_set(GIT_ERROR);

    err = git_diff_merge(self->diff, py_diff->diff);
    if (err < 0)
        return Error_set(err);

    Py_RETURN_NONE;
}


PyDoc_STRVAR(Diff_find_similar__doc__,
  "find_similar([flags, rename_threshold, copy_threshold, rename_from_rewrite_threshold, break_rewrite_threshold, rename_limit])\n"
  "\n"
  "Find renamed files in diff and updates them in-place in the diff itself.");

PyObject *
Diff_find_similar(Diff *self, PyObject *args, PyObject *kwds)
{
    int err;
    git_diff_find_options opts = GIT_DIFF_FIND_OPTIONS_INIT;

    char *keywords[] = {"flags", "rename_threshold", "copy_threshold", "rename_from_rewrite_threshold", "break_rewrite_threshold", "rename_limit", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|iHHHHI", keywords,
                &opts.flags, &opts.rename_threshold, &opts.copy_threshold, &opts.rename_from_rewrite_threshold, &opts.break_rewrite_threshold, &opts.rename_limit))
        return NULL;

    err = git_diff_find_similar(self->diff, &opts);
    if (err < 0)
        return Error_set(err);

    Py_RETURN_NONE;
}

PyObject *
Diff_iter(Diff *self)
{
    DiffIter *iter;

    iter = PyObject_New(DiffIter, &DiffIterType);
    if (iter != NULL) {
        Py_INCREF(self);
        iter->diff = self;
        iter->i = 0;
        iter->n = git_diff_num_deltas(self->diff);
    }
    return (PyObject*)iter;
}

PyObject *
Diff_getitem(Diff *self, PyObject *value)
{
    size_t i;

    if (PyLong_Check(value) < 0)
        return NULL;

    i = PyLong_AsUnsignedLong(value);

    return diff_get_patch_byindex(self->diff, i);
}


static void
Diff_dealloc(Diff *self)
{
    git_diff_free(self->diff);
    Py_CLEAR(self->repo);
    PyObject_Del(self);
}

PyGetSetDef Diff_getseters[] = {
    GETTER(Diff, patch),
    {NULL}
};

PyMappingMethods Diff_as_mapping = {
    (lenfunc)Diff_len,               /* mp_length */
    (binaryfunc)Diff_getitem,        /* mp_subscript */
    0,                               /* mp_ass_subscript */
};

static PyMethodDef Diff_methods[] = {
    METHOD(Diff, merge, METH_VARARGS),
    METHOD(Diff, find_similar, METH_VARARGS | METH_KEYWORDS),
    METHOD(Diff, from_c, METH_STATIC | METH_VARARGS),
    {NULL}
};


PyDoc_STRVAR(Diff__doc__, "Diff objects.");

PyTypeObject DiffType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.Diff",                            /* tp_name           */
    sizeof(Diff),                              /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)Diff_dealloc,                  /* tp_dealloc        */
    0,                                         /* tp_print          */
    0,                                         /* tp_getattr        */
    0,                                         /* tp_setattr        */
    0,                                         /* tp_compare        */
    0,                                         /* tp_repr           */
    0,                                         /* tp_as_number      */
    0,                                         /* tp_as_sequence    */
    &Diff_as_mapping,                          /* tp_as_mapping     */
    0,                                         /* tp_hash           */
    0,                                         /* tp_call           */
    0,                                         /* tp_str            */
    0,                                         /* tp_getattro       */
    0,                                         /* tp_setattro       */
    0,                                         /* tp_as_buffer      */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,  /* tp_flags          */
    Diff__doc__,                               /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    (getiterfunc)Diff_iter,                    /* tp_iter           */
    0,                                         /* tp_iternext       */
    Diff_methods,                              /* tp_methods        */
    0,                                         /* tp_members        */
    Diff_getseters,                            /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    0,                                         /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};
