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
#include <structmember.h>
#include "object.h"
#include "error.h"
#include "types.h"
#include "utils.h"
#include "oid.h"
#include "signature.h"
#include "reference.h"


extern PyObject *GitError;
extern PyTypeObject RefLogEntryType;
extern PyTypeObject SignatureType;


void RefLogIter_dealloc(RefLogIter *self)
{
    git_reflog_free(self->reflog);
    PyObject_Del(self);
}

PyObject *
RefLogIter_iternext(RefLogIter *self)
{
    const git_reflog_entry *entry;
    RefLogEntry *py_entry;
    int err;

    if (self->i < self->size) {
        entry = git_reflog_entry_byindex(self->reflog, self->i);
        py_entry = PyObject_New(RefLogEntry, &RefLogEntryType);

        py_entry->oid_old = git_oid_to_python(git_reflog_entry_id_old(entry));
        py_entry->oid_new = git_oid_to_python(git_reflog_entry_id_new(entry));
        py_entry->message = strdup(git_reflog_entry_message(entry));
        err = git_signature_dup(&py_entry->signature,
                                git_reflog_entry_committer(entry));
        if (err < 0)
            return Error_set(err);

        ++(self->i);

        return (PyObject*) py_entry;
    }

    PyErr_SetNone(PyExc_StopIteration);
    return NULL;
}


PyDoc_STRVAR(RefLogIterType__doc__, "Internal reflog iterator object.");

PyTypeObject RefLogIterType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.RefLogIter",                      /* tp_name           */
    sizeof(RefLogIter),                        /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)RefLogIter_dealloc,            /* tp_dealloc        */
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
    RefLogIterType__doc__,                     /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    PyObject_SelfIter,                         /* tp_iter           */
    (iternextfunc)RefLogIter_iternext,         /* tp_iternext       */
};

void
Reference_dealloc(Reference *self)
{
    Py_CLEAR(self->repo);
    git_reference_free(self->reference);
    PyObject_Del(self);
}


PyDoc_STRVAR(Reference_delete__doc__,
  "delete()\n"
  "\n"
  "Delete this reference. It will no longer be valid!");

PyObject *
Reference_delete(Reference *self, PyObject *args)
{
    int err;

    CHECK_REFERENCE(self);

    /* Delete the reference */
    err = git_reference_delete(self->reference);
    if (err < 0)
        return Error_set(err);

    git_reference_free(self->reference);
    self->reference = NULL; /* Invalidate the pointer */

    Py_RETURN_NONE;
}


PyDoc_STRVAR(Reference_rename__doc__,
  "rename(new_name)\n"
  "\n"
  "Rename the reference.");

PyObject *
Reference_rename(Reference *self, PyObject *py_name)
{
    char *c_name;
    int err;
    git_reference *new_reference;

    CHECK_REFERENCE(self);

    /* Get the C name */
    c_name = py_path_to_c_str(py_name);
    if (c_name == NULL)
        return NULL;

    /* Rename */
    err = git_reference_rename(&new_reference, self->reference, c_name, 0, NULL);
    git_reference_free(self->reference);
    free(c_name);
    if (err < 0)
        return Error_set(err);

    self->reference = new_reference;
    Py_RETURN_NONE;
}


PyDoc_STRVAR(Reference_resolve__doc__,
  "resolve() -> Reference\n"
  "\n"
  "Resolve a symbolic reference and return a direct reference.");

PyObject *
Reference_resolve(Reference *self, PyObject *args)
{
    git_reference *c_reference;
    int err;

    CHECK_REFERENCE(self);

    /* Direct: return myself */
    if (git_reference_type(self->reference) == GIT_REF_OID) {
        Py_INCREF(self);
        return (PyObject *)self;
    }

    /* Symbolic: resolve */
    err = git_reference_resolve(&c_reference, self->reference);
    if (err < 0)
        return Error_set(err);

    return wrap_reference(c_reference, self->repo);
}


PyDoc_STRVAR(Reference_target__doc__,
    "The reference target: If direct the value will be an Oid object, if it\n"
    "is symbolic it will be an string with the full name of the target\n"
    "reference.\n");

PyObject *
Reference_target__get__(Reference *self)
{
    const char * c_name;

    CHECK_REFERENCE(self);

    /* Case 1: Direct */
    if (GIT_REF_OID == git_reference_type(self->reference))
        return git_oid_to_python(git_reference_target(self->reference));

    /* Case 2: Symbolic */
    c_name = git_reference_symbolic_target(self->reference);
    if (c_name == NULL) {
        PyErr_SetString(PyExc_ValueError, "no target available");
        return NULL;
    }
    return to_path(c_name);
}

PyDoc_STRVAR(Reference_set_target__doc__,
    "set_target(target, [message])\n"
    "\n"
    "Set the target of this reference.\n"
    "\n"
    "Update the reference using the given signature and message.\n"
    "These will be used to fill the reflog entry which will be created\n"
    "as a result of this update\n"
    "\n"
    "Arguments:\n"
    "\n"
    "target\n"
    "    The new target for this reference\n"
    "message\n"
    "    Message to use for the reflog.\n");

PyObject *
Reference_set_target(Reference *self, PyObject *args, PyObject *kwds)
{
    git_oid oid;
    char *c_name;
    int err;
    git_reference *new_ref;
    PyObject *py_target = NULL;
    const char *message = NULL;
    char *keywords[] = {"target", "message", NULL};

    CHECK_REFERENCE(self);

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O|s", keywords,
                                     &py_target, &message))
        return NULL;

    /* Case 1: Direct */
    if (GIT_REF_OID == git_reference_type(self->reference)) {
        err = py_oid_to_git_oid_expand(self->repo->repo, py_target, &oid);
        if (err < 0)
            goto error;

        err = git_reference_set_target(&new_ref, self->reference, &oid, message);
        if (err < 0)
            goto error;

        git_reference_free(self->reference);
        self->reference = new_ref;
        Py_RETURN_NONE;
    }

    /* Case 2: Symbolic */
    c_name = py_path_to_c_str(py_target);
    if (c_name == NULL)
        return NULL;

    err = git_reference_symbolic_set_target(&new_ref, self->reference, c_name, message);
    free(c_name);
    if (err < 0)
        goto error;

    git_reference_free(self->reference);
    self->reference = new_ref;

    Py_RETURN_NONE;

error:
    Error_set(err);
    return NULL;
}


PyDoc_STRVAR(Reference_name__doc__, "The full name of the reference.");

PyObject *
Reference_name__get__(Reference *self)
{
    CHECK_REFERENCE(self);
    return to_path(git_reference_name(self->reference));
}

PyDoc_STRVAR(Reference_shorthand__doc__,
    "The shorthand \"human-readable\" name of the reference.");

PyObject *
Reference_shorthand__get__(Reference *self)
{
    CHECK_REFERENCE(self);
    return to_path(git_reference_shorthand(self->reference));
}

PyDoc_STRVAR(Reference_type__doc__,
    "Type, either GIT_REF_OID or GIT_REF_SYMBOLIC.");

PyObject *
Reference_type__get__(Reference *self)
{
    git_ref_t c_type;

    CHECK_REFERENCE(self);
    c_type = git_reference_type(self->reference);
    return PyLong_FromLong(c_type);
}


PyDoc_STRVAR(Reference_log__doc__,
  "log() -> RefLogIter\n"
  "\n"
  "Retrieves the current reference log.");

PyObject *
Reference_log(Reference *self)
{
    int err;
    RefLogIter *iter;
    git_repository *repo;

    CHECK_REFERENCE(self);

    repo = git_reference_owner(self->reference);
    iter = PyObject_New(RefLogIter, &RefLogIterType);
    if (iter != NULL) {
        err = git_reflog_read(&iter->reflog, repo, git_reference_name(self->reference));
        if (err < 0)
            return Error_set(err);

        iter->size = git_reflog_entrycount(iter->reflog);
        iter->i = 0;
    }
    return (PyObject*)iter;
}

PyDoc_STRVAR(Reference_get_object__doc__,
  "get_object() -> object\n"
  "\n"
  "Retrieves the object the current reference is pointing to.\n"
  "\n"
  "This method is deprecated, please use Reference.peel() instead.");

PyObject *
Reference_get_object(Reference *self)
{
    return PyObject_CallMethod((PyObject *) self, "peel", NULL);
}

PyDoc_STRVAR(Reference_peel__doc__,
  "peel(type=None) -> object\n"
  "\n"
  "Retrieve an object of the given type by recursive peeling.\n"
  "\n"
  "If no type is provided, the first non-tag object will be returned.");

PyObject *
Reference_peel(Reference *self, PyObject *args)
{
    int err, type;
    git_object *obj;
    PyObject *py_type = Py_None;

    CHECK_REFERENCE(self);

    if (!PyArg_ParseTuple(args, "|O", &py_type))
        return NULL;

    type = py_object_to_object_type(py_type);
    if (type == -1)
        return NULL;

    err = git_reference_peel(&obj, self->reference, type);
    if (err < 0)
        return Error_set(err);

    return wrap_object(obj, self->repo);
}

PyDoc_STRVAR(RefLogEntry_committer__doc__, "Committer.");

PyObject *
RefLogEntry_committer__get__(RefLogEntry *self)
{
    return build_signature((Object*) self, self->signature, "utf-8");
}


static int
RefLogEntry_init(RefLogEntry *self, PyObject *args, PyObject *kwds)
{
    self->oid_old   = NULL;
    self->oid_new   = NULL;
    self->message   = NULL;
    self->signature = NULL;

    return 0;
}


static void
RefLogEntry_dealloc(RefLogEntry *self)
{
    Py_CLEAR(self->oid_old);
    Py_CLEAR(self->oid_new);
    free(self->message);
    git_signature_free(self->signature);
    PyObject_Del(self);
}

PyMemberDef RefLogEntry_members[] = {
    MEMBER(RefLogEntry, oid_new, T_OBJECT, "New oid."),
    MEMBER(RefLogEntry, oid_old, T_OBJECT, "Old oid."),
    MEMBER(RefLogEntry, message, T_STRING, "Message."),
    {NULL}
};

PyGetSetDef RefLogEntry_getseters[] = {
    GETTER(RefLogEntry, committer),
    {NULL}
};


PyDoc_STRVAR(RefLogEntry__doc__, "Reference log object.");

PyTypeObject RefLogEntryType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.RefLogEntry",                     /* tp_name           */
    sizeof(RefLogEntry),                       /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)RefLogEntry_dealloc,           /* tp_dealloc        */
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
    RefLogEntry__doc__,                        /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    0,                                         /* tp_methods        */
    RefLogEntry_members,                       /* tp_members        */
    RefLogEntry_getseters,                     /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    (initproc)RefLogEntry_init,                /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};

PyMethodDef Reference_methods[] = {
    METHOD(Reference, delete, METH_NOARGS),
    METHOD(Reference, rename, METH_O),
    METHOD(Reference, resolve, METH_NOARGS),
    METHOD(Reference, log, METH_NOARGS),
    METHOD(Reference, get_object, METH_NOARGS),
    METHOD(Reference, set_target, METH_VARARGS | METH_KEYWORDS),
    METHOD(Reference, peel, METH_VARARGS),
    {NULL}
};

PyGetSetDef Reference_getseters[] = {
    GETTER(Reference, name),
    GETTER(Reference, shorthand),
    GETTER(Reference, target),
    GETTER(Reference, type),
    {NULL}
};


PyDoc_STRVAR(Reference__doc__, "Reference.");

PyTypeObject ReferenceType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.Reference",                       /* tp_name           */
    sizeof(Reference),                         /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)Reference_dealloc,             /* tp_dealloc        */
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
    Reference__doc__,                          /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    Reference_methods,                         /* tp_methods        */
    0,                                         /* tp_members        */
    Reference_getseters,                       /* tp_getset         */
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
wrap_reference(git_reference * c_reference, Repository *repo)
{
    Reference *py_reference=NULL;

    py_reference = PyObject_New(Reference, &ReferenceType);
    if (py_reference) {
        py_reference->reference = c_reference;
        if (repo) {
            py_reference->repo = repo;
            Py_INCREF(repo);
        }
    }

    return (PyObject *)py_reference;
}
