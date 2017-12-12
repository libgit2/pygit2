/*
 * Copyright 2010-2017 The pygit2 contributors
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
#include "oid.h"
#include "patch.h"
#include "types.h"
#include "utils.h"

extern PyObject *GitError;

extern PyTypeObject TreeType;
extern PyTypeObject IndexType;
extern PyTypeObject DiffType;
extern PyTypeObject DiffDeltaType;
extern PyTypeObject DiffFileType;
extern PyTypeObject DiffHunkType;
extern PyTypeObject DiffLineType;
extern PyTypeObject DiffStatsType;
extern PyTypeObject RepositoryType;

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
wrap_diff_file(const git_diff_file *file)
{
    DiffFile *py_file;

    if (!file)
        Py_RETURN_NONE;

    py_file = PyObject_New(DiffFile, &DiffFileType);
    if (py_file) {
        py_file->id = git_oid_to_python(&file->id);
        py_file->path = file->path != NULL ? strdup(file->path) : NULL;
        py_file->size = file->size;
        py_file->flags = file->flags;
        py_file->mode = file->mode;
    }

    return (PyObject *) py_file;
}

PyObject *
wrap_diff_delta(const git_diff_delta *delta)
{
    DiffDelta *py_delta;

    if (!delta)
        Py_RETURN_NONE;

    py_delta = PyObject_New(DiffDelta, &DiffDeltaType);
    if (py_delta) {
        py_delta->status = delta->status;
        py_delta->flags = delta->flags;
        py_delta->similarity = delta->similarity;
        py_delta->nfiles = delta->nfiles;
        py_delta->old_file = wrap_diff_file(&delta->old_file);
        py_delta->new_file = wrap_diff_file(&delta->new_file);
    }

    return (PyObject *) py_delta;
}

PyObject *
wrap_diff_hunk(git_patch *patch, size_t idx)
{
    DiffHunk *py_hunk;
    const git_diff_hunk *hunk;
    const git_diff_line *line;
    size_t j, lines_in_hunk;
    int err;

    err = git_patch_get_hunk(&hunk, &lines_in_hunk, patch, idx);
    if (err < 0)
        return Error_set(err);

    py_hunk = PyObject_New(DiffHunk, &DiffHunkType);
    if (py_hunk) {
        py_hunk->old_start = hunk->old_start;
        py_hunk->old_lines = hunk->old_lines;
        py_hunk->new_start = hunk->new_start;
        py_hunk->new_lines = hunk->new_lines;
        py_hunk->header = to_unicode_n((const char *) &hunk->header,
                hunk->header_len, NULL, NULL);

        py_hunk->lines = PyList_New(lines_in_hunk);
        for (j = 0; j < lines_in_hunk; ++j) {
            PyObject *py_line = NULL;

            err = git_patch_get_line_in_hunk(&line, patch, idx, j);
            if (err < 0)
                return Error_set(err);

            py_line = wrap_diff_line(line);
            if (py_line == NULL)
                return NULL;

            PyList_SetItem(py_hunk->lines, j, py_line);
        }
    }

    return (PyObject *) py_hunk;
}

PyObject *
wrap_diff_stats(git_diff *diff)
{
    git_diff_stats *stats;
    DiffStats *py_stats;
    int err;

    err = git_diff_get_stats(&stats, diff);
    if (err < 0)
        return Error_set(err);

    py_stats = PyObject_New(DiffStats, &DiffStatsType);
    if (!py_stats) {
        git_diff_stats_free(stats);
        return NULL;
    }

    py_stats->stats = stats;

    return (PyObject *) py_stats;
}

PyObject *
wrap_diff_line(const git_diff_line *line)
{
    DiffLine *py_line;

    py_line = PyObject_New(DiffLine, &DiffLineType);
    if (py_line) {
        py_line->origin = line->origin;
        py_line->old_lineno = line->old_lineno;
        py_line->new_lineno = line->new_lineno;
        py_line->num_lines = line->num_lines;
        py_line->content = to_unicode_n(line->content, line->content_len,
                NULL, NULL);
        py_line->content_offset = line->content_offset;
    }

    return (PyObject *) py_line;
}

static void
DiffFile_dealloc(DiffFile *self)
{
    Py_CLEAR(self->id);
    if (self->path)
        free(self->path);
    PyObject_Del(self);
}

PyMemberDef DiffFile_members[] = {
    MEMBER(DiffFile, id, T_OBJECT, "Oid of the item."),
    MEMBER(DiffFile, path, T_STRING, "Path to the entry."),
    MEMBER(DiffFile, size, T_LONG, "Size of the entry."),
    MEMBER(DiffFile, flags, T_UINT, "Combination of GIT_DIFF_FLAG_* flags."),
    MEMBER(DiffFile, mode, T_USHORT, "Mode of the entry."),
    {NULL}
};


PyDoc_STRVAR(DiffFile__doc__, "DiffFile object.");

PyTypeObject DiffFileType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.DiffFile",                        /* tp_name           */
    sizeof(DiffFile),                          /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)DiffFile_dealloc,              /* tp_dealloc        */
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
    DiffFile__doc__,                           /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    0,                                         /* tp_methods        */
    DiffFile_members,                          /* tp_members        */
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


PyDoc_STRVAR(DiffDelta_status_char__doc__,
  "status_char()\n"
  "\n"
  "Return the single character abbreviation for a delta status code."
);

PyObject *
DiffDelta_status_char(DiffDelta *self)
{
    char status = git_diff_status_char(self->status);

#if PY_MAJOR_VERSION == 2
    return Py_BuildValue("c", status);
#else
    return Py_BuildValue("C", status);
#endif
}

PyDoc_STRVAR(DiffDelta_is_binary__doc__, "True if binary data, False if not.");

PyObject *
DiffDelta_is_binary__get__(DiffDelta *self)
{
    if (!(self->flags & GIT_DIFF_FLAG_NOT_BINARY) &&
            (self->flags & GIT_DIFF_FLAG_BINARY))
        Py_RETURN_TRUE;
    Py_RETURN_FALSE;
}

static void
DiffDelta_dealloc(DiffDelta *self)
{
    Py_CLEAR(self->old_file);
    Py_CLEAR(self->new_file);
    PyObject_Del(self);
}

static PyMethodDef DiffDelta_methods[] = {
    METHOD(DiffDelta, status_char, METH_NOARGS),
    {NULL}
};

PyMemberDef DiffDelta_members[] = {
    MEMBER(DiffDelta, status, T_UINT, "A GIT_DELTA_* constant."),
    MEMBER(DiffDelta, flags, T_UINT, "Combination of GIT_DIFF_FLAG_* flags."),
    MEMBER(DiffDelta, similarity, T_USHORT, "For renamed and copied."),
    MEMBER(DiffDelta, nfiles, T_USHORT, "Number of files in the delta."),
    MEMBER(DiffDelta, old_file, T_OBJECT, "\"from\" side of the diff."),
    MEMBER(DiffDelta, new_file, T_OBJECT, "\"to\" side of the diff."),
    {NULL}
};

PyGetSetDef DiffDelta_getseters[] = {
    GETTER(DiffDelta, is_binary),
    {NULL}
};

PyDoc_STRVAR(DiffDelta__doc__, "DiffDelta object.");

PyTypeObject DiffDeltaType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.DiffDelta",                       /* tp_name           */
    sizeof(DiffDelta),                         /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)DiffDelta_dealloc,             /* tp_dealloc        */
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
    DiffDelta__doc__,                          /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    DiffDelta_methods,                         /* tp_methods        */
    DiffDelta_members,                         /* tp_members        */
    DiffDelta_getseters,                       /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    0,                                         /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};

static void
DiffLine_dealloc(DiffLine *self)
{
    Py_CLEAR(self->content);
    PyObject_Del(self);
}

PyMemberDef DiffLine_members[] = {
    MEMBER(DiffLine, origin, T_CHAR, "Type of the diff line"),
    MEMBER(DiffLine, old_lineno, T_INT,
           "Line number in old file or -1 for added line"),
    MEMBER(DiffLine, new_lineno, T_INT,
           "Line number in new file or -1 for deleted line"),
    MEMBER(DiffLine, num_lines, T_INT,
           "Number of newline characters in content"),
    MEMBER(DiffLine, content_offset, T_INT,
           "Offset in the original file to the content"),
    MEMBER(DiffLine, content, T_OBJECT, "Content of the diff line"),
    {NULL}
};

PyDoc_STRVAR(DiffLine__doc__, "DiffLine object.");

PyTypeObject DiffLineType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.DiffLine",                        /* tp_name           */
    sizeof(DiffLine),                          /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)DiffLine_dealloc,              /* tp_dealloc        */
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
    DiffLine__doc__,                           /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    0,                                         /* tp_methods        */
    DiffLine_members,                          /* tp_members        */
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
diff_get_patch_byindex(git_diff *diff, size_t idx)
{
    git_patch *patch = NULL;
    int err;

    err = git_patch_from_diff(&patch, diff, idx);
    if (err < 0)
        return Error_set(err);

    return (PyObject*) wrap_patch(patch, NULL, NULL);
}

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

PyObject *
diff_get_delta_byindex(git_diff *diff, size_t idx)
{
    const git_diff_delta *delta = git_diff_get_delta(diff, idx);
    if (delta == NULL) {
        PyErr_SetObject(PyExc_IndexError, PyInt_FromSize_t(idx));
        return NULL;
    }

    return (PyObject*) wrap_diff_delta(delta);
}

PyObject *
DeltasIter_iternext(DeltasIter *self)
{
    if (self->i < self->n)
        return diff_get_delta_byindex(self->diff->diff, self->i++);

    PyErr_SetNone(PyExc_StopIteration);
    return NULL;
}

void
DeltasIter_dealloc(DeltasIter *self)
{
    Py_CLEAR(self->diff);
    PyObject_Del(self);
}

PyDoc_STRVAR(DeltasIter__doc__, "Deltas iterator object.");

PyTypeObject DeltasIterType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.DeltasIter",                      /* tp_name           */
    sizeof(DeltasIter),                        /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)DeltasIter_dealloc,            /* tp_dealloc        */
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
    DeltasIter__doc__,                         /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    PyObject_SelfIter,                         /* tp_iter           */
    (iternextfunc) DeltasIter_iternext,        /* tp_iternext       */
};


Py_ssize_t
Diff_len(Diff *self)
{
    assert(self->diff);
    return (Py_ssize_t)git_diff_num_deltas(self->diff);
}

PyDoc_STRVAR(Diff_deltas__doc__, "Iterate over the diff deltas.");

PyObject *
Diff_deltas__get__(Diff *self)
{
    DeltasIter *iter;

    iter = PyObject_New(DeltasIter, &DeltasIterType);
    if (iter != NULL) {
        Py_INCREF(self);
        iter->diff = self;
        iter->i = 0;
        iter->n = git_diff_num_deltas(self->diff);
    }
    return (PyObject*)iter;
}

PyDoc_STRVAR(Diff_patch__doc__,
    "Patch diff string. Can be None in some cases, such as empty commits.");

PyObject *
Diff_patch__get__(Diff *self)
{
    git_patch* patch;
    git_buf buf = {NULL};
    int err = GIT_ERROR;
    size_t i, num;
    PyObject *py_patch = NULL;

    num = git_diff_num_deltas(self->diff);
    if (num == 0)
        Py_RETURN_NONE;

    for (i = 0; i < num ; ++i) {
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
DiffHunk_dealloc(DiffHunk *self)
{
    Py_CLEAR(self->header);
    Py_CLEAR(self->lines);
    PyObject_Del(self);
}

PyMemberDef DiffHunk_members[] = {
    MEMBER(DiffHunk, old_start, T_INT, "Old start."),
    MEMBER(DiffHunk, old_lines, T_INT, "Old lines."),
    MEMBER(DiffHunk, new_start, T_INT, "New start."),
    MEMBER(DiffHunk, new_lines, T_INT, "New lines."),
    MEMBER(DiffHunk, header, T_OBJECT, "Header."),
    MEMBER(DiffHunk, lines, T_OBJECT, "Lines."),
    {NULL}
};


PyDoc_STRVAR(DiffHunk__doc__, "DiffHunk object.");

PyTypeObject DiffHunkType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.DiffHunk",                        /* tp_name           */
    sizeof(DiffHunk),                          /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)DiffHunk_dealloc,              /* tp_dealloc        */
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
    DiffHunk__doc__,                           /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    0,                                         /* tp_methods        */
    DiffHunk_members,                          /* tp_members        */
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

PyDoc_STRVAR(DiffStats_insertions__doc__, "Total number of insertions");

PyObject *
DiffStats_insertions__get__(DiffStats *self)
{
    return PyInt_FromSize_t(git_diff_stats_insertions(self->stats));
}

PyDoc_STRVAR(DiffStats_deletions__doc__, "Total number of deletions");

PyObject *
DiffStats_deletions__get__(DiffStats *self)
{
    return PyInt_FromSize_t(git_diff_stats_deletions(self->stats));
}

PyDoc_STRVAR(DiffStats_files_changed__doc__, "Total number of files changed");

PyObject *
DiffStats_files_changed__get__(DiffStats *self)
{
    return PyInt_FromSize_t(git_diff_stats_files_changed(self->stats));
}

PyDoc_STRVAR(DiffStats_format__doc__,
    "format(format, width)\n"
    "\n"
    "Format the stats as a string.\n"
    "\n"
    "Returns: str.\n"
    "\n"
    "Parameters:\n"
    "\n"
    "format\n"
    "    The format to use. A pygit2.GIT_DIFF_STATS_* constant.\n"
    "\n"
    "width\n"
    "    The width of the output. The output will be scaled to fit.");

PyObject *
DiffStats_format(DiffStats *self, PyObject *args, PyObject *kwds)
{
    int err, format;
    git_buf buf = { 0 };
    Py_ssize_t width;
    PyObject *str;
    char *keywords[] = {"format", "width", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "in", keywords, &format, &width))
        return NULL;

    if (width <= 0) {
        PyErr_SetString(PyExc_ValueError, "width must be positive");
        return NULL;
    }

    err = git_diff_stats_to_buf(&buf, self->stats, format, width);
    if (err < 0)
        return Error_set(err);

    str = to_unicode(buf.ptr, NULL, NULL);
    git_buf_free(&buf);

    return str;
}

static void
DiffStats_dealloc(DiffStats *self)
{
    git_diff_stats_free(self->stats);
    PyObject_Del(self);
}

PyMethodDef DiffStats_methods[] = {
    METHOD(DiffStats, format, METH_VARARGS | METH_KEYWORDS),
    {NULL}
};

PyGetSetDef DiffStats_getseters[] = {
    GETTER(DiffStats, insertions),
    GETTER(DiffStats, deletions),
    GETTER(DiffStats, files_changed),
    {NULL}
};

PyDoc_STRVAR(DiffStats__doc__, "DiffStats object.");

PyTypeObject DiffStatsType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.DiffStats",                       /* tp_name           */
    sizeof(DiffStats),                          /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)DiffStats_dealloc,             /* tp_dealloc        */
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
    DiffStats__doc__,                          /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    DiffStats_methods,                                         /* tp_methods        */
    0,                                         /* tp_members        */
    DiffStats_getseters,                       /* tp_getset         */
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

    if (!PyInt_Check(value))
        return NULL; /* FIXME Raise error */

    i = PyInt_AsSize_t(value);
    return diff_get_patch_byindex(self->diff, i);
}

PyDoc_STRVAR(Diff_stats__doc__, "Accumulate diff statistics for all patches.");

PyObject *
Diff_stats__get__(Diff *self)
{
    return wrap_diff_stats(self->diff);
}

static void
Diff_dealloc(Diff *self)
{
    git_diff_free(self->diff);
    Py_CLEAR(self->repo);
    PyObject_Del(self);
}

PyGetSetDef Diff_getseters[] = {
    GETTER(Diff, deltas),
    GETTER(Diff, patch),
    GETTER(Diff, stats),
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
