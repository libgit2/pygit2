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
#include <pygit2/types.h>
#include <pygit2/utils.h>
#include <pygit2/diff.h>

extern PyObject *GitError;

extern PyTypeObject TreeType;
extern PyTypeObject IndexType;
extern PyTypeObject DiffType;
extern PyTypeObject HunkType;

static int diff_data_cb(
  const git_diff_delta *delta,
  const git_diff_range *range,
  char line_origin,
  const char *content,
  size_t content_len,
  void *cb_data)
{
    PyObject *hunks, *data;
    Hunk *hunk;
    Py_ssize_t size;

    hunks = PyDict_GetItemString(cb_data, "hunks");
    if (hunks == NULL)
      return -1;

    size = PyList_Size(hunks);
    hunk = (Hunk *)PyList_GetItem(hunks, size - 1);
    if (hunk == NULL)
      return -1;

    data = Py_BuildValue("(s#,i)",
        content, content_len,
        line_origin
    );
    PyList_Append(hunk->data, data);
    Py_DECREF(data);

    return 0;
}

static int diff_hunk_cb(
  const git_diff_delta *delta,
  const git_diff_range *range,
  const char *header,
  size_t header_len,
  void *cb_data)
{
    PyObject *hunks;
    Hunk *hunk;
    int len;
    char* old_path = NULL, *new_path = NULL;
    char oid[GIT_OID_HEXSZ];


    hunks = PyDict_GetItemString(cb_data, "hunks");
    if (hunks == NULL) {
        hunks = PyList_New(0);
        PyDict_SetItemString(cb_data, "hunks", hunks);
        Py_DECREF(hunks);
    }

    hunk = (Hunk*)PyType_GenericNew(&HunkType, NULL, NULL);
    if (hunk == NULL)
        return -1;

    hunk->old_start = range->old_start;
    hunk->old_lines = range->old_lines;
    hunk->new_start = range->new_start;
    hunk->new_lines = range->new_lines;

    hunk->old_mode = delta->old_file.mode;
    hunk->new_mode = delta->new_file.mode;

    git_oid_fmt(oid, &delta->old_file.oid);
    hunk->old_oid = PyUnicode_FromStringAndSize(oid, GIT_OID_HEXSZ);
    git_oid_fmt(oid, &delta->new_file.oid);
    hunk->new_oid = PyUnicode_FromStringAndSize(oid, GIT_OID_HEXSZ);

    if (header) {
        hunk->header = malloc(header_len+1);

        if (hunk->header == NULL)
            return -1;

        memcpy(hunk->header, header, header_len);
        hunk->header[header_len] = '\0';
    }

    if (delta->old_file.path != NULL) {
        len = strlen(delta->old_file.path) + 1;
        old_path = malloc(sizeof(char) * len);
        if (old_path == NULL) {
            free(hunk->header);
            hunk->header = NULL;
            return -1;
        }

        memcpy(old_path, delta->old_file.path, len);
        hunk->old_file = old_path;
    } else {
        hunk->old_file = "";
    }

    if (delta->new_file.path != NULL) {
        len = strlen(delta->new_file.path) + 1;
        new_path = malloc(sizeof(char) * len);
        if (new_path == NULL) {
            free(hunk->header);
            free(old_path);
            return -1;
        }

        memcpy(new_path, delta->new_file.path, len);
        hunk->new_file = new_path;
    } else {
        hunk->new_file = "";
    }

    if (hunk->data == NULL) {
      hunk->data = PyList_New(0);
    }

    if(PyList_Append(hunks, (PyObject *)hunk) == 0) {
        Py_DECREF(hunk);
    }
    else {
        return -1;
    }

    return 0;
};

static int
diff_file_cb(const git_diff_delta *delta, float progress, void *cb_data)
{
    PyObject *files, *file;

    if(delta->old_file.path != NULL && delta->new_file.path != NULL) {
        files = PyDict_GetItemString(cb_data, "files");

        if(files == NULL) {
            files = PyList_New(0);
            PyDict_SetItemString(cb_data, "files", files);
            Py_DECREF(files);
        }

        file = Py_BuildValue("(s,s,i,i)",
            delta->old_file.path,
            delta->new_file.path,
            delta->status,
            delta->similarity
        );

        if (PyList_Append(files, file) == 0) {
            // If success
            Py_DECREF(file);
        }
    }

    return 0;
}


PyDoc_STRVAR(Diff_changes__doc__, "Raw changes.");

PyObject *
Diff_changes__get__(Diff *self)
{

    if (self->diff_changes == NULL) {
        self->diff_changes = PyDict_New();

        git_diff_foreach(
            self->diff,
            &diff_file_cb,
            &diff_hunk_cb,
            &diff_data_cb,
            self->diff_changes
        );
    }

    return PyDict_Copy(self->diff_changes);
}

static int diff_print_cb(
    const git_diff_delta *delta,
    const git_diff_range *range,
    char usage,
    const char *line,
    size_t line_len,
    void *cb_data)
{
    PyObject *data = PyBytes_FromStringAndSize(line, line_len);
    PyBytes_ConcatAndDel((PyObject **)cb_data, data);

    return 0;
}


PyDoc_STRVAR(Diff_patch__doc__, "Patch.");

PyObject *
Diff_patch__get__(Diff *self)
{
    PyObject *patch = PyBytes_FromString("");

    git_diff_print_patch(self->diff, &diff_print_cb, (void*) &patch);

    return patch;
}

static int
Hunk_init(Hunk *self, PyObject *args, PyObject *kwds)
{
    self->header = NULL;

    self->old_file = NULL;
    self->old_start = 0;
    self->old_lines = 0;

    self->new_file = NULL;
    self->new_start = 0;
    self->new_lines = 0;

    self->old_oid = NULL;
    self->new_oid = NULL;

    self->data = PyList_New(0);
    if (self->data == NULL) {
        Py_XDECREF(self);
        return -1;
    }

    return 0;
}

static void
Hunk_dealloc(Hunk *self)
{
    if (self->header != NULL) {
        free(self->header);
    }
    if (self->new_file != NULL) {
        free(self->new_file);
    }
    if (self->old_file != NULL) {
        free(self->old_file);
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
    MEMBER(Hunk, old_oid, T_OBJECT, "Old oid."),
    MEMBER(Hunk, new_start, T_INT, "New start."),
    MEMBER(Hunk, new_lines, T_INT, "New lines."),
    MEMBER(Hunk, new_mode, T_INT, "New mode."),
    MEMBER(Hunk, new_file, T_STRING, "New file."),
    MEMBER(Hunk, new_oid, T_OBJECT, "New oid."),
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
    (initproc)Hunk_init,                       /* tp_init           */
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

    err = git_diff_merge(self->diff, py_diff->diff);
    if (err < 0)
        return Error_set(err);

    Py_XDECREF(self->diff_changes);
    self->diff_changes = NULL;
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

    err = git_diff_find_similar(self->diff, &opts);
    if (err < 0)
        return Error_set(err);

    Py_XDECREF(self->diff_changes);
    self->diff_changes = NULL;
    Py_RETURN_NONE;
}

static void
Diff_dealloc(Diff *self)
{
    git_diff_list_free(self->diff);
    Py_XDECREF(self->repo);
    Py_XDECREF(self->diff_changes);
    PyObject_Del(self);
}

PyGetSetDef Diff_getseters[] = {
    GETTER(Diff, changes),
    GETTER(Diff, patch),
    {NULL}
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
    0,                                         /* tp_as_mapping     */
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
    0,                                         /* tp_iter           */
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
