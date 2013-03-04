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
#include <pygit2/error.h>
#include <pygit2/types.h>
#include <pygit2/utils.h>
#include <pygit2/diff.h>

extern PyObject *GitError;

extern PyTypeObject TreeType;
extern PyTypeObject IndexType;
extern PyTypeObject DiffType;
extern PyTypeObject HunkType;

PyTypeObject DiffEntryType;

PyObject*
diff_get_patch_byindex(git_diff_list* list, size_t i)
{
    const git_diff_delta* delta;
    const git_diff_range* range;
    git_diff_patch* patch = NULL;

    char buffer[41];
    const char* hunk_content;
    size_t hunk_amounts, j, hunk_header_len, hunk_lines;
    int err;

    PyObject *file;
    Hunk *py_hunk;
    DiffEntry *py_entry = NULL;

    err = git_diff_get_patch(&patch, &delta, list, i);

    if (err == GIT_OK) {
        py_entry = (DiffEntry*) INSTANCIATE_CLASS(DiffEntryType, NULL);
        if (py_entry != NULL) {
            if (err == GIT_OK) {
                file = Py_BuildValue("(s,s,i,i)",
                    delta->old_file.path,
                    delta->new_file.path,
                    delta->status,
                    delta->similarity
                );

                PyList_Append((PyObject*) py_entry->files, file);
            }

            hunk_amounts = git_diff_patch_num_hunks(patch);

            for (j=0; j < hunk_amounts; ++j) {
                err = git_diff_patch_get_hunk(&range, &hunk_content,
                          &hunk_header_len, &hunk_lines, patch, j);

                if (err == GIT_OK) {
                    py_hunk = (Hunk*)PyType_GenericNew(&HunkType, NULL, NULL);
                    if (py_hunk != NULL) {
                        py_hunk->old_file  = delta->old_file.path;
                        py_hunk->new_file  = delta->new_file.path;
                        py_hunk->header    = hunk_content;
                        py_hunk->old_start = range->old_start;
                        py_hunk->old_lines = range->old_lines;
                        py_hunk->new_start = range->new_start;
                        py_hunk->new_lines = range->new_lines;

                        git_oid_fmt(buffer, &delta->old_file.oid);
                        py_hunk->old_oid = calloc(41, sizeof(char));
                        memcpy(py_hunk->old_oid, buffer, 40);

                        git_oid_fmt(buffer, &delta->new_file.oid);
                        py_hunk->new_oid = calloc(41, sizeof(char));
                        memcpy(py_hunk->new_oid, buffer, 40);

                        py_hunk->data = Py_BuildValue("(s#,i)",
                                            hunk_content, hunk_header_len,
                                            hunk_lines);

                        PyList_Append((PyObject*) py_entry->hunks,
                            (PyObject*) py_hunk);
                    }
                }
            }
        }
    }

    if (err < 0)
        return Error_set(err);

    return (PyObject*) py_entry;
}

PyObject *
DiffEntry_call(DiffEntry *self, PyObject *args, PyObject *kwds)
{
    self->files = PyList_New(0);
    if (self->files == NULL) {
        Py_XDECREF(self);
        return NULL;
    }

    self->hunks = PyList_New(0);
    if (self->hunks == NULL) {
        Py_XDECREF(self);
        return NULL;
    }

    return (PyObject*) self;
}

static void
DiffEntry_dealloc(DiffEntry *self)
{
    Py_DECREF((PyObject*) self->files);
    Py_DECREF((PyObject*) self->hunks);
    PyObject_Del(self);
}

PyMemberDef DiffEntry_members[] = {
    MEMBER(DiffEntry, files, T_OBJECT, "files"),
    MEMBER(DiffEntry, hunks, T_OBJECT, "hunks"),
    {NULL}
};

PyDoc_STRVAR(DiffEntry__doc__, "Diff entry object.");

PyTypeObject DiffEntryType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.DiffEntry",                       /* tp_name           */
    sizeof(DiffEntry),                         /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)DiffEntry_dealloc,             /* tp_dealloc        */
    0,                                         /* tp_print          */
    0,                                         /* tp_getattr        */
    0,                                         /* tp_setattr        */
    0,                                         /* tp_compare        */
    0,                                         /* tp_repr           */
    0,                                         /* tp_as_number      */
    0,                                         /* tp_as_sequence    */
    0,                                         /* tp_as_mapping     */
    0,                                         /* tp_hash           */
    (ternaryfunc) DiffEntry_call,              /* tp_call           */
    0,                                         /* tp_str            */
    0,                                         /* tp_getattro       */
    0,                                         /* tp_setattro       */
    0,                                         /* tp_as_buffer      */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,  /* tp_flags          */
    DiffEntry__doc__,                          /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    0,                                         /* tp_methods        */
    DiffEntry_members,                         /* tp_members        */
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


PyObject *
DiffIter_iternext(DiffIter *self)
{
    if (self->i < self->n)
        return diff_get_patch_byindex(self->list, self->i++);

    PyErr_SetNone(PyExc_StopIteration);
    return NULL;
}

void
DiffIter_dealloc(DiffIter *self)
{
    Py_CLEAR(self->list);
    PyObject_Del(self);
}


PyDoc_STRVAR(DiffIter__doc__, "Diff iterator object.");

PyTypeObject DiffIterType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.DiffIter",                       /* tp_name           */
    sizeof(DiffIter),                         /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)DiffIter_dealloc,             /* tp_dealloc        */
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
    DiffIter__doc__,                           /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    PyObject_SelfIter,                         /* tp_iter           */
   (iternextfunc) DiffIter_iternext,           /* tp_iternext       */
};


PyDoc_STRVAR(Diff_patch__doc__, "Patch.");

PyObject *
Diff_patch__get__(Diff *self)
{
    const git_diff_delta* delta;
    git_diff_patch* patch;
    char* str = NULL, *buffer = NULL;
    int err = 0;
    size_t i, len, num, size;
    PyObject *py_patch = NULL;

    num = git_diff_num_deltas(self->list);
    for (i = 0; i < num ; ++i) {
        err = git_diff_get_patch(&patch, &delta, self->list, i);

        if (err < 0 || (err = git_diff_patch_to_str(&str, patch)) < 0)
            goto error;

        len = strlen(str) + 1;
        size = (buffer == NULL) ? len : strlen(buffer) + len;
        MALLOC(buffer, size, error);

        if (len == size)
            strcpy(buffer, str);
        else
            strcat(buffer, str);

        FREE(str);
    }

    py_patch = PyUnicode_FromString(buffer);

error:
    FREE(str);
    FREE(buffer);
    FREE_FUNC(patch, git_diff_patch_free);

    return (err < 0) ? Error_set(err) : py_patch;
}


static void
Hunk_dealloc(Hunk *self)
{
    if (self->header != NULL) {
        free((void*) self->header);
    }
    if (self->new_file != NULL) {
        free((void*) self->new_file);
    }
    if (self->old_file != NULL) {
        free((void*) self->old_file);
    }
    Py_XDECREF(self->old_oid);
    Py_XDECREF(self->new_oid);
    Py_XDECREF(self->data);
    PyObject_Del(self);
}

PyMemberDef Hunk_members[] = {
    MEMBER(Hunk, header, T_STRING, "Header."),
    MEMBER(Hunk, old_start, T_INT, "Old start."),
    MEMBER(Hunk, old_lines, T_INT, "Old lines."),
    MEMBER(Hunk, old_mode, T_INT, "Old mode."),
    MEMBER(Hunk, old_file, T_STRING, "Old file."),
    MEMBER(Hunk, old_oid, T_STRING, "Old oid."),
    MEMBER(Hunk, new_start, T_INT, "New start."),
    MEMBER(Hunk, new_lines, T_INT, "New lines."),
    MEMBER(Hunk, new_mode, T_INT, "New mode."),
    MEMBER(Hunk, new_file, T_STRING, "New file."),
    MEMBER(Hunk, new_oid, T_STRING, "New oid."),
    MEMBER(Hunk, data, T_OBJECT, "Data."),
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

    err = git_diff_merge(self->list, py_diff->list);
    if (err < 0)
        return Error_set(err);

    Py_RETURN_NONE;
}


PyDoc_STRVAR(Diff_find_similar__doc__,
  "find_similar([flags])\n"
  "\n"
  "Find renamed files in diff.");

PyObject *
Diff_find_similar(Diff *self, PyObject *args)
{
    int err;
    git_diff_find_options opts = GIT_DIFF_FIND_OPTIONS_INIT;

    if (!PyArg_ParseTuple(args, "|i", &opts.flags))
        return NULL;

    err = git_diff_find_similar(self->list, &opts);
    if (err < 0)
        return Error_set(err);

    Py_RETURN_NONE;
}

PyObject *
Diff_iter(Diff *self)
{
    DiffIter *iter;

    iter = PyObject_New(DiffIter, &DiffIterType);
    if (iter) {
        Py_INCREF(self);
        iter->list = self->list;
        iter->i = 0;
        iter->n = git_diff_num_deltas(self->list);
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

    return diff_get_patch_byindex(self->list, i);
}


static void
Diff_dealloc(Diff *self)
{
    git_diff_list_free(self->list);
    Py_XDECREF(self->repo);
    PyObject_Del(self);
}

PyGetSetDef Diff_getseters[] = {
    GETTER(Diff, patch),
    {NULL}
};

PyMappingMethods Diff_as_mapping = {
    0,                               /* mp_length */
    (binaryfunc)Diff_getitem,        /* mp_subscript */
    0,                               /* mp_ass_subscript */
};

static PyMethodDef Diff_methods[] = {
    METHOD(Diff, merge, METH_VARARGS),
    METHOD(Diff, find_similar, METH_VARARGS),
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
