/*
 * Copyright 2010-2020 The pygit2 contributors
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

#include <git2.h>
#include "error.h"
#include "types.h"
#include "utils.h"
#include "repository.h"
#include "oid.h"
#include "options.h"

PyObject *GitError;
PyObject *AlreadyExistsError;
PyObject *InvalidSpecError;

extern PyTypeObject RepositoryType;
extern PyTypeObject OdbType;
extern PyTypeObject OdbBackendType;
extern PyTypeObject OdbBackendPackType;
extern PyTypeObject OdbBackendLooseType;
extern PyTypeObject OidType;
extern PyTypeObject ObjectType;
extern PyTypeObject CommitType;
extern PyTypeObject DiffType;
extern PyTypeObject DeltasIterType;
extern PyTypeObject DiffIterType;
extern PyTypeObject DiffDeltaType;
extern PyTypeObject DiffFileType;
extern PyTypeObject DiffHunkType;
extern PyTypeObject DiffLineType;
extern PyTypeObject DiffStatsType;
extern PyTypeObject PatchType;
extern PyTypeObject TreeType;
extern PyTypeObject TreeBuilderType;
extern PyTypeObject TreeIterType;
extern PyTypeObject BlobType;
extern PyTypeObject TagType;
extern PyTypeObject WalkerType;
extern PyTypeObject RefdbType;
extern PyTypeObject RefdbBackendType;
extern PyTypeObject RefdbFsBackendType;
extern PyTypeObject ReferenceType;
extern PyTypeObject RevSpecType;
extern PyTypeObject RefLogIterType;
extern PyTypeObject RefLogEntryType;
extern PyTypeObject BranchType;
extern PyTypeObject SignatureType;
extern PyTypeObject RemoteType;
extern PyTypeObject RefspecType;
extern PyTypeObject NoteType;
extern PyTypeObject NoteIterType;
extern PyTypeObject WorktreeType;
extern PyTypeObject MailmapType;


PyDoc_STRVAR(discover_repository__doc__,
  "discover_repository(path[, across_fs[, ceiling_dirs]]) -> str\n"
  "\n"
  "Look for a git repository and return its path. If not found returns None.");

PyObject *
discover_repository(PyObject *self, PyObject *args)
{
    git_buf repo_path = {NULL};
    const char *path = NULL;
    PyBytesObject *py_path = NULL;
    int across_fs = 0;
    PyBytesObject *py_ceiling_dirs = NULL;
    const char *ceiling_dirs = NULL;
    PyObject *py_repo_path = NULL;
    int err;

    if (!PyArg_ParseTuple(args, "O&|IO&", PyUnicode_FSConverter, &py_path, &across_fs,
                          PyUnicode_FSConverter, &py_ceiling_dirs))
        return NULL;

    if (py_path != NULL)
        path = PyBytes_AS_STRING(py_path);
    if (py_ceiling_dirs != NULL)
        ceiling_dirs = PyBytes_AS_STRING(py_ceiling_dirs);

    memset(&repo_path, 0, sizeof(git_buf));
    err = git_repository_discover(&repo_path, path, across_fs, ceiling_dirs);

    Py_XDECREF(py_path);
    Py_XDECREF(py_ceiling_dirs);

    if (err == GIT_ENOTFOUND)
        Py_RETURN_NONE;
    if (err < 0)
        return Error_set_str(err, path);

    py_repo_path = to_path(repo_path.ptr);
    git_buf_dispose(&repo_path);

    return py_repo_path;
};

PyDoc_STRVAR(hashfile__doc__,
    "hashfile(path) -> Oid\n"
    "\n"
    "Returns the oid of a new blob from a file path without actually writing\n"
    "to the odb.");
PyObject *
hashfile(PyObject *self, PyObject *args)
{
    git_oid oid;
    PyBytesObject *py_path = NULL;
    const char* path = NULL;
    int err;

    if (!PyArg_ParseTuple(args, "O&", PyUnicode_FSConverter, &py_path))
        return NULL;

    if (py_path != NULL)
        path = PyBytes_AS_STRING(py_path);

    err = git_odb_hashfile(&oid, path, GIT_OBJ_BLOB);
    Py_XDECREF(py_path);
    if (err < 0)
        return Error_set(err);

    return git_oid_to_python(&oid);
}

PyDoc_STRVAR(hash__doc__,
    "hash(data) -> Oid\n"
    "\n"
    "Returns the oid of a new blob from a string without actually writing to\n"
    "the odb.");
PyObject *
hash(PyObject *self, PyObject *args)
{
    git_oid oid;
    const char *data;
    Py_ssize_t size;
    int err;

    if (!PyArg_ParseTuple(args, "s#", &data, &size))
        return NULL;

    err = git_odb_hash(&oid, data, size, GIT_OBJ_BLOB);
    if (err < 0) {
        return Error_set(err);
    }

    return git_oid_to_python(&oid);
}


PyDoc_STRVAR(init_file_backend__doc__,
  "init_file_backend(path[, flags]) -> object\n"
  "\n"
  "Open repo backend given path.");
PyObject *
init_file_backend(PyObject *self, PyObject *args)
{
    PyBytesObject *py_path = NULL;
    const char* path = NULL;
    unsigned int flags = 0;
    int err = GIT_OK;
    git_repository *repository = NULL;

    if (!PyArg_ParseTuple(args, "O&|I", PyUnicode_FSConverter, &py_path, &flags))
        return NULL;
    if (py_path != NULL)
        path = PyBytes_AS_STRING(py_path);

    err = git_repository_open_ext(&repository, path, flags, NULL);

    Py_XDECREF(py_path);

    if (err < 0) {
        Error_set_str(err, path);
        goto cleanup;
    }

    return PyCapsule_New(repository, "backend", NULL);

cleanup:
    if (repository) {
        git_repository_free(repository);
    }

    if (err == GIT_ENOTFOUND) {
        PyErr_Format(GitError, "Repository not found at %s", path);
    }

    return NULL;
}


PyDoc_STRVAR(reference_is_valid_name__doc__,
    "reference_is_valid_name(refname) -> bool\n"
    "\n"
    "Check if the passed string is a valid reference name.");
PyObject *
reference_is_valid_name(PyObject *self, PyObject *py_refname)
{
    const char *refname = pgit_borrow(py_refname);
    if (refname == NULL)
        return NULL;

    int result = git_reference_is_valid_name(refname);
    return PyBool_FromLong(result);
}


PyDoc_STRVAR(tree_entry_cmp__doc__,
    "tree_entry_obj(a, b) -> int\n"
    "\n"
    "Rich comparison for objects, only available when the objects have been\n"
    "obtained through a tree. The sort criteria is the one Git uses to sort\n"
    "tree entries in a tree object. This function wraps git_tree_entry_cmp.\n"
    "\n"
    "Returns < 0 if a is before b, > 0 if a is after b, and 0 if a and b are\n"
    "the same.");

PyObject *
tree_entry_cmp(PyObject *self, PyObject *args)
{
    Object *a, *b;
    int cmp;

    if (!PyArg_ParseTuple(args, "O!O!", &ObjectType, &a, &ObjectType, &b))
        return NULL;

    if (a->entry == NULL || b->entry == NULL) {
        PyErr_SetString(PyExc_ValueError, "objects lack entry information");
        return NULL;
    }

    cmp = git_tree_entry_cmp(a->entry, b->entry);
    return PyLong_FromLong(cmp);
}


PyMethodDef module_methods[] = {
    {"discover_repository", discover_repository, METH_VARARGS, discover_repository__doc__},
    {"hash", hash, METH_VARARGS, hash__doc__},
    {"hashfile", hashfile, METH_VARARGS, hashfile__doc__},
    {"init_file_backend", init_file_backend, METH_VARARGS, init_file_backend__doc__},
    {"option", option, METH_VARARGS, option__doc__},
    {"reference_is_valid_name", reference_is_valid_name, METH_O, reference_is_valid_name__doc__},
    {"tree_entry_cmp", tree_entry_cmp, METH_VARARGS, tree_entry_cmp__doc__},
    {NULL}
};


struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "_pygit2",                       /* m_name */
    "Python bindings for libgit2.",  /* m_doc */
    -1,                              /* m_size */
    module_methods,                  /* m_methods */
    NULL,                            /* m_reload */
    NULL,                            /* m_traverse */
    NULL,                            /* m_clear */
    NULL,                            /* m_free */
};

PyMODINIT_FUNC
PyInit__pygit2(void)
{
    PyObject *m = PyModule_Create(&moduledef);
    if (m == NULL)
        return NULL;

    /* libgit2 version info */
    ADD_CONSTANT_INT(m, LIBGIT2_VER_MAJOR)
    ADD_CONSTANT_INT(m, LIBGIT2_VER_MINOR)
    ADD_CONSTANT_INT(m, LIBGIT2_VER_REVISION)
    ADD_CONSTANT_STR(m, LIBGIT2_VERSION)

    /* libgit2 options */
    ADD_CONSTANT_INT(m, GIT_OPT_GET_MWINDOW_SIZE);
    ADD_CONSTANT_INT(m, GIT_OPT_SET_MWINDOW_SIZE);
    ADD_CONSTANT_INT(m, GIT_OPT_GET_MWINDOW_MAPPED_LIMIT);
    ADD_CONSTANT_INT(m, GIT_OPT_SET_MWINDOW_MAPPED_LIMIT);
    ADD_CONSTANT_INT(m, GIT_OPT_GET_SEARCH_PATH);
    ADD_CONSTANT_INT(m, GIT_OPT_SET_SEARCH_PATH);
    ADD_CONSTANT_INT(m, GIT_OPT_SET_CACHE_OBJECT_LIMIT);
    ADD_CONSTANT_INT(m, GIT_OPT_SET_CACHE_MAX_SIZE);
    ADD_CONSTANT_INT(m, GIT_OPT_ENABLE_CACHING);
    ADD_CONSTANT_INT(m, GIT_OPT_GET_CACHED_MEMORY);
    ADD_CONSTANT_INT(m, GIT_OPT_GET_TEMPLATE_PATH);
    ADD_CONSTANT_INT(m, GIT_OPT_SET_TEMPLATE_PATH);
    ADD_CONSTANT_INT(m, GIT_OPT_SET_SSL_CERT_LOCATIONS);
    ADD_CONSTANT_INT(m, GIT_OPT_SET_USER_AGENT);
    ADD_CONSTANT_INT(m, GIT_OPT_ENABLE_STRICT_OBJECT_CREATION);
    ADD_CONSTANT_INT(m, GIT_OPT_ENABLE_STRICT_SYMBOLIC_REF_CREATION);
    ADD_CONSTANT_INT(m, GIT_OPT_SET_SSL_CIPHERS);
    ADD_CONSTANT_INT(m, GIT_OPT_GET_USER_AGENT);
    ADD_CONSTANT_INT(m, GIT_OPT_ENABLE_OFS_DELTA);
    ADD_CONSTANT_INT(m, GIT_OPT_ENABLE_FSYNC_GITDIR);
    ADD_CONSTANT_INT(m, GIT_OPT_GET_WINDOWS_SHAREMODE);
    ADD_CONSTANT_INT(m, GIT_OPT_SET_WINDOWS_SHAREMODE);
    ADD_CONSTANT_INT(m, GIT_OPT_ENABLE_STRICT_HASH_VERIFICATION);
    ADD_CONSTANT_INT(m, GIT_OPT_SET_ALLOCATOR);
    ADD_CONSTANT_INT(m, GIT_OPT_ENABLE_UNSAVED_INDEX_SAFETY);
    ADD_CONSTANT_INT(m, GIT_OPT_GET_PACK_MAX_OBJECTS);
    ADD_CONSTANT_INT(m, GIT_OPT_SET_PACK_MAX_OBJECTS);
    ADD_CONSTANT_INT(m, GIT_OPT_DISABLE_PACK_KEEP_FILE_CHECKS);

    /* Exceptions */
    ADD_EXC(m, GitError, NULL);
    ADD_EXC(m, AlreadyExistsError, PyExc_ValueError);
    ADD_EXC(m, InvalidSpecError, PyExc_ValueError);

    /* Repository */
    INIT_TYPE(RepositoryType, NULL, PyType_GenericNew)
    ADD_TYPE(m, Repository)

    /* Odb */
    INIT_TYPE(OdbType, NULL, PyType_GenericNew)
    ADD_TYPE(m, Odb)

    INIT_TYPE(OdbBackendType, NULL, PyType_GenericNew)
    ADD_TYPE(m, OdbBackend)
    INIT_TYPE(OdbBackendPackType, &OdbBackendType, PyType_GenericNew)
    ADD_TYPE(m, OdbBackendPack)
    INIT_TYPE(OdbBackendLooseType, &OdbBackendType, PyType_GenericNew)
    ADD_TYPE(m, OdbBackendLoose)

    /* Oid */
    INIT_TYPE(OidType, NULL, PyType_GenericNew)
    ADD_TYPE(m, Oid)
    ADD_CONSTANT_INT(m, GIT_OID_RAWSZ)
    ADD_CONSTANT_INT(m, GIT_OID_HEXSZ)
    ADD_CONSTANT_STR(m, GIT_OID_HEX_ZERO)
    ADD_CONSTANT_INT(m, GIT_OID_MINPREFIXLEN)

    /*
     * Objects
     */
    INIT_TYPE(ObjectType, NULL, NULL)
    INIT_TYPE(CommitType, &ObjectType, NULL)
    INIT_TYPE(SignatureType, NULL, PyType_GenericNew)
    INIT_TYPE(TreeType, &ObjectType, NULL)
    INIT_TYPE(TreeIterType, NULL, NULL)
    INIT_TYPE(TreeBuilderType, NULL, NULL)
    INIT_TYPE(BlobType, &ObjectType, NULL)
    INIT_TYPE(TagType, &ObjectType, NULL)
    ADD_TYPE(m, Object)
    ADD_TYPE(m, Commit)
    ADD_TYPE(m, Signature)
    ADD_TYPE(m, Tree)
    ADD_TYPE(m, TreeBuilder)
    ADD_TYPE(m, Blob)
    ADD_TYPE(m, Tag)
    ADD_CONSTANT_INT(m, GIT_OBJ_ANY)
    ADD_CONSTANT_INT(m, GIT_OBJ_COMMIT)
    ADD_CONSTANT_INT(m, GIT_OBJ_TREE)
    ADD_CONSTANT_INT(m, GIT_OBJ_BLOB)
    ADD_CONSTANT_INT(m, GIT_OBJ_TAG)
    /* Valid modes for index and tree entries. */
    ADD_CONSTANT_INT(m, GIT_FILEMODE_TREE)
    ADD_CONSTANT_INT(m, GIT_FILEMODE_BLOB)
    ADD_CONSTANT_INT(m, GIT_FILEMODE_BLOB_EXECUTABLE)
    ADD_CONSTANT_INT(m, GIT_FILEMODE_LINK)
    ADD_CONSTANT_INT(m, GIT_FILEMODE_COMMIT)

    /*
     * Log
     */
    INIT_TYPE(WalkerType, NULL, NULL)
    ADD_TYPE(m, Walker);
    ADD_CONSTANT_INT(m, GIT_SORT_NONE)
    ADD_CONSTANT_INT(m, GIT_SORT_TOPOLOGICAL)
    ADD_CONSTANT_INT(m, GIT_SORT_TIME)
    ADD_CONSTANT_INT(m, GIT_SORT_REVERSE)

    /*
     * Reset
     */
    ADD_CONSTANT_INT(m, GIT_RESET_SOFT)
    ADD_CONSTANT_INT(m, GIT_RESET_MIXED)
    ADD_CONSTANT_INT(m, GIT_RESET_HARD)

    /* Refdb */
    INIT_TYPE(RefdbType, NULL, PyType_GenericNew)
    ADD_TYPE(m, Refdb)

    INIT_TYPE(RefdbBackendType, NULL, PyType_GenericNew)
    ADD_TYPE(m, RefdbBackend)
    INIT_TYPE(RefdbFsBackendType, &RefdbBackendType, PyType_GenericNew)
    ADD_TYPE(m, RefdbFsBackend)

    /*
     * References
     */
    INIT_TYPE(ReferenceType, NULL, PyType_GenericNew)
    INIT_TYPE(RefLogEntryType, NULL, NULL)
    INIT_TYPE(RefLogIterType, NULL, NULL)
    INIT_TYPE(NoteType, NULL, NULL)
    INIT_TYPE(NoteIterType, NULL, NULL)
    ADD_TYPE(m, Reference)
    ADD_TYPE(m, RefLogEntry)
    ADD_TYPE(m, Note)
    ADD_CONSTANT_INT(m, GIT_REF_INVALID)
    ADD_CONSTANT_INT(m, GIT_REF_OID)
    ADD_CONSTANT_INT(m, GIT_REF_SYMBOLIC)
    ADD_CONSTANT_INT(m, GIT_REF_LISTALL)

    /*
     * RevSpec
     */
    INIT_TYPE(RevSpecType, NULL, NULL)
    ADD_TYPE(m, RevSpec)
    ADD_CONSTANT_INT(m, GIT_REVPARSE_SINGLE)
    ADD_CONSTANT_INT(m, GIT_REVPARSE_RANGE)
    ADD_CONSTANT_INT(m, GIT_REVPARSE_MERGE_BASE)

    /*
     * Worktree
     */
    INIT_TYPE(WorktreeType, NULL, NULL)
    ADD_TYPE(m, Worktree)

    /*
     * Branches
     */
    INIT_TYPE(BranchType, &ReferenceType, NULL);
    ADD_TYPE(m, Branch)
    ADD_CONSTANT_INT(m, GIT_BRANCH_LOCAL)
    ADD_CONSTANT_INT(m, GIT_BRANCH_REMOTE)
    ADD_CONSTANT_INT(m, GIT_BRANCH_ALL)

    /*
     * Index & Working copy
     */
    /* Status */
    ADD_CONSTANT_INT(m, GIT_STATUS_CURRENT)
    ADD_CONSTANT_INT(m, GIT_STATUS_INDEX_NEW)
    ADD_CONSTANT_INT(m, GIT_STATUS_INDEX_MODIFIED)
    ADD_CONSTANT_INT(m, GIT_STATUS_INDEX_DELETED)
    ADD_CONSTANT_INT(m, GIT_STATUS_INDEX_RENAMED)
    ADD_CONSTANT_INT(m, GIT_STATUS_INDEX_TYPECHANGE)
    ADD_CONSTANT_INT(m, GIT_STATUS_WT_NEW)
    ADD_CONSTANT_INT(m, GIT_STATUS_WT_MODIFIED)
    ADD_CONSTANT_INT(m, GIT_STATUS_WT_DELETED)
    ADD_CONSTANT_INT(m, GIT_STATUS_WT_TYPECHANGE)
    ADD_CONSTANT_INT(m, GIT_STATUS_WT_RENAMED)
    ADD_CONSTANT_INT(m, GIT_STATUS_WT_UNREADABLE)
    ADD_CONSTANT_INT(m, GIT_STATUS_IGNORED) /* Flags for ignored files */
    ADD_CONSTANT_INT(m, GIT_STATUS_CONFLICTED)
    /* Different checkout strategies */
    ADD_CONSTANT_INT(m, GIT_CHECKOUT_NONE)
    ADD_CONSTANT_INT(m, GIT_CHECKOUT_SAFE)
    ADD_CONSTANT_INT(m, GIT_CHECKOUT_RECREATE_MISSING)
    ADD_CONSTANT_INT(m, GIT_CHECKOUT_FORCE)
    ADD_CONSTANT_INT(m, GIT_CHECKOUT_ALLOW_CONFLICTS)
    ADD_CONSTANT_INT(m, GIT_CHECKOUT_REMOVE_UNTRACKED)
    ADD_CONSTANT_INT(m, GIT_CHECKOUT_REMOVE_IGNORED)
    ADD_CONSTANT_INT(m, GIT_CHECKOUT_UPDATE_ONLY)
    ADD_CONSTANT_INT(m, GIT_CHECKOUT_DONT_UPDATE_INDEX)
    ADD_CONSTANT_INT(m, GIT_CHECKOUT_NO_REFRESH)
    ADD_CONSTANT_INT(m, GIT_CHECKOUT_DISABLE_PATHSPEC_MATCH)

    /*
     * Diff
     */
    INIT_TYPE(DiffType, NULL, NULL)
    INIT_TYPE(DeltasIterType, NULL, NULL)
    INIT_TYPE(DiffIterType, NULL, NULL)
    INIT_TYPE(DiffDeltaType, NULL, NULL)
    INIT_TYPE(DiffFileType, NULL, NULL)
    INIT_TYPE(DiffHunkType, NULL, NULL)
    INIT_TYPE(DiffLineType, NULL, NULL)
    INIT_TYPE(DiffStatsType, NULL, NULL)
    INIT_TYPE(PatchType, NULL, NULL)
    ADD_TYPE(m, Diff)
    ADD_TYPE(m, DiffDelta)
    ADD_TYPE(m, DiffFile)
    ADD_TYPE(m, DiffHunk)
    ADD_TYPE(m, DiffLine)
    ADD_TYPE(m, DiffStats)
    ADD_TYPE(m, Patch)

    /* (git_diff_options in libgit2) */
    ADD_CONSTANT_INT(m, GIT_DIFF_NORMAL)
    ADD_CONSTANT_INT(m, GIT_DIFF_REVERSE)
    ADD_CONSTANT_INT(m, GIT_DIFF_INCLUDE_IGNORED)
    ADD_CONSTANT_INT(m, GIT_DIFF_RECURSE_IGNORED_DIRS)
    ADD_CONSTANT_INT(m, GIT_DIFF_INCLUDE_UNTRACKED)
    ADD_CONSTANT_INT(m, GIT_DIFF_RECURSE_UNTRACKED_DIRS)
    ADD_CONSTANT_INT(m, GIT_DIFF_INCLUDE_UNMODIFIED)
    ADD_CONSTANT_INT(m, GIT_DIFF_INCLUDE_TYPECHANGE)
    ADD_CONSTANT_INT(m, GIT_DIFF_INCLUDE_TYPECHANGE_TREES)
    ADD_CONSTANT_INT(m, GIT_DIFF_IGNORE_FILEMODE)
    ADD_CONSTANT_INT(m, GIT_DIFF_IGNORE_SUBMODULES)
    ADD_CONSTANT_INT(m, GIT_DIFF_IGNORE_CASE)
    ADD_CONSTANT_INT(m, GIT_DIFF_INCLUDE_CASECHANGE)
    ADD_CONSTANT_INT(m, GIT_DIFF_DISABLE_PATHSPEC_MATCH)
    ADD_CONSTANT_INT(m, GIT_DIFF_SKIP_BINARY_CHECK)
    ADD_CONSTANT_INT(m, GIT_DIFF_ENABLE_FAST_UNTRACKED_DIRS)
    ADD_CONSTANT_INT(m, GIT_DIFF_UPDATE_INDEX)
    ADD_CONSTANT_INT(m, GIT_DIFF_INCLUDE_UNREADABLE)
    ADD_CONSTANT_INT(m, GIT_DIFF_INCLUDE_UNREADABLE_AS_UNTRACKED)
    ADD_CONSTANT_INT(m, GIT_DIFF_INDENT_HEURISTIC)
    ADD_CONSTANT_INT(m, GIT_DIFF_FORCE_TEXT)
    ADD_CONSTANT_INT(m, GIT_DIFF_FORCE_BINARY)
    ADD_CONSTANT_INT(m, GIT_DIFF_IGNORE_WHITESPACE)
    ADD_CONSTANT_INT(m, GIT_DIFF_IGNORE_WHITESPACE_CHANGE)
    ADD_CONSTANT_INT(m, GIT_DIFF_IGNORE_WHITESPACE_EOL)
    ADD_CONSTANT_INT(m, GIT_DIFF_SHOW_UNTRACKED_CONTENT)
    ADD_CONSTANT_INT(m, GIT_DIFF_SHOW_UNMODIFIED)
    ADD_CONSTANT_INT(m, GIT_DIFF_PATIENCE)
    ADD_CONSTANT_INT(m, GIT_DIFF_MINIMAL)
    ADD_CONSTANT_INT(m, GIT_DIFF_SHOW_BINARY)

    /* Formatting options for diff stats (git_diff_stats_format_t in libgit2) */
    ADD_CONSTANT_INT(m, GIT_DIFF_STATS_NONE)
    ADD_CONSTANT_INT(m, GIT_DIFF_STATS_FULL)
    ADD_CONSTANT_INT(m, GIT_DIFF_STATS_SHORT)
    ADD_CONSTANT_INT(m, GIT_DIFF_STATS_NUMBER)
    ADD_CONSTANT_INT(m, GIT_DIFF_STATS_INCLUDE_SUMMARY)

    /* Flags for Diff.find_similar (git_diff_find_t in libgit2) */
    ADD_CONSTANT_INT(m, GIT_DIFF_FIND_BY_CONFIG) /** Obey diff.renames */
    ADD_CONSTANT_INT(m, GIT_DIFF_FIND_RENAMES) /* --find-renames */
    ADD_CONSTANT_INT(m, GIT_DIFF_FIND_RENAMES_FROM_REWRITES) /* --break-rewrites=N */
    ADD_CONSTANT_INT(m, GIT_DIFF_FIND_COPIES) /* --find-copies */
    ADD_CONSTANT_INT(m, GIT_DIFF_FIND_COPIES_FROM_UNMODIFIED) /* --find-copies-harder */
    ADD_CONSTANT_INT(m, GIT_DIFF_FIND_REWRITES) /* --break-rewrites=/M */
    ADD_CONSTANT_INT(m, GIT_DIFF_BREAK_REWRITES)
    ADD_CONSTANT_INT(m, GIT_DIFF_FIND_AND_BREAK_REWRITES)
    ADD_CONSTANT_INT(m, GIT_DIFF_FIND_FOR_UNTRACKED)
    ADD_CONSTANT_INT(m, GIT_DIFF_FIND_ALL) /* Turn on all finding features. */
    ADD_CONSTANT_INT(m, GIT_DIFF_FIND_IGNORE_LEADING_WHITESPACE)
    ADD_CONSTANT_INT(m, GIT_DIFF_FIND_IGNORE_WHITESPACE)
    ADD_CONSTANT_INT(m, GIT_DIFF_FIND_DONT_IGNORE_WHITESPACE)
    ADD_CONSTANT_INT(m, GIT_DIFF_FIND_EXACT_MATCH_ONLY)
    ADD_CONSTANT_INT(m, GIT_DIFF_BREAK_REWRITES_FOR_RENAMES_ONLY)
    ADD_CONSTANT_INT(m, GIT_DIFF_FIND_REMOVE_UNMODIFIED)

    /* DiffDelta and DiffFile flags (git_diff_flag_t in libgit2) */
    ADD_CONSTANT_INT(m, GIT_DIFF_FLAG_BINARY)
    ADD_CONSTANT_INT(m, GIT_DIFF_FLAG_NOT_BINARY)
    ADD_CONSTANT_INT(m, GIT_DIFF_FLAG_VALID_ID)
    ADD_CONSTANT_INT(m, GIT_DIFF_FLAG_EXISTS)

    /* DiffDelta.status (git_delta_t in libgit2) */
    ADD_CONSTANT_INT(m, GIT_DELTA_UNMODIFIED)
    ADD_CONSTANT_INT(m, GIT_DELTA_ADDED)
    ADD_CONSTANT_INT(m, GIT_DELTA_DELETED)
    ADD_CONSTANT_INT(m, GIT_DELTA_MODIFIED)
    ADD_CONSTANT_INT(m, GIT_DELTA_RENAMED)
    ADD_CONSTANT_INT(m, GIT_DELTA_COPIED)
    ADD_CONSTANT_INT(m, GIT_DELTA_IGNORED)
    ADD_CONSTANT_INT(m, GIT_DELTA_UNTRACKED)
    ADD_CONSTANT_INT(m, GIT_DELTA_TYPECHANGE)
    ADD_CONSTANT_INT(m, GIT_DELTA_UNREADABLE)
    ADD_CONSTANT_INT(m, GIT_DELTA_CONFLICTED)

    /* Config */
    ADD_CONSTANT_INT(m, GIT_CONFIG_LEVEL_LOCAL);
    ADD_CONSTANT_INT(m, GIT_CONFIG_LEVEL_GLOBAL);
    ADD_CONSTANT_INT(m, GIT_CONFIG_LEVEL_XDG);
    ADD_CONSTANT_INT(m, GIT_CONFIG_LEVEL_SYSTEM);

    /* Blame */
    ADD_CONSTANT_INT(m, GIT_BLAME_NORMAL)
    ADD_CONSTANT_INT(m, GIT_BLAME_TRACK_COPIES_SAME_FILE)
    ADD_CONSTANT_INT(m, GIT_BLAME_TRACK_COPIES_SAME_COMMIT_MOVES)
    ADD_CONSTANT_INT(m, GIT_BLAME_TRACK_COPIES_SAME_COMMIT_COPIES)
    ADD_CONSTANT_INT(m, GIT_BLAME_TRACK_COPIES_ANY_COMMIT_COPIES)
    ADD_CONSTANT_INT(m, GIT_BLAME_FIRST_PARENT)
    ADD_CONSTANT_INT(m, GIT_BLAME_USE_MAILMAP)
    ADD_CONSTANT_INT(m, GIT_BLAME_IGNORE_WHITESPACE)

    /* Merge */
    ADD_CONSTANT_INT(m, GIT_MERGE_ANALYSIS_NONE)
    ADD_CONSTANT_INT(m, GIT_MERGE_ANALYSIS_NORMAL)
    ADD_CONSTANT_INT(m, GIT_MERGE_ANALYSIS_UP_TO_DATE)
    ADD_CONSTANT_INT(m, GIT_MERGE_ANALYSIS_FASTFORWARD)
    ADD_CONSTANT_INT(m, GIT_MERGE_ANALYSIS_UNBORN)

    /* Describe */
    ADD_CONSTANT_INT(m, GIT_DESCRIBE_DEFAULT);
    ADD_CONSTANT_INT(m, GIT_DESCRIBE_TAGS);
    ADD_CONSTANT_INT(m, GIT_DESCRIBE_ALL);

    /* Stash */
    ADD_CONSTANT_INT(m, GIT_STASH_DEFAULT);
    ADD_CONSTANT_INT(m, GIT_STASH_KEEP_INDEX);
    ADD_CONSTANT_INT(m, GIT_STASH_INCLUDE_UNTRACKED);
    ADD_CONSTANT_INT(m, GIT_STASH_INCLUDE_IGNORED);
    ADD_CONSTANT_INT(m, GIT_STASH_APPLY_DEFAULT);
    ADD_CONSTANT_INT(m, GIT_STASH_APPLY_REINSTATE_INDEX);

    /* Mailmap */
    INIT_TYPE(MailmapType, NULL, PyType_GenericNew)
    ADD_TYPE(m, Mailmap)

    /* Global initialization of libgit2 */
    git_libgit2_init();

    return m;

fail:
    Py_DECREF(m);
    return NULL;
}
