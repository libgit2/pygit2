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
#include <osdefs.h>
#include <pygit2/error.h>
#include <pygit2/types.h>
#include <pygit2/utils.h>
#include <pygit2/repository.h>
#include <git2.h>

extern PyObject *GitError;

extern PyTypeObject RepositoryType;
extern PyTypeObject ObjectType;
extern PyTypeObject CommitType;
extern PyTypeObject DiffType;
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


PyObject *
init_repository(PyObject *self, PyObject *args)
{
    git_repository *repo;
    Repository *py_repo;
    const char *path;
    unsigned int bare;
    int err;

    if (!PyArg_ParseTuple(args, "sI", &path, &bare))
        return NULL;

    err = git_repository_init(&repo, path, bare);
    if (err < 0)
        return Error_set_str(err, path);

    py_repo = PyObject_GC_New(Repository, &RepositoryType);
    if (py_repo) {
        py_repo->repo = repo;
        py_repo->index = NULL;
        PyObject_GC_Track(py_repo);
        return (PyObject*)py_repo;
    }

    git_repository_free(repo);
    return NULL;
};

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

PyMethodDef module_methods[] = {
    {"init_repository", init_repository, METH_VARARGS,
     "Creates a new Git repository in the given folder."},
    {"discover_repository", discover_repository, METH_VARARGS,
     "Look for a git repository and return its path."},
    {NULL}
};

PyObject*
moduleinit(PyObject* m)
{
    if (m == NULL)
        return NULL;

    GitError = PyErr_NewException("_pygit2.GitError", NULL, NULL);

    RepositoryType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&RepositoryType) < 0)
        return NULL;

    /* Do not set 'tp_new' for Git objects. To create Git objects use the
     * Repository.create_XXX methods */
    if (PyType_Ready(&ObjectType) < 0)
        return NULL;
    CommitType.tp_base = &ObjectType;
    if (PyType_Ready(&CommitType) < 0)
        return NULL;
    TreeType.tp_base = &ObjectType;
    if (PyType_Ready(&TreeType) < 0)
        return NULL;
    BlobType.tp_base = &ObjectType;
    if (PyType_Ready(&BlobType) < 0)
        return NULL;
    TagType.tp_base = &ObjectType;
    if (PyType_Ready(&TagType) < 0)
        return NULL;

    if (PyType_Ready(&DiffType) < 0)
        return NULL;
    if (PyType_Ready(&HunkType) < 0)
        return NULL;

    TreeEntryType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&TreeEntryType) < 0)
        return NULL;
    IndexType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&IndexType) < 0)
        return NULL;
    IndexEntryType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&IndexEntryType) < 0)
        return NULL;
    TreeBuilderType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&TreeBuilderType) < 0)
        return NULL;
    ConfigType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&ConfigType) < 0)
        return NULL;
    WalkerType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&WalkerType) < 0)
        return NULL;
    ReferenceType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&ReferenceType) < 0)
        return NULL;
    if (PyType_Ready(&RefLogEntryType) < 0)
        return NULL;
    SignatureType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&SignatureType) < 0)
        return NULL;

    Py_INCREF(GitError);
    PyModule_AddObject(m, "GitError", GitError);

    Py_INCREF(&RepositoryType);
    PyModule_AddObject(m, "Repository", (PyObject *)&RepositoryType);

    Py_INCREF(&ObjectType);
    PyModule_AddObject(m, "Object", (PyObject *)&ObjectType);

    Py_INCREF(&CommitType);
    PyModule_AddObject(m, "Commit", (PyObject *)&CommitType);

    Py_INCREF(&TreeEntryType);
    PyModule_AddObject(m, "TreeEntry", (PyObject *)&TreeEntryType);

    Py_INCREF(&TreeType);
    PyModule_AddObject(m, "Tree", (PyObject *)&TreeType);

    Py_INCREF(&ConfigType);
    PyModule_AddObject(m, "Config", (PyObject *)&ConfigType);

    Py_INCREF(&BlobType);
    PyModule_AddObject(m, "Blob", (PyObject *)&BlobType);

    Py_INCREF(&TagType);
    PyModule_AddObject(m, "Tag", (PyObject *)&TagType);

    Py_INCREF(&IndexType);
    PyModule_AddObject(m, "Index", (PyObject *)&IndexType);

    Py_INCREF(&IndexEntryType);
    PyModule_AddObject(m, "IndexEntry", (PyObject *)&IndexEntryType);

    Py_INCREF(&ReferenceType);
    PyModule_AddObject(m, "Reference", (PyObject *)&ReferenceType);

    Py_INCREF(&SignatureType);
    PyModule_AddObject(m, "Signature", (PyObject *)&SignatureType);

    PyModule_AddIntConstant(m, "GIT_OBJ_ANY", GIT_OBJ_ANY);
    PyModule_AddIntConstant(m, "GIT_OBJ_COMMIT", GIT_OBJ_COMMIT);
    PyModule_AddIntConstant(m, "GIT_OBJ_TREE", GIT_OBJ_TREE);
    PyModule_AddIntConstant(m, "GIT_OBJ_BLOB", GIT_OBJ_BLOB);
    PyModule_AddIntConstant(m, "GIT_OBJ_TAG", GIT_OBJ_TAG);
    PyModule_AddIntConstant(m, "GIT_SORT_NONE", GIT_SORT_NONE);
    PyModule_AddIntConstant(m, "GIT_SORT_TOPOLOGICAL", GIT_SORT_TOPOLOGICAL);
    PyModule_AddIntConstant(m, "GIT_SORT_TIME", GIT_SORT_TIME);
    PyModule_AddIntConstant(m, "GIT_SORT_REVERSE", GIT_SORT_REVERSE);
    PyModule_AddIntConstant(m, "GIT_REF_OID", GIT_REF_OID);
    PyModule_AddIntConstant(m, "GIT_REF_SYMBOLIC", GIT_REF_SYMBOLIC);
    PyModule_AddIntConstant(m, "GIT_REF_PACKED", GIT_REF_PACKED);

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

    /* Flags for diffed files */
    PyModule_AddIntConstant(m, "GIT_DIFF_FILE_VALID_OID",
                            GIT_DIFF_FILE_VALID_OID);
    PyModule_AddIntConstant(m, "GIT_DIFF_FILE_FREE_PATH",
                            GIT_DIFF_FILE_FREE_PATH);
    PyModule_AddIntConstant(m, "GIT_DIFF_FILE_BINARY", GIT_DIFF_FILE_BINARY);
    PyModule_AddIntConstant(m, "GIT_DIFF_FILE_NOT_BINARY",
                            GIT_DIFF_FILE_NOT_BINARY);
    PyModule_AddIntConstant(m, "GIT_DIFF_FILE_FREE_DATA",
                            GIT_DIFF_FILE_FREE_DATA);
    PyModule_AddIntConstant(m, "GIT_DIFF_FILE_UNMAP_DATA",
                            GIT_DIFF_FILE_UNMAP_DATA);

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
      "_pygit2",                        /* m_name */
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
