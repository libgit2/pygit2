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
#include "error.h"
#include "types.h"
#include "reference.h"
#include "utils.h"
#include "object.h"
#include "oid.h"
#include "note.h"
#include "repository.h"
#include "remote.h"
#include "branch.h"
#include "blame.h"
#include "mergeresult.h"
#include "signature.h"
#include <git2/odb_backend.h>

extern PyObject *GitError;

extern PyTypeObject IndexType;
extern PyTypeObject WalkerType;
extern PyTypeObject SignatureType;
extern PyTypeObject ObjectType;
extern PyTypeObject OidType;
extern PyTypeObject CommitType;
extern PyTypeObject TreeType;
extern PyTypeObject TreeBuilderType;
extern PyTypeObject ConfigType;
extern PyTypeObject DiffType;
extern PyTypeObject RemoteType;
extern PyTypeObject ReferenceType;
extern PyTypeObject NoteType;
extern PyTypeObject NoteIterType;

git_otype
int_to_loose_object_type(int type_id)
{
    switch((git_otype)type_id) {
        case GIT_OBJ_COMMIT: return GIT_OBJ_COMMIT;
        case GIT_OBJ_TREE: return GIT_OBJ_TREE;
        case GIT_OBJ_BLOB: return GIT_OBJ_BLOB;
        case GIT_OBJ_TAG: return GIT_OBJ_TAG;
        default: return GIT_OBJ_BAD;
    }
}

int
Repository_init(Repository *self, PyObject *args, PyObject *kwds)
{
    char *path;
    int err;

    if (kwds && PyDict_Size(kwds) > 0) {
        PyErr_SetString(PyExc_TypeError,
                        "Repository takes no keyword arguments");
        return -1;
    }

    if (!PyArg_ParseTuple(args, "s", &path))
        return -1;

    err = git_repository_open(&self->repo, path);
    if (err < 0) {
        Error_set_str(err, path);
        return -1;
    }

    self->config = NULL;
    self->index = NULL;

    return 0;
}

void
Repository_dealloc(Repository *self)
{
    PyObject_GC_UnTrack(self);
    Py_CLEAR(self->index);
    Py_CLEAR(self->config);
    git_repository_free(self->repo);
    PyObject_GC_Del(self);
}

int
Repository_traverse(Repository *self, visitproc visit, void *arg)
{
    Py_VISIT(self->index);
    return 0;
}

int
Repository_clear(Repository *self)
{
    Py_CLEAR(self->index);
    return 0;
}

static int
Repository_build_as_iter(const git_oid *oid, void *accum)
{
    int err;
    PyObject *py_oid = git_oid_to_python(oid);

    err = PyList_Append((PyObject*)accum, py_oid);
    Py_DECREF(py_oid);
    return err;
}

PyObject *
Repository_as_iter(Repository *self)
{
    git_odb *odb;
    int err;
    PyObject *accum = PyList_New(0);

    err = git_repository_odb(&odb, self->repo);
    if (err < 0)
        return Error_set(err);

    err = git_odb_foreach(odb, Repository_build_as_iter, (void*)accum);
    git_odb_free(odb);
    if (err == GIT_EUSER)
        return NULL;
    if (err < 0)
        return Error_set(err);

    return PyObject_GetIter(accum);
}


PyDoc_STRVAR(Repository_head__doc__,
  "Current head reference of the repository.");

PyObject *
Repository_head__get__(Repository *self)
{
    git_reference *head;
    int err;

    err = git_repository_head(&head, self->repo);
    if (err < 0) {
        if (err == GIT_ENOTFOUND)
            PyErr_SetString(GitError, "head reference does not exist");
        else
            Error_set(err);

        return NULL;
    }

    return wrap_reference(head, self);
}

int
Repository_head__set__(Repository *self, PyObject *py_refname)
{
    int err;
    const char *refname;
    PyObject *trefname;

    refname = py_str_borrow_c_str(&trefname, py_refname, NULL);
    if (refname == NULL)
        return -1;

    err = git_repository_set_head(self->repo, refname);
    Py_DECREF(trefname);
    if (err < 0) {
        Error_set_str(err, refname);
        return -1;
    }

    return 0;
}


PyDoc_STRVAR(Repository_head_is_detached__doc__,
  "A repository's HEAD is detached when it points directly to a commit\n"
  "instead of a branch.");

PyObject *
Repository_head_is_detached__get__(Repository *self)
{
    if (git_repository_head_detached(self->repo) > 0)
        Py_RETURN_TRUE;

    Py_RETURN_FALSE;
}


PyDoc_STRVAR(Repository_head_is_unborn__doc__,
  "An unborn branch is one named from HEAD but which doesn't exist in the\n"
  "refs namespace, because it doesn't have any commit to point to.");

PyObject *
Repository_head_is_unborn__get__(Repository *self)
{
    if (git_repository_head_unborn(self->repo) > 0)
        Py_RETURN_TRUE;

    Py_RETURN_FALSE;
}


PyDoc_STRVAR(Repository_is_empty__doc__,
  "Check if a repository is empty.");

PyObject *
Repository_is_empty__get__(Repository *self)
{
    if (git_repository_is_empty(self->repo) > 0)
        Py_RETURN_TRUE;

    Py_RETURN_FALSE;
}


PyDoc_STRVAR(Repository_is_bare__doc__,
  "Check if a repository is a bare repository.");

PyObject *
Repository_is_bare__get__(Repository *self)
{
    if (git_repository_is_bare(self->repo) > 0)
        Py_RETURN_TRUE;

    Py_RETURN_FALSE;
}


PyDoc_STRVAR(Repository_git_object_lookup_prefix__doc__,
  "git_object_lookup_prefix(oid) -> Object\n"
  "\n"
  "Returns the Git object with the given oid.");

PyObject *
Repository_git_object_lookup_prefix(Repository *self, PyObject *key)
{
    int err;
    size_t len;
    git_oid oid;
    git_object *obj;

    len = py_oid_to_git_oid(key, &oid);
    if (len == 0)
        return NULL;

    err = git_object_lookup_prefix(&obj, self->repo, &oid, len, GIT_OBJ_ANY);
    if (err == 0)
        return wrap_object(obj, self);

    if (err == GIT_ENOTFOUND)
        Py_RETURN_NONE;

    return Error_set_oid(err, &oid, len);
}


PyDoc_STRVAR(Repository_lookup_branch__doc__,
  "lookup_branch(branch_name, [branch_type]) -> Object\n"
  "\n"
  "Returns the Git reference for the given branch name (local or remote).");

PyObject *
Repository_lookup_branch(Repository *self, PyObject *args)
{
    git_reference *c_reference;
    const char *c_name;
    git_branch_t branch_type = GIT_BRANCH_LOCAL;
    int err;

    if (!PyArg_ParseTuple(args, "s|I", &c_name, &branch_type))
        return NULL;

    err = git_branch_lookup(&c_reference, self->repo, c_name, branch_type);
    if (err == 0)
        return wrap_branch(c_reference, self);

    if (err == GIT_ENOTFOUND)
        Py_RETURN_NONE;

    return Error_set(err);
}


PyDoc_STRVAR(Repository_revparse_single__doc__,
  "revparse_single(revision) -> Object\n"
  "\n"
  "Find an object, as specified by a revision string. See\n"
  "`man gitrevisions`, or the documentation for `git rev-parse` for\n"
  "information on the syntax accepted.");

PyObject *
Repository_revparse_single(Repository *self, PyObject *py_spec)
{
    git_object *c_obj;
    const char *c_spec;
    PyObject *tspec;
    int err;

    /* 1- Get the C revision spec */
    c_spec = py_str_borrow_c_str(&tspec, py_spec, NULL);
    if (c_spec == NULL)
        return NULL;

    /* 2- Lookup */
    err = git_revparse_single(&c_obj, self->repo, c_spec);

    if (err < 0) {
        PyObject *err_obj = Error_set_str(err, c_spec);
	Py_DECREF(tspec);
        return err_obj;
    }
    Py_DECREF(tspec);

    return wrap_object(c_obj, self);
}

git_odb_object *
Repository_read_raw(git_repository *repo, const git_oid *oid, size_t len)
{
    git_odb *odb;
    git_odb_object *obj;
    int err;

    err = git_repository_odb(&odb, repo);
    if (err < 0) {
        Error_set(err);
        return NULL;
    }

    err = git_odb_read_prefix(&obj, odb, oid, (unsigned int)len);
    git_odb_free(odb);
    if (err < 0) {
        Error_set_oid(err, oid, len);
        return NULL;
    }

    return obj;
}


PyDoc_STRVAR(Repository_read__doc__,
  "read(oid) -> type, data, size\n"
  "\n"
  "Read raw object data from the repository.");

PyObject *
Repository_read(Repository *self, PyObject *py_hex)
{
    git_oid oid;
    git_odb_object *obj;
    size_t len;
    PyObject* tuple;

    len = py_oid_to_git_oid(py_hex, &oid);
    if (len == 0)
        return NULL;

    obj = Repository_read_raw(self->repo, &oid, len);
    if (obj == NULL)
        return NULL;

    tuple = Py_BuildValue(
    #if PY_MAJOR_VERSION == 2
        "(ns#)",
    #else
        "(ny#)",
    #endif
        git_odb_object_type(obj),
        git_odb_object_data(obj),
        git_odb_object_size(obj));

    git_odb_object_free(obj);
    return tuple;
}


PyDoc_STRVAR(Repository_write__doc__,
    "write(type, data) -> Oid\n"
    "\n"
    "Write raw object data into the repository. First arg is the object\n"
    "type, the second one a buffer with data. Return the Oid of the created\n"
    "object.");

PyObject *
Repository_write(Repository *self, PyObject *args)
{
    int err;
    git_oid oid;
    git_odb *odb;
    git_odb_stream* stream;
    int type_id;
    const char* buffer;
    Py_ssize_t buflen;
    git_otype type;

    if (!PyArg_ParseTuple(args, "Is#", &type_id, &buffer, &buflen))
        return NULL;

    type = int_to_loose_object_type(type_id);
    if (type == GIT_OBJ_BAD)
        return PyErr_Format(PyExc_ValueError, "%d", type_id);

    err = git_repository_odb(&odb, self->repo);
    if (err < 0)
        return Error_set(err);

    err = git_odb_open_wstream(&stream, odb, buflen, type);
    git_odb_free(odb);
    if (err < 0)
        return Error_set(err);

    err = git_odb_stream_write(stream, buffer, buflen);
    if (err) {
        git_odb_stream_free(stream);
        return Error_set(err);
    }

    err = git_odb_stream_finalize_write(&oid, stream);
    git_odb_stream_free(stream);
    if (err)
        return Error_set(err);

    return git_oid_to_python(&oid);
}


PyDoc_STRVAR(Repository_index__doc__, "Index file.");

PyObject *
Repository_index__get__(Repository *self, void *closure)
{
    int err;
    git_index *index;
    Index *py_index;

    assert(self->repo);

    if (self->index == NULL) {
        err = git_repository_index(&index, self->repo);
        if (err < 0)
            return Error_set(err);

        py_index = PyObject_GC_New(Index, &IndexType);
        if (!py_index) {
            git_index_free(index);
            return NULL;
        }

        Py_INCREF(self);
        py_index->repo = self;
        py_index->index = index;
        PyObject_GC_Track(py_index);
        self->index = (PyObject*)py_index;
    }

    Py_INCREF(self->index);
    return self->index;
}


PyDoc_STRVAR(Repository_path__doc__,
  "The normalized path to the git repository.");

PyObject *
Repository_path__get__(Repository *self, void *closure)
{
    return to_path(git_repository_path(self->repo));
}


PyDoc_STRVAR(Repository_workdir__doc__,
  "The normalized path to the working directory of the repository. If the\n"
  "repository is bare, None will be returned.");

PyObject *
Repository_workdir__get__(Repository *self, void *closure)
{
    const char *c_path;

    c_path = git_repository_workdir(self->repo);
    if (c_path == NULL)
        Py_RETURN_NONE;

    return to_path(c_path);
}


PyDoc_STRVAR(Repository_config__doc__,
  "Get the configuration file for this repository.\n"
  "\n"
  "If a configuration file has not been set, the default config set for the\n"
  "repository will be returned, including global and system configurations\n"
  "(if they are available).");

PyObject *
Repository_config__get__(Repository *self)
{
    int err;
    git_config *config;
    Config *py_config;

    assert(self->repo);

    if (self->config == NULL) {
        err = git_repository_config(&config, self->repo);
        if (err < 0)
            return Error_set(err);

        py_config = PyObject_New(Config, &ConfigType);
        if (py_config == NULL) {
            git_config_free(config);
            return NULL;
        }

        py_config->config = config;
        self->config = (PyObject*)py_config;
        /* We need 2 refs here. One is returned, one is kept internally. */
        Py_INCREF(self->config);
    } else {
        Py_INCREF(self->config);
    }

    return self->config;
}

PyDoc_STRVAR(Repository_merge_base__doc__,
  "merge_base(oid, oid) -> Oid\n"
  "\n"
  "Find as good common ancestors as possible for a merge.");

PyObject *
Repository_merge_base(Repository *self, PyObject *args)
{
    PyObject *value1;
    PyObject *value2;
    git_oid oid;
    git_oid oid1;
    git_oid oid2;
    int err;

    if (!PyArg_ParseTuple(args, "OO", &value1, &value2))
        return NULL;

    err = py_oid_to_git_oid_expand(self->repo, value1, &oid1);
    if (err < 0)
        return NULL;

    err = py_oid_to_git_oid_expand(self->repo, value2, &oid2);
    if (err < 0)
        return NULL;

    err = git_merge_base(&oid, self->repo, &oid1, &oid2);
    if (err < 0)
        return Error_set(err);

    return git_oid_to_python(&oid);
}

PyDoc_STRVAR(Repository_merge__doc__,
  "merge(oid) -> MergeResult\n"
  "\n"
  "Merges the given oid and returns the MergeResult.\n"
  "\n"
  "If the merge is fastforward the MergeResult will contain the new\n"
  "fastforward oid.\n"
  "If the branch is uptodate, nothing to merge, the MergeResult will\n"
  "have the fastforward oid as None.\n"
  "If the merge is not fastforward the MergeResult will have the status\n"
  "produced by the merge, even if there are conflicts.");

PyObject *
Repository_merge(Repository *self, PyObject *py_oid)
{
    git_merge_result *merge_result;
    git_merge_head *oid_merge_head;
    git_oid oid;
    const git_merge_opts default_opts = GIT_MERGE_OPTS_INIT;
    int err;
    size_t len;
    PyObject *py_merge_result;

    len = py_oid_to_git_oid(py_oid, &oid);
    if (len == 0)
        return NULL;

    err = git_merge_head_from_oid(&oid_merge_head, self->repo, &oid);
    if (err < 0)
        return Error_set(err);

    err = git_merge(&merge_result, self->repo,
                    (const git_merge_head **)&oid_merge_head, 1,
                    &default_opts);
    git_merge_head_free(oid_merge_head);
    if (err < 0)
        return Error_set(err);

    py_merge_result = git_merge_result_to_python(merge_result);
    return py_merge_result;
}

PyDoc_STRVAR(Repository_walk__doc__,
  "walk(oid, sort_mode) -> iterator\n"
  "\n"
  "Generator that traverses the history starting from the given commit.\n"
  "The following types of sorting could be used to control traversing\n"
  "direction:\n"
  "\n"
  "* GIT_SORT_NONE. This is the default sorting for new walkers\n"
  "  Sort the repository contents in no particular ordering\n"
  "* GIT_SORT_TOPOLOGICAL. Sort the repository contents in topological order\n"
  "  (parents before children); this sorting mode can be combined with\n"
  "  time sorting.\n"
  "* GIT_SORT_TIME. Sort the repository contents by commit time\n"
  "* GIT_SORT_REVERSE. Iterate through the repository contents in reverse\n"
  "  order; this sorting mode can be combined with any of the above.\n"
  "\n"
  "Example:\n"
  "\n"
  "  >>> from pygit2 import Repository\n"
  "  >>> from pygit2 import GIT_SORT_TOPOLOGICAL, GIT_SORT_REVERSE\n"
  "  >>> repo = Repository('.git')\n"
  "  >>> for commit in repo.walk(repo.head.target, GIT_SORT_TOPOLOGICAL):\n"
  "  ...    print commit.message\n"
  "  >>> for commit in repo.walk(repo.head.target, GIT_SORT_TOPOLOGICAL | GIT_SORT_REVERSE):\n"
  "  ...    print commit.message\n"
  "  >>>\n");

PyObject *
Repository_walk(Repository *self, PyObject *args)
{
    PyObject *value;
    unsigned int sort;
    int err;
    git_oid oid;
    git_revwalk *walk;
    Walker *py_walker;

    if (!PyArg_ParseTuple(args, "OI", &value, &sort))
        return NULL;

    err = git_revwalk_new(&walk, self->repo);
    if (err < 0)
        return Error_set(err);

    /* Sort */
    git_revwalk_sorting(walk, sort);

    /* Push */
    if (value != Py_None) {
        err = py_oid_to_git_oid_expand(self->repo, value, &oid);
        if (err < 0) {
            git_revwalk_free(walk);
            return NULL;
        }

        err = git_revwalk_push(walk, &oid);
        if (err < 0) {
            git_revwalk_free(walk);
            return Error_set(err);
        }
    }

    py_walker = PyObject_New(Walker, &WalkerType);
    if (!py_walker) {
        git_revwalk_free(walk);
        return NULL;
    }

    Py_INCREF(self);
    py_walker->repo = self;
    py_walker->walk = walk;
    return (PyObject*)py_walker;
}


PyDoc_STRVAR(Repository_create_blob__doc__,
    "create_blob(data) -> Oid\n"
    "\n"
    "Create a new blob from a bytes string. The blob is added to the Git\n"
    "object database. Returns the oid of the blob.");

PyObject *
Repository_create_blob(Repository *self, PyObject *args)
{
    git_oid oid;
    const char *raw;
    Py_ssize_t size;
    int err;

    if (!PyArg_ParseTuple(args, "s#", &raw, &size))
        return NULL;

    err = git_blob_create_frombuffer(&oid, self->repo, (const void*)raw, size);
    if (err < 0)
        return Error_set(err);

    return git_oid_to_python(&oid);
}


PyDoc_STRVAR(Repository_create_blob_fromworkdir__doc__,
    "create_blob_fromworkdir(path) -> Oid\n"
    "\n"
    "Create a new blob from a file within the working directory. The given\n"
    "path must be relative to the working directory, if it is not an error\n"
    "is raised.");

PyObject *
Repository_create_blob_fromworkdir(Repository *self, PyObject *args)
{
    git_oid oid;
    const char* path;
    int err;

    if (!PyArg_ParseTuple(args, "s", &path))
        return NULL;

    err = git_blob_create_fromworkdir(&oid, self->repo, path);
    if (err < 0)
        return Error_set(err);

    return git_oid_to_python(&oid);
}


PyDoc_STRVAR(Repository_create_blob_fromdisk__doc__,
    "create_blob_fromdisk(path) -> Oid\n"
    "\n"
    "Create a new blob from a file anywhere (no working directory check).");

PyObject *
Repository_create_blob_fromdisk(Repository *self, PyObject *args)
{
    git_oid oid;
    const char* path;
    int err;

    if (!PyArg_ParseTuple(args, "s", &path))
        return NULL;

    err = git_blob_create_fromdisk(&oid, self->repo, path);
    if (err < 0)
        return Error_set(err);

    return git_oid_to_python(&oid);
}


PyDoc_STRVAR(Repository_create_commit__doc__,
  "create_commit(reference, author, committer, message, tree, parents[, encoding]) -> Oid\n"
  "\n"
  "Create a new commit object, return its oid.");

PyObject *
Repository_create_commit(Repository *self, PyObject *args)
{
    Signature *py_author, *py_committer;
    PyObject *py_oid, *py_message, *py_parents, *py_parent;
    PyObject *py_result = NULL;
    PyObject *tmessage;
    const char *message = NULL;
    char *update_ref = NULL;
    char *encoding = NULL;
    git_oid oid;
    git_tree *tree = NULL;
    int parent_count;
    git_commit **parents = NULL;
    int err = 0, i = 0;
    size_t len;

    if (!PyArg_ParseTuple(args, "zO!O!OOO!|s",
                          &update_ref,
                          &SignatureType, &py_author,
                          &SignatureType, &py_committer,
                          &py_message,
                          &py_oid,
                          &PyList_Type, &py_parents,
                          &encoding))
        return NULL;

    len = py_oid_to_git_oid(py_oid, &oid);
    if (len == 0)
        goto out;

    message = py_str_borrow_c_str(&tmessage, py_message, encoding);
    if (message == NULL)
        goto out;

    err = git_tree_lookup_prefix(&tree, self->repo, &oid, len);
    if (err < 0) {
        Error_set(err);
        goto out;
    }

    parent_count = (int)PyList_Size(py_parents);
    parents = malloc(parent_count * sizeof(git_commit*));
    if (parents == NULL) {
        PyErr_SetNone(PyExc_MemoryError);
        goto out;
    }
    for (; i < parent_count; i++) {
        py_parent = PyList_GET_ITEM(py_parents, i);
        len = py_oid_to_git_oid(py_parent, &oid);
        if (len == 0)
            goto out;
        err = git_commit_lookup_prefix(&parents[i], self->repo, &oid, len);
        if (err < 0) {
            Error_set(err);
            goto out;
        }
    }

    err = git_commit_create(&oid, self->repo, update_ref,
                            py_author->signature, py_committer->signature,
                            encoding, message, tree, parent_count,
                            (const git_commit**)parents);
    if (err < 0) {
        Error_set(err);
        goto out;
    }

    py_result = git_oid_to_python(&oid);

out:
    Py_DECREF(tmessage);
    git_tree_free(tree);
    while (i > 0) {
        i--;
        git_commit_free(parents[i]);
    }
    free(parents);
    return py_result;
}


PyDoc_STRVAR(Repository_create_tag__doc__,
  "create_tag(name, oid, type, tagger, message) -> Oid\n"
  "\n"
  "Create a new tag object, return its oid.");

PyObject *
Repository_create_tag(Repository *self, PyObject *args)
{
    PyObject *py_oid;
    Signature *py_tagger;
    char *tag_name, *message;
    git_oid oid;
    git_object *target = NULL;
    int err, target_type;
    size_t len;

    if (!PyArg_ParseTuple(args, "sOiO!s",
                          &tag_name,
                          &py_oid,
                          &target_type,
                          &SignatureType, &py_tagger,
                          &message))
        return NULL;

    len = py_oid_to_git_oid(py_oid, &oid);
    if (len == 0)
        return NULL;

    err = git_object_lookup_prefix(&target, self->repo, &oid, len,
                                   target_type);
    err = err < 0 ? err : git_tag_create(&oid, self->repo, tag_name, target,
                         py_tagger->signature, message, 0);
    git_object_free(target);
    if (err < 0)
        return Error_set_oid(err, &oid, len);
    return git_oid_to_python(&oid);
}


PyDoc_STRVAR(Repository_create_branch__doc__,
  "create_branch(name, commit, force=False) -> bytes\n"
  "\n"
  "Create a new branch \"name\" which points to a commit.\n"
  "\n"
  "Arguments:\n"
  "\n"
  "force\n"
  "    If True branches will be overridden, otherwise (the default) an\n"
  "    exception is raised.\n"
  "\n"
  "Examples::\n"
  "\n"
  "    repo.create_branch('foo', repo.head.hex, force=False)");

PyObject *
Repository_create_branch(Repository *self, PyObject *args)
{
    Commit *py_commit;
    git_reference *c_reference;
    char *c_name;
    int err, force = 0;

    if (!PyArg_ParseTuple(args, "sO!|i", &c_name, &CommitType, &py_commit, &force))
        return NULL;

    err = git_branch_create(&c_reference, self->repo, c_name, py_commit->commit, force);
    if (err < 0)
        return Error_set(err);

    return wrap_branch(c_reference, self);
}


PyDoc_STRVAR(Repository_listall_references__doc__,
  "listall_references() -> [str, ...]\n"
  "\n"
  "Return a list with all the references in the repository.");

PyObject *
Repository_listall_references(Repository *self, PyObject *args)
{
    git_strarray c_result;
    PyObject *py_result, *py_string;
    unsigned index;
    int err;

    /* Get the C result */
    err = git_reference_list(&c_result, self->repo);
    if (err < 0)
        return Error_set(err);

    /* Create a new PyTuple */
    py_result = PyList_New(c_result.count);
    if (py_result == NULL)
        goto out;

    /* Fill it */
    for (index=0; index < c_result.count; index++) {
        py_string = to_path(c_result.strings[index]);
        if (py_string == NULL) {
            Py_CLEAR(py_result);
            goto out;
        }
        PyList_SET_ITEM(py_result, index, py_string);
    }

out:
    git_strarray_free(&c_result);
    return py_result;
}


PyDoc_STRVAR(Repository_listall_branches__doc__,
  "listall_branches([flags]) -> [str, ...]\n"
  "\n"
  "Return a tuple with all the branches in the repository.");

PyObject *
Repository_listall_branches(Repository *self, PyObject *args)
{
    git_branch_t list_flags = GIT_BRANCH_LOCAL;
    git_branch_iterator *iter;
    git_reference *ref = NULL;
    int err;
    git_branch_t type;
    PyObject *list;

    /* 1- Get list_flags */
    if (!PyArg_ParseTuple(args, "|I", &list_flags))
        return NULL;

    list = PyList_New(0);
    if (list == NULL)
        return NULL;

    if ((err = git_branch_iterator_new(&iter, self->repo, list_flags)) < 0)
        return Error_set(err);

    while ((err = git_branch_next(&ref, &type, iter)) == 0) {
        PyObject *py_branch_name = to_path(git_reference_shorthand(ref));
        git_reference_free(ref);

        if (py_branch_name == NULL)
            goto error;

        err = PyList_Append(list, py_branch_name);
        Py_DECREF(py_branch_name);

        if (err < 0)
            goto error;
    }

    git_branch_iterator_free(iter);
    if (err == GIT_ITEROVER)
        err = 0;

    if (err < 0) {
        Py_CLEAR(list);
        return Error_set(err);
    }

    return list;

error:
    git_branch_iterator_free(iter);
    Py_CLEAR(list);
    return NULL;
}


PyDoc_STRVAR(Repository_lookup_reference__doc__,
  "lookup_reference(name) -> Reference\n"
  "\n"
  "Lookup a reference by its name in a repository.");

PyObject *
Repository_lookup_reference(Repository *self, PyObject *py_name)
{
    git_reference *c_reference;
    char *c_name;
    int err;

    /* 1- Get the C name */
    c_name = py_path_to_c_str(py_name);
    if (c_name == NULL)
        return NULL;

    /* 2- Lookup */
    err = git_reference_lookup(&c_reference, self->repo, c_name);
    if (err < 0) {
        PyObject *err_obj = Error_set_str(err, c_name);
	free(c_name);
        return err_obj;
    }
    free(c_name);

    /* 3- Make an instance of Reference and return it */
    return wrap_reference(c_reference, self);
}

PyDoc_STRVAR(Repository_create_reference_direct__doc__,
  "git_reference_create(name, target, force) -> Reference\n"
  "\n"
  "Create a new reference \"name\" which points to an object.\n"
  "\n"
  "Arguments:\n"
  "\n"
  "force\n"
  "    If True references will be overridden, otherwise (the default) an\n"
  "    exception is raised.\n"
  "\n"
  "Examples::\n"
  "\n"
  "    repo.git_reference_create('refs/heads/foo', repo.head.hex, False)");

PyObject *
Repository_create_reference_direct(Repository *self,  PyObject *args,
                                   PyObject *kw)
{
    PyObject *py_obj;
    git_reference *c_reference;
    char *c_name;
    git_oid oid;
    int err, force;

    if (!PyArg_ParseTuple(args, "sOi", &c_name, &py_obj, &force))
        return NULL;

    err = py_oid_to_git_oid_expand(self->repo, py_obj, &oid);
    if (err < 0)
        return NULL;

    err = git_reference_create(&c_reference, self->repo, c_name, &oid, force);
    if (err < 0)
        return Error_set(err);

    return wrap_reference(c_reference, self);
}

PyDoc_STRVAR(Repository_create_reference_symbolic__doc__,
  "git_reference_symbolic_create(name, source, force) -> Reference\n"
  "\n"
  "Create a new reference \"name\" which points to another reference.\n"
  "\n"
  "Arguments:\n"
  "\n"
  "force\n"
  "    If True references will be overridden, otherwise (the default) an\n"
  "    exception is raised.\n"
  "\n"
  "Examples::\n"
  "\n"
  "    repo.git_reference_symbolic_create('refs/tags/foo', 'refs/heads/master', False)");

PyObject *
Repository_create_reference_symbolic(Repository *self,  PyObject *args,
                                     PyObject *kw)
{
    git_reference *c_reference;
    char *c_name, *c_target;
    int err, force;

    if (!PyArg_ParseTuple(args, "ssi", &c_name, &c_target, &force))
        return NULL;

    err = git_reference_symbolic_create(&c_reference, self->repo, c_name,
                                        c_target, force);
    if (err < 0)
        return Error_set(err);

    return wrap_reference(c_reference, self);
}


PyDoc_STRVAR(Repository_status__doc__,
  "status() -> {str: int}\n"
  "\n"
  "Reads the status of the repository and returns a dictionary with file\n"
  "paths as keys and status flags as values. See pygit2.GIT_STATUS_*.");

PyObject *
Repository_status(Repository *self)
{
    PyObject *dict;
    int err;
    size_t len, i;
    git_status_list *list;

    dict = PyDict_New();
    if (dict == NULL)
        return NULL;

    err = git_status_list_new(&list, self->repo, NULL);
    if (err < 0)
        return Error_set(err);

    len = git_status_list_entrycount(list);
    for (i = 0; i < len; i++) {
        const git_status_entry *entry;
        const char *path;
        PyObject *status;

        entry = git_status_byindex(list, i);
        if (entry == NULL)
            goto error;

        /* We need to choose one of the strings */
        if (entry->head_to_index)
            path = entry->head_to_index->old_file.path;
        else
            path = entry->index_to_workdir->old_file.path;
        status = PyLong_FromLong((long) entry->status);

        err = PyDict_SetItemString(dict, path, status);
        Py_CLEAR(status);

        if (err < 0)
            goto error;

    }

    git_status_list_free(list);
    return dict;

error:
    git_status_list_free(list);
    Py_CLEAR(dict);
    return NULL;
}


PyDoc_STRVAR(Repository_status_file__doc__,
  "status_file(path) -> int\n"
  "\n"
  "Returns the status of the given file path.");

PyObject *
Repository_status_file(Repository *self, PyObject *value)
{
    char *path;
    unsigned int status;
    int err;

    path = py_path_to_c_str(value);
    if (!path)
        return NULL;

    err = git_status_file(&status, self->repo, path);
    if (err < 0) {
        PyObject *err_obj =  Error_set_str(err, path);
        free(path);
        return err_obj;
    }
    return PyLong_FromLong(status);
}


PyDoc_STRVAR(Repository_TreeBuilder__doc__,
  "TreeBuilder([tree]) -> TreeBuilder\n"
  "\n"
  "Create a TreeBuilder object for this repository.");

PyObject *
Repository_TreeBuilder(Repository *self, PyObject *args)
{
    TreeBuilder *builder;
    git_treebuilder *bld;
    PyObject *py_src = NULL;
    git_oid oid;
    git_tree *tree = NULL;
    git_tree *must_free = NULL;
    int err;

    if (!PyArg_ParseTuple(args, "|O", &py_src))
        return NULL;

    if (py_src) {
        if (PyObject_TypeCheck(py_src, &TreeType)) {
            Tree *py_tree = (Tree *)py_src;
            if (py_tree->repo->repo != self->repo) {
                /* return Error_set(GIT_EINVALIDARGS); */
                return Error_set(GIT_ERROR);
            }
            tree = py_tree->tree;
        } else {
            err = py_oid_to_git_oid_expand(self->repo, py_src, &oid);
            if (err < 0)
                return NULL;

            err = git_tree_lookup(&tree, self->repo, &oid);
            if (err < 0)
                return Error_set(err);
            must_free = tree;
        }
    }

    err = git_treebuilder_create(&bld, tree);
    if (must_free != NULL)
        git_tree_free(must_free);

    if (err < 0)
        return Error_set(err);

    builder = PyObject_New(TreeBuilder, &TreeBuilderType);
    if (builder) {
        builder->repo = self;
        builder->bld = bld;
        Py_INCREF(self);
    }

    return (PyObject*)builder;
}


PyDoc_STRVAR(Repository_create_remote__doc__,
  "create_remote(name, url) -> Remote\n"
  "\n"
  "Creates a new remote.");

PyObject *
Repository_create_remote(Repository *self, PyObject *args)
{
    git_remote *remote;
    char *name = NULL, *url = NULL;
    int err;

    if (!PyArg_ParseTuple(args, "ss", &name, &url))
        return NULL;

    err = git_remote_create(&remote, self->repo, name, url);
    if (err < 0)
        return Error_set(err);

    return (PyObject*) wrap_remote(remote, self);
}


PyDoc_STRVAR(Repository_remotes__doc__, "Returns all configured remotes.");

PyObject *
Repository_remotes__get__(Repository *self)
{
    git_strarray remotes;
    git_remote *remote = NULL;
    PyObject *py_list = NULL;
    PyObject *py_remote = NULL;
    size_t i;
    int err;

    git_remote_list(&remotes, self->repo);

    py_list = PyList_New(remotes.count);
    for (i=0; i < remotes.count; ++i) {
        err = git_remote_load(&remote, self->repo, remotes.strings[i]);
        if (err < 0)
            goto cleanup;
        py_remote = wrap_remote(remote, self);
        if (py_remote == NULL)
            goto cleanup;
        PyList_SetItem(py_list, i, py_remote);
    }

    git_strarray_free(&remotes);
    return (PyObject*) py_list;

cleanup:
    git_strarray_free(&remotes);
    if (py_list)
        Py_DECREF(py_list);
    if (err < 0)
        return Error_set(err);
    return NULL;
}

PyDoc_STRVAR(Repository_default_signature__doc__, "Return the signature according to the repository's configuration");

PyObject *
Repository_default_signature__get__(Repository *self)
{
    git_signature *sig;
    int err;

    if ((err = git_signature_default(&sig, self->repo)) < 0)
        return Error_set(err);

    return build_signature((Object*) self, sig, "utf-8");
}

PyDoc_STRVAR(Repository_checkout_head__doc__,
    "checkout_head(strategy)\n"
    "\n"
    "Checkout the head using the given strategy.");

PyObject *
Repository_checkout_head(Repository *self, PyObject *args)
{
    git_checkout_opts opts = GIT_CHECKOUT_OPTS_INIT;
    unsigned int strategy;
    int err;

    if (!PyArg_ParseTuple(args, "I", &strategy))
        return NULL;

    opts.checkout_strategy = strategy;
    err = git_checkout_head(self->repo, &opts);
    if (err < 0)
        return Error_set(err);

    Py_RETURN_NONE;
}


PyDoc_STRVAR(Repository_checkout_index__doc__,
    "checkout_index(strategy)\n"
    "\n"
    "Checkout the index using the given strategy.");

PyObject *
Repository_checkout_index(Repository *self, PyObject *args)
{
    git_checkout_opts opts = GIT_CHECKOUT_OPTS_INIT;
    unsigned int strategy;
    int err;

    if (!PyArg_ParseTuple(args, "I", &strategy))
        return NULL;

    opts.checkout_strategy = strategy;
    err = git_checkout_index(self->repo, NULL, &opts);
    if (err < 0)
        return Error_set(err);

    Py_RETURN_NONE;
}


PyDoc_STRVAR(Repository_checkout_tree__doc__,
    "checkout_tree(treeish, strategy)\n"
    "\n"
    "Checkout the given tree, commit or tag, using the given strategy.");

PyObject *
Repository_checkout_tree(Repository *self, PyObject *args)
{
    git_checkout_opts opts = GIT_CHECKOUT_OPTS_INIT;
    unsigned int strategy;
    Object *py_object;
    int err;

    if (!PyArg_ParseTuple(args, "O!I", &ObjectType, &py_object, &strategy))
        return NULL;

    opts.checkout_strategy = strategy;
    err = git_checkout_tree(self->repo, py_object->obj, &opts);
    if (err < 0)
        return Error_set(err);

    Py_RETURN_NONE;
}


PyDoc_STRVAR(Repository_notes__doc__, "");

PyObject *
Repository_notes(Repository *self, PyObject *args)
{
    NoteIter *iter = NULL;
    char *ref = "refs/notes/commits";
    int err = GIT_ERROR;

    if (!PyArg_ParseTuple(args, "|s", &ref))
        return NULL;

    iter = PyObject_New(NoteIter, &NoteIterType);
    if (iter != NULL) {
        iter->repo = self;
        iter->ref = ref;

        err = git_note_iterator_new(&iter->iter, self->repo, iter->ref);
        if (err == GIT_OK) {
            Py_INCREF(self);
            return (PyObject*)iter;
        }
    }

    return Error_set(err);
}


PyDoc_STRVAR(Repository_create_note__doc__,
  "create_note(message, author, committer, annotated_id [,ref, force]) -> Oid\n"
  "\n"
  "Create a new note for an object, return its SHA-ID."
  "If no ref is given 'refs/notes/commits' will be used.");

PyObject *
Repository_create_note(Repository *self, PyObject* args)
{
    git_oid note_id, annotated_id;
    char *annotated = NULL, *message = NULL, *ref = "refs/notes/commits";
    int err = GIT_ERROR;
    unsigned int force = 0;
    Signature *py_author, *py_committer;

    if (!PyArg_ParseTuple(args, "sO!O!s|si",
                          &message,
                          &SignatureType, &py_author,
                          &SignatureType, &py_committer,
                          &annotated, &ref, &force))
        return NULL;

    err = git_oid_fromstr(&annotated_id, annotated);
    if (err < 0)
        return Error_set(err);

    err = git_note_create(&note_id, self->repo, py_author->signature,
                          py_committer->signature, ref,
                          &annotated_id, message, force);
    if (err < 0)
        return Error_set(err);

    return git_oid_to_python(&note_id);
}


PyDoc_STRVAR(Repository_lookup_note__doc__,
  "lookup_note(annotated_id [, ref]) -> Note\n"
  "\n"
  "Lookup a note for an annotated object in a repository.");

PyObject *
Repository_lookup_note(Repository *self, PyObject* args)
{
    git_oid annotated_id;
    char* annotated = NULL, *ref = "refs/notes/commits";
    int err;

    if (!PyArg_ParseTuple(args, "s|s", &annotated, &ref))
        return NULL;

    err = git_oid_fromstr(&annotated_id, annotated);
    if (err < 0)
        return Error_set(err);

    return (PyObject*) wrap_note(self, &annotated_id, ref);
}

PyDoc_STRVAR(Repository_blame__doc__,
  "blame(path, [flags, min_match_characters, newest_commit, oldest_commit,\n"
  "             min_line, max_line]) -> blame\n"
  "\n"
  "Get the blame for a single file.\n"
  "\n"
  "Arguments:\n"
  "\n"
  "path\n"
  "    A path to file to consider.\n"
  "flags\n"
  "    A GIT_BLAME_* constant.\n"
  "min_match_characters\n"
  "    The number of alphanum chars that must be detected as moving/copying\n"
  "    within a file for it to associate those lines with the parent commit.\n"
  "newest_commit\n"
  "    The id of the newest commit to consider.\n"
  "oldest_commit\n"
  "    The id of the oldest commit to consider.\n"
  "min_line\n"
  "    The first line in the file to blame.\n"
  "max_line\n"
  "    The last line in the file to blame.\n"
  "\n"
  "Examples::\n"
  "\n"
  "    repo.blame('foo.c', flags=GIT_BLAME_TRACK_COPIES_SAME_FILE)");

PyObject *
Repository_blame(Repository *self, PyObject *args, PyObject *kwds)
{
    git_blame_options opts = GIT_BLAME_OPTIONS_INIT;
    git_blame *blame;
    char *path;
    PyObject *value1 = NULL;
    PyObject *value2 = NULL;
    int err;
    char *keywords[] = {"path", "flags", "min_match_characters", "newest_commit",
                        "oldest_commit", "min_line", "max_line", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "s|IHO!O!II", keywords,
                                     &path, &opts.flags,
                                     &opts.min_match_characters,
                                     &OidType, &value1,
                                     &OidType, &value2,
                                     &opts.min_line, &opts.max_line))
        return NULL;

    if (value1) {
        err = py_oid_to_git_oid_expand(self->repo, value1, &opts.newest_commit);
        if (err < 0)
            return NULL;
    }
    if (value2) {
        err = py_oid_to_git_oid_expand(self->repo, value2, &opts.oldest_commit);
        if (err < 0)
            return NULL;
    }

    err = git_blame_file(&blame, self->repo, path, &opts);
    if (err < 0)
        return Error_set(err);

    return wrap_blame(blame, self);
}

PyDoc_STRVAR(Repository_reset__doc__,
    "reset(oid, reset_type)\n"
    "\n"
    "Resets current head to the provided oid.\n"
    "reset_type:\n"
    "GIT_RESET_SOFT: resets head to point to oid, but does not modfy working copy, and leaves the changes in the index.\n"
    "GIT_RESET_MIXED: resets head to point to oid, but does not modfy working copy. It empties the index too.\n"
    "GIT_RESET_HARD: resets head to point to oid, and resets too the working copy and the content of the index.\n");

PyObject *
Repository_reset(Repository *self, PyObject* args)
{
    PyObject *py_oid;
    git_oid oid;
    git_object *target = NULL;
    int err, reset_type;
    size_t len;

    if (!PyArg_ParseTuple(args, "Oi",
                          &py_oid,
                          &reset_type
                          ))
        return NULL;

    len = py_oid_to_git_oid(py_oid, &oid);
    if (len == 0)
        return NULL;

    err = git_object_lookup_prefix(&target, self->repo, &oid, len,
                                   GIT_OBJ_ANY);
    err = err < 0 ? err : git_reset(self->repo, target, reset_type);
    git_object_free(target);
    if (err < 0)
        return Error_set_oid(err, &oid, len);
    Py_RETURN_NONE;
}

PyMethodDef Repository_methods[] = {
    METHOD(Repository, create_blob, METH_VARARGS),
    METHOD(Repository, create_blob_fromworkdir, METH_VARARGS),
    METHOD(Repository, create_blob_fromdisk, METH_VARARGS),
    METHOD(Repository, create_commit, METH_VARARGS),
    METHOD(Repository, create_tag, METH_VARARGS),
    METHOD(Repository, TreeBuilder, METH_VARARGS),
    METHOD(Repository, walk, METH_VARARGS),
    METHOD(Repository, merge_base, METH_VARARGS),
    METHOD(Repository, merge, METH_O),
    METHOD(Repository, read, METH_O),
    METHOD(Repository, write, METH_VARARGS),
    METHOD(Repository, create_reference_direct, METH_VARARGS),
    METHOD(Repository, create_reference_symbolic, METH_VARARGS),
    METHOD(Repository, listall_references, METH_NOARGS),
    METHOD(Repository, lookup_reference, METH_O),
    METHOD(Repository, revparse_single, METH_O),
    METHOD(Repository, status, METH_NOARGS),
    METHOD(Repository, status_file, METH_O),
    METHOD(Repository, create_remote, METH_VARARGS),
    METHOD(Repository, checkout_head, METH_VARARGS),
    METHOD(Repository, checkout_index, METH_VARARGS),
    METHOD(Repository, checkout_tree, METH_VARARGS),
    METHOD(Repository, notes, METH_VARARGS),
    METHOD(Repository, create_note, METH_VARARGS),
    METHOD(Repository, lookup_note, METH_VARARGS),
    METHOD(Repository, git_object_lookup_prefix, METH_O),
    METHOD(Repository, lookup_branch, METH_VARARGS),
    METHOD(Repository, listall_branches, METH_VARARGS),
    METHOD(Repository, create_branch, METH_VARARGS),
    METHOD(Repository, blame, METH_VARARGS | METH_KEYWORDS),
    METHOD(Repository, reset, METH_VARARGS),
    {NULL}
};

PyGetSetDef Repository_getseters[] = {
    GETTER(Repository, index),
    GETTER(Repository, path),
    GETSET(Repository, head),
    GETTER(Repository, head_is_detached),
    GETTER(Repository, head_is_unborn),
    GETTER(Repository, is_empty),
    GETTER(Repository, is_bare),
    GETTER(Repository, config),
    GETTER(Repository, workdir),
    GETTER(Repository, remotes),
    GETTER(Repository, default_signature),
    {NULL}
};


PyDoc_STRVAR(Repository__doc__,
  "Repository(path) -> Repository\n"
  "\n"
  "Git repository.");

PyTypeObject RepositoryType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.Repository",                      /* tp_name           */
    sizeof(Repository),                        /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)Repository_dealloc,            /* tp_dealloc        */
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
    Py_TPFLAGS_DEFAULT |
    Py_TPFLAGS_BASETYPE |
    Py_TPFLAGS_HAVE_GC,                        /* tp_flags          */
    Repository__doc__,                         /* tp_doc            */
    (traverseproc)Repository_traverse,         /* tp_traverse       */
    (inquiry)Repository_clear,                 /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    (getiterfunc)Repository_as_iter,           /* tp_iter           */
    0,                                         /* tp_iternext       */
    Repository_methods,                        /* tp_methods        */
    0,                                         /* tp_members        */
    Repository_getseters,                      /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    (initproc)Repository_init,                 /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};
