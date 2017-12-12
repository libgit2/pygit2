/*
 * Copyright 2010-2017 The pygit2 contributors
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

#if !(LIBGIT2_VER_MAJOR == 0 && LIBGIT2_VER_MINOR == 26)
#error You need a compatible libgit2 version (v0.26.x)
#endif

/*
 * Python objects
 *
 **/

/* git_repository */
typedef struct {
    PyObject_HEAD
    git_repository *repo;
    PyObject *index;  /* It will be None for a bare repository */
    PyObject *config; /* It will be None for a bare repository */
    int owned;    /* _from_c() sometimes means we don't own the C pointer */
} Repository;


typedef struct {
    PyObject_HEAD
    git_oid oid;
} Oid;


#define SIMPLE_TYPE(_name, _ptr_type, _ptr_name) \
        typedef struct {\
            PyObject_HEAD\
            Repository *repo;\
            _ptr_type *_ptr_name;\
        } _name;


/* git object types
 *
 * The structs for some of the object subtypes are identical except for
 * the type of their object pointers. */
SIMPLE_TYPE(Object, git_object, obj)
SIMPLE_TYPE(Commit, git_commit, commit)
SIMPLE_TYPE(Tree, git_tree, tree)
SIMPLE_TYPE(Blob, git_blob, blob)
SIMPLE_TYPE(Tag, git_tag, tag)

/* git_note */
typedef struct {
    PyObject_HEAD
    Repository *repo;
    git_note *note;
    PyObject* annotated_id;
} Note;

typedef struct {
    PyObject_HEAD
    Repository *repo;
    git_note_iterator* iter;
    char* ref;
} NoteIter;

/* git_patch */
typedef struct {
    PyObject_HEAD
    git_patch *patch;
    PyObject* hunks;
    Blob* oldblob;
    Blob* newblob;
} Patch;

/* git_diff */
SIMPLE_TYPE(Diff, git_diff, diff)

typedef struct {
    PyObject_HEAD
    Diff *diff;
    size_t i;
    size_t n;
} DeltasIter;

typedef struct {
    PyObject_HEAD
    Diff *diff;
    size_t i;
    size_t n;
} DiffIter;

typedef struct {
    PyObject_HEAD
    PyObject *id;
    char *path;
    git_off_t size;
    uint32_t flags;
    uint16_t mode;
} DiffFile;

typedef struct {
    PyObject_HEAD
    git_delta_t status;
    uint32_t flags;
    uint16_t similarity;
    uint16_t nfiles;
    PyObject *old_file;
    PyObject *new_file;
} DiffDelta;

typedef struct {
    PyObject_HEAD
    PyObject* lines;
    int old_start;
    int old_lines;
    int new_start;
    int new_lines;
    PyObject *header;
} DiffHunk;

typedef struct {
    PyObject_HEAD
    char origin;
    int old_lineno;
    int new_lineno;
    int num_lines;
    git_off_t content_offset;
    PyObject *content;
} DiffLine;

SIMPLE_TYPE(DiffStats, git_diff_stats, stats);

/* git_tree_walk , git_treebuilder*/
SIMPLE_TYPE(TreeBuilder, git_treebuilder, bld)

typedef struct {
    PyObject_HEAD
    const git_tree_entry *entry;
} TreeEntry;

typedef struct {
    PyObject_HEAD
    Tree *owner;
    int i;
} TreeIter;


/* git_index */
SIMPLE_TYPE(Index, git_index, index)

typedef struct {
    PyObject_HEAD
    git_index_entry entry;
} IndexEntry;


/* git_reference, git_reflog */
SIMPLE_TYPE(Walker, git_revwalk, walk)

SIMPLE_TYPE(Reference, git_reference, reference)

typedef Reference Branch;

typedef struct {
    PyObject_HEAD
    git_signature *signature;
    PyObject *oid_old;
    PyObject *oid_new;
    char *message;
} RefLogEntry;

typedef struct {
    PyObject_HEAD
    git_reflog *reflog;
    size_t i;
    size_t size;
} RefLogIter;


/* git_signature */
typedef struct {
    PyObject_HEAD
    Object *obj;
    const git_signature *signature;
    char *encoding;
} Signature;

#endif
