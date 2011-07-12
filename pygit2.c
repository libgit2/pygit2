/*
 * Copyright 2010 Google, Inc.
 * Copyright 2011 Itaapy
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

#include <Python.h>
#include <git2.h>

/* Define PyVarObject_HEAD_INIT for Python 2.5 */
#ifndef PyVarObject_HEAD_INIT
#define PyVarObject_HEAD_INIT(type, size) \
    PyObject_HEAD_INIT(type) size,
#endif


typedef struct {
    PyObject_HEAD
    git_repository *repo;
    PyObject *index; /* It will be None for a bare repository */
} Repository;

/* The structs for some of the object subtypes are identical except for the
 * type of their object pointers. */
#define OBJECT_STRUCT(_name, _ptr_type, _ptr_name) \
        typedef struct {\
            PyObject_HEAD\
            Repository *repo;\
            _ptr_type *_ptr_name;\
        } _name;

OBJECT_STRUCT(Object, git_object, obj)
OBJECT_STRUCT(Commit, git_commit, commit)
OBJECT_STRUCT(Tree, git_tree, tree)
OBJECT_STRUCT(Blob, git_blob, blob)
OBJECT_STRUCT(Walker, git_revwalk, walk)

typedef struct {
    PyObject_HEAD
    Repository *repo;
    git_tag *tag;
    PyObject *target;
} Tag;

typedef struct {
    PyObject_HEAD
    const git_tree_entry *entry;
    Tree *tree;
} TreeEntry;

typedef struct {
    PyObject_HEAD
    Repository *repo;
    git_index *index;
    int own_obj:1;
} Index;

typedef struct {
  PyObject_HEAD
  Index *owner;
  int i;
} IndexIter;

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
    git_reference *reference;
} Reference;

static PyTypeObject RepositoryType;
static PyTypeObject ObjectType;
static PyTypeObject CommitType;
static PyTypeObject TreeEntryType;
static PyTypeObject TreeType;
static PyTypeObject BlobType;
static PyTypeObject TagType;
static PyTypeObject IndexType;
static PyTypeObject TreeIterType;
static PyTypeObject IndexIterType;
static PyTypeObject IndexEntryType;
static PyTypeObject WalkerType;
static PyTypeObject ReferenceType;

static PyObject *GitError;

static PyObject *
Error_type(int err) {
    switch (err) {
        case GIT_ENOTFOUND:
            return PyExc_KeyError;
        case GIT_EOSERR:
            return PyExc_OSError;
        case GIT_ENOTOID:
            return PyExc_ValueError;
        case GIT_ENOMEM:
            return PyExc_MemoryError;
        case GIT_EREVWALKOVER:
            return PyExc_StopIteration;
        default:
            return GitError;
    }
}

static PyObject *
Error_set(int err) {
    assert(err < 0);
    if (err == GIT_ENOTFOUND) {
        /* KeyError expects the arg to be the missing key. If the caller called
         * this instead of Error_set_py_obj, it means we don't know the key, but
         * nor should we use git_lasterror. */
        PyErr_SetNone(PyExc_KeyError);
        return NULL;
    } else if (err == GIT_EOSERR) {
        PyErr_SetFromErrno(GitError);
        return NULL;
    }
    PyErr_SetString(Error_type(err), git_lasterror());
    return NULL;
}

static PyObject *
Error_set_str(int err, const char *str) {
    if (err == GIT_ENOTFOUND) {
        /* KeyError expects the arg to be the missing key. */
        PyErr_Format(PyExc_KeyError, "%s", str);
        return NULL;
    }
    PyErr_Format(Error_type(err), "%s: %s", str, git_lasterror());
    return NULL;
}

static PyObject *
Error_set_py_obj(int err, PyObject *py_obj) {
    PyObject *py_str;
    char *str;

    assert(err < 0);

    if (err == GIT_ENOTOID && !PyString_Check(py_obj)) {
        PyErr_Format(PyExc_TypeError, "Git object id must be str, not %.200s",
                     py_obj->ob_type->tp_name);
        return NULL;
    } else if (err == GIT_ENOTFOUND) {
        /* KeyError expects the arg to be the missing key. */
        PyErr_SetObject(PyExc_KeyError, py_obj);
        return NULL;
    }
    py_str = PyObject_Str(py_obj);
    str = py_str ? PyString_AS_STRING(py_str) : "<error in __str__>";
    PyErr_Format(Error_type(err), "%s: %s", str, git_lasterror());
    Py_XDECREF(py_str);
    return NULL;
}

static PyObject *
lookup_object(Repository *repo, const git_oid *oid, git_otype type) {
    int err;
    char hex[GIT_OID_HEXSZ + 1];
    git_object *obj;
    Object *py_obj = NULL;

    err = git_object_lookup(&obj, repo->repo, oid, type);
    if (err < 0) {
        git_oid_fmt(hex, oid);
        hex[GIT_OID_HEXSZ] = '\0';
        return Error_set_str(err, hex);
    }

    switch (git_object_type(obj)) {
        case GIT_OBJ_COMMIT:
            py_obj = (Object*)CommitType.tp_alloc(&CommitType, 0);
            break;
        case GIT_OBJ_TREE:
            py_obj = (Object*)TreeType.tp_alloc(&TreeType, 0);
            break;
        case GIT_OBJ_BLOB:
            py_obj = (Object*)BlobType.tp_alloc(&BlobType, 0);
            break;
        case GIT_OBJ_TAG:
            py_obj = (Object*)TagType.tp_alloc(&TagType, 0);
            break;
        default:
            assert(0);
    }
    if (!py_obj)
        return PyErr_NoMemory();

    py_obj->obj = obj;
    py_obj->repo = repo;
    Py_INCREF(repo);
    return (PyObject*)py_obj;
}

static PyObject *
wrap_reference(git_reference * c_reference)
{
    Reference *py_reference=NULL;

    py_reference = (Reference *)ReferenceType.tp_alloc(&ReferenceType, 0);
    if (py_reference == NULL)
        return NULL;
    py_reference->reference = c_reference;
    return (PyObject *)py_reference;
}

static int
py_str_to_git_oid(PyObject *py_str, git_oid *oid) {
    const char *hex_or_bin;
    int err;

    hex_or_bin = PyString_AsString(py_str);
    if (hex_or_bin == NULL) {
        Error_set_py_obj(GIT_ENOTOID, py_str);
        return 0;
    }

    if (PyString_Size(py_str) == 20) {
        git_oid_fromraw(oid, (const unsigned char*)hex_or_bin);
        err = 0;
    } else {
        err = git_oid_fromstr(oid, hex_or_bin);
    }

    if (err < 0) {
        Error_set_py_obj(err, py_str);
        return 0;
    }

    return 1;
}

static int
Repository_init(Repository *self, PyObject *args, PyObject *kwds) {
    char *path;
    int err;

    if (kwds) {
        PyErr_SetString(PyExc_TypeError,
                        "Repository takes no keyword arugments");
        return -1;
    }

    if (!PyArg_ParseTuple(args, "s", &path))
        return -1;

    err = git_repository_open(&self->repo, path);
    if (err < 0) {
        Error_set_str(err, path);
        return -1;
    }

    return 0;
}

static void
Repository_dealloc(Repository *self) {
    if (self->repo)
        git_repository_free(self->repo);
    Py_XDECREF(self->index);
    self->ob_type->tp_free((PyObject*)self);
}

static int
Repository_contains(Repository *self, PyObject *value) {
    git_oid oid;

    if (!py_str_to_git_oid(value, &oid))
        return -1;

    return git_odb_exists(git_repository_database(self->repo), &oid);
}

static PyObject *
Repository_getitem(Repository *self, PyObject *value) {
    git_oid oid;

    if (!py_str_to_git_oid(value, &oid))
        return NULL;

    return lookup_object(self, &oid, GIT_OBJ_ANY);
}

static int
Repository_read_raw(git_odb_object **obj, git_repository *repo,
                    const git_oid *oid) {
    return git_odb_read(obj, git_repository_database(repo), oid);
}

static PyObject *
Repository_read(Repository *self, PyObject *py_hex) {
    git_oid oid;
    int err;
    git_odb_object *obj;

    if (!py_str_to_git_oid(py_hex, &oid))
        return NULL;

    err = Repository_read_raw(&obj, self->repo, &oid);
    if (err < 0)
        return Error_set_py_obj(err, py_hex);

    PyObject* tuple = Py_BuildValue(
        "(ns#)",
        git_odb_object_type(obj),
        git_odb_object_data(obj),
        git_odb_object_size(obj));

    git_odb_object_close(obj);
    return tuple;
}

static PyObject *
Repository_get_index(Repository *self, void *closure) {
    int err;
    git_index *index;
    Index *py_index;

    assert(self->repo);

    if (self->index == NULL) {
        err = git_repository_index(&index, self->repo);
        if (err == GIT_SUCCESS) {
            py_index = (Index*)IndexType.tp_alloc(&IndexType, 0);
            if (!py_index)
                return PyErr_NoMemory();
            py_index->repo = self;
            py_index->index = index;
            py_index->own_obj = 0;
            self->index = (PyObject*)py_index;
        } else if (err == GIT_EBAREINDEX) {
            Py_INCREF(Py_None);
            self->index = Py_None;
        } else {
            return Error_set(err);
        }
    }

    Py_INCREF(self->index);
    return self->index;
}

static PyObject *
Repository_get_path(Repository *self, void *closure) {
    const char *c_path;

    c_path = git_repository_path(self->repo, GIT_REPO_PATH);
    return PyString_FromString(c_path);
}

static PyObject *
Repository_get_workdir(Repository *self, void *closure) {
    const char *c_path;

    c_path = git_repository_path(self->repo, GIT_REPO_PATH_WORKDIR);
    if (c_path == NULL)
        Py_RETURN_NONE;

    return PyString_FromString(c_path);
}

static PyObject *
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

    if (value != Py_None && !PyString_Check(value)) {
        PyErr_SetObject(PyExc_TypeError, value);
        return NULL;
    }

    err = git_revwalk_new(&walk, self->repo);
    if (err < 0)
        return Error_set(err);

    /* Sort */
    git_revwalk_sorting(walk, sort);

    /* Push */
    if (value != Py_None) {
        if (!py_str_to_git_oid(value, &oid)) {
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

static PyObject *
build_person(const git_signature *signature) {
    return Py_BuildValue("(ssLi)", signature->name, signature->email,
                         signature->when.time, signature->when.offset);
}

static int
signature_converter(PyObject *value, git_signature **out) {
    char *name, *email;
    long long time;
    int offset;
    git_signature *signature;

    if (!PyArg_ParseTuple(value, "ssLi", &name, &email, &time, &offset))
        return 0;

    signature = git_signature_new(name, email, time, offset);
    if (signature == NULL) {
        PyErr_SetNone(PyExc_MemoryError);
        return 0;
    }

    *out = signature;
    return 1;
}

static PyObject *
free_parents(git_oid **parents, int n) {
    int i;

    for (i = 0; i < n; i++)
        free(parents[i]);
    free(parents);
    return NULL;
}

static PyObject *
Repository_create_commit(Repository *self, PyObject *args) {
    git_signature *author, *committer;
    char *message, *update_ref;
    git_oid tree_oid, oid;
    PyObject *py_parents, *py_parent;
    int parent_count;
    git_oid **parents;
    int err, i;
    char hex[GIT_OID_HEXSZ];

    if (!PyArg_ParseTuple(args, "zO&O&sO&O!",
                          &update_ref,
                          signature_converter, &author,
                          signature_converter, &committer,
                          &message,
                          py_str_to_git_oid, &tree_oid,
                          &PyList_Type, &py_parents))
        return NULL;

    parent_count = (int)PyList_Size(py_parents);
    parents = malloc(parent_count * sizeof(git_oid*));
    if (parents == NULL) {
        PyErr_SetNone(PyExc_MemoryError);
        return NULL;
    }
    for (i = 0; i < parent_count; i++) {
        parents[i] = malloc(sizeof(git_oid));
        if (parents[i] == NULL) {
            PyErr_SetNone(PyExc_MemoryError);
            return free_parents(parents, i);
        }
        py_parent = PyList_GET_ITEM(py_parents, i);
        if (!py_str_to_git_oid(py_parent, parents[i]))
            return free_parents(parents, i);
    }

    err = git_commit_create(&oid, self->repo, update_ref, author, committer,
        message, &tree_oid, parent_count, (const git_oid**)parents);
    free_parents(parents, parent_count);
    if (err < 0)
        return Error_set(err);

    git_oid_fmt(hex, &oid);
    return PyString_FromStringAndSize(hex, GIT_OID_HEXSZ);
}

static PyObject *
Repository_create_tag(Repository *self, PyObject *args) {
    char *tag_name, *message;
    git_signature *tagger;
    git_oid target, oid;
    int err, target_type;
    char hex[GIT_OID_HEXSZ];

    if (!PyArg_ParseTuple(args, "sO&iO&s",
                          &tag_name,
                          py_str_to_git_oid, &target,
                          &target_type,
                          signature_converter, &tagger,
                          &message))
        return NULL;

    err = git_tag_create(&oid, self->repo,
        tag_name, &target, target_type, tagger, message);
    if (err < 0)
        return NULL;

    git_oid_fmt(hex, &oid);
    return PyString_FromStringAndSize(hex, GIT_OID_HEXSZ);
}

static PyObject *
Repository_listall_references(Repository *self, PyObject *args) {
    unsigned list_flags=GIT_REF_LISTALL;
    git_strarray c_result;
    PyObject *py_result, *py_string;
    unsigned index;
    int err;

    /* 1- Get list_flags */
    if (!PyArg_ParseTuple(args, "|I", &list_flags))
        return NULL;

    /* 2- Get the C result */
    err = git_reference_listall(&c_result, self->repo, list_flags);
    if (err < 0)
        return Error_set(err);

    /* 3- Create a new PyTuple */
    if ( (py_result = PyTuple_New(c_result.count)) == NULL) {
        git_strarray_free(&c_result);
        return NULL;
    }

    /* 4- Fill it */
    for (index=0; index < c_result.count; index++) {
        if ((py_string = PyString_FromString( (c_result.strings)[index] ))
             == NULL) {
            Py_XDECREF(py_result);
            git_strarray_free(&c_result);
            return NULL;
        }
        PyTuple_SET_ITEM(py_result, index, py_string);
    }

    /* 5- Destroy the c_result */
    git_strarray_free(&c_result);

    /* 6- And return the py_result */
    return py_result;
}

static PyObject *
Repository_lookup_reference(Repository *self, PyObject *py_name) {
    git_reference *c_reference;
    char *c_name;
    int err;

    /* 1- Get the C name */
    c_name = PyString_AsString(py_name);
    if (c_name == NULL)
        return NULL;

    /* 2- Lookup */
    err = git_reference_lookup(&c_reference, self->repo, c_name);
    if (err < 0)
      return Error_set(err);

    /* 3- Make an instance of Reference and return it */
    return wrap_reference(c_reference);
}

static PyObject *
Repository_create_reference(Repository *self,  PyObject *args) {
    git_reference *c_reference;
    char *c_name;
    git_oid oid;
    int err;

    /* 1- Get the C variables */
    if (!PyArg_ParseTuple(args, "sO&", &c_name,
                                       py_str_to_git_oid, &oid))
        return NULL;

    /* 2- Create the reference */
    err = git_reference_create_oid(&c_reference, self->repo, c_name, &oid);
    if (err < 0)
      return Error_set(err);

    /* 3- Make an instance of Reference and return it */
    return wrap_reference(c_reference);
}

static PyObject *
Repository_create_symbolic_reference(Repository *self,  PyObject *args) {
    git_reference *c_reference;
    char *c_name, *c_target;
    int err;

    /* 1- Get the C variables */
    if (!PyArg_ParseTuple(args, "ss", &c_name, &c_target))
        return NULL;

    /* 2- Create the reference */
    err = git_reference_create_symbolic(&c_reference, self->repo, c_name,
                                        c_target);
    if (err < 0)
      return Error_set(err);

    /* 3- Make an instance of Reference and return it */
    return wrap_reference(c_reference);
}

static PyObject *
Repository_packall_references(Repository *self,  PyObject *args) {
    int err;

    /* 1- Pack */
    err = git_reference_packall(self->repo);
    if (err < 0)
        return Error_set(err);

    /* 2- Return None */
    Py_RETURN_NONE;
}

static PyMethodDef Repository_methods[] = {
    {"create_commit", (PyCFunction)Repository_create_commit, METH_VARARGS,
     "Create a new commit object, return its SHA."},
    {"create_tag", (PyCFunction)Repository_create_tag, METH_VARARGS,
     "Create a new tag object, return its SHA."},
    {"walk", (PyCFunction)Repository_walk, METH_VARARGS,
     "Generator that traverses the history starting from the given commit."},
    {"read", (PyCFunction)Repository_read, METH_O,
     "Read raw object data from the repository."},
    {"listall_references", (PyCFunction)Repository_listall_references,
      METH_VARARGS,
      "Return a list with all the references that can be found in a "
      "repository."},
    {"lookup_reference", (PyCFunction)Repository_lookup_reference, METH_O,
       "Lookup a reference by its name in a repository."},
    {"create_reference", (PyCFunction)Repository_create_reference, METH_VARARGS,
     "Create a new reference \"name\" that points to the object given by its "
     "\"sha\"."},
    {"create_symbolic_reference",
      (PyCFunction)Repository_create_symbolic_reference, METH_VARARGS,
     "Create a new symbolic reference \"name\" that points to the reference "
     "\"target\"."},
    {"packall_references", (PyCFunction)Repository_packall_references,
     METH_NOARGS, "Pack all the loose references in the repository."},
    {NULL}
};

static PyGetSetDef Repository_getseters[] = {
    {"index", (getter)Repository_get_index, NULL, "index file. ", NULL},
    {"path", (getter)Repository_get_path, NULL,
     "The normalized path to the git repository.", NULL},
    {"workdir", (getter)Repository_get_workdir, NULL,
     "The normalized path to the working directory of the repository. "
     "If the repository is bare, None will be returned.", NULL},
    {NULL}
};

static PySequenceMethods Repository_as_sequence = {
    0,                               /* sq_length */
    0,                               /* sq_concat */
    0,                               /* sq_repeat */
    0,                               /* sq_item */
    0,                               /* sq_slice */
    0,                               /* sq_ass_item */
    0,                               /* sq_ass_slice */
    (objobjproc)Repository_contains, /* sq_contains */
};

static PyMappingMethods Repository_as_mapping = {
    0,                               /* mp_length */
    (binaryfunc)Repository_getitem,  /* mp_subscript */
    0,                               /* mp_ass_subscript */
};

static PyTypeObject RepositoryType = {
    PyObject_HEAD_INIT(NULL)
    0,                                         /* ob_size */
    "pygit2.Repository",                       /* tp_name */
    sizeof(Repository),                        /* tp_basicsize */
    0,                                         /* tp_itemsize */
    (destructor)Repository_dealloc,            /* tp_dealloc */
    0,                                         /* tp_print */
    0,                                         /* tp_getattr */
    0,                                         /* tp_setattr */
    0,                                         /* tp_compare */
    0,                                        /* tp_repr */
    0,                                         /* tp_as_number */
    &Repository_as_sequence,                   /* tp_as_sequence */
    &Repository_as_mapping,                    /* tp_as_mapping */
    0,                                         /* tp_hash  */
    0,                                         /* tp_call */
    0,                                         /* tp_str */
    0,                                         /* tp_getattro */
    0,                                         /* tp_setattro */
    0,                                         /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,  /* tp_flags */
    "Git repository",                          /* tp_doc */
    0,                                         /* tp_traverse */
    0,                                         /* tp_clear */
    0,                                         /* tp_richcompare */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter */
    0,                                         /* tp_iternext */
    Repository_methods,                        /* tp_methods */
    0,                                         /* tp_members */
    Repository_getseters,                      /* tp_getset */
    0,                                         /* tp_base */
    0,                                         /* tp_dict */
    0,                                         /* tp_descr_get */
    0,                                         /* tp_descr_set */
    0,                                         /* tp_dictoffset */
    (initproc)Repository_init,                 /* tp_init */
    0,                                         /* tp_alloc */
    0,                                         /* tp_new */
};

static void
Object_dealloc(Object* self)
{
    git_object_close(self->obj);
    Py_XDECREF(self->repo);
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
Object_get_type(Object *self) {
    return PyInt_FromLong(git_object_type(self->obj));
}

static PyObject *
Object_get_sha(Object *self) {
    const git_oid *id;
    char hex[GIT_OID_HEXSZ];

    id = git_object_id(self->obj);
    if (!id)
        Py_RETURN_NONE;

    git_oid_fmt(hex, id);
    return PyString_FromStringAndSize(hex, GIT_OID_HEXSZ);
}

static PyObject *
Object_read_raw(Object *self) {
    const git_oid *id;
    git_odb_object *obj;
    int err;
    PyObject *result = NULL, *py_sha = NULL;

    id = git_object_id(self->obj);
    if (!id)
        Py_RETURN_NONE;  /* in-memory object */

    err = Repository_read_raw(&obj, self->repo->repo, id);
    if (err < 0) {
        py_sha = Object_get_sha(self);
        Error_set_py_obj(err, py_sha);
        goto cleanup;
    }

    result = PyString_FromStringAndSize(
        git_odb_object_data(obj),
        git_odb_object_size(obj));

    git_odb_object_close(obj);

cleanup:
    Py_XDECREF(py_sha);
    return result;
}

static PyGetSetDef Object_getseters[] = {
    {"type", (getter)Object_get_type, NULL, "type number", NULL},
    {"sha", (getter)Object_get_sha, NULL, "hex SHA", NULL},
    {NULL}
};

static PyMethodDef Object_methods[] = {
    {"read_raw", (PyCFunction)Object_read_raw, METH_NOARGS,
     "Read the raw contents of the object from the repo."},
    {NULL}
};

static PyTypeObject ObjectType = {
    PyObject_HEAD_INIT(NULL)
    0,                                         /*ob_size*/
    "pygit2.Object",                           /*tp_name*/
    sizeof(Object),                            /*tp_basicsize*/
    0,                                         /*tp_itemsize*/
    (destructor)Object_dealloc,                /*tp_dealloc*/
    0,                                         /*tp_print*/
    0,                                         /*tp_getattr*/
    0,                                         /*tp_setattr*/
    0,                                         /*tp_compare*/
    0,                                         /*tp_repr*/
    0,                                         /*tp_as_number*/
    0,                                         /*tp_as_sequence*/
    0,                                         /*tp_as_mapping*/
    0,                                         /*tp_hash */
    0,                                         /*tp_call*/
    0,                                         /*tp_str*/
    0,                                         /*tp_getattro*/
    0,                                         /*tp_setattro*/
    0,                                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,  /*tp_flags*/
    "Object objects",                          /* tp_doc */
    0,                                         /* tp_traverse */
    0,                                         /* tp_clear */
    0,                                         /* tp_richcompare */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter */
    0,                                         /* tp_iternext */
    Object_methods,                            /* tp_methods */
    0,                                         /* tp_members */
    Object_getseters,                          /* tp_getset */
    0,                                         /* tp_base */
    0,                                         /* tp_dict */
    0,                                         /* tp_descr_get */
    0,                                         /* tp_descr_set */
    0,                                         /* tp_dictoffset */
    0,                                         /* tp_init */
    0,                                         /* tp_alloc */
    0,                                         /* tp_new */
};

static PyObject *
Commit_get_message_short(Commit *commit) {
    return PyString_FromString(git_commit_message_short(commit->commit));
}

static PyObject *
Commit_get_message(Commit *commit) {
    return PyString_FromString(git_commit_message(commit->commit));
}

static PyObject *
Commit_get_commit_time(Commit *commit) {
    return PyLong_FromLong(git_commit_time(commit->commit));
}

static PyObject *
Commit_get_committer(Commit *commit) {
    const git_signature *signature = git_commit_committer(commit->commit);

    return build_person(signature);
}

static PyObject *
Commit_get_author(Commit *commit) {
    const git_signature *signature = git_commit_author(commit->commit);

    return build_person(signature);
}

static PyObject *
Commit_get_tree(Commit *commit) {
    git_tree *tree;
    Tree *py_tree;
    int err;

    err = git_commit_tree(&tree, commit->commit);
    if (err == GIT_ENOTFOUND)
        Py_RETURN_NONE;

    if (err < 0)
        return Error_set(err);

    py_tree = PyObject_New(Tree, &TreeType);
    Py_INCREF(commit->repo);
    py_tree->repo = commit->repo;
    py_tree->tree = (git_tree*)tree;

    return (PyObject*)py_tree;
}

static PyObject *
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

static PyGetSetDef Commit_getseters[] = {
    {"message_short", (getter)Commit_get_message_short, NULL, "short message",
     NULL},
    {"message", (getter)Commit_get_message, NULL, "message", NULL},
    {"commit_time", (getter)Commit_get_commit_time, NULL, "commit time",
     NULL},
    {"committer", (getter)Commit_get_committer, NULL, "committer", NULL},
    {"author", (getter)Commit_get_author, NULL, "author", NULL},
    {"tree", (getter)Commit_get_tree, NULL, "tree object", NULL},
    {"parents", (getter)Commit_get_parents, NULL, "parents of this commit",
      NULL},
    {NULL}
};

static PyTypeObject CommitType = {
    PyObject_HEAD_INIT(NULL)
    0,                                         /*ob_size*/
    "pygit2.Commit",                           /*tp_name*/
    sizeof(Commit),                            /*tp_basicsize*/
    0,                                         /*tp_itemsize*/
    0,                                         /*tp_dealloc*/
    0,                                         /*tp_print*/
    0,                                         /*tp_getattr*/
    0,                                         /*tp_setattr*/
    0,                                         /*tp_compare*/
    0,                                         /*tp_repr*/
    0,                                         /*tp_as_number*/
    0,                                         /*tp_as_sequence*/
    0,                                         /*tp_as_mapping*/
    0,                                         /*tp_hash */
    0,                                         /*tp_call*/
    0,                                         /*tp_str*/
    0,                                         /*tp_getattro*/
    0,                                         /*tp_setattro*/
    0,                                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,  /*tp_flags*/
    "Commit objects",                          /* tp_doc */
    0,                                         /* tp_traverse */
    0,                                         /* tp_clear */
    0,                                         /* tp_richcompare */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter */
    0,                                         /* tp_iternext */
    0,                                         /* tp_methods */
    0,                                         /* tp_members */
    Commit_getseters,                          /* tp_getset */
    0,                                         /* tp_base */
    0,                                         /* tp_dict */
    0,                                         /* tp_descr_get */
    0,                                         /* tp_descr_set */
    0,                                         /* tp_dictoffset */
    0,                                         /* tp_init */
    0,                                         /* tp_alloc */
    0,                                         /* tp_new */
};

static void
TreeEntry_dealloc(TreeEntry *self) {
    Py_XDECREF(self->tree);
    self->ob_type->tp_free((PyObject *)self);
}

static PyObject *
TreeEntry_get_attributes(TreeEntry *self) {
    return PyInt_FromLong(git_tree_entry_attributes(self->entry));
}

static PyObject *
TreeEntry_get_name(TreeEntry *self) {
    return PyString_FromString(git_tree_entry_name(self->entry));
}

static PyObject *
TreeEntry_get_sha(TreeEntry *self) {
    char hex[GIT_OID_HEXSZ];
    git_oid_fmt(hex, git_tree_entry_id(self->entry));
    return PyString_FromStringAndSize(hex, GIT_OID_HEXSZ);
}

static PyObject *
TreeEntry_to_object(TreeEntry *self) {
    const git_oid *entry_oid;

    entry_oid = git_tree_entry_id(self->entry);
    return lookup_object(self->tree->repo, entry_oid, GIT_OBJ_ANY);
}

static PyGetSetDef TreeEntry_getseters[] = {
    {"attributes", (getter)TreeEntry_get_attributes, NULL, "attributes", NULL},
    {"name", (getter)TreeEntry_get_name, NULL, "name", NULL},
    {"sha", (getter)TreeEntry_get_sha, NULL, "sha", NULL},
    {NULL}
};

static PyMethodDef TreeEntry_methods[] = {
    {"to_object", (PyCFunction)TreeEntry_to_object, METH_NOARGS,
     "Look up the corresponding object in the repo."},
    {NULL, NULL, 0, NULL}
};

static PyTypeObject TreeEntryType = {
    PyObject_HEAD_INIT(NULL)
    0,                                         /*ob_size*/
    "pygit2.TreeEntry",                        /*tp_name*/
    sizeof(TreeEntry),                         /*tp_basicsize*/
    0,                                         /*tp_itemsize*/
    (destructor)TreeEntry_dealloc,             /*tp_dealloc*/
    0,                                         /*tp_print*/
    0,                                         /*tp_getattr*/
    0,                                         /*tp_setattr*/
    0,                                         /*tp_compare*/
    0,                                         /*tp_repr*/
    0,                                         /*tp_as_number*/
    0,                                         /*tp_as_sequence*/
    0,                                         /*tp_as_mapping*/
    0,                                         /*tp_hash */
    0,                                         /*tp_call*/
    0,                                         /*tp_str*/
    0,                                         /*tp_getattro*/
    0,                                         /*tp_setattro*/
    0,                                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,  /*tp_flags*/
    "TreeEntry objects",                       /* tp_doc */
    0,                                         /* tp_traverse */
    0,                                         /* tp_clear */
    0,                                         /* tp_richcompare */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter */
    0,                                         /* tp_iternext */
    TreeEntry_methods,                         /* tp_methods */
    0,                                         /* tp_members */
    TreeEntry_getseters,                       /* tp_getset */
    0,                                         /* tp_base */
    0,                                         /* tp_dict */
    0,                                         /* tp_descr_get */
    0,                                         /* tp_descr_set */
    0,                                         /* tp_dictoffset */
    0,                                         /* tp_init */
    0,                                         /* tp_alloc */
    0,                                         /* tp_new */
};

static Py_ssize_t
Tree_len(Tree *self) {
    assert(self->tree);
    return (Py_ssize_t)git_tree_entrycount(self->tree);
}

static int
Tree_contains(Tree *self, PyObject *py_name) {
    char *name;

    name = PyString_AsString(py_name);
    if (name == NULL)
        return -1;

    return git_tree_entry_byname(self->tree, name) ? 1 : 0;
}

static TreeEntry *
wrap_tree_entry(const git_tree_entry *entry, Tree *tree) {
    TreeEntry *py_entry = NULL;
    py_entry = (TreeEntry*)TreeEntryType.tp_alloc(&TreeEntryType, 0);
    if (!py_entry)
        return NULL;

    py_entry->entry = entry;
    py_entry->tree = tree;
    Py_INCREF(tree);
    return py_entry;
}

static TreeEntry *
Tree_getitem_by_name(Tree *self, PyObject *py_name) {
    char *name;
    const git_tree_entry *entry;

    name = PyString_AS_STRING(py_name);
    entry = git_tree_entry_byname(self->tree, name);
    if (!entry) {
        PyErr_SetObject(PyExc_KeyError, py_name);
        return NULL;
    }
    return wrap_tree_entry(entry, self);
}

static int
Tree_fix_index(Tree *self, PyObject *py_index) {
    long index;
    size_t len;
    long slen;

    index = PyInt_AsLong(py_index);
    if (PyErr_Occurred())
        return -1;

    len = git_tree_entrycount(self->tree);
    slen = (long)len;
    if (index >= slen) {
        PyErr_SetObject(PyExc_IndexError, py_index);
        return -1;
    } else if (index < -slen) {
        PyErr_SetObject(PyExc_IndexError, py_index);
        return -1;
    }

    /* This function is called via mp_subscript, which doesn't do negative index
     * rewriting, so we have to do it manually. */
    if (index < 0)
        index = len + index;
    return (int)index;
}

static PyObject *
Tree_iter(Tree *self) {
  TreeIter *iter;

  iter = PyObject_New(TreeIter, &TreeIterType);
  if (!iter)
      return NULL;

  Py_INCREF(self);
  iter->owner = self;
  iter->i = 0;

  return (PyObject*)iter;
}

static TreeEntry *
Tree_getitem_by_index(Tree *self, PyObject *py_index) {
    int index;
    const git_tree_entry *entry;

    index = Tree_fix_index(self, py_index);
    if (PyErr_Occurred())
        return NULL;

    entry = git_tree_entry_byindex(self->tree, index);
    if (!entry) {
        PyErr_SetObject(PyExc_IndexError, py_index);
        return NULL;
    }
    return wrap_tree_entry(entry, self);
}

static TreeEntry *
Tree_getitem(Tree *self, PyObject *value) {
    if (PyString_Check(value)) {
        return Tree_getitem_by_name(self, value);
    } else if (PyInt_Check(value)) {
        return Tree_getitem_by_index(self, value);
    } else {
        PyErr_Format(PyExc_TypeError,
                     "Tree entry index must be int or str, not %.200s",
                     value->ob_type->tp_name);
        return NULL;
    }
}

static PySequenceMethods Tree_as_sequence = {
    0,                          /* sq_length */
    0,                          /* sq_concat */
    0,                          /* sq_repeat */
    0,                          /* sq_item */
    0,                          /* sq_slice */
    0,                          /* sq_ass_item */
    0,                          /* sq_ass_slice */
    (objobjproc)Tree_contains,  /* sq_contains */
};

static PyMappingMethods Tree_as_mapping = {
    (lenfunc)Tree_len,            /* mp_length */
    (binaryfunc)Tree_getitem,     /* mp_subscript */
    0,                            /* mp_ass_subscript */
};

static PyTypeObject TreeType = {
    PyObject_HEAD_INIT(NULL)
    0,                                         /*ob_size*/
    "pygit2.Tree",                             /*tp_name*/
    sizeof(Tree),                              /*tp_basicsize*/
    0,                                         /*tp_itemsize*/
    0,                                         /*tp_dealloc*/
    0,                                         /*tp_print*/
    0,                                         /*tp_getattr*/
    0,                                         /*tp_setattr*/
    0,                                         /*tp_compare*/
    0,                                         /*tp_repr*/
    0,                                         /*tp_as_number*/
    &Tree_as_sequence,                         /*tp_as_sequence*/
    &Tree_as_mapping,                          /*tp_as_mapping*/
    0,                                         /*tp_hash */
    0,                                         /*tp_call*/
    0,                                         /*tp_str*/
    0,                                         /*tp_getattro*/
    0,                                         /*tp_setattro*/
    0,                                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,  /*tp_flags*/
    "Tree objects",                            /* tp_doc */
    0,                                         /* tp_traverse */
    0,                                         /* tp_clear */
    0,                                         /* tp_richcompare */
    0,                                         /* tp_weaklistoffset */
    (getiterfunc)Tree_iter,                    /* tp_iter */
    0,                                         /* tp_iternext */
    0,                                         /* tp_methods */
    0,                                         /* tp_members */
    0,                                         /* tp_getset */
    0,                                         /* tp_base */
    0,                                         /* tp_dict */
    0,                                         /* tp_descr_get */
    0,                                         /* tp_descr_set */
    0,                                         /* tp_dictoffset */
    0,                                         /* tp_init */
    0,                                         /* tp_alloc */
    0,                                         /* tp_new */
};

static void
TreeIter_dealloc(TreeIter *self) {
    Py_CLEAR(self->owner);
    PyObject_Del(self);
}

static TreeEntry *
TreeIter_iternext(TreeIter *self) {
    const git_tree_entry *tree_entry;

    tree_entry = git_tree_entry_byindex(self->owner->tree, self->i);
    if (!tree_entry)
        return NULL;

    self->i += 1;
    return (TreeEntry*)wrap_tree_entry(tree_entry, self->owner);
}

static PyTypeObject TreeIterType = {
   PyVarObject_HEAD_INIT(&PyType_Type, 0)
   "pygit2.TreeIter",                      /* tp_name           */
   sizeof(TreeIter),                       /* tp_basicsize      */
   0,                                       /* tp_itemsize       */
   (destructor)TreeIter_dealloc ,          /* tp_dealloc        */
   0,                                       /* tp_print          */
   0,                                       /* tp_getattr        */
   0,                                       /* tp_setattr        */
   0,                                       /* tp_compare        */
   0,                                       /* tp_repr           */
   0,                                       /* tp_as_number      */
   0,                                       /* tp_as_sequence    */
   0,                                       /* tp_as_mapping     */
   0,                                       /* tp_hash           */
   0,                                       /* tp_call           */
   0,                                       /* tp_str            */
   PyObject_GenericGetAttr,                 /* tp_getattro       */
   0,                                       /* tp_setattro       */
   0,                                       /* tp_as_buffer      */
   Py_TPFLAGS_DEFAULT |
   Py_TPFLAGS_BASETYPE,                     /* tp_flags          */
   0,                                       /* tp_doc            */
   0,                                       /* tp_traverse       */
   0,                                       /* tp_clear          */
   0,                                       /* tp_richcompare    */
   0,                                       /* tp_weaklistoffset */
   PyObject_SelfIter,                       /* tp_iter           */
   (iternextfunc)TreeIter_iternext,        /* tp_iternext       */
 };

static PyGetSetDef Blob_getseters[] = {
    {"data", (getter)Object_read_raw, NULL, "raw data", NULL},
    {NULL}
};

static PyTypeObject BlobType = {
    PyObject_HEAD_INIT(NULL)
    0,                                         /*ob_size*/
    "pygit2.Blob",                             /*tp_name*/
    sizeof(Blob),                              /*tp_basicsize*/
    0,                                         /*tp_itemsize*/
    0,                                         /*tp_dealloc*/
    0,                                         /*tp_print*/
    0,                                         /*tp_getattr*/
    0,                                         /*tp_setattr*/
    0,                                         /*tp_compare*/
    0,                                         /*tp_repr*/
    0,                                         /*tp_as_number*/
    0,                                         /*tp_as_sequence*/
    0,                                         /*tp_as_mapping*/
    0,                                         /*tp_hash */
    0,                                         /*tp_call*/
    0,                                         /*tp_str*/
    0,                                         /*tp_getattro*/
    0,                                         /*tp_setattro*/
    0,                                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,  /*tp_flags*/
    "Blob objects",                            /* tp_doc */
    0,                                         /* tp_traverse */
    0,                                         /* tp_clear */
    0,                                         /* tp_richcompare */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter */
    0,                                         /* tp_iternext */
    0,                                         /* tp_methods */
    0,                                         /* tp_members */
    Blob_getseters,                            /* tp_getset */
    0,                                         /* tp_base */
    0,                                         /* tp_dict */
    0,                                         /* tp_descr_get */
    0,                                         /* tp_descr_set */
    0,                                         /* tp_dictoffset */
    0,                                         /* tp_init */
    0,                                         /* tp_alloc */
    0,                                         /* tp_new */
};

static void
Tag_dealloc(Tag *self) {
    Py_XDECREF(self->target);
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
Tag_get_target(Tag *self) {
    const git_oid *target_oid;
    git_otype target_type;

    if (self->target == NULL) {
        target_oid = git_tag_target_oid(self->tag);
        target_type = git_tag_type(self->tag);
        self->target = lookup_object(self->repo, target_oid, target_type);
        if (self->target == NULL)
            return NULL;
    }

    Py_INCREF(self->target);
    return self->target;
}

static PyObject *
Tag_get_name(Tag *self) {
    const char *name;
    name = git_tag_name(self->tag);
    if (!name)
        Py_RETURN_NONE;
    return PyString_FromString(name);
}

static PyObject *
Tag_get_tagger(Tag *tag) {
    const git_signature *signature = git_tag_tagger(tag->tag);
    if (!signature)
        Py_RETURN_NONE;
    return build_person(signature);
}

static PyObject *
Tag_get_message(Tag *self) {
    const char *message;
    message = git_tag_message(self->tag);
    if (!message)
        Py_RETURN_NONE;
    return PyString_FromString(message);
}

static PyGetSetDef Tag_getseters[] = {
    {"target", (getter)Tag_get_target, NULL, "tagged object", NULL},
    {"name", (getter)Tag_get_name, NULL, "tag name", NULL},
    {"tagger", (getter)Tag_get_tagger, NULL, "tagger", NULL},
    {"message", (getter)Tag_get_message, NULL, "tag message",
     NULL},
    {NULL}
};

static PyTypeObject TagType = {
    PyObject_HEAD_INIT(NULL)
    0,                                         /*ob_size*/
    "pygit2.Tag",                              /*tp_name*/
    sizeof(Tag),                               /*tp_basicsize*/
    0,                                         /*tp_itemsize*/
    (destructor)Tag_dealloc,                   /*tp_dealloc*/
    0,                                         /*tp_print*/
    0,                                         /*tp_getattr*/
    0,                                         /*tp_setattr*/
    0,                                         /*tp_compare*/
    0,                                         /*tp_repr*/
    0,                                         /*tp_as_number*/
    0,                                         /*tp_as_sequence*/
    0,                                         /*tp_as_mapping*/
    0,                                         /*tp_hash */
    0,                                         /*tp_call*/
    0,                                         /*tp_str*/
    0,                                         /*tp_getattro*/
    0,                                         /*tp_setattro*/
    0,                                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,  /*tp_flags*/
    "Tag objects",                             /* tp_doc */
    0,                                         /* tp_traverse */
    0,                                         /* tp_clear */
    0,                                         /* tp_richcompare */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter */
    0,                                         /* tp_iternext */
    0,                                         /* tp_methods */
    0,                                         /* tp_members */
    Tag_getseters,                             /* tp_getset */
    0,                                         /* tp_base */
    0,                                         /* tp_dict */
    0,                                         /* tp_descr_get */
    0,                                         /* tp_descr_set */
    0,                                         /* tp_dictoffset */
    0,                                         /* tp_init */
    0,                                         /* tp_alloc */
    0,                                         /* tp_new */
};

static int
Index_init(Index *self, PyObject *args, PyObject *kwds) {
    char *path;
    int err;

    if (kwds) {
        PyErr_SetString(PyExc_TypeError,
                        "Index takes no keyword arugments");
        return -1;
    }

    if (!PyArg_ParseTuple(args, "s", &path))
        return -1;

    err = git_index_open(&self->index, path);
    if (err < 0) {
        Error_set_str(err, path);
        return -1;
    }

    self->own_obj = 1;
    return 0;
}

static void
Index_dealloc(Index* self)
{
    if (self->own_obj)
        git_index_free(self->index);
    Py_XDECREF(self->repo);
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
Index_add(Index *self, PyObject *args) {
    int err;
    const char *path;
    int stage=0;

    if (!PyArg_ParseTuple(args, "s|i", &path, &stage))
        return NULL;

    err = git_index_add(self->index, path, stage);
    if (err < 0)
        return Error_set_str(err, path);

    Py_RETURN_NONE;
}

static PyObject *
Index_clear(Index *self) {
    git_index_clear(self->index);
    Py_RETURN_NONE;
}

static PyObject *
Index_find(Index *self, PyObject *py_path) {
    char *path;
    long idx;

    path = PyString_AsString(py_path);
    if (!path)
        return NULL;

    idx = (long)git_index_find(self->index, path);
    if (idx < 0)
        return Error_set_str(idx, path);

    return PyInt_FromLong(idx);
}

static PyObject *
Index_read(Index *self) {
    int err;

    err = git_index_read(self->index);
    if (err < GIT_SUCCESS)
        return Error_set(err);

    Py_RETURN_NONE;
}

static PyObject *
Index_write(Index *self) {
    int err;

    err = git_index_write(self->index);
    if (err < GIT_SUCCESS)
        return Error_set(err);

    Py_RETURN_NONE;
}

/* This is an internal function, used by Index_getitem and Index_setitem */
static int
Index_get_position(Index *self, PyObject *value) {
    char *path;
    int idx;

    if (PyString_Check(value)) {
        path = PyString_AsString(value);
        if (!path)
            return -1;
        idx = git_index_find(self->index, path);
        if (idx < 0) {
            Error_set_str(idx, path);
            return -1;
        }
    } else if (PyInt_Check(value)) {
        idx = (int)PyInt_AsLong(value);
        if (idx == -1 && PyErr_Occurred())
            return -1;
        if (idx < 0) {
            PyErr_SetObject(PyExc_ValueError, value);
            return -1;
        }
    } else {
        PyErr_Format(PyExc_TypeError,
                     "Index entry key must be int or str, not %.200s",
                     value->ob_type->tp_name);
        return -1;
    }

    return idx;
}

static int
Index_contains(Index *self, PyObject *value) {
    char *path;
    int idx;

    path = PyString_AsString(value);
    if (!path)
        return -1;
    idx = git_index_find(self->index, path);
    if (idx == GIT_ENOTFOUND)
        return 0;
    if (idx < 0) {
        Error_set_str(idx, path);
        return -1;
    }

    return 1;
}

static PyObject *
Index_iter(Index *self) {
  IndexIter *iter;

  iter = PyObject_New(IndexIter, &IndexIterType);
  if (!iter)
      return NULL;

  Py_INCREF(self);
  iter->owner = self;
  iter->i = 0;
  return (PyObject*)iter;
}

static Py_ssize_t
Index_len(Index *self) {
    return (Py_ssize_t)git_index_entrycount(self->index);
}

static PyObject *
wrap_index_entry(git_index_entry *entry, Index *index) {
    IndexEntry *py_entry;

    py_entry = (IndexEntry*)IndexEntryType.tp_alloc(&IndexEntryType, 0);
    if (!py_entry)
        return PyErr_NoMemory();

    py_entry->entry = entry;

    Py_INCREF(py_entry);
    return (PyObject*)py_entry;
}

static PyObject *
Index_getitem(Index *self, PyObject *value) {
    int idx;
    git_index_entry *index_entry;

    idx = Index_get_position(self, value);
    if (idx == -1)
        return NULL;

    index_entry = git_index_get(self->index, idx);
    if (!index_entry) {
        PyErr_SetObject(PyExc_KeyError, value);
        return NULL;
    }

    return wrap_index_entry(index_entry, self);
}

static int
Index_setitem(Index *self, PyObject *key, PyObject *value) {
    int err;
    int idx;

    if (value) {
        PyErr_SetString(PyExc_NotImplementedError,
                        "set item on index not yet implemented");
        return -1;
    }

    idx = Index_get_position(self, key);
    if (idx == -1)
        return -1;

    err = git_index_remove(self->index, idx);
    if (err < 0) {
        Error_set(err);
        return -1;
    }

    return 0;
}

static PyObject *
Index_create_tree(Index *self) {
    git_oid oid;
    int err;
    char hex[GIT_OID_HEXSZ];

    err = git_tree_create_fromindex(&oid, self->index);
    if (err < 0)
        return Error_set(err);

    git_oid_fmt(hex, &oid);
    return PyString_FromStringAndSize(hex, GIT_OID_HEXSZ);
}

static PyMethodDef Index_methods[] = {
    {"add", (PyCFunction)Index_add, METH_VARARGS,
     "Add or update an index entry from a file in disk."},
    {"clear", (PyCFunction)Index_clear, METH_NOARGS,
     "Clear the contents (all the entries) of an index object."},
    {"_find", (PyCFunction)Index_find, METH_O,
     "Find the first index of any entries which point to given path in the"
     " Git index."},
    {"read", (PyCFunction)Index_read, METH_NOARGS,
     "Update the contents of an existing index object in memory by reading"
     " from the hard disk."},
    {"write", (PyCFunction)Index_write, METH_NOARGS,
     "Write an existing index object from memory back to disk using an"
     " atomic file lock."},
    {"create_tree", (PyCFunction)Index_create_tree, METH_NOARGS,
     "Create a tree from the index file, return its SHA."},
    {NULL}
};

static PySequenceMethods Index_as_sequence = {
    0,                          /* sq_length */
    0,                          /* sq_concat */
    0,                          /* sq_repeat */
    0,                          /* sq_item */
    0,                          /* sq_slice */
    0,                          /* sq_ass_item */
    0,                          /* sq_ass_slice */
    (objobjproc)Index_contains, /* sq_contains */
};

static PyMappingMethods Index_as_mapping = {
    (lenfunc)Index_len,              /* mp_length */
    (binaryfunc)Index_getitem,       /* mp_subscript */
    (objobjargproc)Index_setitem,    /* mp_ass_subscript */
};

static PyTypeObject IndexType = {
    PyObject_HEAD_INIT(NULL)
    0,                                         /* ob_size */
    "pygit2.Index",                            /* tp_name */
    sizeof(Index),                             /* tp_basicsize */
    0,                                         /* tp_itemsize */
    (destructor)Index_dealloc,                 /* tp_dealloc */
    0,                                         /* tp_print */
    0,                                         /* tp_getattr */
    0,                                         /* tp_setattr */
    0,                                         /* tp_compare */
    0,                                         /* tp_repr */
    0,                                         /* tp_as_number */
    &Index_as_sequence,                        /* tp_as_sequence */
    &Index_as_mapping,                         /* tp_as_mapping */
    0,                                         /* tp_hash */
    0,                                         /* tp_call */
    0,                                         /* tp_str */
    0,                                         /* tp_getattro */
    0,                                         /* tp_setattro */
    0,                                         /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,  /* tp_flags */
    "Index file",                              /* tp_doc */
    0,                                         /* tp_traverse */
    0,                                         /* tp_clear */
    0,                                         /* tp_richcompare */
    0,                                         /* tp_weaklistoffset */
    (getiterfunc)Index_iter,                   /* tp_iter */
    0,                                         /* tp_iternext */
    Index_methods,                             /* tp_methods */
    0,                                         /* tp_members */
    0,                                         /* tp_getset */
    0,                                         /* tp_base */
    0,                                         /* tp_dict */
    0,                                         /* tp_descr_get */
    0,                                         /* tp_descr_set */
    0,                                         /* tp_dictoffset */
    (initproc)Index_init,                      /* tp_init */
    0,                                         /* tp_alloc */
    0,                                         /* tp_new */
};


static void
IndexIter_dealloc(IndexIter *self) {
    Py_CLEAR(self->owner);
    PyObject_Del(self);
}

static PyObject *
IndexIter_iternext(IndexIter *self) {
    git_index_entry *index_entry;

    index_entry = git_index_get(self->owner->index, self->i);
    if (!index_entry)
        return NULL;

    self->i += 1;
    return wrap_index_entry(index_entry, self->owner);
}

static PyTypeObject IndexIterType = {
   PyVarObject_HEAD_INIT(&PyType_Type, 0)
   "pygit2.IndexIter",                      /* tp_name           */
   sizeof(IndexIter),                       /* tp_basicsize      */
   0,                                       /* tp_itemsize       */
   (destructor)IndexIter_dealloc ,          /* tp_dealloc        */
   0,                                       /* tp_print          */
   0,                                       /* tp_getattr        */
   0,                                       /* tp_setattr        */
   0,                                       /* tp_compare        */
   0,                                       /* tp_repr           */
   0,                                       /* tp_as_number      */
   0,                                       /* tp_as_sequence    */
   0,                                       /* tp_as_mapping     */
   0,                                       /* tp_hash           */
   0,                                       /* tp_call           */
   0,                                       /* tp_str            */
   PyObject_GenericGetAttr,                 /* tp_getattro       */
   0,                                       /* tp_setattro       */
   0,                                       /* tp_as_buffer      */
   Py_TPFLAGS_DEFAULT |
   Py_TPFLAGS_BASETYPE,                     /* tp_flags          */
   0,                                       /* tp_doc            */
   0,                                       /* tp_traverse       */
   0,                                       /* tp_clear          */
   0,                                       /* tp_richcompare    */
   0,                                       /* tp_weaklistoffset */
   PyObject_SelfIter,                       /* tp_iter           */
   (iternextfunc)IndexIter_iternext,        /* tp_iternext       */
 };

static void
IndexEntry_dealloc(IndexEntry *self) {
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
IndexEntry_get_mode(IndexEntry *self) {
    return PyInt_FromLong(self->entry->mode);
}

static PyObject *
IndexEntry_get_path(IndexEntry *self) {
    return PyString_FromString(self->entry->path);
}

static PyObject *
IndexEntry_get_sha(IndexEntry *self) {
    char hex[GIT_OID_HEXSZ];

    git_oid_fmt(hex, &self->entry->oid);
    return PyString_FromStringAndSize(hex, GIT_OID_HEXSZ);
}

static PyGetSetDef IndexEntry_getseters[] = {
    {"mode", (getter)IndexEntry_get_mode, NULL, "mode", NULL},
    {"path", (getter)IndexEntry_get_path, NULL, "path", NULL},
    {"sha", (getter)IndexEntry_get_sha, NULL, "hex SHA",  NULL},
    {NULL},
};

static PyTypeObject IndexEntryType = {
    PyObject_HEAD_INIT(NULL)
    0,                                         /* ob_size */
    "pygit2.IndexEntry",                       /* tp_name */
    sizeof(IndexEntry),                        /* tp_basicsize */
    0,                                         /* tp_itemsize */
    (destructor)IndexEntry_dealloc,            /* tp_dealloc */
    0,                                         /* tp_print */
    0,                                         /* tp_getattr */
    0,                                         /* tp_setattr */
    0,                                         /* tp_compare */
    0,                                         /* tp_repr */
    0,                                         /* tp_as_number */
    0,                                         /* tp_as_sequence */
    0,                                         /* tp_as_mapping */
    0,                                         /* tp_hash */
    0,                                         /* tp_call */
    0,                                         /* tp_str */
    0,                                         /* tp_getattro */
    0,                                         /* tp_setattro */
    0,                                         /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,                        /* tp_flags */
    "Index entry",                             /* tp_doc */
    0,                                         /* tp_traverse */
    0,                                         /* tp_clear */
    0,                                         /* tp_richcompare */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter */
    0,                                         /* tp_iternext */
    0,                                         /* tp_methods */
    0,                                         /* tp_members */
    IndexEntry_getseters,                      /* tp_getset */
    0,                                         /* tp_base */
    0,                                         /* tp_dict */
    0,                                         /* tp_descr_get */
    0,                                         /* tp_descr_set */
    0,                                         /* tp_dictoffset */
    0,                                         /* tp_init */
    0,                                         /* tp_alloc */
    0,                                         /* tp_new */
};

static void
Walker_dealloc(Walker *self) {
    git_revwalk_free(self->walk);
    Py_DECREF(self->repo);
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
Walker_hide(Walker *self, PyObject *py_hex) {
    int err;
    git_oid oid;

    if (!py_str_to_git_oid(py_hex, &oid))
        return NULL;

    err = git_revwalk_hide(self->walk, &oid);
    if (err < 0)
        return Error_set(err);

    Py_RETURN_NONE;
}

static PyObject *
Walker_push(Walker *self, PyObject *py_hex) {
    int err;
    git_oid oid;

    if (!py_str_to_git_oid(py_hex, &oid))
        return NULL;

    err = git_revwalk_push(self->walk, &oid);
    if (err < 0)
        return Error_set(err);

    Py_RETURN_NONE;
}

static PyObject *
Walker_sort(Walker *self, PyObject *py_sort_mode) {
    int sort_mode;

    sort_mode = (int)PyInt_AsLong(py_sort_mode);
    if (sort_mode == -1 && PyErr_Occurred())
        return NULL;

    git_revwalk_sorting(self->walk, sort_mode);

    Py_RETURN_NONE;
}

static PyObject *
Walker_reset(Walker *self) {
    git_revwalk_reset(self->walk);
    Py_RETURN_NONE;
}

static PyObject *
Walker_iter(Walker *self) {
    Py_INCREF(self);
    return (PyObject*)self;
}

static PyObject *
Walker_iternext(Walker *self) {
    int err;
    git_commit *commit;
    Commit *py_commit;
    git_oid oid;

    err = git_revwalk_next(&oid, self->walk);
    if (err < 0)
        return Error_set(err);

    err = git_commit_lookup(&commit, self->repo->repo, &oid);
    if (err < 0)
        return Error_set(err);

    py_commit = PyObject_New(Commit, &CommitType);
    if (!py_commit)
        return NULL;
    py_commit->commit = commit;
    Py_INCREF(self->repo);
    py_commit->repo = self->repo;

    return (PyObject*)py_commit;
}

static PyMethodDef Walker_methods[] = {
    {"hide", (PyCFunction)Walker_hide, METH_O,
     "Mark a commit (and its ancestors) uninteresting for the output."},
    {"push", (PyCFunction)Walker_push, METH_O,
     "Mark a commit to start traversal from."},
    {"reset", (PyCFunction)Walker_reset, METH_NOARGS,
     "Reset the walking machinery for reuse."},
    {"sort", (PyCFunction)Walker_sort, METH_O,
     "Change the sorting mode (this resets the walker)."},
    {NULL}
};

static PyTypeObject WalkerType = {
    PyObject_HEAD_INIT(NULL)
    0,                                         /* ob_size */
    "pygit2.Walker",                           /* tp_name */
    sizeof(Walker),                            /* tp_basicsize */
    0,                                         /* tp_itemsize */
    (destructor)Walker_dealloc,                /* tp_dealloc */
    0,                                         /* tp_print */
    0,                                         /* tp_getattr */
    0,                                         /* tp_setattr */
    0,                                         /* tp_compare */
    0,                                         /* tp_repr */
    0,                                         /* tp_as_number */
    0,                                         /* tp_as_sequence */
    0,                                         /* tp_as_mapping */
    0,                                         /* tp_hash */
    0,                                         /* tp_call */
    0,                                         /* tp_str */
    0,                                         /* tp_getattro */
    0,                                         /* tp_setattro */
    0,                                         /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_ITER, /* tp_flags */
    "Revision walker",                         /* tp_doc */
    0,                                         /* tp_traverse */
    0,                                         /* tp_clear */
    0,                                         /* tp_richcompare */
    0,                                         /* tp_weaklistoffset */
    (getiterfunc)Walker_iter,                  /* tp_iter */
    (iternextfunc)Walker_iternext,             /* tp_iternext */
    Walker_methods,                            /* tp_methods */
    0,                                         /* tp_members */
    0,                                         /* tp_getset */
    0,                                         /* tp_base */
    0,                                         /* tp_dict */
    0,                                         /* tp_descr_get */
    0,                                         /* tp_descr_set */
    0,                                         /* tp_dictoffset */
    0,                                         /* tp_init */
    0,                                         /* tp_alloc */
    0,                                         /* tp_new */
};

static PyObject *
Reference_delete(Reference *self, PyObject *args) {
    int err;

    /* 1- Delete the reference */
    err = git_reference_delete(self->reference);
    if (err < 0)
      return Error_set(err);

    /* 2- Invalidate the pointer */
    self->reference = NULL;

    /* 3- Return None */
    Py_RETURN_NONE;
}

static PyObject *
Reference_rename(Reference *self, PyObject *py_name) {
    char *c_name;
    int err;

    /* 1- Get the C name */
    c_name = PyString_AsString(py_name);
    if (c_name == NULL)
        return NULL;

    /* 2- Rename */
    err = git_reference_rename(self->reference, c_name);
    if (err < 0)
      return Error_set(err);

    /* 3- Return None */
    Py_RETURN_NONE;
}

static PyObject *
Reference_resolve(Reference *self, PyObject *args) {
    git_reference *c_reference;
    int err;

    /* 1- Resolve */
    err = git_reference_resolve(&c_reference, self->reference);
    if (err < 0)
      return Error_set(err);

    /* 2- Make an instance of Reference and return it */
    return wrap_reference(c_reference);
}

static PyObject *
Reference_get_target(Reference *self) {
    const char * c_name;

    /* 1- Get the target */
    c_name = git_reference_target(self->reference);
    if (c_name == NULL) {
        PyErr_Format(PyExc_ValueError, "Not target available");
        return NULL;
    }

    /* 2- Make a PyString and return it */
    return PyString_FromString(c_name);
}

static int
Reference_set_target(Reference *self, PyObject *py_name) {
    char *c_name;
    int err;

    /* 1- Get the C name */
    c_name = PyString_AsString(py_name);
    if (c_name == NULL)
        return -1;

    /* 2- Set the new target */
    err = git_reference_set_target(self->reference, c_name);
    if (err < 0) {
        Error_set(err);
        return -1;
    }

    /* 3- All OK */
    return 0;
}

static PyObject *
Reference_get_name(Reference *self) {
    const char *c_name;

    c_name = git_reference_name(self->reference);
    return PyString_FromString(c_name);
}

static PyObject *
Reference_get_sha(Reference *self) {
    char hex[GIT_OID_HEXSZ];
    const git_oid *oid;

    /* 1- Get the oid (only for "direct" references) */
    oid = git_reference_oid(self->reference);
    if (oid == NULL)
    {
        PyErr_Format(PyExc_ValueError,
        "sha is only available if the reference is direct (i.e. not symbolic)");
        return NULL;
    }

    /* 2- Convert and return it */
    git_oid_fmt(hex, oid);
    return PyString_FromStringAndSize(hex, GIT_OID_HEXSZ);
}

static int
Reference_set_sha(Reference *self, PyObject *py_sha) {
    git_oid oid;
    int err;

    /* 1- Get the oid from the py_sha */
    if (!py_str_to_git_oid(py_sha, &oid))
        return -1;

    /* 2- Set the oid */
    err = git_reference_set_oid (self->reference, &oid);
    if (err < 0) {
        Error_set(err);
        return -1;
    }

    /* 3- All OK */
    return 0;
}

static PyObject *
Reference_get_type(Reference *self) {
    git_rtype c_type;

    c_type = git_reference_type(self->reference);
    return PyInt_FromLong(c_type);
}

static PyMethodDef Reference_methods[] = {
    {"delete", (PyCFunction)Reference_delete, METH_NOARGS,
     "Delete this reference. It will no longer be valid!"},
    {"rename", (PyCFunction)Reference_rename, METH_O,
      "Rename the reference."},
    {"resolve", (PyCFunction)Reference_resolve, METH_NOARGS,
      "Resolve a symbolic reference and return a direct reference."},
    {NULL}
};

static PyGetSetDef Reference_getseters[] = {
    {"name", (getter)Reference_get_name, NULL,
     "The full name of a reference.", NULL},
    {"sha", (getter)Reference_get_sha, (setter)Reference_set_sha, "hex SHA",
     NULL},
    {"target", (getter)Reference_get_target, (setter)Reference_set_target,
     "target", NULL},
    {"type", (getter)Reference_get_type, NULL,
     "type (GIT_REF_OID, GIT_REF_SYMBOLIC or GIT_REF_PACKED).", NULL},
    {NULL}
};

static PyTypeObject ReferenceType = {
    PyObject_HEAD_INIT(NULL)
    0,                                         /* ob_size */
    "pygit2.Reference",                        /* tp_name */
    sizeof(Reference),                         /* tp_basicsize */
    0,                                         /* tp_itemsize */
    0,                                         /* tp_dealloc */
    0,                                         /* tp_print */
    0,                                         /* tp_getattr */
    0,                                         /* tp_setattr */
    0,                                         /* tp_compare */
    0,                                         /* tp_repr */
    0,                                         /* tp_as_number */
    0,                                         /* tp_as_sequence */
    0,                                         /* tp_as_mapping */
    0,                                         /* tp_hash */
    0,                                         /* tp_call */
    0,                                         /* tp_str */
    0,                                         /* tp_getattro */
    0,                                         /* tp_setattro */
    0,                                         /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,                        /* tp_flags */
    "Reference",                               /* tp_doc */
    0,                                         /* tp_traverse */
    0,                                         /* tp_clear */
    0,                                         /* tp_richcompare */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter */
    0,                                         /* tp_iternext */
    Reference_methods,                         /* tp_methods */
    0,                                         /* tp_members */
    Reference_getseters,                       /* tp_getset */
    0,                                         /* tp_base */
    0,                                         /* tp_dict */
    0,                                         /* tp_descr_get */
    0,                                         /* tp_descr_set */
    0,                                         /* tp_dictoffset */
    0,                                         /* tp_init */
    0,                                         /* tp_alloc */
    0,                                         /* tp_new */
};

static PyObject *
init_repository(PyObject *self, PyObject *args) {
    git_repository *repo;
    Repository *py_repo;
    const char *path;
    unsigned int bare;
    int err;

    if (!PyArg_ParseTuple(args, "sI", &path, &bare))
        return NULL;

    err = git_repository_init(&repo, path, bare);
    if (err < 0) {
        Error_set_str(err, path);
        return NULL;
    }

    py_repo = PyObject_New(Repository, &RepositoryType);
    if (!py_repo) {
        git_repository_free(repo);
        return NULL;
    }

    py_repo->repo = repo;
    py_repo->index = NULL;
    return (PyObject*)py_repo;
};

static PyMethodDef module_methods[] = {
    {"init_repository", init_repository, METH_VARARGS,
     "Creates a new Git repository in the given folder."},
    {NULL}
};

PyMODINIT_FUNC
initpygit2(void)
{
    PyObject* m;

    GitError = PyErr_NewException("pygit2.GitError", NULL, NULL);

    RepositoryType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&RepositoryType) < 0)
        return;

    /* Do not set 'tp_new' for Git objects. To create Git objects use the
     * Repository.create_XXX methods */
    if (PyType_Ready(&ObjectType) < 0)
        return;
    CommitType.tp_base = &ObjectType;
    if (PyType_Ready(&CommitType) < 0)
        return;
    TreeType.tp_base = &ObjectType;
    if (PyType_Ready(&TreeType) < 0)
        return;
    BlobType.tp_base = &ObjectType;
    if (PyType_Ready(&BlobType) < 0)
        return;
    TagType.tp_base = &ObjectType;
    if (PyType_Ready(&TagType) < 0)
        return;

    TreeEntryType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&TreeEntryType) < 0)
        return;
    IndexType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&IndexType) < 0)
        return;
    IndexEntryType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&IndexEntryType) < 0)
        return;
    WalkerType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&WalkerType) < 0)
        return;
    ReferenceType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&ReferenceType) < 0)
        return;

    m = Py_InitModule3("pygit2", module_methods,
                       "Python bindings for libgit2.");

    if (m == NULL)
      return;

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

    PyModule_AddIntConstant(m, "GIT_OBJ_ANY", GIT_OBJ_ANY);
    PyModule_AddIntConstant(m, "GIT_OBJ_COMMIT", GIT_OBJ_COMMIT);
    PyModule_AddIntConstant(m, "GIT_OBJ_TREE", GIT_OBJ_TREE);
    PyModule_AddIntConstant(m, "GIT_OBJ_BLOB", GIT_OBJ_BLOB);
    PyModule_AddIntConstant(m, "GIT_OBJ_TAG", GIT_OBJ_TAG);
    PyModule_AddIntConstant(m, "GIT_SORT_NONE", GIT_SORT_NONE);
    PyModule_AddIntConstant(m, "GIT_SORT_TOPOLOGICAL", GIT_SORT_TOPOLOGICAL);
    PyModule_AddIntConstant(m, "GIT_SORT_TIME", GIT_SORT_TIME);
    PyModule_AddIntConstant(m, "GIT_SORT_REVERSE", GIT_SORT_REVERSE);
    PyModule_AddIntConstant(m,"GIT_REF_OID", GIT_REF_OID);
    PyModule_AddIntConstant(m,"GIT_REF_SYMBOLIC", GIT_REF_SYMBOLIC);
    PyModule_AddIntConstant(m,"GIT_REF_PACKED", GIT_REF_PACKED);
}
