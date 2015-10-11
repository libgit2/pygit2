/*
 * Copyright 2010-2015 The pygit2 contributors
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
#include "diff.h"

extern PyTypeObject TreeType;
extern PyTypeObject TreeEntryType;
extern PyTypeObject DiffType;
extern PyTypeObject TreeIterType;
extern PyTypeObject IndexType;

void
TreeEntry_dealloc(TreeEntry *self)
{
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


PyDoc_STRVAR(TreeEntry__name__doc__, "Name (bytes).");

PyObject *
TreeEntry__name__get__(TreeEntry *self)
{
    return PyBytes_FromString(git_tree_entry_name(self->entry));
}


PyDoc_STRVAR(TreeEntry_type__doc__, "Type.");

PyObject *
TreeEntry_type__get__(TreeEntry *self)
{
    return to_path(git_object_type2string(git_tree_entry_type(self->entry)));
}


PyDoc_STRVAR(TreeEntry_id__doc__, "Object id.");

PyObject *
TreeEntry_id__get__(TreeEntry *self)
{
    const git_oid *oid;

    oid = git_tree_entry_id(self->entry);
    return git_oid_to_python(oid);
}

PyDoc_STRVAR(TreeEntry_oid__doc__, "Object id.\n"
    "This attribute is deprecated. Please use 'id'");

PyObject *
TreeEntry_oid__get__(TreeEntry *self)
{
    return TreeEntry_id__get__(self);
}

static int
compare_ids(TreeEntry *a, TreeEntry *b)
{
    const git_oid *id_a, *id_b;
    id_a = git_tree_entry_id(a->entry);
    id_b = git_tree_entry_id(b->entry);
    return git_oid_cmp(id_a, id_b);
}

PyObject *
TreeEntry_richcompare(PyObject *a, PyObject *b, int op)
{
    PyObject *res;
    TreeEntry *ta, *tb;
    int cmp;

    /* We only support comparing to another tree entry */
    if (!PyObject_TypeCheck(b, &TreeEntryType)) {
        Py_INCREF(Py_NotImplemented);
        return Py_NotImplemented;
    }

    ta = (TreeEntry *) a;
    tb = (TreeEntry *) b;

    /* This is sorting order, if they sort equally, we still need to compare the ids */
    cmp = git_tree_entry_cmp(ta->entry, tb->entry);
    if (cmp == 0)
        cmp = compare_ids(ta, tb);

    switch (op) {
        case Py_LT:
            res = (cmp <= 0) ? Py_True: Py_False;
            break;
        case Py_LE:
            res = (cmp < 0) ? Py_True: Py_False;
            break;
        case Py_EQ:
            res = (cmp == 0) ? Py_True: Py_False;
            break;
        case Py_NE:
            res = (cmp != 0) ? Py_True: Py_False;
            break;
        case Py_GT:
            res = (cmp > 0) ? Py_True: Py_False;
            break;
        case Py_GE:
            res = (cmp >= 0) ? Py_True: Py_False;
            break;
        default:
            PyErr_Format(PyExc_RuntimeError, "Unexpected '%d' op", op);
            return NULL;
    }

    Py_INCREF(res);
    return res;
}


PyDoc_STRVAR(TreeEntry_hex__doc__, "Hex oid.");

PyObject *
TreeEntry_hex__get__(TreeEntry *self)
{
    return git_oid_to_py_str(git_tree_entry_id(self->entry));
}

PyObject *
TreeEntry_repr(TreeEntry *self)
{
    char str[GIT_OID_HEXSZ + 1] = { 0 };
    const char *typename;

    typename = git_object_type2string(git_tree_entry_type(self->entry));
    git_oid_fmt(str, git_tree_entry_id(self->entry));
    return PyString_FromFormat("pygit2.TreeEntry('%s', %s, %s)", git_tree_entry_name(self->entry), typename, str);
}

PyGetSetDef TreeEntry_getseters[] = {
    GETTER(TreeEntry, filemode),
    GETTER(TreeEntry, name),
    GETTER(TreeEntry, _name),
    GETTER(TreeEntry, oid),
    GETTER(TreeEntry, id),
    GETTER(TreeEntry, hex),
    GETTER(TreeEntry, type),
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
    (reprfunc)TreeEntry_repr,                  /* tp_repr           */
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
    TreeEntry__doc__,                          /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    (richcmpfunc)TreeEntry_richcompare,        /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    0,                                         /* tp_methods        */
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
    int err;
    git_tree_entry *entry;
    char *name;

    name = py_path_to_c_str(py_name);
    if (name == NULL)
        return -1;

    err = git_tree_entry_bypath(&entry, self->tree, name);
    free(name);

    if (err == GIT_ENOTFOUND)
        return 0;

    if (err < 0) {
        Error_set(err);
        return -1;
    }

    git_tree_entry_free(entry);

    return 1;
}

TreeEntry *
wrap_tree_entry(const git_tree_entry *entry)
{
    TreeEntry *py_entry;

    py_entry = PyObject_New(TreeEntry, &TreeEntryType);
    if (py_entry)
        py_entry->entry = entry;

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
    const git_tree_entry *entry_src;
    git_tree_entry *entry;

    index = Tree_fix_index(self, py_index);
    if (PyErr_Occurred())
        return NULL;

    entry_src = git_tree_entry_byindex(self->tree, index);
    if (!entry_src) {
        PyErr_SetObject(PyExc_IndexError, py_index);
        return NULL;
    }

    if (git_tree_entry_dup(&entry, entry_src) < 0) {
        PyErr_SetNone(PyExc_MemoryError);
        return NULL;
    }

    return wrap_tree_entry(entry);
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
    return wrap_tree_entry(entry);
}


PyDoc_STRVAR(Tree_diff_to_workdir__doc__,
  "diff_to_workdir([flags, context_lines, interhunk_lines]) -> Diff\n"
  "\n"
  "Show the changes between the :py:class:`~pygit2.Tree` and the workdir.\n"
  "\n"
  "Arguments:\n"
  "\n"
  "flag: a GIT_DIFF_* constant.\n"
  "\n"
  "context_lines: the number of unchanged lines that define the boundary\n"
  "   of a hunk (and to display before and after)\n"
  "\n"
  "interhunk_lines: the maximum number of unchanged lines between hunk\n"
  "   boundaries before the hunks will be merged into a one.\n");

PyObject *
Tree_diff_to_workdir(Tree *self, PyObject *args)
{
    git_diff_options opts = GIT_DIFF_OPTIONS_INIT;
    git_diff *diff;
    Repository *py_repo;
    int err;

    if (!PyArg_ParseTuple(args, "|IHH", &opts.flags, &opts.context_lines,
                                        &opts.interhunk_lines))
        return NULL;

    py_repo = self->repo;
    err = git_diff_tree_to_workdir(&diff, py_repo->repo, self->tree, &opts);
    if (err < 0)
        return Error_set(err);

    return wrap_diff(diff, py_repo);
}


PyDoc_STRVAR(Tree_diff_to_index__doc__,
  "diff_to_index(index, [flags, context_lines, interhunk_lines]) -> Diff\n"
  "\n"
  "Show the changes between the index and a given :py:class:`~pygit2.Tree`.\n"
  "\n"
  "Arguments:\n"
  "\n"
  "tree: the :py:class:`~pygit2.Tree` to diff.\n"
  "\n"
  "flag: a GIT_DIFF_* constant.\n"
  "\n"
  "context_lines: the number of unchanged lines that define the boundary\n"
  "   of a hunk (and to display before and after)\n"
  "\n"
  "interhunk_lines: the maximum number of unchanged lines between hunk\n"
  "   boundaries before the hunks will be merged into a one.\n");

PyObject *
Tree_diff_to_index(Tree *self, PyObject *args, PyObject *kwds)
{
    git_diff_options opts = GIT_DIFF_OPTIONS_INIT;
    git_diff *diff;
    git_index *index;
    char *buffer;
    Py_ssize_t length;
    Repository *py_repo;
    PyObject *py_idx, *py_idx_ptr;
    int err;

    if (!PyArg_ParseTuple(args, "O|IHH", &py_idx, &opts.flags,
                                        &opts.context_lines,
                                        &opts.interhunk_lines))
        return NULL;

    /*
     * This is a hack to check whether we're passed an index, as I
     * haven't found a good way to grab a type object for
     * pygit2.index.Index.
     */
    if (!PyObject_GetAttrString(py_idx, "_index")) {
        PyErr_SetString(PyExc_TypeError, "argument must be an Index");
        return NULL;
    }
    py_idx_ptr = PyObject_GetAttrString(py_idx, "_pointer");
    if (!py_idx_ptr)
        return NULL;

    /* Here we need to do the opposite conversion from the _pointer getters */
    if (PyBytes_AsStringAndSize(py_idx_ptr, &buffer, &length))
        return NULL;

    if (length != sizeof(git_index *)) {
        PyErr_SetString(PyExc_TypeError, "passed value is not a pointer");
        return NULL;
    }

    /* the "buffer" contains the pointer */
    index = *((git_index **) buffer);

    py_repo = self->repo;
    err = git_diff_tree_to_index(&diff, py_repo->repo, self->tree, index, &opts);
    if (err < 0)
        return Error_set(err);

    return wrap_diff(diff, py_repo);
}


PyDoc_STRVAR(Tree_diff_to_tree__doc__,
  "diff_to_tree([tree, flags, context_lines, interhunk_lines, swap]) -> Diff\n"
  "\n"
  "Show the changes between two trees\n"
  "\n"
  "Arguments:\n"
  "\n"
  "tree: the :py:class:`~pygit2.Tree` to diff. If no tree is given the empty\n"
  "   tree will be used instead.\n"
  "\n"
  "flag: a GIT_DIFF_* constant.\n"
  "\n"
  "context_lines: the number of unchanged lines that define the boundary\n"
  "   of a hunk (and to display before and after)\n"
  "\n"
  "interhunk_lines: the maximum number of unchanged lines between hunk\n"
  "   boundaries before the hunks will be merged into a one.\n"
  "\n"
  "swap: instead of diffing a to b. Diff b to a.\n");

PyObject *
Tree_diff_to_tree(Tree *self, PyObject *args, PyObject *kwds)
{
    git_diff_options opts = GIT_DIFF_OPTIONS_INIT;
    git_diff *diff;
    git_tree *from, *to, *tmp;
    Repository *py_repo;
    int err, swap = 0;
    char *keywords[] = {"obj", "flags", "context_lines", "interhunk_lines",
                        "swap", NULL};

    Tree *py_tree = NULL;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|O!IHHi", keywords,
                                     &TreeType, &py_tree, &opts.flags,
                                     &opts.context_lines,
                                     &opts.interhunk_lines, &swap))
        return NULL;

    py_repo = self->repo;
    to = (py_tree == NULL) ? NULL : py_tree->tree;
    from = self->tree;
    if (swap > 0) {
        tmp = from;
        from = to;
        to = tmp;
    }

    err = git_diff_tree_to_tree(&diff, py_repo->repo, from, to, &opts);
    if (err < 0)
        return Error_set(err);

    return wrap_diff(diff, py_repo);
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
    METHOD(Tree, diff_to_tree, METH_VARARGS | METH_KEYWORDS),
    METHOD(Tree, diff_to_workdir, METH_VARARGS),
    METHOD(Tree, diff_to_index, METH_VARARGS | METH_KEYWORDS),
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
    Py_TPFLAGS_DEFAULT,                        /* tp_flags          */
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
    const git_tree_entry *entry_src;
    git_tree_entry *entry;

    entry_src = git_tree_entry_byindex(self->owner->tree, self->i);
    if (!entry_src)
        return NULL;

    self->i += 1;

    if (git_tree_entry_dup(&entry, entry_src) < 0) {
        PyErr_SetNone(PyExc_MemoryError);
        return NULL;
    }
    return wrap_tree_entry(entry);
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
    Py_TPFLAGS_DEFAULT,                        /* tp_flags          */
    TreeIter__doc__,                           /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    PyObject_SelfIter,                         /* tp_iter           */
    (iternextfunc)TreeIter_iternext,           /* tp_iternext       */
};
