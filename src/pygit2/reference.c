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
#include <string.h>
#include <structmember.h>
#include <pygit2/error.h>
#include <pygit2/types.h>
#include <pygit2/utils.h>
#include <pygit2/oid.h>
#include <pygit2/signature.h>
#include <pygit2/reference.h>


extern PyObject *GitError;
extern PyTypeObject RefLogEntryType;


void RefLogIter_dealloc(RefLogIter *self)
{
    Py_XDECREF(self->reference);
    git_reflog_free(self->reflog);
    PyObject_GC_Del(self);
}

PyObject* RefLogIter_iternext(PyObject *self)
{
    RefLogIter *p = (RefLogIter *) self;

    if (p->i < p->size) {
        char oid_old[40], oid_new[40];
        RefLogEntry *py_entry;
        git_signature *signature;

        const git_reflog_entry *entry = git_reflog_entry_byindex(p->reflog, p->i);

        py_entry = (RefLogEntry*) PyType_GenericNew(
                        &RefLogEntryType, NULL, NULL
                    );

        git_oid_fmt(oid_old, git_reflog_entry_oidold(entry));
        git_oid_fmt(oid_new, git_reflog_entry_oidnew(entry));

        py_entry->oid_new = PyUnicode_FromStringAndSize(oid_new, 40);
        py_entry->oid_old = PyUnicode_FromStringAndSize(oid_old, 40);

        py_entry->msg = strdup(git_reflog_entry_msg(entry));

        signature = git_signature_dup(
              git_reflog_entry_committer(entry)
            );

        if(signature != NULL)
          py_entry->committer = build_signature(
                (Object*)py_entry, signature, "utf-8"
              );

        ++(p->i);

        return (PyObject*) py_entry;

    }

    PyErr_SetNone(PyExc_StopIteration);
    return NULL;
}

PyTypeObject RefLogIterType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_libgit2.RefLogIter",            /*tp_name*/
    sizeof(RefLogIter),       /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)RefLogIter_dealloc,     /* tp_dealloc        */
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT |
    Py_TPFLAGS_BASETYPE,                     /* tp_flags          */
      /* tp_flags: Py_TPFLAGS_HAVE_ITER tells python to
         use tp_iter and tp_iternext fields. */
    "Internal reflog iterator object.",           /* tp_doc */
    0,  /* tp_traverse */
    0,  /* tp_clear */
    0,  /* tp_richcompare */
    0,  /* tp_weaklistoffset */
    PyObject_SelfIter,  /* tp_iter: __iter__() method */
    (iternextfunc) RefLogIter_iternext  /* tp_iternext: next() method */
};

void
Reference_dealloc(Reference *self)
{
    git_reference_free(self->reference);
    PyObject_Del(self);
}

PyObject *
Reference_delete(Reference *self, PyObject *args)
{
    int err;

    CHECK_REFERENCE(self);

    /* Delete the reference */
    err = git_reference_delete(self->reference);
    if (err < 0)
        return Error_set(err);

    self->reference = NULL; /* Invalidate the pointer */
    Py_RETURN_NONE;         /* Return None */
}

PyObject *
Reference_rename(Reference *self, PyObject *py_name)
{
    char *c_name;
    int err;

    CHECK_REFERENCE(self);

    /* Get the C name */
    c_name = py_path_to_c_str(py_name);
    if (c_name == NULL)
        return NULL;

    /* Rename */
    err = git_reference_rename(self->reference, c_name, 0);
    free(c_name);
    if (err < 0)
        return Error_set(err);

    Py_RETURN_NONE; /* Return None */
}

PyObject *
Reference_reload(Reference *self)
{
    int err;

    CHECK_REFERENCE(self);

    err = git_reference_reload(self->reference);
    if (err < 0) {
        self->reference = NULL;
        return Error_set(err);
    }

    Py_RETURN_NONE;
}


PyObject *
Reference_resolve(Reference *self, PyObject *args)
{
    git_reference *c_reference;
    int err;

    CHECK_REFERENCE(self);

    /* Direct: reload */
    if (git_reference_type(self->reference) == GIT_REF_OID) {
        err = git_reference_reload(self->reference);
        if (err < 0) {
            self->reference = NULL;
            return Error_set(err);
        }
        Py_INCREF(self);
        return (PyObject *)self;
    }

    /* Symbolic: resolve */
    err = git_reference_resolve(&c_reference, self->reference);
    if (err < 0)
        return Error_set(err);

    return wrap_reference(c_reference);
}

PyObject *
Reference_get_target(Reference *self)
{
    const char * c_name;

    CHECK_REFERENCE(self);

    /* Get the target */
    c_name = git_reference_target(self->reference);
    if (c_name == NULL) {
        PyErr_SetString(PyExc_ValueError, "no target available");
        return NULL;
    }

    /* Make a PyString and return it */
    return to_path(c_name);
}

int
Reference_set_target(Reference *self, PyObject *py_name)
{
    char *c_name;
    int err;

    CHECK_REFERENCE_INT(self);

    /* Get the C name */
    c_name = py_path_to_c_str(py_name);
    if (c_name == NULL)
        return -1;

    /* Set the new target */
    err = git_reference_set_target(self->reference, c_name);
    free(c_name);
    if (err < 0) {
        Error_set(err);
        return -1;
    }

    return 0;
}

PyObject *
Reference_get_name(Reference *self)
{
    CHECK_REFERENCE(self);
    return to_path(git_reference_name(self->reference));
}

PyObject *
Reference_get_oid(Reference *self)
{
    const git_oid *oid;

    CHECK_REFERENCE(self);

    /* Get the oid (only for "direct" references) */
    oid = git_reference_oid(self->reference);
    if (oid == NULL) {
        PyErr_SetString(PyExc_ValueError,
                        "oid is only available if the reference is direct "
                        "(i.e. not symbolic)");
        return NULL;
    }

    /* Convert and return it */
    return git_oid_to_python(oid->id);
}

int
Reference_set_oid(Reference *self, PyObject *py_hex)
{
    git_oid oid;
    int err;

    CHECK_REFERENCE_INT(self);

    /* Get the oid */
    err = py_str_to_git_oid_expand(git_reference_owner(self->reference), py_hex, &oid);
    if (err < 0) {
        Error_set(err);
        return -1;
    }

    /* Set the oid */
    err = git_reference_set_oid(self->reference, &oid);
    if (err < 0) {
        Error_set(err);
        return -1;
    }

    return 0;
}

PyObject *
Reference_get_hex(Reference *self)
{
    const git_oid *oid;

    CHECK_REFERENCE(self);

    /* Get the oid (only for "direct" references) */
    oid = git_reference_oid(self->reference);
    if (oid == NULL) {
        PyErr_SetString(PyExc_ValueError,
                        "oid is only available if the reference is direct "
                        "(i.e. not symbolic)");
        return NULL;
    }

    /* Convert and return it */
    return git_oid_to_py_str(oid);
}

PyObject *
Reference_get_type(Reference *self)
{
    git_ref_t c_type;

    CHECK_REFERENCE(self);
    c_type = git_reference_type(self->reference);
    return PyInt_FromLong(c_type);
}

PyObject *
Reference_log(Reference *self)
{
    RefLogIter *iter;

    CHECK_REFERENCE(self);

    iter = PyObject_New(RefLogIter, &RefLogIterType);
    if (iter) {
        iter->reference = self;
        git_reflog_read(&iter->reflog, self->reference);
        iter->size = git_reflog_entrycount(iter->reflog);
        iter->i = 0;

        Py_INCREF(self);
        Py_INCREF(iter);
    }
    return (PyObject*)iter;
}

static int
RefLogEntry_init(RefLogEntry *self, PyObject *args, PyObject *kwds)
{
    self->oid_old = Py_None;
    self->oid_new = Py_None;
    self->msg = "";
    self->committer = Py_None;

    return 0;
}


static void
RefLogEntry_dealloc(RefLogEntry *self)
{
    Py_XDECREF(self->oid_old);
    Py_XDECREF(self->oid_new);
    Py_XDECREF(self->committer);
    free(self->msg);
    PyObject_Del(self);
}

PyMemberDef RefLogEntry_members[] = {
    {"oid_new", T_OBJECT, offsetof(RefLogEntry, oid_new), 0, "new oid"},
    {"oid_old", T_OBJECT, offsetof(RefLogEntry, oid_old), 0, "old oid"},
    {"message",  T_STRING, offsetof(RefLogEntry, msg), 0, "message"},
    {"committer",  T_OBJECT, offsetof(RefLogEntry, committer), 0, "committer"},
    {NULL}
};

PyTypeObject RefLogEntryType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.RefLogEntry",               /* tp_name           */
    sizeof(RefLogEntry),                 /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)RefLogEntry_dealloc,     /* tp_dealloc        */
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
    "ReferenceLog object",                     /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    0,                                         /* tp_methods        */
    RefLogEntry_members,                 /* tp_members        */
    0,                                         /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    (initproc)RefLogEntry_init,          /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};

PyMethodDef Reference_methods[] = {
    {"delete", (PyCFunction)Reference_delete, METH_NOARGS,
     "Delete this reference. It will no longer be valid!"},
    {"rename", (PyCFunction)Reference_rename, METH_O,
      "Rename the reference."},
    {"reload", (PyCFunction)Reference_reload, METH_NOARGS,
     "Reload the reference from the file-system."},
    {"resolve", (PyCFunction)Reference_resolve, METH_NOARGS,
      "Resolve a symbolic reference and return a direct reference."},
    {"log", (PyCFunction)Reference_log, METH_NOARGS,
      "Retrieves the current reference log."},
    {NULL}
};

PyGetSetDef Reference_getseters[] = {
    {"name", (getter)Reference_get_name, NULL,
     "The full name of a reference.", NULL},
    {"oid", (getter)Reference_get_oid, (setter)Reference_set_oid, "object id",
     NULL},
    {"hex", (getter)Reference_get_hex, NULL, "hex oid", NULL},
    {"target", (getter)Reference_get_target, (setter)Reference_set_target,
     "target", NULL},
    {"type", (getter)Reference_get_type, NULL,
     "type (GIT_REF_OID, GIT_REF_SYMBOLIC or GIT_REF_PACKED).", NULL},
    {NULL}
};

PyTypeObject ReferenceType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.Reference",                        /* tp_name           */
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
    "Reference",                               /* tp_doc            */
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
wrap_reference(git_reference * c_reference)
{
    Reference *py_reference=NULL;

    py_reference = PyObject_New(Reference, &ReferenceType);
    if (py_reference)
        py_reference->reference = c_reference;

    return (PyObject *)py_reference;
}
