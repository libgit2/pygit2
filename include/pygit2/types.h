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

typedef struct {
    PyObject_HEAD
    PyObject *owner; /* Tree or TreeBuilder */
    const git_tree_entry *entry;
} TreeEntry;

typedef struct {
    PyObject_HEAD
    PyObject *a;
    PyObject *b;
} Diff;

typedef struct {
    PyObject_HEAD
    int old_start;
    int old_lines;
    char* old_file;
    int new_start;
    int new_lines;
    char* new_file;
    PyObject *old_data;
    PyObject *new_data;
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
} ReferenceLogEntry;

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
