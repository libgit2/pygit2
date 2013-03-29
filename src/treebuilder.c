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
#include "oid.h"
#include "treebuilder.h"


void
TreeBuilder_dealloc(TreeBuilder *self)
{
    Py_CLEAR(self->repo);
    git_treebuilder_free(self->bld);
    PyObject_Del(self);
}


PyDoc_STRVAR(TreeBuilder_insert__doc__,
  "insert(name, oid, attr)\n"
  "\n"
  "Insert or replace an entry in the treebuilder.");

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


PyDoc_STRVAR(TreeBuilder_write__doc__,
  "write() -> bytes\n"
  "\n"
  "Write the tree to the given repository.");

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


PyDoc_STRVAR(TreeBuilder_remove__doc__,
  "remove(name)\n"
  "\n"
  "Remove an entry from the builder.");

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


PyDoc_STRVAR(TreeBuilder_clear__doc__,
  "clear()\n"
  "\n"
  "Clear all the entries in the builder.");

PyObject *
TreeBuilder_clear(TreeBuilder *self)
{
    git_treebuilder_clear(self->bld);
    Py_RETURN_NONE;
}

PyMethodDef TreeBuilder_methods[] = {
    METHOD(TreeBuilder, insert, METH_VARARGS),
    METHOD(TreeBuilder, write, METH_NOARGS),
    METHOD(TreeBuilder, remove, METH_O),
    METHOD(TreeBuilder, clear, METH_NOARGS),
    {NULL}
};


PyDoc_STRVAR(TreeBuilder__doc__, "TreeBuilder objects.");

PyTypeObject TreeBuilderType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.TreeBuilder",                     /* tp_name           */
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
    TreeBuilder__doc__,                        /* tp_doc            */
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
