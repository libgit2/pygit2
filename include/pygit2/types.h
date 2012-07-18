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

#ifndef INCLUDE_pygit2_objects_h
#define INCLUDE_pygit2_objects_h

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <git2.h>

/* Python objects */
typedef struct {
    PyObject_HEAD
    git_repository *repo;
    PyObject *index; /* It will be None for a bare repository */
    PyObject *config;
} Repository;

/* The structs for some of the object subtypes are identical except for
 * the type of their object pointers. */
#define OBJECT_STRUCT(_name, _ptr_type, _ptr_name) \
        typedef struct {\
            PyObject_HEAD\
            Repository *repo;\
            _ptr_type *_ptr_name;\
        } _name;

OBJECT_STRUCT(Object, git_object, obj)
OBJECT_STRUCT(Commit, git_commit, commit)
OBJECT_STRUCT(Tree, git_tree, tree)
OBJECT_STRUCT(TreeBuilder, git_treebuilder, bld)
OBJECT_STRUCT(Blob, git_blob, blob)
OBJECT_STRUCT(Tag, git_tag, tag)
OBJECT_STRUCT(Index, git_index, index)
OBJECT_STRUCT(Walker, git_revwalk, walk)
OBJECT_STRUCT(Diff, git_diff_list, diff)
OBJECT_STRUCT(Config, git_config, config)

typedef struct {
    PyObject_HEAD
    PyObject *owner; /* Tree or TreeBuilder */
    const git_tree_entry *entry;
} TreeEntry;

typedef struct {
    PyObject_HEAD
    int old_start;
    int old_lines;
    char* old_file;
    int new_start;
    int new_lines;
    char* new_file;
    PyObject *data;
} Hunk;

typedef struct {
    PyObject_HEAD
    Tree *owner;
    int i;
} TreeIter;

typedef struct {
    PyObject_HEAD
    git_index_entry *entry;
} IndexEntry;

typedef struct {
    PyObject_HEAD
    Index *owner;
    int i;
} IndexIter;

typedef struct {
    PyObject_HEAD
    git_reference *reference;
} Reference;

typedef struct {
    PyObject_HEAD
    PyObject *oid_old;
    PyObject *oid_new;
    PyObject *committer;
    char *msg;
} RefLogEntry;

typedef struct {
    PyObject_HEAD
    Reference *reference;
    git_reflog *reflog;
    int i;
    int size;
} RefLogIter;


typedef struct {
    PyObject_HEAD
    Object *obj;
    const git_signature *signature;
    const char *encoding;
} Signature;


PyObject* lookup_object_prefix(Repository *repo, const git_oid *oid, size_t len,
                     git_otype type);
PyObject* lookup_object(Repository *repo, const git_oid *oid, git_otype type);

#endif
