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
#include <pygit2/utils.h>
#include <pygit2/signature.h>
#include <pygit2/commit.h>

extern PyTypeObject TreeType;

PyObject *
Commit_get_message_encoding(Commit *commit)
{
    const char *encoding;

    encoding = git_commit_message_encoding(commit->commit);
    if (encoding == NULL)
        Py_RETURN_NONE;

    return to_encoding(encoding);
}

PyObject *
Commit_get_message(Commit *commit)
{
    const char *message, *encoding;

    message = git_commit_message(commit->commit);
    encoding = git_commit_message_encoding(commit->commit);
    return to_unicode(message, encoding, "strict");
}

PyObject *
Commit_get_raw_message(Commit *commit)
{
    return PyString_FromString(git_commit_message(commit->commit));
}

PyObject *
Commit_get_commit_time(Commit *commit)
{
    return PyLong_FromLong(git_commit_time(commit->commit));
}

PyObject *
Commit_get_commit_time_offset(Commit *commit)
{
    return PyLong_FromLong(git_commit_time_offset(commit->commit));
}

PyObject *
Commit_get_committer(Commit *self)
{
    const git_signature *signature;
    const char *encoding;

    signature = git_commit_committer(self->commit);
    encoding = git_commit_message_encoding(self->commit);

    return build_signature((Object*)self, signature, encoding);
}

PyObject *
Commit_get_author(Commit *self)
{
    const git_signature *signature;
    const char *encoding;

    signature = git_commit_author(self->commit);
    encoding = git_commit_message_encoding(self->commit);

    return build_signature((Object*)self, signature, encoding);
}

PyObject *
Commit_get_tree(Commit *commit)
{
    git_tree *tree;
    Tree *py_tree;
    int err;

    err = git_commit_tree(&tree, commit->commit);
    if (err == GIT_ENOTFOUND)
        Py_RETURN_NONE;

    if (err < 0)
        return Error_set(err);

    py_tree = PyObject_New(Tree, &TreeType);
    if (py_tree) {
        Py_INCREF(commit->repo);
        py_tree->repo = commit->repo;
        py_tree->tree = (git_tree*)tree;
    }
    return (PyObject*)py_tree;
}

PyObject *
Commit_get_parents(Commit *commit)
{
    unsigned int i, parent_count;
    const git_oid *parent_oid;
    PyObject *obj;
    PyObject *list;

    parent_count = git_commit_parentcount(commit->commit);
    list = PyList_New(parent_count);
    if (!list)
        return NULL;

    for (i=0; i < parent_count; i++) {
        parent_oid = git_commit_parent_oid(commit->commit, i);
        if (parent_oid == NULL) {
            Py_DECREF(list);
            Error_set(GIT_ENOTFOUND);
            return NULL;
        }
        obj = lookup_object(commit->repo, parent_oid, GIT_OBJ_COMMIT);
        if (obj == NULL) {
            Py_DECREF(list);
            return NULL;
        }

        PyList_SET_ITEM(list, i, obj);
    }

    return list;
}

PyGetSetDef Commit_getseters[] = {
    {"message_encoding", (getter)Commit_get_message_encoding, NULL,
     "message encoding", NULL},
    {"message", (getter)Commit_get_message, NULL, "message", NULL},
    {"_message", (getter)Commit_get_raw_message, NULL, "message (bytes)", NULL},
    {"commit_time", (getter)Commit_get_commit_time, NULL, "commit time",
     NULL},
    {"commit_time_offset", (getter)Commit_get_commit_time_offset, NULL,
     "commit time offset", NULL},
    {"committer", (getter)Commit_get_committer, NULL, "committer", NULL},
    {"author", (getter)Commit_get_author, NULL, "author", NULL},
    {"tree", (getter)Commit_get_tree, NULL, "tree object", NULL},
    {"parents", (getter)Commit_get_parents, NULL, "parents of this commit",
      NULL},
    {NULL}
};

PyTypeObject CommitType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.Commit",                           /* tp_name           */
    sizeof(Commit),                            /* tp_basicsize      */
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
    "Commit objects",                          /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    0,                                         /* tp_methods        */
    0,                                         /* tp_members        */
    Commit_getseters,                          /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    0,                                         /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};
