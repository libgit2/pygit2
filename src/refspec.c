/*
 * Copyright 2010-2014 The pygit2 contributors
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
#include "types.h"
#include "utils.h"
#include "refspec.h"


extern PyTypeObject RefspecType;

Refspec *
wrap_refspec(const Remote *owner, const git_refspec *refspec)
{
    Refspec *spec;

    spec = PyObject_New(Refspec, &RefspecType);
    if (!spec)
        return NULL;

    Py_INCREF(owner);
    spec->owner = owner;
    spec->refspec = refspec;

    return spec;
}

PyDoc_STRVAR(Refspec_direction__doc__,
             "The direction of this refspec (fetch or push)");

PyObject *
Refspec_direction__get__(Refspec *self)
{
    return Py_BuildValue("i", git_refspec_direction(self->refspec));
}

PyDoc_STRVAR(Refspec_src__doc__, "Source or lhs of the refspec");

PyObject *
Refspec_src__get__(Refspec *self)
{
    return to_unicode(git_refspec_src(self->refspec), NULL, NULL);
}

PyDoc_STRVAR(Refspec_dst__doc__, "Destination or rhs of the refspec");

PyObject *
Refspec_dst__get__(Refspec *self)
{
    return to_unicode(git_refspec_dst(self->refspec), NULL, NULL);
}

PyDoc_STRVAR(Refspec_string__doc__, "String used to create this refspec");

PyObject *
Refspec_string__get__(Refspec *self)
{
    return to_unicode(git_refspec_string(self->refspec), NULL, NULL);
}

PyDoc_STRVAR(Refspec_force__doc__,
             "Whether this refspec allows non-fast-forward updates");

PyObject *
Refspec_force__get__(Refspec *self)
{
    if (git_refspec_force(self->refspec))
        Py_RETURN_TRUE;

    Py_RETURN_FALSE;
}

PyDoc_STRVAR(Refspec_src_matches__doc__,
    "src_matches(str) -> Bool\n"
    "\n"
    "Returns whether the string matches the source refspec\n");

PyObject *
Refspec_src_matches(Refspec *self, PyObject *py_str)
{
    const char *str;
    PyObject *tstr;
    int res;

    str = py_str_borrow_c_str(&tstr, py_str, NULL);
    if (!str)
        return NULL;

    res = git_refspec_src_matches(self->refspec, str);
    Py_DECREF(tstr);

    if (res)
        Py_RETURN_TRUE;

    Py_RETURN_FALSE;
}

PyDoc_STRVAR(Refspec_dst_matches__doc__,
    "dst_matches(str) -> Bool\n"
    "\n"
    "Returns whether the string matches the destination refspec\n");

PyObject *
Refspec_dst_matches(Refspec *self, PyObject *py_str)
{
    const char *str;
    PyObject *tstr;
    int res;

    str = py_str_borrow_c_str(&tstr, py_str, NULL);
    if (!str)
        return NULL;

    res = git_refspec_dst_matches(self->refspec, str);
    Py_DECREF(tstr);

    if (res)
        Py_RETURN_TRUE;

    Py_RETURN_FALSE;
}

PyDoc_STRVAR(Refspec_transform__doc__,
    "transform(str) -> str\n"
    "\n"
    "Transform a reference according to the refspec\n");

PyObject *
Refspec_transform(Refspec *self, PyObject *py_str)
{
    const char *str;
    char *trans;
    int err, len, alen;
    PyObject *py_trans, *tstr;

    str = py_str_borrow_c_str(&tstr, py_str, NULL);
    alen = len = strlen(str);

    do {
        alen *= alen;
        trans = malloc(alen);
        if (!trans) {
            Py_DECREF(tstr);
            return PyErr_NoMemory();
        }

        err = git_refspec_transform(trans, alen, self->refspec, str);
    } while(err == GIT_EBUFS);
    Py_DECREF(tstr);

    if (err < 0) {
        free(trans);
        Error_set(err);
        return NULL;
    }

    py_trans = to_unicode(trans, NULL, NULL);

    free(trans);

    return py_trans;
}

PyDoc_STRVAR(Refspec_rtransform__doc__,
    "rtransform(str) -> str\n"
    "\n"
    "Transform a reference according to the refspec in reverse\n");

PyObject *
Refspec_rtransform(Refspec *self, PyObject *py_str)
{
    const char *str;
    char *trans;
    int err, len, alen;
    PyObject *py_trans, *tstr;

    str = py_str_borrow_c_str(&tstr, py_str, NULL);
    alen = len = strlen(str);

    do {
        alen *= alen;
        trans = malloc(alen);
        if (!trans) {
            Py_DECREF(tstr);
            return PyErr_NoMemory();
        }

        err = git_refspec_rtransform(trans, alen, self->refspec, str);
    } while(err == GIT_EBUFS);
    Py_DECREF(tstr);

    if (err < 0) {
        free(trans);
        Error_set(err);
        return NULL;
    }

    py_trans = to_unicode(trans, NULL, NULL);

    free(trans);

    return py_trans;
}

PyMethodDef Refspec_methods[] = {
    METHOD(Refspec, src_matches, METH_O),
    METHOD(Refspec, dst_matches, METH_O),
    METHOD(Refspec, transform, METH_O),
    METHOD(Refspec, rtransform, METH_O),
    {NULL}
};

PyGetSetDef Refspec_getseters[] = {
    GETTER(Refspec, direction),
    GETTER(Refspec, src),
    GETTER(Refspec, dst),
    GETTER(Refspec, string),
    GETTER(Refspec, force),
    {NULL}
};

static void
Refspec_dealloc(Refspec *self)
{
    Py_CLEAR(self->owner);
    PyObject_Del(self);
}

PyDoc_STRVAR(Refspec__doc__, "Refspec object.");

PyTypeObject RefspecType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.Refspec",                         /* tp_name           */
    sizeof(Refspec),                           /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)Refspec_dealloc,               /* tp_dealloc        */
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
    Refspec__doc__,                            /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    Refspec_methods,                           /* tp_methods        */
    0,                                         /* tp_members        */
    Refspec_getseters,                         /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    0,                                         /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};
