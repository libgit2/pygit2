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

#ifndef INCLUDE_pygit2_objects_h
#define INCLUDE_pygit2_objects_h

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <git2.h>

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


/* git_config */
typedef struct {
    PyObject_HEAD
    git_config* config;
} Config;

typedef struct {
    PyObject_HEAD
    Config *owner;
    git_config_iterator *iter;
} ConfigIter;

/* git_note */
typedef struct {
    PyObject_HEAD
    Repository *repo;
    git_note *note;
    char* annotated_id;
} Note;

typedef struct {
    PyObject_HEAD
    Repository *repo;
    git_note_iterator* iter;
    char* ref;
} NoteIter;


/* git _diff */
SIMPLE_TYPE(Diff, git_diff, list)

typedef struct {
    PyObject_HEAD
    Diff* diff;
    size_t i;
    size_t n;
} DiffIter;

typedef struct {
    PyObject_HEAD
    PyObject* hunks;
    const char * old_file_path;
    const char * new_file_path;
    char* old_oid;
    char* new_oid;
    char status;
    unsigned similarity;
    unsigned additions;
    unsigned deletions;
    unsigned flags;
} Patch;

typedef struct {
    PyObject_HEAD
    PyObject* lines;
    int old_start;
    int old_lines;
    int new_start;
    int new_lines;
} Hunk;


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

typedef struct {
    PyObject_HEAD
    Index *owner;
    int i;
} IndexIter;


/* git_reference, git_reflog */
SIMPLE_TYPE(Walker, git_revwalk, walk)

SIMPLE_TYPE(Reference, git_reference, reference)

typedef Reference Branch;

typedef struct {
    PyObject_HEAD
    git_signature *signature;
    char *oid_old;
    char *oid_new;
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
    const char *encoding;
} Signature;


/* git_remote */
typedef struct {
    PyObject_HEAD
    Repository *repo;
    git_remote *remote;
    /* Callbacks for network events */
    PyObject *progress;
    PyObject *transfer_progress;
    PyObject *update_tips;
} Remote;

/* git_refspec */
typedef struct {
    PyObject_HEAD
    const Remote *owner;
    const git_refspec *refspec;
} Refspec;

/* git_transfer_progress */
typedef struct {
    PyObject_HEAD
    unsigned int total_objects;
    unsigned int indexed_objects;
    unsigned int received_objects;
    unsigned int local_objects;
    unsigned int total_deltas;
    unsigned int indexed_deltas;
    size_t received_bytes;
} TransferProgress;

/* git_blame */
SIMPLE_TYPE(Blame, git_blame, blame)

typedef struct {
    PyObject_HEAD
    Blame* blame;
    size_t i;
    size_t n;
} BlameIter;

typedef struct {
    PyObject_HEAD
    unsigned lines_in_hunk;
    char* final_commit_id;
    unsigned final_start_line_number;
    git_signature* final_signature;
    char* orig_commit_id;
    char* orig_path;
    unsigned orig_start_line_number;
    git_signature* orig_signature;
    char boundary;
} BlameHunk;

/* git_merge */
typedef struct {
    PyObject_HEAD
    git_merge_result *result;
} MergeResult;

#endif
