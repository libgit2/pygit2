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
  void *cb_data,
  git_diff_delta *delta,
  git_diff_range *range,
  char line_origin,
  const char *content,
  size_t content_len)
{
    PyObject *hunks, *data, *tmp;
    Hunk *hunk;
    Py_ssize_t size;

    hunks = PyDict_GetItemString(cb_data, "hunks");
    if (hunks == NULL)
      return -1;

    size = PyList_Size(hunks);
    hunk = (Hunk *)PyList_GetItem(hunks, size - 1);
    if (hunk == NULL)
      return -1;

    tmp = PyBytes_FromStringAndSize(content, content_len);

    data = Py_BuildValue("(O,i)",
        tmp,
        line_origin
    );

    PyList_Append(hunk->data, data);

    return 0;
}

static int diff_hunk_cb(
  void *cb_data,
  git_diff_delta *delta,
  git_diff_range *range,
  const char *header,
  size_t header_len)
{
    PyObject *hunks;
    Hunk *hunk;
    int len;
    char* old_path, *new_path;


    hunks = PyDict_GetItemString(cb_data, "hunks");
    if (hunks == NULL) {
        hunks = PyList_New(0);
        PyDict_SetItemString(cb_data, "hunks", hunks);
    }

    hunk = (Hunk*)PyType_GenericNew(&HunkType, NULL, NULL);
    if (hunk == NULL)
        return -1;

    hunk->old_start = range->old_start;
    hunk->old_lines = range->old_lines;
    hunk->new_start = range->new_start;
    hunk->new_lines = range->new_lines;

    if (delta->old_file.path != NULL) {
        len = strlen(delta->old_file.path) + 1;
        old_path = malloc(sizeof(char) * len);
        memcpy(old_path, delta->old_file.path, len);
        hunk->old_file = old_path;
    } else {
        hunk->old_file = "";
    }

    if (delta->new_file.path != NULL) {
        len = strlen(delta->new_file.path) + 1;
        new_path = malloc(sizeof(char) * len);
        memcpy(new_path, delta->new_file.path, len);
        hunk->new_file = new_path;
    } else {
        hunk->new_file = "";
    }

    if (hunk->data == NULL) {
      hunk->data = PyList_New(0);
    }

    PyList_Append(hunks, (PyObject *)hunk);

    return 0;
};

static int diff_file_cb(void *cb_data, git_diff_delta *delta, float progress)
{
    PyObject *files, *file;

    if(delta->old_file.path != NULL && delta->new_file.path != NULL) {
        files = PyDict_GetItemString(cb_data, "files");

        if(files == NULL) {
            files = PyList_New(0);
            PyDict_SetItemString(cb_data, "files", files);
        }

        file = Py_BuildValue("(s,s,i)",
            delta->old_file.path,
            delta->new_file.path,
            delta->status
        );

        PyList_Append(files, file);
    }

    return 0;
}

PyObject *
Diff_changes(Diff *self)
{
    PyObject *payload;
    payload = PyDict_New();

    git_diff_foreach(
        self->diff,
        payload,
        &diff_file_cb,
        &diff_hunk_cb,
        &diff_data_cb
    );

    return payload;
}

static int diff_print_cb(
    void *cb_data,
    git_diff_delta *delta,
    git_diff_range *range,
    char usage,
    const char *line,
    size_t line_len)
{
    PyObject *data = PyBytes_FromStringAndSize(line, line_len);
    PyBytes_ConcatAndDel((PyObject **)cb_data, data);

    return 0;
}

PyObject *
Diff_patch(Diff *self)
{
    PyObject *patch = PyBytes_FromString("");

    git_diff_print_patch(self->diff, &patch, &diff_print_cb);

    return patch;
}

static int
Hunk_init(Hunk *self, PyObject *args, PyObject *kwds)
{
      self->old_start = 0;
      self->old_lines = 0;

      self->new_start = 0;
      self->new_lines = 0;

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
    Py_XDECREF(self->data);
    PyObject_Del(self);
}

PyMemberDef Hunk_members[] = {
    {"old_start", T_INT, offsetof(Hunk, old_start), 0, "old start"},
    {"old_lines", T_INT, offsetof(Hunk, old_lines), 0, "old lines"},
    {"old_file",  T_STRING, offsetof(Hunk, old_file), 0, "old file"},
    {"new_start", T_INT, offsetof(Hunk, new_start), 0, "new start"},
    {"new_lines", T_INT, offsetof(Hunk, new_lines), 0, "new lines"},
    {"new_file",  T_STRING, offsetof(Hunk, new_file), 0, "old file"},
    {"data",      T_OBJECT, offsetof(Hunk, data), 0, "data"},
    {NULL}
};

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
    "Hunk object",                             /* tp_doc            */
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

static void
Diff_dealloc(Diff *self)
{
    git_diff_list_free(self->diff);
    Py_XDECREF(self->repo);
    PyObject_Del(self);
}

PyGetSetDef Diff_getseters[] = {
    {"changes", (getter)Diff_changes, NULL, "raw changes", NULL},
    {"patch", (getter)Diff_patch, NULL, "patch", NULL},
    {NULL}
};

static PyMethodDef Diff_methods[] = {
    {"merge", (PyCFunction)Diff_merge, METH_VARARGS,
     "Merge one diff into another."},
    {NULL, NULL, 0, NULL}
};

PyTypeObject DiffType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.Diff",                             /* tp_name           */
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
    "Diff objects",                            /* tp_doc            */
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
