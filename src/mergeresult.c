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
#include "utils.h"
#include "types.h"
#include "oid.h"
#include "repository.h"
#include "mergeresult.h"

extern PyTypeObject MergeResultType;
extern PyTypeObject IndexType;

PyObject *
git_merge_result_to_python(git_merge_result *merge_result)
{
    MergeResult *py_merge_result;

    py_merge_result = PyObject_New(MergeResult, &MergeResultType);
    if (!py_merge_result)
        return NULL;

    py_merge_result->result = merge_result;

    return (PyObject*) py_merge_result;
}

PyDoc_STRVAR(MergeResult_is_uptodate__doc__, "Is up to date");

PyObject *
MergeResult_is_uptodate__get__(MergeResult *self)
{
    if (git_merge_result_is_uptodate(self->result))
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}

PyDoc_STRVAR(MergeResult_is_fastforward__doc__, "Is fastforward");

PyObject *
MergeResult_is_fastforward__get__(MergeResult *self)
{
    if (git_merge_result_is_fastforward(self->result))
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}

PyDoc_STRVAR(MergeResult_fastforward_oid__doc__, "Fastforward Oid");

PyObject *
MergeResult_fastforward_oid__get__(MergeResult *self)
{
    if (git_merge_result_is_fastforward(self->result)) {
        git_oid fastforward_oid;
        git_merge_result_fastforward_oid(&fastforward_oid, self->result);
        return git_oid_to_python((const git_oid *)&fastforward_oid);
    }
    else Py_RETURN_NONE;
}

PyGetSetDef MergeResult_getseters[] = {
    GETTER(MergeResult, is_uptodate),
    GETTER(MergeResult, is_fastforward),
    GETTER(MergeResult, fastforward_oid),
    {NULL},
};

PyDoc_STRVAR(MergeResult__doc__, "MergeResult object.");

PyTypeObject MergeResultType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.MergeResult",                     /* tp_name           */
    sizeof(MergeResult),                       /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    0,                                         /* tp_dealloc        */
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
    MergeResult__doc__,                        /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    0,                                         /* tp_methods        */
    0,                                         /* tp_members        */
    MergeResult_getseters,                     /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    0,                                         /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};

