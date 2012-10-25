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
#include <pygit2/error.h>
#include <pygit2/types.h>
#include <pygit2/utils.h>
#include <pygit2/oid.h>
#include <pygit2/index.h>

extern PyTypeObject IndexType;
extern PyTypeObject TreeType;
extern PyTypeObject DiffType;
extern PyTypeObject IndexIterType;
extern PyTypeObject IndexEntryType;

int
Index_init(Index *self, PyObject *args, PyObject *kwds)
{
    char *path;
    int err;

    if (kwds) {
        PyErr_SetString(PyExc_TypeError,
                        "Index takes no keyword arguments");
        return -1;
    }

    if (!PyArg_ParseTuple(args, "s", &path))
        return -1;

    err = git_index_open(&self->index, path);
    if (err < 0) {
        Error_set_str(err, path);
        return -1;
    }

    return 0;
}

void
Index_dealloc(Index* self)
{
    PyObject_GC_UnTrack(self);
    Py_XDECREF(self->repo);
    git_index_free(self->index);
    PyObject_GC_Del(self);
}

int
Index_traverse(Index *self, visitproc visit, void *arg)
{
    Py_VISIT(self->repo);
    return 0;
}

PyObject *
Index_add(Index *self, PyObject *args)
{
    int err;
    const char *path;
    int stage=0;

    if (!PyArg_ParseTuple(args, "s|i", &path, &stage))
        return NULL;

    err = git_index_add(self->index, path, stage);
    if (err < 0)
        return Error_set_str(err, path);

    Py_RETURN_NONE;
}

PyObject *
Index_clear(Index *self)
{
    git_index_clear(self->index);
    Py_RETURN_NONE;
}

PyObject *
Index_diff_tree(Index *self, PyObject *args)
{
    git_diff_options opts = {0};
    git_diff_list *diff;
    int err;

    Diff *py_diff;
    PyObject *py_obj = NULL;

    if (!PyArg_ParseTuple(args, "|O", &py_obj))
        return NULL;

    if (py_obj == NULL) {
        err = git_diff_workdir_to_index(
                self->repo->repo,
                &opts,
                &diff);
    } else if (PyObject_TypeCheck(py_obj, &TreeType)) {
        err = git_diff_index_to_tree(
                self->repo->repo,
                &opts,
                ((Tree *)py_obj)->tree,
                &diff);
    } else {
        PyErr_SetObject(PyExc_TypeError, py_obj);
        return NULL;
    }
    if (err < 0)
        return Error_set(err);

    py_diff = PyObject_New(Diff, &DiffType);
    if (py_diff) {
        Py_INCREF(py_diff);
        Py_INCREF(self->repo);
        py_diff->repo = self->repo;
        py_diff->diff = diff;
    }

    return (PyObject*)py_diff;
}

PyObject *
Index_find(Index *self, PyObject *py_path)
{
    char *path;
    long idx;

    path = PyString_AsString(py_path);
    if (!path)
        return NULL;

    idx = (long)git_index_find(self->index, path);
    if (idx < 0)
        return Error_set_str(idx, path);

    return PyInt_FromLong(idx);
}

PyObject *
Index_read(Index *self)
{
    int err;

    err = git_index_read(self->index);
    if (err < GIT_OK)
        return Error_set(err);

    Py_RETURN_NONE;
}

PyObject *
Index_write(Index *self)
{
    int err;

    err = git_index_write(self->index);
    if (err < GIT_OK)
        return Error_set(err);

    Py_RETURN_NONE;
}

/* This is an internal function, used by Index_getitem and Index_setitem */
int
Index_get_position(Index *self, PyObject *value)
{
    char *path;
    int idx;

    /* Case 1: integer */
    if (PyInt_Check(value)) {
        idx = (int)PyInt_AsLong(value);
        if (idx == -1 && PyErr_Occurred())
            return -1;
        if (idx < 0) {
            PyErr_SetObject(PyExc_ValueError, value);
            return -1;
        }
        return idx;
    }

    /* Case 2: byte or text string */
    path = py_path_to_c_str(value);
    if (!path)
        return -1;
    idx = git_index_find(self->index, path);
    if (idx < 0) {
        Error_set_str(idx, path);
        free(path);
        return -1;
    }
    return idx;
}

int
Index_contains(Index *self, PyObject *value)
{
    char *path;
    int idx;

    path = py_path_to_c_str(value);
    if (!path)
        return -1;
    idx = git_index_find(self->index, path);
    if (idx == GIT_ENOTFOUND)
        return 0;
    if (idx < 0) {
        Error_set_str(idx, path);
        free(path);
        return -1;
    }

    return 1;
}

PyObject *
Index_iter(Index *self)
{
    IndexIter *iter;

    iter = PyObject_New(IndexIter, &IndexIterType);
    if (iter) {
        Py_INCREF(self);
        iter->owner = self;
        iter->i = 0;
    }
    return (PyObject*)iter;
}

Py_ssize_t
Index_len(Index *self)
{
    return (Py_ssize_t)git_index_entrycount(self->index);
}

PyObject *
wrap_index_entry(git_index_entry *entry, Index *index)
{
    IndexEntry *py_entry;

    py_entry = PyObject_New(IndexEntry, &IndexEntryType);
    if (py_entry)
        py_entry->entry = entry;

    return (PyObject*)py_entry;
}

PyObject *
Index_getitem(Index *self, PyObject *value)
{
    int idx;
    git_index_entry *index_entry;

    idx = Index_get_position(self, value);
    if (idx == -1)
        return NULL;

    index_entry = git_index_get(self->index, idx);
    if (!index_entry) {
        PyErr_SetObject(PyExc_KeyError, value);
        return NULL;
    }

    return wrap_index_entry(index_entry, self);
}

int
Index_setitem(Index *self, PyObject *key, PyObject *value)
{
    int err;
    int idx;

    if (value) {
        PyErr_SetString(PyExc_NotImplementedError,
                        "set item on index not yet implemented");
        return -1;
    }

    idx = Index_get_position(self, key);
    if (idx == -1)
        return -1;

    err = git_index_remove(self->index, idx);
    if (err < 0) {
        Error_set(err);
        return -1;
    }

    return 0;
}

PyObject *
Index_read_tree(Index *self, PyObject *value)
{
    git_oid oid;
    git_tree *tree;
    int err, len;

    len = py_str_to_git_oid(value, &oid);
    if (len < 0)
        return NULL;

    err = git_tree_lookup_prefix(&tree, self->repo->repo, &oid,
                                 (unsigned int)len);
    if (err < 0)
        return Error_set(err);

    err = git_index_read_tree(self->index, tree);
    if (err < 0)
        return Error_set(err);

    Py_RETURN_NONE;
}

PyObject *
Index_write_tree(Index *self)
{
    git_oid oid;
    int err;

    err = git_tree_create_fromindex(&oid, self->index);
    if (err < 0)
        return Error_set(err);

    return git_oid_to_python(oid.id);
}

PyMethodDef Index_methods[] = {
    {"add", (PyCFunction)Index_add, METH_VARARGS,
     "Add or update an index entry from a file in disk."},
    {"clear", (PyCFunction)Index_clear, METH_NOARGS,
     "Clear the contents (all the entries) of an index object."},
    {"diff", (PyCFunction)Index_diff_tree, METH_VARARGS,
     "Diff index to tree."},
    {"_find", (PyCFunction)Index_find, METH_O,
     "Find the first index of any entries which point to given path in the"
     " Git index."},
    {"read", (PyCFunction)Index_read, METH_NOARGS,
     "Update the contents of an existing index object in memory by reading"
     " from the hard disk."},
    {"write", (PyCFunction)Index_write, METH_NOARGS,
     "Write an existing index object from memory back to disk using an"
     " atomic file lock."},
    {"read_tree", (PyCFunction)Index_read_tree, METH_O,
     "Update the index file from the given tree object."},
    {"write_tree", (PyCFunction)Index_write_tree, METH_NOARGS,
     "Create a tree object from the index file, return its oid."},
    {NULL}
};

PySequenceMethods Index_as_sequence = {
    0,                          /* sq_length */
    0,                          /* sq_concat */
    0,                          /* sq_repeat */
    0,                          /* sq_item */
    0,                          /* sq_slice */
    0,                          /* sq_ass_item */
    0,                          /* sq_ass_slice */
    (objobjproc)Index_contains, /* sq_contains */
};

PyMappingMethods Index_as_mapping = {
    (lenfunc)Index_len,              /* mp_length */
    (binaryfunc)Index_getitem,       /* mp_subscript */
    (objobjargproc)Index_setitem,    /* mp_ass_subscript */
};

PyTypeObject IndexType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.Index",                            /* tp_name           */
    sizeof(Index),                             /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)Index_dealloc,                 /* tp_dealloc        */
    0,                                         /* tp_print          */
    0,                                         /* tp_getattr        */
    0,                                         /* tp_setattr        */
    0,                                         /* tp_compare        */
    0,                                         /* tp_repr           */
    0,                                         /* tp_as_number      */
    &Index_as_sequence,                        /* tp_as_sequence    */
    &Index_as_mapping,                         /* tp_as_mapping     */
    0,                                         /* tp_hash           */
    0,                                         /* tp_call           */
    0,                                         /* tp_str            */
    0,                                         /* tp_getattro       */
    0,                                         /* tp_setattro       */
    0,                                         /* tp_as_buffer      */
    Py_TPFLAGS_DEFAULT |
    Py_TPFLAGS_BASETYPE |
    Py_TPFLAGS_HAVE_GC,                        /* tp_flags          */
    "Index file",                              /* tp_doc            */
    (traverseproc)Index_traverse,              /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    (getiterfunc)Index_iter,                   /* tp_iter           */
    0,                                         /* tp_iternext       */
    Index_methods,                             /* tp_methods        */
    0,                                         /* tp_members        */
    0,                                         /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    (initproc)Index_init,                      /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};


void
IndexIter_dealloc(IndexIter *self)
{
    Py_CLEAR(self->owner);
    PyObject_Del(self);
}

PyObject *
IndexIter_iternext(IndexIter *self)
{
    git_index_entry *index_entry;

    index_entry = git_index_get(self->owner->index, self->i);
    if (!index_entry)
        return NULL;

    self->i += 1;
    return wrap_index_entry(index_entry, self->owner);
}

PyTypeObject IndexIterType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.IndexIter",                      /* tp_name           */
    sizeof(IndexIter),                       /* tp_basicsize      */
    0,                                       /* tp_itemsize       */
    (destructor)IndexIter_dealloc ,          /* tp_dealloc        */
    0,                                       /* tp_print          */
    0,                                       /* tp_getattr        */
    0,                                       /* tp_setattr        */
    0,                                       /* tp_compare        */
    0,                                       /* tp_repr           */
    0,                                       /* tp_as_number      */
    0,                                       /* tp_as_sequence    */
    0,                                       /* tp_as_mapping     */
    0,                                       /* tp_hash           */
    0,                                       /* tp_call           */
    0,                                       /* tp_str            */
    PyObject_GenericGetAttr,                 /* tp_getattro       */
    0,                                       /* tp_setattro       */
    0,                                       /* tp_as_buffer      */
    Py_TPFLAGS_DEFAULT |
    Py_TPFLAGS_BASETYPE,                     /* tp_flags          */
    0,                                       /* tp_doc            */
    0,                                       /* tp_traverse       */
    0,                                       /* tp_clear          */
    0,                                       /* tp_richcompare    */
    0,                                       /* tp_weaklistoffset */
    PyObject_SelfIter,                       /* tp_iter           */
    (iternextfunc)IndexIter_iternext,        /* tp_iternext       */
};

void
IndexEntry_dealloc(IndexEntry *self)
{
    PyObject_Del(self);
}

PyObject *
IndexEntry_get_mode(IndexEntry *self)
{
    return PyInt_FromLong(self->entry->mode);
}

PyObject *
IndexEntry_get_path(IndexEntry *self)
{
    return to_path(self->entry->path);
}

PyObject *
IndexEntry_get_oid(IndexEntry *self)
{
    return git_oid_to_python(self->entry->oid.id);
}

PyObject *
IndexEntry_get_hex(IndexEntry *self)
{
    return git_oid_to_py_str(&self->entry->oid);
}

PyGetSetDef IndexEntry_getseters[] = {
    {"mode", (getter)IndexEntry_get_mode, NULL, "mode", NULL},
    {"path", (getter)IndexEntry_get_path, NULL, "path", NULL},
    {"oid", (getter)IndexEntry_get_oid, NULL, "object id",  NULL},
    {"hex", (getter)IndexEntry_get_hex, NULL, "hex oid",  NULL},
    {NULL},
};

PyTypeObject IndexEntryType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.IndexEntry",                       /* tp_name           */
    sizeof(IndexEntry),                        /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)IndexEntry_dealloc,            /* tp_dealloc        */
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
    "Index entry",                             /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    0,                                         /* tp_methods        */
    0,                                         /* tp_members        */
    IndexEntry_getseters,                      /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    0,                                         /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};
