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
#include <pygit2/signature.h>
#include <pygit2/oid.h>
#include <pygit2/tag.h>

PyObject *
Tag_get_target(Tag *self)
{
    const git_oid *oid;

    oid = git_tag_target_oid(self->tag);
    return git_oid_to_python(oid->id);
}

PyObject *
Tag_get_name(Tag *self)
{
    const char *name;
    name = git_tag_name(self->tag);
    if (!name)
        Py_RETURN_NONE;
    return to_unicode(name, "utf-8", "strict");
}

PyObject *
Tag_get_tagger(Tag *self)
{
    const git_signature *signature = git_tag_tagger(self->tag);
    if (!signature)
        Py_RETURN_NONE;

    return build_signature((Object*)self, signature, "utf-8");
}

PyObject *
Tag_get_message(Tag *self)
{
    const char *message;
    message = git_tag_message(self->tag);
    if (!message)
        Py_RETURN_NONE;
    return to_unicode(message, "utf-8", "strict");
}

PyObject *
Tag_get_raw_message(Tag *self)
{
    return PyString_FromString(git_tag_message(self->tag));
}

PyGetSetDef Tag_getseters[] = {
    {"target", (getter)Tag_get_target, NULL, "tagged object", NULL},
    {"name", (getter)Tag_get_name, NULL, "tag name", NULL},
    {"tagger", (getter)Tag_get_tagger, NULL, "tagger", NULL},
    {"message", (getter)Tag_get_message, NULL, "tag message", NULL},
    {"_message", (getter)Tag_get_raw_message, NULL, "tag message (bytes)", NULL},
    {NULL}
};

PyTypeObject TagType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.Tag",                              /* tp_name           */
    sizeof(Tag),                               /* tp_basicsize      */
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
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,  /* tp_flags          */
    "Tag objects",                             /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    0,                                         /* tp_methods        */
    0,                                         /* tp_members        */
    Tag_getseters,                             /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    0,                                         /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};
