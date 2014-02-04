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
#include "signature.h"
#include "blame.h"

extern PyObject *GitError;

extern PyTypeObject BlameType;
extern PyTypeObject BlameIterType;
extern PyTypeObject BlameHunkType;

PyObject*
wrap_blame(git_blame *blame, Repository *repo)
{
    Blame *py_blame;

    py_blame = PyObject_New(Blame, &BlameType);
    if (py_blame) {
        Py_INCREF(repo);
        py_blame->repo = repo;
        py_blame->blame = blame;
    }

    return (PyObject*) py_blame;
}

#include <stdio.h>
PyObject*
wrap_blame_hunk(const git_blame_hunk *hunk, Blame *blame)
{
    BlameHunk *py_hunk = NULL;

    if (!hunk)
        Py_RETURN_NONE;

    py_hunk = PyObject_New(BlameHunk, &BlameHunkType);
    if (py_hunk != NULL) {
        py_hunk->lines_in_hunk = hunk->lines_in_hunk;
        py_hunk->final_commit_id = git_oid_allocfmt(&hunk->final_commit_id);
        py_hunk->final_start_line_number = hunk->final_start_line_number;
        py_hunk->final_signature = hunk->final_signature != NULL ?
            git_signature_dup(hunk->final_signature) : NULL;
        py_hunk->orig_commit_id = git_oid_allocfmt(&hunk->orig_commit_id);
        py_hunk->orig_path = hunk->orig_path != NULL ?
            strdup(hunk->orig_path) : NULL;
        py_hunk->orig_start_line_number = hunk->orig_start_line_number;
        py_hunk->orig_signature = hunk->orig_signature != NULL ?
            git_signature_dup(hunk->orig_signature) : NULL;
        py_hunk->boundary = hunk->boundary;
    }

    return (PyObject*) py_hunk;
}

PyDoc_STRVAR(BlameHunk_final_committer__doc__, "Final committer.");

PyObject *
BlameHunk_final_committer__get__(BlameHunk *self)
{
    if (!self->final_signature)
        Py_RETURN_NONE;

    return build_signature((Object*) self, self->final_signature, "utf-8");
}

PyDoc_STRVAR(BlameHunk_orig_committer__doc__, "Origin committer.");

PyObject *
BlameHunk_orig_committer__get__(BlameHunk *self)
{
    if (!self->orig_signature)
        Py_RETURN_NONE;

    return build_signature((Object*) self, self->orig_signature, "utf-8");
}

static int
BlameHunk_init(BlameHunk *self, PyObject *args, PyObject *kwds)
{
    self->final_commit_id = NULL;
    self->final_signature = NULL;
    self->orig_commit_id = NULL;
    self->orig_path = NULL;
    self->orig_signature = NULL;

    return 0;
}

static void
BlameHunk_dealloc(BlameHunk *self)
{
    free(self->final_commit_id);
    if (self->final_signature)
        git_signature_free(self->final_signature);
    free(self->orig_commit_id);
    if (self->orig_path)
        free(self->orig_path);
    if (self->orig_signature)
        git_signature_free(self->orig_signature);
    PyObject_Del(self);
}

PyMemberDef BlameHunk_members[] = {
    MEMBER(BlameHunk, lines_in_hunk, T_UINT, "Number of lines."),
    MEMBER(BlameHunk, final_commit_id, T_STRING, "Last changed oid."),
    MEMBER(BlameHunk, final_start_line_number, T_UINT, "final start line no."),
    MEMBER(BlameHunk, orig_commit_id, T_STRING, "oid where hunk was found."),
    MEMBER(BlameHunk, orig_path, T_STRING, "Origin path."),
    MEMBER(BlameHunk, orig_start_line_number, T_UINT, "Origin start line no."),
    MEMBER(BlameHunk, boundary, T_BOOL, "Tracked to a boundary commit."),
    {NULL}
};

PyGetSetDef BlameHunk_getseters[] = {
    GETTER(BlameHunk, final_committer),
    GETTER(BlameHunk, orig_committer),
    {NULL}
};

PyDoc_STRVAR(BlameHunk__doc__, "Blame Hunk object.");

PyTypeObject BlameHunkType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.BlameHunk",                       /* tp_name           */
    sizeof(BlameHunk),                         /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)BlameHunk_dealloc,             /* tp_dealloc        */
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
    BlameHunk__doc__,                          /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    0,                                         /* tp_methods        */
    BlameHunk_members,                         /* tp_members        */
    BlameHunk_getseters,                       /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    (initproc)BlameHunk_init,                  /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};


PyObject *
BlameIter_iternext(BlameIter *self)
{
    if (self->i < self->n)
        return wrap_blame_hunk(git_blame_get_hunk_byindex(
                    self->blame->blame, self->i++), self->blame);

    PyErr_SetNone(PyExc_StopIteration);
    return NULL;
}

static void
BlameIter_dealloc(BlameIter *self)
{
    Py_CLEAR(self->blame);
    PyObject_Del(self);
}


PyDoc_STRVAR(BlameIter__doc__, "Blame iterator object.");

PyTypeObject BlameIterType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.BlameIter",                       /* tp_name           */
    sizeof(BlameIter),                         /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)BlameIter_dealloc,             /* tp_dealloc        */
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
    BlameIter__doc__,                          /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    PyObject_SelfIter,                         /* tp_iter           */
    (iternextfunc) BlameIter_iternext,         /* tp_iternext       */
};


PyObject *
Blame_iter(Blame *self)
{
    BlameIter *iter;

    iter = PyObject_New(BlameIter, &BlameIterType);
    if (iter != NULL) {
        Py_INCREF(self);
        iter->blame = self;
        iter->i = 0;
        iter->n = git_blame_get_hunk_count(self->blame);
    }
    return (PyObject*)iter;
}

Py_ssize_t
Blame_len(Blame *self)
{
    assert(self->blame);
    return (Py_ssize_t)git_blame_get_hunk_count(self->blame);
}

PyObject *
Blame_getitem(Blame *self, PyObject *value)
{
    size_t i;
    const git_blame_hunk *hunk;

    if (PyLong_Check(value) < 0) {
        PyErr_SetObject(PyExc_IndexError, value);
        return NULL;
    }

    i = PyLong_AsUnsignedLong(value);
    if (PyErr_Occurred()) {
        PyErr_SetObject(PyExc_IndexError, value);
        return NULL;
    }

    hunk = git_blame_get_hunk_byindex(self->blame, i);
    if (!hunk) {
        PyErr_SetObject(PyExc_IndexError, value);
        return NULL;
    }

    return wrap_blame_hunk(hunk, self);
}

PyDoc_STRVAR(Blame_for_line__doc__,
  "for_line(line_no) -> hunk\n"
  "\n"
  "Returns the blame hunk data for the given \"line_no\" in blame.\n"
  "\n"
  "Arguments:\n"
  "\n"
  "line_no\n"
  "    Line number, countings starts with 1.");

PyObject *
Blame_for_line(Blame *self, PyObject *args)
{
    size_t line_no;
    const git_blame_hunk *hunk;

    if (!PyArg_ParseTuple(args, "I", &line_no))
        return NULL;

    hunk = git_blame_get_hunk_byline(self->blame, line_no);
    if (!hunk) {
        PyErr_SetObject(PyExc_IndexError, args);
        return NULL;
    }

    return wrap_blame_hunk(hunk, self);
}

static void
Blame_dealloc(Blame *self)
{
    git_blame_free(self->blame);
    Py_CLEAR(self->repo);
    PyObject_Del(self);
}

PyMappingMethods Blame_as_mapping = {
    (lenfunc)Blame_len,              /* mp_length */
    (binaryfunc)Blame_getitem,       /* mp_subscript */
    0,                               /* mp_ass_subscript */
};

static PyMethodDef Blame_methods[] = {
    METHOD(Blame, for_line, METH_VARARGS),
    {NULL}
};


PyDoc_STRVAR(Blame__doc__, "Blame objects.");

PyTypeObject BlameType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.Blame",                           /* tp_name           */
    sizeof(Blame),                             /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)Blame_dealloc,                 /* tp_dealloc        */
    0,                                         /* tp_print          */
    0,                                         /* tp_getattr        */
    0,                                         /* tp_setattr        */
    0,                                         /* tp_compare        */
    0,                                         /* tp_repr           */
    0,                                         /* tp_as_number      */
    0,                                         /* tp_as_sequence    */
    &Blame_as_mapping,                         /* tp_as_mapping     */
    0,                                         /* tp_hash           */
    0,                                         /* tp_call           */
    0,                                         /* tp_str            */
    0,                                         /* tp_getattro       */
    0,                                         /* tp_setattro       */
    0,                                         /* tp_as_buffer      */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,  /* tp_flags          */
    Blame__doc__,                              /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    (getiterfunc)Blame_iter,                   /* tp_iter           */
    0,                                         /* tp_iternext       */
    Blame_methods,                             /* tp_methods        */
    0,                                         /* tp_members        */
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
