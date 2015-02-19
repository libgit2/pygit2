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
#include <structmember.h>
#include "error.h"
#include "utils.h"
#include "types.h"
#include "submodule.h"
#include "repository.h"

PyTypeObject SubmoduleType;

PyDoc_STRVAR(Submodule_open__doc__,
    "open() -> Repository\n"
    "\n"
    "Open the submodule as repository.");

PyObject *
Submodule_open(Submodule *self, PyObject *args)
{
    int err;
    git_repository *repo;

    err = git_submodule_open(&repo, self->submodule);
    if (err < 0)
        return Error_set_str(err, giterr_last()->message);

    return wrap_repository(repo);
}

PyDoc_STRVAR(Submodule_name__doc__,
  "Gets name of the submodule\n");

PyObject *
Submodule_name__get__(Submodule *self)
{
    return to_unicode(git_submodule_name(self->submodule), NULL, NULL);
}

PyDoc_STRVAR(Submodule_path__doc__,
  "Gets path of the submodule\n");

PyObject *
Submodule_path__get__(Submodule *self)
{
    return to_unicode(git_submodule_path(self->submodule), NULL, NULL);
}

PyDoc_STRVAR(Submodule_url__doc__,
  "Gets URL of the submodule\n");

PyObject *
Submodule_url__get__(Submodule *self)
{
    const char *url = git_submodule_url(self->submodule);
    if (url == NULL)
        return Py_None;
    return to_unicode(url, NULL, NULL);
}

PyDoc_STRVAR(Submodule_branch__doc__,
  "Gets branch of the submodule\n");

PyObject *
Submodule_branch__get__(Submodule *self)
{
    const char *branch = git_submodule_branch(self->submodule);
    if (branch == NULL)
        return Py_None;
    return to_unicode(branch, NULL, NULL);
}

static void
Submodule_dealloc(Submodule *self)
{
    Py_CLEAR(self->repo);
    git_submodule_free(self->submodule);
    PyObject_Del(self);
}

PyMethodDef Submodule_methods[] = {
    METHOD(Submodule, open, METH_NOARGS),
    {NULL}
};

PyGetSetDef Submodule_getseters[] = {
    GETTER(Submodule, name),
    GETTER(Submodule, path),
    GETTER(Submodule, url),
    GETTER(Submodule, branch),
    {NULL}
};

PyDoc_STRVAR(Submodule__doc__, "Submodule object.");

PyTypeObject SubmoduleType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.Submodule",                       /* tp_name           */
    sizeof(Submodule),                         /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)Submodule_dealloc,             /* tp_dealloc        */
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
    Submodule__doc__,                          /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    Submodule_methods,                         /* tp_methods        */
    0,                                         /* tp_members        */
    Submodule_getseters,                       /* tp_getset         */
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
wrap_submodule(Repository *repo, git_submodule *c_submodule)
{
    Submodule *py_submodule = NULL;

    py_submodule = PyObject_New(Submodule, &SubmoduleType);
    if (py_submodule) {
        py_submodule->submodule = c_submodule;
        if (repo) {
            py_submodule->repo = repo;
            Py_INCREF(repo);
        }
    }

    return (PyObject *)py_submodule;
}
