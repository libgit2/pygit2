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
#include <pygit2/repository.h>
#include <pygit2/object.h>

void
Object_dealloc(Object* self)
{
    git_object_free(self->obj);
    Py_XDECREF(self->repo);
    PyObject_Del(self);
}

PyObject *
Object_get_oid(Object *self)
{
    const git_oid *oid;

    oid = git_object_id(self->obj);
    assert(oid);

    return git_oid_to_python(oid->id);
}

PyObject *
Object_get_hex(Object *self)
{
    const git_oid *oid;

    oid = git_object_id(self->obj);
    assert(oid);

    return git_oid_to_py_str(oid);
}

PyObject *
Object_get_type(Object *self)
{
    return PyInt_FromLong(git_object_type(self->obj));
}

PyObject *
Object_read_raw(Object *self)
{
    const git_oid *oid;
    git_odb_object *obj;
    PyObject *aux;

    oid = git_object_id(self->obj);
    assert(oid);

    obj = Repository_read_raw(self->repo->repo, oid, GIT_OID_HEXSZ);
    if (obj == NULL)
        return NULL;

    aux = PyString_FromStringAndSize(
        git_odb_object_data(obj),
        git_odb_object_size(obj));

    git_odb_object_free(obj);
    return aux;
}

PyGetSetDef Object_getseters[] = {
    {"oid", (getter)Object_get_oid, NULL, "object id", NULL},
    {"hex", (getter)Object_get_hex, NULL, "hex oid", NULL},
    {"type", (getter)Object_get_type, NULL, "type number", NULL},
    {NULL}
};

PyMethodDef Object_methods[] = {
    {"read_raw", (PyCFunction)Object_read_raw, METH_NOARGS,
     "Read the raw contents of the object from the repo."},
    {NULL}
};

PyTypeObject ObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.Object",                           /* tp_name           */
    sizeof(Object),                            /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)Object_dealloc,                /* tp_dealloc        */
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
    "Object objects",                          /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    Object_methods,                            /* tp_methods        */
    0,                                         /* tp_members        */
    Object_getseters,                          /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    0,                                         /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};
