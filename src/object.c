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
#include "error.h"
#include "types.h"
#include "utils.h"
#include "oid.h"
#include "repository.h"
#include "object.h"

extern PyTypeObject TreeType;
extern PyTypeObject CommitType;
extern PyTypeObject BlobType;
extern PyTypeObject TagType;


void
Object_dealloc(Object* self)
{
    Py_CLEAR(self->repo);
    git_object_free(self->obj);
    Py_TYPE(self)->tp_free(self);
}


PyDoc_STRVAR(Object_id__doc__,
    "The object id, an instance of the Oid type.");

PyObject *
Object_id__get__(Object *self)
{
    const git_oid *oid;

    oid = git_object_id(self->obj);
    assert(oid);

    return git_oid_to_python(oid);
}

PyDoc_STRVAR(Object_oid__doc__,
    "The object id, an instance of the Oid type.\n"
    "This attribute is deprecated, please use 'id'\n");

PyObject *
Object_oid__get__(Object *self)
{
    return Object_id__get__(self);
}

PyDoc_STRVAR(Object_hex__doc__,
    "Hexadecimal representation of the object id. This is a shortcut for\n"
    "Object.oid.hex\n"
    "This attribute is deprecated, please use 'id'\n");

PyObject *
Object_hex__get__(Object *self)
{
    const git_oid *oid;

    oid = git_object_id(self->obj);
    assert(oid);

    return git_oid_to_py_str(oid);
}


PyDoc_STRVAR(Object_type__doc__,
    "One of the GIT_OBJ_COMMIT, GIT_OBJ_TREE, GIT_OBJ_BLOB or GIT_OBJ_TAG\n"
    "constants.");

PyObject *
Object_type__get__(Object *self)
{
    return PyLong_FromLong(git_object_type(self->obj));
}

PyDoc_STRVAR(Object__pointer__doc__, "Get the object's pointer. For internal use only.");
PyObject *
Object__pointer__get__(Object *self)
{
    /* Bytes means a raw buffer */
    return PyBytes_FromStringAndSize((char *) &self->obj, sizeof(git_object *));
}


PyDoc_STRVAR(Object_read_raw__doc__,
  "read_raw()\n"
  "\n"
  "Returns the byte string with the raw contents of the object.");

PyObject *
Object_read_raw(Object *self)
{
    const git_oid *oid;
    git_odb_object *obj;
    PyObject *aux;

    oid = git_object_id(self->obj);

    obj = Repository_read_raw(self->repo->repo, oid, GIT_OID_HEXSZ);
    if (obj == NULL)
        return NULL;

    aux = PyBytes_FromStringAndSize(
        git_odb_object_data(obj),
        git_odb_object_size(obj));

    git_odb_object_free(obj);
    return aux;
}

PyDoc_STRVAR(Object_peel__doc__,
  "peel(target_type) -> Object\n"
  "\n"
  "Peel the current object and returns the first object of the given type\n");

PyObject *
Object_peel(Object *self, PyObject *py_type)
{
    int type = -1, err;
    git_object *peeled;

    type = py_object_to_object_type(py_type);
    if (type == -1)
        return NULL;

    err = git_object_peel(&peeled, self->obj, (git_otype)type);
    if (err < 0)
        return Error_set(err);

    return wrap_object(peeled, self->repo);
}

PyGetSetDef Object_getseters[] = {
    GETTER(Object, oid),
    GETTER(Object, id),
    GETTER(Object, hex),
    GETTER(Object, type),
    GETTER(Object, _pointer),
    {NULL}
};

PyMethodDef Object_methods[] = {
    METHOD(Object, read_raw, METH_NOARGS),
    METHOD(Object, peel, METH_O),
    {NULL}
};


PyDoc_STRVAR(Object__doc__, "Base class for Git objects.");

PyTypeObject ObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.Object",                          /* tp_name           */
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
    Object__doc__,                             /* tp_doc            */
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

PyObject *
wrap_object(git_object *c_object, Repository *repo)
{
    Object *py_obj = NULL;

    switch (git_object_type(c_object)) {
        case GIT_OBJ_COMMIT:
            py_obj = PyObject_New(Object, &CommitType);
            break;
        case GIT_OBJ_TREE:
            py_obj = PyObject_New(Object, &TreeType);
            break;
        case GIT_OBJ_BLOB:
            py_obj = PyObject_New(Object, &BlobType);
            break;
        case GIT_OBJ_TAG:
            py_obj = PyObject_New(Object, &TagType);
            break;
        default:
            assert(0);
    }

    if (py_obj) {
        py_obj->obj = c_object;
        if (repo) {
            py_obj->repo = repo;
            Py_INCREF(repo);
        }
    }
    return (PyObject *)py_obj;
}
