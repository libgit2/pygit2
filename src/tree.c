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
#include <string.h>
#include "error.h"
#include "utils.h"
#include "repository.h"
#include "oid.h"
#include "tree.h"

extern PyTypeObject TreeType;
extern PyTypeObject DiffType;
extern PyTypeObject TreeIterType;
extern PyTypeObject IndexType;

void
TreeEntry_dealloc(TreeEntry *self)
{
    Py_CLEAR(self->owner);
    git_tree_entry_free((git_tree_entry*)self->entry);
    PyObject_Del(self);
}


PyDoc_STRVAR(TreeEntry_filemode__doc__, "Filemode.");

PyObject *
TreeEntry_filemode__get__(TreeEntry *self)
{
    return PyLong_FromLong(git_tree_entry_filemode(self->entry));
}


PyDoc_STRVAR(TreeEntry_name__doc__, "Name.");

PyObject *
TreeEntry_name__get__(TreeEntry *self)
{
    return to_path(git_tree_entry_name(self->entry));
}


PyDoc_STRVAR(TreeEntry_oid__doc__, "Object id.");

PyObject *
TreeEntry_oid__get__(TreeEntry *self)
{
    const git_oid *oid;

    oid = git_tree_entry_id(self->entry);
    return git_oid_to_python(oid->id);
}


PyDoc_STRVAR(TreeEntry_hex__doc__, "Hex oid.");

PyObject *
TreeEntry_hex__get__(TreeEntry *self)
{
    return git_oid_to_py_str(git_tree_entry_id(self->entry));
}


PyDoc_STRVAR(TreeEntry_to_object__doc__,
  "to_object() -> Object\n"
  "\n"
  "Look up the corresponding object in the repo.");

PyObject *
TreeEntry_to_object(TreeEntry *self)
{
    const git_oid *entry_oid;
    Repository *repo;

    repo = ((Object*)(self->owner))->repo;
    entry_oid = git_tree_entry_id(self->entry);
    return lookup_object(repo, entry_oid, GIT_OBJ_ANY);
}

PyGetSetDef TreeEntry_getseters[] = {
    GETTER(TreeEntry, filemode),
    GETTER(TreeEntry, name),
    GETTER(TreeEntry, oid),
    GETTER(TreeEntry, hex),
    {NULL}
};

PyMethodDef TreeEntry_methods[] = {
    METHOD(TreeEntry, to_object, METH_NOARGS),
    {NULL}
};


PyDoc_STRVAR(TreeEntry__doc__, "TreeEntry objects.");

PyTypeObject TreeEntryType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.TreeEntry",                       /* tp_name           */
    sizeof(TreeEntry),                         /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)TreeEntry_dealloc,             /* tp_dealloc        */
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
    TreeEntry__doc__,                          /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    TreeEntry_methods,                         /* tp_methods        */
    0,                                         /* tp_members        */
    TreeEntry_getseters,                       /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    0,                                         /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};

Py_ssize_t
Tree_len(Tree *self)
{
    assert(self->tree);
    return (Py_ssize_t)git_tree_entrycount(self->tree);
}

int
Tree_contains(Tree *self, PyObject *py_name)
{
    int result = 0;
    char *name = py_path_to_c_str(py_name);
    if (name == NULL)
        return -1;

    result = git_tree_entry_byname(self->tree, name) ? 1 : 0;
    free(name);
    return result;
}

TreeEntry *
wrap_tree_entry(const git_tree_entry *entry, Tree *tree)
{
    TreeEntry *py_entry;

    py_entry = PyObject_New(TreeEntry, &TreeEntryType);
    if (py_entry) {
        py_entry->entry = entry;
        py_entry->owner = (PyObject*)tree;
        Py_INCREF(tree);
    }
    return py_entry;
}

int
Tree_fix_index(Tree *self, PyObject *py_index)
{
    long index;
    size_t len;
    long slen;

    index = PyLong_AsLong(py_index);
    if (PyErr_Occurred())
        return -1;

    len = git_tree_entrycount(self->tree);
    slen = (long)len;
    if (index >= slen) {
        PyErr_SetObject(PyExc_IndexError, py_index);
        return -1;
    }
    else if (index < -slen) {
        PyErr_SetObject(PyExc_IndexError, py_index);
        return -1;
    }

    /* This function is called via mp_subscript, which doesn't do negative
     * index rewriting, so we have to do it manually. */
    if (index < 0)
        index = len + index;
    return (int)index;
}

PyObject *
Tree_iter(Tree *self)
{
    TreeIter *iter;

    iter = PyObject_New(TreeIter, &TreeIterType);
    if (iter) {
        Py_INCREF(self);
        iter->owner = self;
        iter->i = 0;
    }
    return (PyObject*)iter;
}

TreeEntry *
Tree_getitem_by_index(Tree *self, PyObject *py_index)
{
    int index;
    const git_tree_entry *entry;

    index = Tree_fix_index(self, py_index);
    if (PyErr_Occurred())
        return NULL;

    entry = git_tree_entry_byindex(self->tree, index);
    if (!entry) {
        PyErr_SetObject(PyExc_IndexError, py_index);
        return NULL;
    }
    return wrap_tree_entry(git_tree_entry_dup(entry), self);
}

TreeEntry *
Tree_getitem(Tree *self, PyObject *value)
{
    char *path;
    git_tree_entry *entry;
    int err;

    /* Case 1: integer */
    if (PyLong_Check(value))
        return Tree_getitem_by_index(self, value);

    /* Case 2: byte or text string */
    path = py_path_to_c_str(value);
    if (path == NULL)
        return NULL;

    err = git_tree_entry_bypath(&entry, self->tree, path);
    free(path);

    if (err == GIT_ENOTFOUND) {
        PyErr_SetObject(PyExc_KeyError, value);
        return NULL;
    }

    if (err < 0)
        return (TreeEntry*)Error_set(err);

    /* git_tree_entry_dup is already done in git_tree_entry_bypath */
    return wrap_tree_entry(entry, self);
}


PyDoc_STRVAR(Tree_diff__doc__,
  "diff([obj, flags]) -> Diff\n"
  "\n"
  "Get changes between current tree instance with another tree, an index or\n"
  "the working dir.\n"
  "\n"
  "Arguments:\n"
  "\n"
  "obj\n"
  "    If not given compare diff against working dir. Possible valid\n"
  "    arguments are instances of Tree or Index.\n"
  "\n"
  "flags\n"
  "    TODO");

PyObject *
Tree_diff(Tree *self, PyObject *args)
{
    git_diff_options opts = GIT_DIFF_OPTIONS_INIT;
    git_diff_list *diff;
    int err;

    Diff *py_diff;
    PyObject *py_obj = NULL;

    if (!PyArg_ParseTuple(args, "|Oi", &py_obj, &opts.flags))
        return NULL;

    if (py_obj == NULL) {
        err = git_diff_tree_to_workdir(
                &diff,
                self->repo->repo,
                self->tree,
                &opts);
    } else if (PyObject_TypeCheck(py_obj, &TreeType)) {
        err = git_diff_tree_to_tree(
                &diff,
                self->repo->repo,
                self->tree,
                ((Tree *)py_obj)->tree,
                &opts);
    } else if (PyObject_TypeCheck(py_obj, &IndexType)) {
        err = git_diff_tree_to_index(
                &diff,
                self->repo->repo,
                self->tree,
                ((Index *)py_obj)->index,
                &opts);
    } else {
        PyErr_SetObject(PyExc_TypeError, py_obj);
        return NULL;
    }

    if (err < 0)
        return Error_set(err);

    py_diff = PyObject_New(Diff, &DiffType);
    if (py_diff) {
        Py_INCREF(self->repo);
        py_diff->repo = self->repo;
        py_diff->list = diff;
    }

    return (PyObject*)py_diff;
}


PySequenceMethods Tree_as_sequence = {
    0,                          /* sq_length */
    0,                          /* sq_concat */
    0,                          /* sq_repeat */
    0,                          /* sq_item */
    0,                          /* sq_slice */
    0,                          /* sq_ass_item */
    0,                          /* sq_ass_slice */
    (objobjproc)Tree_contains,  /* sq_contains */
};

PyMappingMethods Tree_as_mapping = {
    (lenfunc)Tree_len,            /* mp_length */
    (binaryfunc)Tree_getitem,     /* mp_subscript */
    0,                            /* mp_ass_subscript */
};

PyMethodDef Tree_methods[] = {
    METHOD(Tree, diff, METH_VARARGS),
    {NULL}
};


PyDoc_STRVAR(Tree__doc__, "Tree objects.");

PyTypeObject TreeType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.Tree",                            /* tp_name           */
    sizeof(Tree),                              /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    0,                                         /* tp_dealloc        */
    0,                                         /* tp_print          */
    0,                                         /* tp_getattr        */
    0,                                         /* tp_setattr        */
    0,                                         /* tp_compare        */
    0,                                         /* tp_repr           */
    0,                                         /* tp_as_number      */
    &Tree_as_sequence,                         /* tp_as_sequence    */
    &Tree_as_mapping,                          /* tp_as_mapping     */
    0,                                         /* tp_hash           */
    0,                                         /* tp_call           */
    0,                                         /* tp_str            */
    0,                                         /* tp_getattro       */
    0,                                         /* tp_setattro       */
    0,                                         /* tp_as_buffer      */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,  /* tp_flags          */
    Tree__doc__,                               /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    (getiterfunc)Tree_iter,                    /* tp_iter           */
    0,                                         /* tp_iternext       */
    Tree_methods,                              /* tp_methods        */
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


void
TreeIter_dealloc(TreeIter *self)
{
    Py_CLEAR(self->owner);
    PyObject_Del(self);
}

TreeEntry *
TreeIter_iternext(TreeIter *self)
{
    const git_tree_entry *tree_entry;

    tree_entry = git_tree_entry_byindex(self->owner->tree, self->i);
    if (!tree_entry)
        return NULL;

    self->i += 1;
    return (TreeEntry*)wrap_tree_entry(git_tree_entry_dup(tree_entry),
                                       self->owner);
}


PyDoc_STRVAR(TreeIter__doc__, "Tree iterator.");

PyTypeObject TreeIterType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.TreeIter",                        /* tp_name           */
    sizeof(TreeIter),                          /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)TreeIter_dealloc ,             /* tp_dealloc        */
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
    TreeIter__doc__,                           /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    PyObject_SelfIter,                         /* tp_iter           */
    (iternextfunc)TreeIter_iternext,           /* tp_iternext       */
};
