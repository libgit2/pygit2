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

/* Pypy does not provide this header */
#ifndef PYPY_VERSION
# include <osdefs.h>
#endif

#include <git2.h>
#include "error.h"
#include "types.h"
#include "utils.h"
#include "repository.h"
#include "oid.h"

/* FIXME: This is for pypy */
#ifndef MAXPATHLEN
# define MAXPATHLEN 1024
#endif

extern PyObject *GitError;

extern PyTypeObject RepositoryType;
extern PyTypeObject OidType;
extern PyTypeObject ObjectType;
extern PyTypeObject CommitType;
extern PyTypeObject DiffType;
extern PyTypeObject DiffIterType;
extern PyTypeObject PatchType;
extern PyTypeObject HunkType;
extern PyTypeObject TreeType;
extern PyTypeObject TreeBuilderType;
extern PyTypeObject TreeEntryType;
extern PyTypeObject TreeIterType;
extern PyTypeObject BlobType;
extern PyTypeObject TagType;
extern PyTypeObject IndexType;
extern PyTypeObject IndexEntryType;
extern PyTypeObject IndexIterType;
extern PyTypeObject WalkerType;
extern PyTypeObject ConfigType;
extern PyTypeObject ConfigIterType;
extern PyTypeObject ReferenceType;
extern PyTypeObject RefLogIterType;
extern PyTypeObject RefLogEntryType;
extern PyTypeObject BranchType;
extern PyTypeObject SignatureType;
extern PyTypeObject RemoteType;
extern PyTypeObject RefspecType;
extern PyTypeObject TransferProgressType;
extern PyTypeObject NoteType;
extern PyTypeObject NoteIterType;
extern PyTypeObject BlameType;
extern PyTypeObject BlameIterType;
extern PyTypeObject BlameHunkType;
extern PyTypeObject MergeResultType;



PyDoc_STRVAR(init_repository__doc__,
    "init_repository(path, bare)\n"
    "\n"
    "Creates a new Git repository in the given path.\n"
    "\n"
    "Arguments:\n"
    "\n"
    "path\n"
    "  Path where to create the repository.\n"
    "\n"
    "bare\n"
    "  Whether the repository will be bare or not.\n");

PyObject *
init_repository(PyObject *self, PyObject *args) {
    git_repository *repo;
    const char *path;
    unsigned int bare;
    int err;

    if (!PyArg_ParseTuple(args, "sI", &path, &bare))
        return NULL;

    err = git_repository_init(&repo, path, bare);
    if (err < 0)
        return Error_set_str(err, path);

    git_repository_free(repo);
    Py_RETURN_NONE;
};

PyDoc_STRVAR(clone_repository__doc__,
    "clone_repository(url, path, bare, remote_name, checkout_branch)\n"
    "\n"
    "Clones a Git repository in the given url to the given path "
    "with the specified options.\n"
    "\n"
    "Arguments:\n"
    "\n"
    "url\n"
    "  Git repository remote url.\n"
    "path\n"
    "  Path where to create the repository.\n"
    "bare\n"
    "  If 'bare' is not 0, then a bare git repository will be created.\n"
    "remote_name\n"
    "  The name given to the 'origin' remote.  The default is 'origin'.\n"
    "checkout_branch\n"
    "  The name of the branch to checkout. None means use the remote's "
    "HEAD.\n");


PyObject *
clone_repository(PyObject *self, PyObject *args) {
    git_repository *repo;
    const char *url;
    const char *path;
    unsigned int bare, ignore_cert_errors;
    const char *remote_name, *checkout_branch;
    int err;
    git_clone_options opts = GIT_CLONE_OPTIONS_INIT;

    if (!PyArg_ParseTuple(args, "zzIIzz",
                          &url, &path, &bare, &ignore_cert_errors, &remote_name, &checkout_branch))
        return NULL;

    opts.bare = bare;
    opts.ignore_cert_errors = ignore_cert_errors;
    opts.remote_name = remote_name;
    opts.checkout_branch = checkout_branch;

    err = git_clone(&repo, url, path, &opts);
    if (err < 0)
        return Error_set(err);

    git_repository_free(repo);
    Py_RETURN_NONE;
};


PyDoc_STRVAR(discover_repository__doc__,
  "discover_repository(path[, across_fs[, ceiling_dirs]]) -> str\n"
  "\n"
  "Look for a git repository and return its path.");

PyObject *
discover_repository(PyObject *self, PyObject *args)
{
    const char *path;
    int across_fs = 0;
    const char *ceiling_dirs = NULL;
    char repo_path[MAXPATHLEN];
    int err;

    if (!PyArg_ParseTuple(args, "s|Is", &path, &across_fs, &ceiling_dirs))
        return NULL;

    err = git_repository_discover(repo_path, sizeof(repo_path),
            path, across_fs, ceiling_dirs);
    if (err < 0)
        return Error_set_str(err, path);

    return to_path(repo_path);
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
    const char* path;
    int err;

    if (!PyArg_ParseTuple(args, "s", &path))
        return NULL;

    err = git_odb_hashfile(&oid, path, GIT_OBJ_BLOB);
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


PyMethodDef module_methods[] = {
    {"init_repository", init_repository, METH_VARARGS, init_repository__doc__},
    {"clone_repository", clone_repository, METH_VARARGS,
     clone_repository__doc__},
    {"discover_repository", discover_repository, METH_VARARGS,
     discover_repository__doc__},
    {"hashfile", hashfile, METH_VARARGS, hashfile__doc__},
    {"hash", hash, METH_VARARGS, hash__doc__},
    {NULL}
};

PyObject*
moduleinit(PyObject* m)
{
    if (m == NULL)
        return NULL;

    /* libgit2 version info */
    ADD_CONSTANT_INT(m, LIBGIT2_VER_MAJOR)
    ADD_CONSTANT_INT(m, LIBGIT2_VER_MINOR)
    ADD_CONSTANT_INT(m, LIBGIT2_VER_REVISION)
    ADD_CONSTANT_STR(m, LIBGIT2_VERSION)

    /* Errors */
    GitError = PyErr_NewException("_pygit2.GitError", NULL, NULL);
    Py_INCREF(GitError);
    PyModule_AddObject(m, "GitError", GitError);

    /* Repository */
    INIT_TYPE(RepositoryType, NULL, PyType_GenericNew)
    ADD_TYPE(m, Repository)

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
    INIT_TYPE(TreeEntryType, NULL, NULL)
    INIT_TYPE(TreeIterType, NULL, NULL)
    INIT_TYPE(TreeBuilderType, NULL, NULL)
    INIT_TYPE(BlobType, &ObjectType, NULL)
    INIT_TYPE(TagType, &ObjectType, NULL)
    ADD_TYPE(m, Object)
    ADD_TYPE(m, Commit)
    ADD_TYPE(m, Signature)
    ADD_TYPE(m, Tree)
    ADD_TYPE(m, TreeEntry)
    ADD_TYPE(m, TreeBuilder)
    ADD_TYPE(m, Blob)
    ADD_TYPE(m, Tag)
    ADD_CONSTANT_INT(m, GIT_OBJ_ANY)
    ADD_CONSTANT_INT(m, GIT_OBJ_COMMIT)
    ADD_CONSTANT_INT(m, GIT_OBJ_TREE)
    ADD_CONSTANT_INT(m, GIT_OBJ_BLOB)
    ADD_CONSTANT_INT(m, GIT_OBJ_TAG)
    /* Valid modes for index and tree entries. */
    ADD_CONSTANT_INT(m, GIT_FILEMODE_NEW)
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

    /*
     * References
     */
    INIT_TYPE(ReferenceType, NULL, NULL)
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
     * Branches
     */
    INIT_TYPE(BranchType, &ReferenceType, NULL);
    ADD_TYPE(m, Branch)
    ADD_CONSTANT_INT(m, GIT_BRANCH_LOCAL)
    ADD_CONSTANT_INT(m, GIT_BRANCH_REMOTE)

    /*
     * Index & Working copy
     */
    INIT_TYPE(IndexType, NULL, PyType_GenericNew)
    INIT_TYPE(IndexEntryType, NULL, PyType_GenericNew)
    INIT_TYPE(IndexIterType, NULL, NULL)
    ADD_TYPE(m, Index)
    ADD_TYPE(m, IndexEntry)
    /* Status */
    ADD_CONSTANT_INT(m, GIT_STATUS_CURRENT)
    ADD_CONSTANT_INT(m, GIT_STATUS_INDEX_NEW)
    ADD_CONSTANT_INT(m, GIT_STATUS_INDEX_MODIFIED)
    ADD_CONSTANT_INT(m, GIT_STATUS_INDEX_DELETED)
    ADD_CONSTANT_INT(m, GIT_STATUS_WT_NEW)
    ADD_CONSTANT_INT(m, GIT_STATUS_WT_MODIFIED)
    ADD_CONSTANT_INT(m, GIT_STATUS_WT_DELETED)
    ADD_CONSTANT_INT(m, GIT_STATUS_IGNORED) /* Flags for ignored files */
    /* Different checkout strategies */
    ADD_CONSTANT_INT(m, GIT_CHECKOUT_NONE)
    ADD_CONSTANT_INT(m, GIT_CHECKOUT_SAFE)
    ADD_CONSTANT_INT(m, GIT_CHECKOUT_SAFE_CREATE)
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
    INIT_TYPE(DiffIterType, NULL, NULL)
    INIT_TYPE(PatchType, NULL, NULL)
    INIT_TYPE(HunkType, NULL, NULL)
    ADD_TYPE(m, Diff)
    ADD_TYPE(m, Patch)
    ADD_TYPE(m, Hunk)
    ADD_CONSTANT_INT(m, GIT_DIFF_NORMAL)
    ADD_CONSTANT_INT(m, GIT_DIFF_REVERSE)
    ADD_CONSTANT_INT(m, GIT_DIFF_FORCE_TEXT)
    ADD_CONSTANT_INT(m, GIT_DIFF_IGNORE_WHITESPACE)
    ADD_CONSTANT_INT(m, GIT_DIFF_IGNORE_WHITESPACE_CHANGE)
    ADD_CONSTANT_INT(m, GIT_DIFF_IGNORE_WHITESPACE_EOL)
    ADD_CONSTANT_INT(m, GIT_DIFF_IGNORE_SUBMODULES)
    ADD_CONSTANT_INT(m, GIT_DIFF_PATIENCE)
    ADD_CONSTANT_INT(m, GIT_DIFF_MINIMAL)
    ADD_CONSTANT_INT(m, GIT_DIFF_INCLUDE_IGNORED)
    ADD_CONSTANT_INT(m, GIT_DIFF_INCLUDE_UNTRACKED)
    ADD_CONSTANT_INT(m, GIT_DIFF_INCLUDE_UNMODIFIED)
    ADD_CONSTANT_INT(m, GIT_DIFF_RECURSE_UNTRACKED_DIRS)
    ADD_CONSTANT_INT(m, GIT_DIFF_RECURSE_UNTRACKED_DIRS)
    ADD_CONSTANT_INT(m, GIT_DIFF_DISABLE_PATHSPEC_MATCH)
    ADD_CONSTANT_INT(m, GIT_DIFF_IGNORE_CASE)
    ADD_CONSTANT_INT(m, GIT_DIFF_SHOW_UNTRACKED_CONTENT)
    ADD_CONSTANT_INT(m, GIT_DIFF_SKIP_BINARY_CHECK)
    ADD_CONSTANT_INT(m, GIT_DIFF_INCLUDE_TYPECHANGE)
    ADD_CONSTANT_INT(m, GIT_DIFF_INCLUDE_TYPECHANGE_TREES)
    ADD_CONSTANT_INT(m, GIT_DIFF_RECURSE_IGNORED_DIRS)
    /* Flags for diff find similar */
    /* --find-renames */
    ADD_CONSTANT_INT(m, GIT_DIFF_FIND_RENAMES)
    /* --break-rewrites=N */
    ADD_CONSTANT_INT(m, GIT_DIFF_FIND_RENAMES_FROM_REWRITES)
    /* --find-copies */
    ADD_CONSTANT_INT(m, GIT_DIFF_FIND_COPIES)
    /* --find-copies-harder */
    ADD_CONSTANT_INT(m, GIT_DIFF_FIND_COPIES_FROM_UNMODIFIED)
    /* --break-rewrites=/M */
    ADD_CONSTANT_INT(m, GIT_DIFF_FIND_AND_BREAK_REWRITES)

    /* Config */
    INIT_TYPE(ConfigType, NULL, PyType_GenericNew)
    INIT_TYPE(ConfigIterType, NULL, NULL)
    ADD_TYPE(m, Config)
    ADD_TYPE(m, ConfigIter)

    /* Remotes */
    INIT_TYPE(RemoteType, NULL, NULL)
    INIT_TYPE(RefspecType, NULL, NULL)
    INIT_TYPE(TransferProgressType, NULL, NULL)
    ADD_TYPE(m, Remote)
    ADD_TYPE(m, Refspec)
    ADD_TYPE(m, TransferProgress)
    /* Direction for the refspec */
    ADD_CONSTANT_INT(m, GIT_DIRECTION_FETCH)
    ADD_CONSTANT_INT(m, GIT_DIRECTION_PUSH)

    /* Blame */
    INIT_TYPE(BlameType, NULL, NULL)
    INIT_TYPE(BlameIterType, NULL, NULL)
    INIT_TYPE(BlameHunkType, NULL, NULL)
    ADD_TYPE(m, Blame)
    ADD_TYPE(m, BlameHunk)
    ADD_CONSTANT_INT(m, GIT_BLAME_NORMAL)
    ADD_CONSTANT_INT(m, GIT_BLAME_TRACK_COPIES_SAME_FILE)
    ADD_CONSTANT_INT(m, GIT_BLAME_TRACK_COPIES_SAME_COMMIT_MOVES)
    ADD_CONSTANT_INT(m, GIT_BLAME_TRACK_COPIES_SAME_COMMIT_COPIES)
    ADD_CONSTANT_INT(m, GIT_BLAME_TRACK_COPIES_ANY_COMMIT_COPIES)

    /* Merge */
    INIT_TYPE(MergeResultType, NULL, NULL)
    ADD_TYPE(m, MergeResult)

    /* Global initialization of libgit2 */
    git_threads_init();

    return m;
}


#if PY_MAJOR_VERSION < 3
    PyMODINIT_FUNC
    init_pygit2(void)
    {
        PyObject* m;
        m = Py_InitModule3("_pygit2", module_methods,
                           "Python bindings for libgit2.");
        moduleinit(m);
    }
#else
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
        PyObject* m;
        m = PyModule_Create(&moduledef);
        return moduleinit(m);
    }
#endif
