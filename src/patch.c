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
#include "diff.h"
#include "error.h"
#include "oid.h"
#include "types.h"
#include "utils.h"

extern PyTypeObject DiffHunkType;
PyTypeObject PatchType;


PyObject *
wrap_patch(git_patch *patch)
{
    Patch *py_patch;
    PyObject *py_hunk;
    size_t i, hunk_amounts;

    if (!patch)
        Py_RETURN_NONE;

    py_patch = PyObject_New(Patch, &PatchType);
    if (py_patch) {
        py_patch->patch = patch;

        hunk_amounts = git_patch_num_hunks(patch);
        py_patch->hunks = PyList_New(hunk_amounts);
        for (i = 0; i < hunk_amounts; ++i) {
            py_hunk = wrap_diff_hunk(patch, i);
            if (py_hunk)
                PyList_SetItem((PyObject*) py_patch->hunks, i, py_hunk);
        }
    }

    return (PyObject*) py_patch;
}

static void
Patch_dealloc(Patch *self)
{
    Py_CLEAR(self->hunks);
    git_patch_free(self->patch);
    PyObject_Del(self);
}

PyDoc_STRVAR(Patch_delta__doc__, "Get the delta associated with a patch.");

PyObject *
Patch_delta__get__(Patch *self)
{
    if (!self->patch)
        Py_RETURN_NONE;

    return wrap_diff_delta(git_patch_get_delta(self->patch));
}

PyDoc_STRVAR(Patch_line_stats__doc__,
    "Get line counts of each type in a patch.");

PyObject *
Patch_line_stats__get__(Patch *self)
{
    size_t context, additions, deletions;
    int err;

    if (!self->patch)
        Py_RETURN_NONE;

    err = git_patch_line_stats(&context, &additions, &deletions,
                               self->patch);
    if (err < 0)
        return Error_set(err);

    return Py_BuildValue("III", context, additions, deletions);
}

PyMemberDef Patch_members[] = {
    MEMBER(Patch, hunks, T_OBJECT, "hunks"),
    {NULL}
};

PyGetSetDef Patch_getseters[] = {
    GETTER(Patch, delta),
    GETTER(Patch, line_stats),
    {NULL}
};

PyDoc_STRVAR(Patch__doc__, "Diff patch object.");

PyTypeObject PatchType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.Patch",                           /* tp_name           */
    sizeof(Patch),                             /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)Patch_dealloc,                 /* tp_dealloc        */
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
    Patch__doc__,                              /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    0,                                         /* tp_methods        */
    Patch_members,                             /* tp_members        */
    Patch_getseters,                           /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    0,                                         /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};
