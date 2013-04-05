/*
 * Copyright 2010-2013 The pygit2 contributors
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
#include <osdefs.h>
#include <git2.h>
#include "error.h"
#include "types.h"
#include "utils.h"
#include "repository.h"
#include "oid.h"

extern PyObject *GitError;

extern PyTypeObject RepositoryType;
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
extern PyTypeObject ReferenceType;
extern PyTypeObject RefLogIterType;
extern PyTypeObject RefLogEntryType;
extern PyTypeObject SignatureType;
extern PyTypeObject RemoteType;
extern PyTypeObject NoteType;
extern PyTypeObject NoteIterType;



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
  "hashfile(path) -> bytes\n"
  "\n"
  "Returns the oid of a new blob from a file path without actually writing \n"
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

    return git_oid_to_python(oid.id);
}

PyDoc_STRVAR(hash__doc__,
  "hash(data) -> bytes\n"
  "\n"
  "Returns the oid of a new blob from a string without actually writing to \n"
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

    return git_oid_to_python(oid.id);
}


PyMethodDef module_methods[] = {
    {"init_repository", init_repository, METH_VARARGS, init_repository__doc__},
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

    /* Errors */
    GitError = PyErr_NewException("_pygit2.GitError", NULL, NULL);
    Py_INCREF(GitError);
    PyModule_AddObject(m, "GitError", GitError);

    /* Repository */
    INIT_TYPE(RepositoryType, NULL, PyType_GenericNew)
    ADD_TYPE(m, Repository);

    /* Objects (make them with the Repository.create_XXX methods). */
    INIT_TYPE(ObjectType, NULL, NULL)
    INIT_TYPE(CommitType, &ObjectType, NULL)
    INIT_TYPE(SignatureType, NULL, PyType_GenericNew)
    INIT_TYPE(TreeType, &ObjectType, NULL)
    INIT_TYPE(TreeEntryType, NULL, PyType_GenericNew)
    INIT_TYPE(TreeIterType, NULL, NULL)
    INIT_TYPE(TreeBuilderType, NULL, PyType_GenericNew)
    INIT_TYPE(BlobType, &ObjectType, NULL)
    INIT_TYPE(TagType, &ObjectType, NULL)
    ADD_TYPE(m, Object);
    ADD_TYPE(m, Commit);
    ADD_TYPE(m, Signature);
    ADD_TYPE(m, Tree);
    ADD_TYPE(m, TreeEntry);
    ADD_TYPE(m, TreeBuilder);
    ADD_TYPE(m, Blob);
    ADD_TYPE(m, Tag);

    /* References */
    INIT_TYPE(ReferenceType, NULL, PyType_GenericNew)
    INIT_TYPE(RefLogEntryType, NULL, NULL)
    INIT_TYPE(RefLogIterType, NULL, NULL)
    INIT_TYPE(NoteType, NULL, NULL)
    INIT_TYPE(NoteIterType, NULL, NULL)
    ADD_TYPE(m, Reference);
    ADD_TYPE(m, RefLogEntry);
    ADD_TYPE(m, Note);

    /* Index */
    INIT_TYPE(IndexType, NULL, PyType_GenericNew)
    INIT_TYPE(IndexEntryType, NULL, PyType_GenericNew)
    INIT_TYPE(IndexIterType, NULL, NULL)
    ADD_TYPE(m, Index);
    ADD_TYPE(m, IndexEntry);

    /* Diff */
    INIT_TYPE(DiffType, NULL, NULL)
    INIT_TYPE(DiffIterType, NULL, NULL)
    INIT_TYPE(PatchType, NULL, NULL)
    INIT_TYPE(HunkType, NULL, NULL)
    ADD_TYPE(m, Diff);
    ADD_TYPE(m, Patch);
    ADD_TYPE(m, Hunk);

    /* Log */
    INIT_TYPE(WalkerType, NULL, PyType_GenericNew)

    /* Config */
    INIT_TYPE(ConfigType, NULL, PyType_GenericNew)
    ADD_TYPE(m, Config);

    /* Remote */
    INIT_TYPE(RemoteType, NULL, NULL)
    ADD_TYPE(m, Remote);

    /* Constants */
    PyModule_AddIntConstant(m, "GIT_OBJ_ANY", GIT_OBJ_ANY);
    PyModule_AddIntConstant(m, "GIT_OBJ_COMMIT", GIT_OBJ_COMMIT);
    PyModule_AddIntConstant(m, "GIT_OBJ_TREE", GIT_OBJ_TREE);
    PyModule_AddIntConstant(m, "GIT_OBJ_BLOB", GIT_OBJ_BLOB);
    PyModule_AddIntConstant(m, "GIT_OBJ_TAG", GIT_OBJ_TAG);
    PyModule_AddIntConstant(m, "GIT_SORT_NONE", GIT_SORT_NONE);
    PyModule_AddIntConstant(m, "GIT_SORT_TOPOLOGICAL", GIT_SORT_TOPOLOGICAL);
    PyModule_AddIntConstant(m, "GIT_SORT_TIME", GIT_SORT_TIME);
    PyModule_AddIntConstant(m, "GIT_SORT_REVERSE", GIT_SORT_REVERSE);
    PyModule_AddIntConstant(m, "GIT_REF_INVALID", GIT_REF_INVALID);
    PyModule_AddIntConstant(m, "GIT_REF_OID", GIT_REF_OID);
    PyModule_AddIntConstant(m, "GIT_REF_SYMBOLIC", GIT_REF_SYMBOLIC);
    PyModule_AddIntConstant(m, "GIT_REF_LISTALL", GIT_REF_LISTALL);

    /* Git status flags */
    PyModule_AddIntConstant(m, "GIT_STATUS_CURRENT", GIT_STATUS_CURRENT);
    PyModule_AddIntConstant(m, "GIT_STATUS_INDEX_NEW", GIT_STATUS_INDEX_NEW);
    PyModule_AddIntConstant(m, "GIT_STATUS_INDEX_MODIFIED",
                            GIT_STATUS_INDEX_MODIFIED);
    PyModule_AddIntConstant(m, "GIT_STATUS_INDEX_DELETED" ,
                            GIT_STATUS_INDEX_DELETED);
    PyModule_AddIntConstant(m, "GIT_STATUS_WT_NEW", GIT_STATUS_WT_NEW);
    PyModule_AddIntConstant(m, "GIT_STATUS_WT_MODIFIED" ,
                            GIT_STATUS_WT_MODIFIED);
    PyModule_AddIntConstant(m, "GIT_STATUS_WT_DELETED", GIT_STATUS_WT_DELETED);

    /* Flags for ignored files */
    PyModule_AddIntConstant(m, "GIT_STATUS_IGNORED", GIT_STATUS_IGNORED);

    /* Git diff flags */
    PyModule_AddIntConstant(m, "GIT_DIFF_NORMAL", GIT_DIFF_NORMAL);
    PyModule_AddIntConstant(m, "GIT_DIFF_REVERSE", GIT_DIFF_REVERSE);
    PyModule_AddIntConstant(m, "GIT_DIFF_FORCE_TEXT", GIT_DIFF_FORCE_TEXT);
    PyModule_AddIntConstant(m, "GIT_DIFF_IGNORE_WHITESPACE",
                            GIT_DIFF_IGNORE_WHITESPACE);
    PyModule_AddIntConstant(m, "GIT_DIFF_IGNORE_WHITESPACE_CHANGE",
                            GIT_DIFF_IGNORE_WHITESPACE_CHANGE);
    PyModule_AddIntConstant(m, "GIT_DIFF_IGNORE_WHITESPACE_EOL",
                            GIT_DIFF_IGNORE_WHITESPACE_EOL);
    PyModule_AddIntConstant(m, "GIT_DIFF_IGNORE_SUBMODULES",
                            GIT_DIFF_IGNORE_SUBMODULES);
    PyModule_AddIntConstant(m, "GIT_DIFF_PATIENCE", GIT_DIFF_PATIENCE);
    PyModule_AddIntConstant(m, "GIT_DIFF_INCLUDE_IGNORED",
                            GIT_DIFF_INCLUDE_IGNORED);
    PyModule_AddIntConstant(m, "GIT_DIFF_INCLUDE_UNTRACKED",
                            GIT_DIFF_INCLUDE_UNTRACKED);
    PyModule_AddIntConstant(m, "GIT_DIFF_INCLUDE_UNMODIFIED",
                            GIT_DIFF_INCLUDE_UNMODIFIED);
    PyModule_AddIntConstant(m, "GIT_DIFF_RECURSE_UNTRACKED_DIRS",
                            GIT_DIFF_RECURSE_UNTRACKED_DIRS);

    /* Flags for diff find similar */
    /* --find-renames */
    PyModule_AddIntConstant(m, "GIT_DIFF_FIND_RENAMES",
                            GIT_DIFF_FIND_RENAMES);
    /* --break-rewrites=N */
    PyModule_AddIntConstant(m, "GIT_DIFF_FIND_RENAMES_FROM_REWRITES",
                            GIT_DIFF_FIND_RENAMES_FROM_REWRITES);
    /* --find-copies */
    PyModule_AddIntConstant(m, "GIT_DIFF_FIND_COPIES",
                            GIT_DIFF_FIND_COPIES);
    /* --find-copies-harder */
    PyModule_AddIntConstant(m, "GIT_DIFF_FIND_COPIES_FROM_UNMODIFIED",
                            GIT_DIFF_FIND_COPIES_FROM_UNMODIFIED);
    /* --break-rewrites=/M */
    PyModule_AddIntConstant(m, "GIT_DIFF_FIND_AND_BREAK_REWRITES",
                            GIT_DIFF_FIND_AND_BREAK_REWRITES);

    /* Flags for diff deltas */
    PyModule_AddIntConstant(m, "GIT_DELTA_UNMODIFIED", GIT_DELTA_UNMODIFIED);
    PyModule_AddIntConstant(m, "GIT_DELTA_ADDED", GIT_DELTA_ADDED);
    PyModule_AddIntConstant(m, "GIT_DELTA_DELETED", GIT_DELTA_DELETED);
    PyModule_AddIntConstant(m, "GIT_DELTA_MODIFIED", GIT_DELTA_MODIFIED);
    PyModule_AddIntConstant(m, "GIT_DELTA_RENAMED", GIT_DELTA_RENAMED);
    PyModule_AddIntConstant(m, "GIT_DELTA_COPIED", GIT_DELTA_COPIED);
    PyModule_AddIntConstant(m, "GIT_DELTA_IGNORED", GIT_DELTA_IGNORED);
    PyModule_AddIntConstant(m, "GIT_DELTA_UNTRACKED", GIT_DELTA_UNTRACKED);

    /* Flags for diffed lines origin */
    PyModule_AddIntConstant(m, "GIT_DIFF_LINE_CONTEXT", GIT_DIFF_LINE_CONTEXT);
    PyModule_AddIntConstant(m, "GIT_DIFF_LINE_ADDITION",
                            GIT_DIFF_LINE_ADDITION);
    PyModule_AddIntConstant(m, "GIT_DIFF_LINE_DELETION",
                            GIT_DIFF_LINE_DELETION);
    PyModule_AddIntConstant(m, "GIT_DIFF_LINE_ADD_EOFNL",
                            GIT_DIFF_LINE_ADD_EOFNL);
    PyModule_AddIntConstant(m, "GIT_DIFF_LINE_DEL_EOFNL",
                            GIT_DIFF_LINE_DEL_EOFNL);
    PyModule_AddIntConstant(m, "GIT_DIFF_LINE_FILE_HDR",
                            GIT_DIFF_LINE_FILE_HDR);
    PyModule_AddIntConstant(m, "GIT_DIFF_LINE_HUNK_HDR",
                            GIT_DIFF_LINE_HUNK_HDR);
    PyModule_AddIntConstant(m, "GIT_DIFF_LINE_BINARY", GIT_DIFF_LINE_BINARY);

    /* Valid modes for index and tree entries. */
    PyModule_AddIntConstant(m, "GIT_FILEMODE_NEW", GIT_FILEMODE_NEW);
    PyModule_AddIntConstant(m, "GIT_FILEMODE_TREE", GIT_FILEMODE_TREE);
    PyModule_AddIntConstant(m, "GIT_FILEMODE_BLOB", GIT_FILEMODE_BLOB);
    PyModule_AddIntConstant(m, "GIT_FILEMODE_BLOB_EXECUTABLE",
                            GIT_FILEMODE_BLOB_EXECUTABLE);
    PyModule_AddIntConstant(m, "GIT_FILEMODE_LINK", GIT_FILEMODE_LINK);
    PyModule_AddIntConstant(m, "GIT_FILEMODE_COMMIT", GIT_FILEMODE_COMMIT);

    /* libgit2 version info */
    PyModule_AddIntConstant(m, "LIBGIT2_VER_MAJOR", LIBGIT2_VER_MAJOR);
    PyModule_AddIntConstant(m, "LIBGIT2_VER_MINOR", LIBGIT2_VER_MINOR);
    PyModule_AddIntConstant(m, "LIBGIT2_VER_REVISION", LIBGIT2_VER_REVISION);
    PyModule_AddStringConstant(m, "LIBGIT2_VERSION", LIBGIT2_VERSION);

    /* Different checkout strategies */
    PyModule_AddIntConstant(m, "GIT_CHECKOUT_NONE", GIT_CHECKOUT_NONE);
    PyModule_AddIntConstant(m, "GIT_CHECKOUT_SAFE", GIT_CHECKOUT_SAFE);
    PyModule_AddIntConstant(m, "GIT_CHECKOUT_SAFE_CREATE",
                            GIT_CHECKOUT_SAFE_CREATE);
    PyModule_AddIntConstant(m, "GIT_CHECKOUT_FORCE", GIT_CHECKOUT_FORCE);
    PyModule_AddIntConstant(m, "GIT_CHECKOUT_ALLOW_CONFLICTS",
                            GIT_CHECKOUT_ALLOW_CONFLICTS);
    PyModule_AddIntConstant(m, "GIT_CHECKOUT_REMOVE_UNTRACKED",
                            GIT_CHECKOUT_REMOVE_UNTRACKED);
    PyModule_AddIntConstant(m, "GIT_CHECKOUT_REMOVE_IGNORED",
                            GIT_CHECKOUT_REMOVE_IGNORED);
    PyModule_AddIntConstant(m, "GIT_CHECKOUT_UPDATE_ONLY",
                            GIT_CHECKOUT_UPDATE_ONLY);
    PyModule_AddIntConstant(m, "GIT_CHECKOUT_DONT_UPDATE_INDEX",
                            GIT_CHECKOUT_DONT_UPDATE_INDEX);
    PyModule_AddIntConstant(m, "GIT_CHECKOUT_NO_REFRESH",
                            GIT_CHECKOUT_NO_REFRESH);
    PyModule_AddIntConstant(m, "GIT_CHECKOUT_DISABLE_PATHSPEC_MATCH",
                            GIT_CHECKOUT_DISABLE_PATHSPEC_MATCH);

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
