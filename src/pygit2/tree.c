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
#include <pygit2/utils.h>
#include <pygit2/repository.h>
#include <pygit2/oid.h>
#include <pygit2/tree.h>

extern PyTypeObject TreeType;
extern PyTypeObject DiffType;
extern PyTypeObject TreeIterType;
extern PyTypeObject IndexType;

void
TreeEntry_dealloc(TreeEntry *self)
{
    Py_XDECREF(self->owner);
    PyObject_Del(self);
}

PyObject *
TreeEntry_get_attributes(TreeEntry *self)
{
    return PyInt_FromLong(git_tree_entry_attributes(self->entry));
}

PyObject *
TreeEntry_get_name(TreeEntry *self)
{
    return to_path(git_tree_entry_name(self->entry));
}

PyObject *
TreeEntry_get_oid(TreeEntry *self)
{
    const git_oid *oid;

    oid = git_tree_entry_id(self->entry);
    return git_oid_to_python(oid->id);
}

PyObject *
TreeEntry_get_hex(TreeEntry *self)
{
    return git_oid_to_py_str(git_tree_entry_id(self->entry));
}

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
    {"attributes", (getter)TreeEntry_get_attributes, NULL, "attributes", NULL},
    {"name", (getter)TreeEntry_get_name, NULL, "name", NULL},
    {"oid", (getter)TreeEntry_get_oid, NULL, "object id", NULL},
    {"hex", (getter)TreeEntry_get_hex, NULL, "hex oid", NULL},
    {NULL}
};

PyMethodDef TreeEntry_methods[] = {
    {"to_object", (PyCFunction)TreeEntry_to_object, METH_NOARGS,
     "Look up the corresponding object in the repo."},
    {NULL, NULL, 0, NULL}
};

PyTypeObject TreeEntryType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.TreeEntry",                        /* tp_name           */
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
    "TreeEntry objects",                       /* tp_doc            */
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

    index = PyInt_AsLong(py_index);
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
    return wrap_tree_entry(entry, self);
}

TreeEntry *
Tree_getitem(Tree *self, PyObject *value)
{
    char *name;
    const git_tree_entry *entry;

    /* Case 1: integer */
    if (PyInt_Check(value))
        return Tree_getitem_by_index(self, value);

    /* Case 2: byte or text string */
    name = py_path_to_c_str(value);
    if (name == NULL)
        return NULL;
    entry = git_tree_entry_byname(self->tree, name);
    free(name);
    if (!entry) {
        PyErr_SetObject(PyExc_KeyError, value);
        return NULL;
    }
    return wrap_tree_entry(entry, self);
}

PyObject *
Tree_diff_tree(Tree *self, PyObject *args)
{
    git_diff_options opts = {0};
    git_diff_list *diff;
    int err;

    Diff *py_diff;
    PyObject *py_obj = NULL;

    if (!PyArg_ParseTuple(args, "|O", &py_obj))
        return NULL;

    if (py_obj == NULL) {
        err = git_diff_workdir_to_tree(
                self->repo->repo,
                &opts,
                self->tree,
                &diff);
    } else if (PyObject_TypeCheck(py_obj, &TreeType)) {
        err = git_diff_tree_to_tree(
                self->repo->repo,
                &opts,
                self->tree,
                ((Tree *)py_obj)->tree,
                &diff);
    } else if (PyObject_TypeCheck(py_obj, &IndexType)) {
        err = git_diff_index_to_tree(
                ((Index *)py_obj)->repo->repo,
                &opts,
                self->tree,
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
    {
     "diff", (PyCFunction)Tree_diff_tree, METH_VARARGS,
     "Get changes between current tree instance with another tree, an "
     "index or the working dir.\n\n"
     "@param obj : if not given compare diff against working dir. "
     "Possible valid arguments are instances of Tree or Index.\n"
     "@returns Diff instance"
    },
    {NULL}
};

PyTypeObject TreeType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.Tree",                             /* tp_name           */
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
    "Tree objects",                            /* tp_doc            */
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
TreeBuilder_dealloc(TreeBuilder* self)
{
    Py_XDECREF(self->repo);
    git_treebuilder_free(self->bld);
    PyObject_Del(self);
}

PyObject *
TreeBuilder_insert(TreeBuilder *self, PyObject *args)
{
    PyObject *py_oid;
    int len, err, attr;
    git_oid oid;
    const char *fname;

    if (!PyArg_ParseTuple(args, "sOi", &fname, &py_oid, &attr)) {
        return NULL;
    }

    len = py_str_to_git_oid(py_oid, &oid);
    if (len < 0) {
        return NULL;
    }

    err = git_treebuilder_insert(NULL, self->bld, fname, &oid, attr);
    if (err < 0) {
        Error_set(err);
        return NULL;
    }

    Py_RETURN_NONE;
}

PyObject *
TreeBuilder_write(TreeBuilder *self)
{
    int err;
    git_oid oid;

    err = git_treebuilder_write(&oid, self->repo->repo, self->bld);
    if (err < 0)
        return Error_set(err);

    return git_oid_to_python(&oid);
}

PyObject *
TreeBuilder_remove(TreeBuilder *self, PyObject *py_filename)
{
    char *filename = py_path_to_c_str(py_filename);
    int err = 0;

    if (filename == NULL)
        return NULL;

    err = git_treebuilder_remove(self->bld, filename);
    free(filename);
    if (err < 0)
        return Error_set(err);

    Py_RETURN_NONE;
}

PyObject *
TreeBuilder_clear(TreeBuilder *self)
{
    git_treebuilder_clear(self->bld);
    Py_RETURN_NONE;
}

PyMethodDef TreeBuilder_methods[] = {
    {"insert", (PyCFunction)TreeBuilder_insert, METH_VARARGS,
     "Insert or replace an entry in the treebuilder"},
    {"write", (PyCFunction)TreeBuilder_write, METH_NOARGS,
     "Write the tree to the given repository"},
    {"remove", (PyCFunction)TreeBuilder_remove, METH_O,
     "Remove an entry from the builder"},
    {"clear", (PyCFunction)TreeBuilder_clear, METH_NOARGS,
     "Clear all the entries in the builder"},
    {NULL, NULL, 0, NULL}
};

PyTypeObject TreeBuilderType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.TreeBuilder",                      /* tp_name           */
    sizeof(TreeBuilder),                       /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)TreeBuilder_dealloc,           /* tp_dealloc        */
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
    "TreeBuilder objects",                     /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    TreeBuilder_methods,                       /* tp_methods        */
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
    return (TreeEntry*)wrap_tree_entry(tree_entry, self->owner);
}

PyTypeObject TreeIterType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.TreeIter",                       /* tp_name           */
    sizeof(TreeIter),                        /* tp_basicsize      */
    0,                                       /* tp_itemsize       */
    (destructor)TreeIter_dealloc ,           /* tp_dealloc        */
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
    (iternextfunc)TreeIter_iternext,         /* tp_iternext       */
};
