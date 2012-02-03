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

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <git2.h>

/* Python 3 support */
#if PY_MAJOR_VERSION >= 3
  #define PyInt_AsLong PyLong_AsLong
  #define PyInt_Check PyLong_Check
  #define PyInt_FromLong PyLong_FromLong
  #define PyString_AS_STRING PyBytes_AS_STRING
  #define PyString_AsString PyBytes_AsString
  #define PyString_AsStringAndSize PyBytes_AsStringAndSize
  #define PyString_Check PyBytes_Check
  #define PyString_FromString PyBytes_FromString
  #define PyString_FromStringAndSize PyBytes_FromStringAndSize
  #define PyString_Size PyBytes_Size
#endif

/* Utilities */
Py_LOCAL_INLINE(PyObject*)
to_unicode(const char *value, const char *encoding, const char *errors)
{
    if (encoding == NULL)
        encoding = "utf-8";
    return PyUnicode_Decode(value, strlen(value), encoding, errors);
}

Py_LOCAL_INLINE(PyObject*)
to_bytes(const char * value)
{
    return PyString_FromString(value);
}

#if PY_MAJOR_VERSION == 2
  #define to_path(x) to_bytes(x)
  #define to_encoding(x) to_bytes(x)
#else
  #define to_path(x) to_unicode(x, Py_FileSystemDefaultEncoding, "strict")
  #define to_encoding(x) PyUnicode_DecodeASCII(x, strlen(x), "strict")
#endif

#define CHECK_REFERENCE(self)\
    if (self->reference == NULL) {\
        PyErr_SetString(GitError, "deleted reference");\
        return NULL;\
    }

#define CHECK_REFERENCE_INT(self)\
    if (self->reference == NULL) {\
        PyErr_SetString(GitError, "deleted reference");\
        return -1;\
    }

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
OBJECT_STRUCT(Blob, git_blob, blob)
OBJECT_STRUCT(Tag, git_tag, tag)
OBJECT_STRUCT(Index, git_index, index)
OBJECT_STRUCT(Walker, git_revwalk, walk)

typedef struct {
    PyObject_HEAD
    const git_tree_entry *entry;
    Tree *tree;
} TreeEntry;

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

typedef struct {
    PyObject_HEAD
    Object *obj;
    const git_signature *signature;
    const char *encoding;
} Signature;

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
static PyTypeObject SignatureType;

static PyObject *GitError;

static PyObject *
Error_type(int err)
{
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

/*
 * Python doesn't like it when the error string is NULL. Not giving
 * back an error string could be a bug in the library
 */
static const char *
git_last_error(void)
{
	const char *ret;

	ret = git_lasterror();

	return ret != NULL ? ret : "(No error information given)";
}

static PyObject *
Error_set(int err)
{
    assert(err < 0);

    if (err == GIT_EOSERR)
        return PyErr_SetFromErrno(GitError);

    PyErr_SetString(Error_type(err), git_last_error());
    return NULL;
}

static PyObject *
Error_set_str(int err, const char *str)
{
    if (err == GIT_ENOTFOUND) {
        /* KeyError expects the arg to be the missing key. */
        PyErr_SetString(PyExc_KeyError, str);
        return NULL;
    }

    return PyErr_Format(Error_type(err), "%s: %s", str, git_last_error());
}

static PyObject *
Error_set_oid(int err, const git_oid *oid, size_t len)
{
    char hex[GIT_OID_HEXSZ + 1];

    git_oid_fmt(hex, oid);
    hex[len] = '\0';
    return Error_set_str(err, hex);
}

static PyObject *
lookup_object_prefix(Repository *repo, const git_oid *oid, size_t len,
                     git_otype type)
{
    int err;
    git_object *obj;
    Object *py_obj = NULL;

    err = git_object_lookup_prefix(&obj, repo->repo, oid,
                                   (unsigned int)len, type);
    if (err < 0)
        return Error_set_oid(err, oid, len);

    switch (git_object_type(obj)) {
        case GIT_OBJ_COMMIT:
            py_obj = PyObject_New(Object, &CommitType);
            break;
        case GIT_OBJ_TREE:
            py_obj = PyObject_New(Object, &TreeType);
            break;
        case GIT_OBJ_BLOB:
            py_obj = PyObject_New(Object, &BlobType);
            break;
        case GIT_OBJ_TAG:
            py_obj = PyObject_New(Object, &TagType);
            break;
        default:
            assert(0);
    }

    if (py_obj) {
        py_obj->obj = obj;
        py_obj->repo = repo;
        Py_INCREF(repo);
    }
    return (PyObject*)py_obj;
}

static PyObject *
lookup_object(Repository *repo, const git_oid *oid, git_otype type)
{
    return lookup_object_prefix(repo, oid, GIT_OID_HEXSZ, type);
}

static git_otype
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

static PyObject *
wrap_reference(git_reference * c_reference)
{
    Reference *py_reference=NULL;

    py_reference = PyObject_New(Reference, &ReferenceType);
    if (py_reference)
        py_reference->reference = c_reference;

    return (PyObject *)py_reference;
}

static size_t
py_str_to_git_oid(PyObject *py_str, git_oid *oid)
{
    PyObject *py_hex;
    char *hex_or_bin;
    int err;
    Py_ssize_t len;

    /* Case 1: raw sha */
    if (PyString_Check(py_str)) {
        hex_or_bin = PyString_AsString(py_str);
        if (hex_or_bin == NULL)
            return 0;
        git_oid_fromraw(oid, (const unsigned char*)hex_or_bin);
        return GIT_OID_HEXSZ;
    }

    /* Case 2: hex sha */
    if (PyUnicode_Check(py_str)) {
        py_hex = PyUnicode_AsASCIIString(py_str);
        if (py_hex == NULL)
            return 0;
        err = PyString_AsStringAndSize(py_hex, &hex_or_bin, &len);
        Py_DECREF(py_hex);
        if (err)
            return 0;
        err = git_oid_fromstrn(oid, hex_or_bin, len);
        if (err < 0) {
            PyErr_SetObject(Error_type(err), py_str);
            return 0;
        }
        return len;
    }

    /* Type error */
    PyErr_Format(PyExc_TypeError,
                 "Git object id must be byte or a text string, not: %.200s",
                 Py_TYPE(py_str)->tp_name);
    return 0;
}

#define TODO_SUPPORT_SHORT_HEXS(len) \
    if (0 < len && len < GIT_OID_HEXSZ) {\
        PyErr_SetString(PyExc_NotImplementedError,\
                        "short strings not yet supported");\
        len = 0;\
    }


#define git_oid_to_python(id) \
        PyString_FromStringAndSize((const char*)id, GIT_OID_RAWSZ)

static PyObject *
git_oid_to_py_str(const git_oid *oid)
{
    char hex[GIT_OID_HEXSZ];

    git_oid_fmt(hex, oid);
    return PyUnicode_DecodeASCII(hex, GIT_OID_HEXSZ, "strict");
}

char *
py_str_to_c_str(PyObject *value, const char *encoding)
{
    char *c_str;

    /* Case 1: byte string */
    if (PyString_Check(value))
        return PyString_AsString(value);

    /* Case 2: text string */
    if (PyUnicode_Check(value)) {
        if (encoding == NULL)
            value = PyUnicode_AsUTF8String(value);
        else
            value = PyUnicode_AsEncodedString(value, encoding, "strict");
        if (value == NULL)
            return NULL;
        c_str = PyString_AsString(value);
        Py_DECREF(value);
        return c_str;
    }

    /* Type error */
    PyErr_Format(PyExc_TypeError, "unexpected %.200s",
                 Py_TYPE(value)->tp_name);
    return NULL;
}

#define py_path_to_c_str(py_path) \
        py_str_to_c_str(py_path, Py_FileSystemDefaultEncoding)


static int
Repository_init(Repository *self, PyObject *args, PyObject *kwds)
{
    char *path;
    int err;

    if (kwds) {
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

    return 0;
}

static void
Repository_dealloc(Repository *self)
{
    PyObject_GC_UnTrack(self);
    Py_XDECREF(self->index);
    git_repository_free(self->repo);
    PyObject_GC_Del(self);
}

static int
Repository_traverse(Repository *self, visitproc visit, void *arg)
{
    Py_VISIT(self->index);
    return 0;
}

static int
Repository_clear(Repository *self)
{
    Py_CLEAR(self->index);
    return 0;
}

static int
Repository_contains(Repository *self, PyObject *value)
{
    git_oid oid;
    git_odb *odb;
    size_t len;
    int err, exists;

    len = py_str_to_git_oid(value, &oid);
    TODO_SUPPORT_SHORT_HEXS(len)
    if (len == 0)
        return -1;

    err = git_repository_odb(&odb, self->repo);
    if (err < 0) {
        Error_set(err);
        return -1;
    }

    exists = git_odb_exists(odb, &oid);
    git_odb_free(odb);
    return exists;
}

static PyObject *
Repository_getitem(Repository *self, PyObject *value)
{
    git_oid oid;
    size_t len;

    len = py_str_to_git_oid(value, &oid);
    if (len == 0)
        return NULL;

    return lookup_object_prefix(self, &oid, len, GIT_OBJ_ANY);
}

static git_odb_object *
Repository_read_raw(git_repository *repo, const git_oid *oid, size_t len)
{
    git_odb *odb;
    git_odb_object *obj;
    int err;
    PyObject *aux;

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

static PyObject *
Repository_read(Repository *self, PyObject *py_hex)
{
    git_oid oid;
    int err;
    git_odb_object *obj;
    size_t len;
    PyObject* tuple;

    len = py_str_to_git_oid(py_hex, &oid);
    if (len == 0)
        return NULL;

    obj = Repository_read_raw(self->repo, &oid, len);
    if (obj == NULL)
        return NULL;

    tuple = Py_BuildValue(
        "(ns#)",
        git_odb_object_type(obj),
        git_odb_object_data(obj),
        git_odb_object_size(obj));

    git_odb_object_free(obj);
    return tuple;
}

static PyObject *
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

    stream->write(stream, buffer, buflen);
    err = stream->finalize_write(&oid, stream);
    stream->free(stream);
    return git_oid_to_python(oid.id);
}

static PyObject *
Repository_get_index(Repository *self, void *closure)
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

static PyObject *
Repository_get_path(Repository *self, void *closure)
{
    return to_path(git_repository_path(self->repo));
}

static PyObject *
Repository_get_workdir(Repository *self, void *closure)
{
    const char *c_path;

    c_path = git_repository_workdir(self->repo);
    if (c_path == NULL)
        Py_RETURN_NONE;

    return to_path(c_path);
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
    size_t len;

    if (!PyArg_ParseTuple(args, "OI", &value, &sort))
        return NULL;

    err = git_revwalk_new(&walk, self->repo);
    if (err < 0)
        return Error_set(err);

    /* Sort */
    git_revwalk_sorting(walk, sort);

    /* Push */
    if (value != Py_None) {
        len = py_str_to_git_oid(value, &oid);
        TODO_SUPPORT_SHORT_HEXS(len)
        if (len == 0) {
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
build_signature(Object *obj, const git_signature *signature,
                const char *encoding)
{
    Signature *py_signature;

    py_signature = PyObject_New(Signature, &SignatureType);
    if (py_signature) {
        Py_INCREF(obj);
        py_signature->obj = obj;
        py_signature->signature = signature;
        py_signature->encoding = encoding;
    }
    return (PyObject*)py_signature;
}

static PyObject *
Repository_create_commit(Repository *self, PyObject *args)
{
    Signature *py_author, *py_committer;
    PyObject *py_oid, *py_message, *py_parents, *py_parent;
    PyObject *py_result = NULL;
    char *message, *update_ref, *encoding = NULL;
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

    len = py_str_to_git_oid(py_oid, &oid);
    if (len == 0)
        goto out;

    message = py_str_to_c_str(py_message, encoding);

    err = git_tree_lookup_prefix(&tree, self->repo, &oid, (unsigned int)len);
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
        len = py_str_to_git_oid(py_parent, &oid);
        if (len == 0)
            goto out;
        if (git_commit_lookup_prefix(&parents[i], self->repo, &oid,
                                     (unsigned int)len))
            goto out;
    }

    err = git_commit_create(&oid, self->repo, update_ref,
                            py_author->signature, py_committer->signature,
                            encoding, message, tree, parent_count,
                            (const git_commit**)parents);
    if (err < 0) {
        Error_set(err);
        goto out;
    }

    py_result = git_oid_to_python(oid.id);

out:
    git_tree_free(tree);
    while (i > 0) {
        i--;
        git_commit_free(parents[i]);
    }
    free(parents);
    return py_result;
}

static PyObject *
Repository_create_tag(Repository *self, PyObject *args)
{
    PyObject *py_oid, *py_result = NULL;
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

    len = py_str_to_git_oid(py_oid, &oid);
    if (len == 0)
        return NULL;

    err = git_object_lookup_prefix(&target, self->repo, &oid,
                                   (unsigned int)len, target_type);
    if (err < 0)
        return Error_set_oid(err, &oid, len);

    err = git_tag_create(&oid, self->repo, tag_name, target,
                         py_tagger->signature, message, 0);
    if (err == 0)
        py_result = git_oid_to_python(oid.id);

    git_object_free(target);
    return py_result;
}

static PyObject *
Repository_listall_references(Repository *self, PyObject *args)
{
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
    py_result = PyTuple_New(c_result.count);
    if (py_result == NULL)
        goto out;

    /* 4- Fill it */
    for (index=0; index < c_result.count; index++) {
        py_string = to_path((c_result.strings)[index]);
        if (py_string == NULL) {
            Py_CLEAR(py_result);
            goto out;
        }
        PyTuple_SET_ITEM(py_result, index, py_string);
    }

out:
    git_strarray_free(&c_result);
    return py_result;
}

static PyObject *
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
    if (err < 0)
        return Error_set_str(err, c_name);

    /* 3- Make an instance of Reference and return it */
    return wrap_reference(c_reference);
}

static PyObject *
Repository_create_reference(Repository *self,  PyObject *args)
{
    PyObject *py_oid;
    git_reference *c_reference;
    char *c_name;
    git_oid oid;
    int err;
    size_t len;

    /* 1- Get the C variables */
    if (!PyArg_ParseTuple(args, "sO", &c_name, &py_oid))
        return NULL;

    len = py_str_to_git_oid(py_oid, &oid);
    TODO_SUPPORT_SHORT_HEXS(len)
    if (len == 0)
        return NULL;

    /* 2- Create the reference */
    err = git_reference_create_oid(&c_reference, self->repo, c_name, &oid, 0);
    if (err < 0)
        return Error_set(err);

    /* 3- Make an instance of Reference and return it */
    return wrap_reference(c_reference);
}

static PyObject *
Repository_create_symbolic_reference(Repository *self,  PyObject *args)
{
    git_reference *c_reference;
    char *c_name, *c_target;
    int err;

    /* 1- Get the C variables */
    if (!PyArg_ParseTuple(args, "ss", &c_name, &c_target))
        return NULL;

    /* 2- Create the reference */
    err = git_reference_create_symbolic(&c_reference, self->repo, c_name,
                                        c_target, 0);
    if (err < 0)
        return Error_set(err);

    /* 3- Make an instance of Reference and return it */
    return wrap_reference(c_reference);
}

static PyObject *
Repository_packall_references(Repository *self,  PyObject *args)
{
    int err;

    /* 1- Pack */
    err = git_reference_packall(self->repo);
    if (err < 0)
        return Error_set(err);

    /* 2- Return None */
    Py_RETURN_NONE;
}

static int
read_status_cb(const char *path, unsigned int status_flags, void *payload)
{
    /* This is the callback that will be called in git_status_foreach. It
     * will be called for every path.*/
    PyObject *flags;

    flags = PyInt_FromLong((long) status_flags);
    PyDict_SetItemString(payload, path, flags);

    return GIT_SUCCESS;
}

static PyObject *
Repository_status(Repository *self, PyObject *args)
{
    PyObject *payload_dict;

    payload_dict = PyDict_New();
    git_status_foreach(self->repo, read_status_cb, payload_dict);

    return payload_dict;
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
    {"write", (PyCFunction)Repository_write, METH_VARARGS,
     "Write raw object data into the repository. First arg is the object\n"
     "type, the second one a buffer with data. Return the object id (sha)\n"
     "of the created object."},
    {"listall_references", (PyCFunction)Repository_listall_references,
      METH_VARARGS,
      "Return a list with all the references in the repository."},
    {"lookup_reference", (PyCFunction)Repository_lookup_reference, METH_O,
       "Lookup a reference by its name in a repository."},
    {"create_reference", (PyCFunction)Repository_create_reference,
     METH_VARARGS,
     "Create a new reference \"name\" that points to the object given by its "
     "\"sha\"."},
    {"create_symbolic_reference",
      (PyCFunction)Repository_create_symbolic_reference, METH_VARARGS,
     "Create a new symbolic reference \"name\" that points to the reference\n"
     "\"target\"."},
    {"packall_references", (PyCFunction)Repository_packall_references,
     METH_NOARGS, "Pack all the loose references in the repository."},
    {"status", (PyCFunction)Repository_status, METH_NOARGS, "Reads the "
     "status of the repository and returns a dictionnary with file paths "
     "as keys and status flags as values.\nSee pygit2.GIT_STATUS_*."},
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
    PyVarObject_HEAD_INIT(NULL, 0)
    "pygit2.Repository",                       /* tp_name           */
    sizeof(Repository),                        /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)Repository_dealloc,            /* tp_dealloc        */
    0,                                         /* tp_print          */
    0,                                         /* tp_getattr        */
    0,                                         /* tp_setattr        */
    0,                                         /* tp_compare        */
    0,                                         /* tp_repr           */
    0,                                         /* tp_as_number      */
    &Repository_as_sequence,                   /* tp_as_sequence    */
    &Repository_as_mapping,                    /* tp_as_mapping     */
    0,                                         /* tp_hash           */
    0,                                         /* tp_call           */
    0,                                         /* tp_str            */
    0,                                         /* tp_getattro       */
    0,                                         /* tp_setattro       */
    0,                                         /* tp_as_buffer      */
    Py_TPFLAGS_DEFAULT |
    Py_TPFLAGS_BASETYPE |
    Py_TPFLAGS_HAVE_GC,                        /* tp_flags          */
    "Git repository",                          /* tp_doc            */
    (traverseproc)Repository_traverse,         /* tp_traverse       */
    (inquiry)Repository_clear,                 /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
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

static void
Object_dealloc(Object* self)
{
    git_object_free(self->obj);
    Py_XDECREF(self->repo);
    PyObject_Del(self);
}

static PyObject *
Object_get_oid(Object *self)
{
    const git_oid *oid;

    oid = git_object_id(self->obj);
    assert(oid);

    return git_oid_to_python(oid->id);
}

static PyObject *
Object_get_hex(Object *self)
{
    const git_oid *oid;

    oid = git_object_id(self->obj);
    assert(oid);

    return git_oid_to_py_str(oid);
}

static PyObject *
Object_get_type(Object *self)
{
    return PyInt_FromLong(git_object_type(self->obj));
}

static PyObject *
Object_read_raw(Object *self)
{
    const git_oid *oid;
    git_odb_object *obj;
    int err;
    PyObject *aux;

    oid = git_object_id(self->obj);
    assert(oid);

    obj = Repository_read_raw(self->repo->repo, oid, GIT_OID_HEXSZ);
    if (obj == NULL)
        return NULL;

    aux = PyString_FromStringAndSize(
        git_odb_object_data(obj),
        git_odb_object_size(obj));

    git_odb_object_free(obj);
    return aux;
}

static PyGetSetDef Object_getseters[] = {
    {"oid", (getter)Object_get_oid, NULL, "object id", NULL},
    {"hex", (getter)Object_get_hex, NULL, "hex oid", NULL},
    {"type", (getter)Object_get_type, NULL, "type number", NULL},
    {NULL}
};

static PyMethodDef Object_methods[] = {
    {"read_raw", (PyCFunction)Object_read_raw, METH_NOARGS,
     "Read the raw contents of the object from the repo."},
    {NULL}
};

static PyTypeObject ObjectType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "pygit2.Object",                           /* tp_name           */
    sizeof(Object),                            /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)Object_dealloc,                /* tp_dealloc        */
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
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,  /* tp_flags          */
    "Object objects",                          /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    Object_methods,                            /* tp_methods        */
    0,                                         /* tp_members        */
    Object_getseters,                          /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    0,                                         /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};

static PyObject *
Commit_get_message_encoding(Commit *commit)
{
    const char *encoding;

    encoding = git_commit_message_encoding(commit->commit);
    if (encoding == NULL)
        Py_RETURN_NONE;

    return to_encoding(encoding);
}

static PyObject *
Commit_get_message(Commit *commit)
{
    const char *message, *encoding;

    message = git_commit_message(commit->commit);
    encoding = git_commit_message_encoding(commit->commit);
    return to_unicode(message, encoding, "strict");
}

static PyObject *
Commit_get_commit_time(Commit *commit)
{
    return PyLong_FromLong(git_commit_time(commit->commit));
}

static PyObject *
Commit_get_commit_time_offset(Commit *commit)
{
    return PyLong_FromLong(git_commit_time_offset(commit->commit));
}

static PyObject *
Commit_get_committer(Commit *self)
{
    const git_signature *signature;
    const char *encoding;

    signature = git_commit_committer(self->commit);
    encoding = git_commit_message_encoding(self->commit);

    return build_signature((Object*)self, signature, encoding);
}

static PyObject *
Commit_get_author(Commit *self)
{
    const git_signature *signature;
    const char *encoding;

    signature = git_commit_author(self->commit);
    encoding = git_commit_message_encoding(self->commit);

    return build_signature((Object*)self, signature, encoding);
}

static PyObject *
Commit_get_tree(Commit *commit)
{
    git_tree *tree;
    Tree *py_tree;
    int err;

    err = git_commit_tree(&tree, commit->commit);
    if (err == GIT_ENOTFOUND)
        Py_RETURN_NONE;

    if (err < 0)
        return Error_set(err);

    py_tree = PyObject_New(Tree, &TreeType);
    if (py_tree) {
        Py_INCREF(commit->repo);
        py_tree->repo = commit->repo;
        py_tree->tree = (git_tree*)tree;
    }
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
    {"message_encoding", (getter)Commit_get_message_encoding, NULL,
     "message encoding", NULL},
    {"message", (getter)Commit_get_message, NULL, "message", NULL},
    {"commit_time", (getter)Commit_get_commit_time, NULL, "commit time",
     NULL},
    {"commit_time_offset", (getter)Commit_get_commit_time_offset, NULL,
     "commit time offset", NULL},
    {"committer", (getter)Commit_get_committer, NULL, "committer", NULL},
    {"author", (getter)Commit_get_author, NULL, "author", NULL},
    {"tree", (getter)Commit_get_tree, NULL, "tree object", NULL},
    {"parents", (getter)Commit_get_parents, NULL, "parents of this commit",
      NULL},
    {NULL}
};

static PyTypeObject CommitType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "pygit2.Commit",                           /* tp_name           */
    sizeof(Commit),                            /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    0,                                         /* tp_dealloc        */
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
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,  /* tp_flags          */
    "Commit objects",                          /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    0,                                         /* tp_methods        */
    0,                                         /* tp_members        */
    Commit_getseters,                          /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    0,                                         /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};

static void
TreeEntry_dealloc(TreeEntry *self)
{
    Py_XDECREF(self->tree);
    PyObject_Del(self);
}

static PyObject *
TreeEntry_get_attributes(TreeEntry *self)
{
    return PyInt_FromLong(git_tree_entry_attributes(self->entry));
}

static PyObject *
TreeEntry_get_name(TreeEntry *self)
{
    return to_path(git_tree_entry_name(self->entry));
}

static PyObject *
TreeEntry_get_oid(TreeEntry *self)
{
    const git_oid *oid;

    oid = git_tree_entry_id(self->entry);
    return git_oid_to_python(oid->id);
}

static PyObject *
TreeEntry_get_hex(TreeEntry *self)
{
    return git_oid_to_py_str(git_tree_entry_id(self->entry));
}

static PyObject *
TreeEntry_to_object(TreeEntry *self)
{
    const git_oid *entry_oid;

    entry_oid = git_tree_entry_id(self->entry);
    return lookup_object(self->tree->repo, entry_oid, GIT_OBJ_ANY);
}

static PyGetSetDef TreeEntry_getseters[] = {
    {"attributes", (getter)TreeEntry_get_attributes, NULL, "attributes", NULL},
    {"name", (getter)TreeEntry_get_name, NULL, "name", NULL},
    {"oid", (getter)TreeEntry_get_oid, NULL, "object id", NULL},
    {"hex", (getter)TreeEntry_get_hex, NULL, "hex oid", NULL},
    {NULL}
};

static PyMethodDef TreeEntry_methods[] = {
    {"to_object", (PyCFunction)TreeEntry_to_object, METH_NOARGS,
     "Look up the corresponding object in the repo."},
    {NULL, NULL, 0, NULL}
};

static PyTypeObject TreeEntryType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "pygit2.TreeEntry",                        /* tp_name           */
    sizeof(TreeEntry),                         /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)TreeEntry_dealloc,             /* tp_dealloc        */
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
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,  /* tp_flags          */
    "TreeEntry objects",                       /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    TreeEntry_methods,                         /* tp_methods        */
    0,                                         /* tp_members        */
    TreeEntry_getseters,                       /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    0,                                         /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};

static Py_ssize_t
Tree_len(Tree *self)
{
    assert(self->tree);
    return (Py_ssize_t)git_tree_entrycount(self->tree);
}

static int
Tree_contains(Tree *self, PyObject *py_name)
{
    char *name;

    name = py_path_to_c_str(py_name);
    if (name == NULL)
        return -1;

    return git_tree_entry_byname(self->tree, name) ? 1 : 0;
}

static TreeEntry *
wrap_tree_entry(const git_tree_entry *entry, Tree *tree)
{
    TreeEntry *py_entry;

    py_entry = PyObject_New(TreeEntry, &TreeEntryType);
    if (py_entry) {
        py_entry->entry = entry;
        py_entry->tree = tree;
        Py_INCREF(tree);
    }
    return py_entry;
}

static int
Tree_fix_index(Tree *self, PyObject *py_index)
{
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
    }
    else if (index < -slen) {
        PyErr_SetObject(PyExc_IndexError, py_index);
        return -1;
    }

    /* This function is called via mp_subscript, which doesn't do negative
     * index rewriting, so we have to do it manually. */
    if (index < 0)
        index = len + index;
    return (int)index;
}

static PyObject *
Tree_iter(Tree *self)
{
    TreeIter *iter;

    iter = PyObject_New(TreeIter, &TreeIterType);
    if (iter) {
        Py_INCREF(self);
        iter->owner = self;
        iter->i = 0;
    }
    return (PyObject*)iter;
}

static TreeEntry *
Tree_getitem_by_index(Tree *self, PyObject *py_index)
{
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
Tree_getitem(Tree *self, PyObject *value)
{
    char *name;
    const git_tree_entry *entry;

    /* Case 1: integer */
    if (PyInt_Check(value))
        return Tree_getitem_by_index(self, value);

    /* Case 2: byte or text string */
    name = py_path_to_c_str(value);
    if (name == NULL)
        return NULL;
    entry = git_tree_entry_byname(self->tree, name);
    if (!entry) {
        PyErr_SetObject(PyExc_KeyError, value);
        return NULL;
    }
    return wrap_tree_entry(entry, self);
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
    PyVarObject_HEAD_INIT(NULL, 0)
    "pygit2.Tree",                             /* tp_name           */
    sizeof(Tree),                              /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    0,                                         /* tp_dealloc        */
    0,                                         /* tp_print          */
    0,                                         /* tp_getattr        */
    0,                                         /* tp_setattr        */
    0,                                         /* tp_compare        */
    0,                                         /* tp_repr           */
    0,                                         /* tp_as_number      */
    &Tree_as_sequence,                         /* tp_as_sequence    */
    &Tree_as_mapping,                          /* tp_as_mapping     */
    0,                                         /* tp_hash           */
    0,                                         /* tp_call           */
    0,                                         /* tp_str            */
    0,                                         /* tp_getattro       */
    0,                                         /* tp_setattro       */
    0,                                         /* tp_as_buffer      */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,  /* tp_flags          */
    "Tree objects",                            /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    (getiterfunc)Tree_iter,                    /* tp_iter           */
    0,                                         /* tp_iternext       */
    0,                                         /* tp_methods        */
    0,                                         /* tp_members        */
    0,                                         /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    0,                                         /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};

static void
TreeIter_dealloc(TreeIter *self)
{
    Py_CLEAR(self->owner);
    PyObject_Del(self);
}

static TreeEntry *
TreeIter_iternext(TreeIter *self)
{
    const git_tree_entry *tree_entry;

    tree_entry = git_tree_entry_byindex(self->owner->tree, self->i);
    if (!tree_entry)
        return NULL;

    self->i += 1;
    return (TreeEntry*)wrap_tree_entry(tree_entry, self->owner);
}

static PyTypeObject TreeIterType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "pygit2.TreeIter",                       /* tp_name           */
    sizeof(TreeIter),                        /* tp_basicsize      */
    0,                                       /* tp_itemsize       */
    (destructor)TreeIter_dealloc ,           /* tp_dealloc        */
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
    (iternextfunc)TreeIter_iternext,         /* tp_iternext       */
};

static PyGetSetDef Blob_getseters[] = {
    {"data", (getter)Object_read_raw, NULL, "raw data", NULL},
    {NULL}
};

static PyTypeObject BlobType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "pygit2.Blob",                             /* tp_name           */
    sizeof(Blob),                              /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    0,                                         /* tp_dealloc        */
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
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,  /* tp_flags          */
    "Blob objects",                            /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    0,                                         /* tp_methods        */
    0,                                         /* tp_members        */
    Blob_getseters,                            /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    0,                                         /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};

static PyObject *
Tag_get_target(Tag *self)
{
    const git_oid *target_oid;
    git_otype target_type;

    target_oid = git_tag_target_oid(self->tag);
    target_type = git_tag_type(self->tag);
    return lookup_object(self->repo, target_oid, target_type);
}

static PyObject *
Tag_get_name(Tag *self)
{
    const char *name;
    name = git_tag_name(self->tag);
    if (!name)
        Py_RETURN_NONE;
    return to_unicode(name, "utf-8", "strict");
}

static PyObject *
Tag_get_tagger(Tag *self)
{
    const git_signature *signature = git_tag_tagger(self->tag);
    if (!signature)
        Py_RETURN_NONE;

    return build_signature((Object*)self, signature, "utf-8");
}

static PyObject *
Tag_get_message(Tag *self)
{
    const char *message;
    message = git_tag_message(self->tag);
    if (!message)
        Py_RETURN_NONE;
    return to_unicode(message, "utf-8", "strict");
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
    PyVarObject_HEAD_INIT(NULL, 0)
    "pygit2.Tag",                              /* tp_name           */
    sizeof(Tag),                               /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    0,                                         /* tp_dealloc        */
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
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,  /* tp_flags          */
    "Tag objects",                             /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    0,                                         /* tp_methods        */
    0,                                         /* tp_members        */
    Tag_getseters,                             /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    0,                                         /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};

static int
Index_init(Index *self, PyObject *args, PyObject *kwds)
{
    char *path;
    int err;

    if (kwds) {
        PyErr_SetString(PyExc_TypeError,
                        "Index takes no keyword arguments");
        return -1;
    }

    if (!PyArg_ParseTuple(args, "s", &path))
        return -1;

    err = git_index_open(&self->index, path);
    if (err < 0) {
        Error_set_str(err, path);
        return -1;
    }

    return 0;
}

static void
Index_dealloc(Index* self)
{
    PyObject_GC_UnTrack(self);
    Py_XDECREF(self->repo);
    git_index_free(self->index);
    PyObject_GC_Del(self);
}

static int
Index_traverse(Index *self, visitproc visit, void *arg)
{
    Py_VISIT(self->repo);
    return 0;
}

static PyObject *
Index_add(Index *self, PyObject *args)
{
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
Index_clear(Index *self)
{
    git_index_clear(self->index);
    Py_RETURN_NONE;
}

static PyObject *
Index_find(Index *self, PyObject *py_path)
{
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
Index_read(Index *self)
{
    int err;

    err = git_index_read(self->index);
    if (err < GIT_SUCCESS)
        return Error_set(err);

    Py_RETURN_NONE;
}

static PyObject *
Index_write(Index *self)
{
    int err;

    err = git_index_write(self->index);
    if (err < GIT_SUCCESS)
        return Error_set(err);

    Py_RETURN_NONE;
}

/* This is an internal function, used by Index_getitem and Index_setitem */
static int
Index_get_position(Index *self, PyObject *value)
{
    char *path;
    int idx;

    /* Case 1: integer */
    if (PyInt_Check(value)) {
        idx = (int)PyInt_AsLong(value);
        if (idx == -1 && PyErr_Occurred())
            return -1;
        if (idx < 0) {
            PyErr_SetObject(PyExc_ValueError, value);
            return -1;
        }
        return idx;
    }

    /* Case 2: byte or text string */
    path = py_path_to_c_str(value);
    if (!path)
        return -1;
    idx = git_index_find(self->index, path);
    if (idx < 0) {
        Error_set_str(idx, path);
        return -1;
    }
    return idx;
}

static int
Index_contains(Index *self, PyObject *value)
{
    char *path;
    int idx;

    path = py_path_to_c_str(value);
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
Index_iter(Index *self)
{
    IndexIter *iter;

    iter = PyObject_New(IndexIter, &IndexIterType);
    if (iter) {
        Py_INCREF(self);
        iter->owner = self;
        iter->i = 0;
    }
    return (PyObject*)iter;
}

static Py_ssize_t
Index_len(Index *self)
{
    return (Py_ssize_t)git_index_entrycount(self->index);
}

static PyObject *
wrap_index_entry(git_index_entry *entry, Index *index)
{
    IndexEntry *py_entry;

    py_entry = PyObject_New(IndexEntry, &IndexEntryType);
    if (py_entry)
        py_entry->entry = entry;

    return (PyObject*)py_entry;
}

static PyObject *
Index_getitem(Index *self, PyObject *value)
{
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
Index_setitem(Index *self, PyObject *key, PyObject *value)
{
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
Index_read_tree(Index *self, PyObject *value)
{
    git_oid oid;
    git_tree *tree;
    size_t len;
    int err;

    len = py_str_to_git_oid(value, &oid);
    TODO_SUPPORT_SHORT_HEXS(len)
    if (len == 0)
        return NULL;

    err = git_tree_lookup_prefix(&tree, self->repo->repo, &oid,
                                 (unsigned int)len);
    if (err < 0)
        return Error_set(err);

    err = git_index_read_tree(self->index, tree);
    if (err < 0)
        return Error_set(err);

    Py_RETURN_NONE;
}

static PyObject *
Index_write_tree(Index *self)
{
    git_oid oid;
    int err;

    err = git_tree_create_fromindex(&oid, self->index);
    if (err < 0)
        return Error_set(err);

    return git_oid_to_python(oid.id);
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
    {"read_tree", (PyCFunction)Index_read_tree, METH_O,
     "Update the index file from the given tree object."},
    {"write_tree", (PyCFunction)Index_write_tree, METH_NOARGS,
     "Create a tree object from the index file, return its oid."},
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
    PyVarObject_HEAD_INIT(NULL, 0)
    "pygit2.Index",                            /* tp_name           */
    sizeof(Index),                             /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)Index_dealloc,                 /* tp_dealloc        */
    0,                                         /* tp_print          */
    0,                                         /* tp_getattr        */
    0,                                         /* tp_setattr        */
    0,                                         /* tp_compare        */
    0,                                         /* tp_repr           */
    0,                                         /* tp_as_number      */
    &Index_as_sequence,                        /* tp_as_sequence    */
    &Index_as_mapping,                         /* tp_as_mapping     */
    0,                                         /* tp_hash           */
    0,                                         /* tp_call           */
    0,                                         /* tp_str            */
    0,                                         /* tp_getattro       */
    0,                                         /* tp_setattro       */
    0,                                         /* tp_as_buffer      */
    Py_TPFLAGS_DEFAULT |
    Py_TPFLAGS_BASETYPE |
    Py_TPFLAGS_HAVE_GC,                        /* tp_flags          */
    "Index file",                              /* tp_doc            */
    (traverseproc)Index_traverse,              /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    (getiterfunc)Index_iter,                   /* tp_iter           */
    0,                                         /* tp_iternext       */
    Index_methods,                             /* tp_methods        */
    0,                                         /* tp_members        */
    0,                                         /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    (initproc)Index_init,                      /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};


static void
IndexIter_dealloc(IndexIter *self)
{
    Py_CLEAR(self->owner);
    PyObject_Del(self);
}

static PyObject *
IndexIter_iternext(IndexIter *self)
{
    git_index_entry *index_entry;

    index_entry = git_index_get(self->owner->index, self->i);
    if (!index_entry)
        return NULL;

    self->i += 1;
    return wrap_index_entry(index_entry, self->owner);
}

static PyTypeObject IndexIterType = {
    PyVarObject_HEAD_INIT(NULL, 0)
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
IndexEntry_dealloc(IndexEntry *self)
{
    PyObject_Del(self);
}

static PyObject *
IndexEntry_get_mode(IndexEntry *self)
{
    return PyInt_FromLong(self->entry->mode);
}

static PyObject *
IndexEntry_get_path(IndexEntry *self)
{
    return to_path(self->entry->path);
}

static PyObject *
IndexEntry_get_oid(IndexEntry *self)
{
    return git_oid_to_python(self->entry->oid.id);
}

static PyObject *
IndexEntry_get_hex(IndexEntry *self)
{
    return git_oid_to_py_str(&self->entry->oid);
}

static PyGetSetDef IndexEntry_getseters[] = {
    {"mode", (getter)IndexEntry_get_mode, NULL, "mode", NULL},
    {"path", (getter)IndexEntry_get_path, NULL, "path", NULL},
    {"oid", (getter)IndexEntry_get_oid, NULL, "object id",  NULL},
    {"hex", (getter)IndexEntry_get_hex, NULL, "hex oid",  NULL},
    {NULL},
};

static PyTypeObject IndexEntryType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "pygit2.IndexEntry",                       /* tp_name           */
    sizeof(IndexEntry),                        /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)IndexEntry_dealloc,            /* tp_dealloc        */
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
    Py_TPFLAGS_DEFAULT,                        /* tp_flags          */
    "Index entry",                             /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    0,                                         /* tp_methods        */
    0,                                         /* tp_members        */
    IndexEntry_getseters,                      /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    0,                                         /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};

static void
Walker_dealloc(Walker *self)
{
    git_revwalk_free(self->walk);
    Py_DECREF(self->repo);
    PyObject_Del(self);
}

static PyObject *
Walker_hide(Walker *self, PyObject *py_hex)
{
    int err;
    git_oid oid;
    size_t len;

    len = py_str_to_git_oid(py_hex, &oid);
    TODO_SUPPORT_SHORT_HEXS(len)
    if (len == 0)
        return NULL;

    err = git_revwalk_hide(self->walk, &oid);
    if (err < 0)
        return Error_set(err);

    Py_RETURN_NONE;
}

static PyObject *
Walker_push(Walker *self, PyObject *py_hex)
{
    int err;
    git_oid oid;
    size_t len;

    len = py_str_to_git_oid(py_hex, &oid);
    TODO_SUPPORT_SHORT_HEXS(len)
    if (len == 0)
        return NULL;

    err = git_revwalk_push(self->walk, &oid);
    if (err < 0)
        return Error_set(err);

    Py_RETURN_NONE;
}

static PyObject *
Walker_sort(Walker *self, PyObject *py_sort_mode)
{
    int sort_mode;

    sort_mode = (int)PyInt_AsLong(py_sort_mode);
    if (sort_mode == -1 && PyErr_Occurred())
        return NULL;

    git_revwalk_sorting(self->walk, sort_mode);

    Py_RETURN_NONE;
}

static PyObject *
Walker_reset(Walker *self)
{
    git_revwalk_reset(self->walk);
    Py_RETURN_NONE;
}

static PyObject *
Walker_iter(Walker *self)
{
    Py_INCREF(self);
    return (PyObject*)self;
}

static PyObject *
Walker_iternext(Walker *self)
{
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
    if (py_commit) {
        py_commit->commit = commit;
        Py_INCREF(self->repo);
        py_commit->repo = self->repo;
    }
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
    PyVarObject_HEAD_INIT(NULL, 0)
    "pygit2.Walker",                           /* tp_name           */
    sizeof(Walker),                            /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)Walker_dealloc,                /* tp_dealloc        */
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
    Py_TPFLAGS_DEFAULT,                        /* tp_flags          */
    "Revision walker",                         /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    (getiterfunc)Walker_iter,                  /* tp_iter           */
    (iternextfunc)Walker_iternext,             /* tp_iternext       */
    Walker_methods,                            /* tp_methods        */
    0,                                         /* tp_members        */
    0,                                         /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    0,                                         /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};

static void
Reference_dealloc(Reference *self)
{
    git_reference_free(self->reference);
    PyObject_Del(self);
}

static PyObject *
Reference_delete(Reference *self, PyObject *args)
{
    int err;

    CHECK_REFERENCE(self);

    /* Delete the reference */
    err = git_reference_delete(self->reference);
    if (err < 0)
        return Error_set(err);

    self->reference = NULL; /* Invalidate the pointer */
    Py_RETURN_NONE;         /* Return None */
}

static PyObject *
Reference_rename(Reference *self, PyObject *py_name)
{
    char *c_name;
    int err;

    CHECK_REFERENCE(self);

    /* Get the C name */
    c_name = py_path_to_c_str(py_name);
    if (c_name == NULL)
        return NULL;

    /* Rename */
    err = git_reference_rename(self->reference, c_name, 0);
    if (err < 0)
        return Error_set(err);

    Py_RETURN_NONE; /* Return None */
}

static PyObject *
Reference_reload(Reference *self)
{
    int err;

    CHECK_REFERENCE(self);

    err = git_reference_reload(self->reference);
    if (err < 0) {
        self->reference = NULL;
        return Error_set(err);
    }

    Py_RETURN_NONE;
}


static PyObject *
Reference_resolve(Reference *self, PyObject *args)
{
    git_reference *c_reference;
    int err;

    CHECK_REFERENCE(self);

    /* Direct: reload */
    if (git_reference_type(self->reference) == GIT_REF_OID) {
        err = git_reference_reload(self->reference);
        if (err < 0) {
            self->reference = NULL;
            return Error_set(err);
        }
        Py_INCREF(self);
        return (PyObject *)self;
    }

    /* Symbolic: resolve */
    err = git_reference_resolve(&c_reference, self->reference);
    if (err < 0)
        return Error_set(err);

    return wrap_reference(c_reference);
}

static PyObject *
Reference_get_target(Reference *self)
{
    const char * c_name;

    CHECK_REFERENCE(self);

    /* Get the target */
    c_name = git_reference_target(self->reference);
    if (c_name == NULL) {
        PyErr_SetString(PyExc_ValueError, "no target available");
        return NULL;
    }

    /* Make a PyString and return it */
    return to_path(c_name);
}

static int
Reference_set_target(Reference *self, PyObject *py_name)
{
    char *c_name;
    int err;

    CHECK_REFERENCE_INT(self);

    /* Get the C name */
    c_name = py_path_to_c_str(py_name);
    if (c_name == NULL)
        return -1;

    /* Set the new target */
    err = git_reference_set_target(self->reference, c_name);
    if (err < 0) {
        Error_set(err);
        return -1;
    }

    return 0;
}

static PyObject *
Reference_get_name(Reference *self)
{
    CHECK_REFERENCE(self);
    return to_path(git_reference_name(self->reference));
}

static PyObject *
Reference_get_oid(Reference *self)
{
    const git_oid *oid;

    CHECK_REFERENCE(self);

    /* Get the oid (only for "direct" references) */
    oid = git_reference_oid(self->reference);
    if (oid == NULL) {
        PyErr_SetString(PyExc_ValueError,
                        "oid is only available if the reference is direct "
                        "(i.e. not symbolic)");
        return NULL;
    }

    /* Convert and return it */
    return git_oid_to_python(oid->id);
}

static int
Reference_set_oid(Reference *self, PyObject *py_hex)
{
    git_oid oid;
    int err;
    size_t len;

    CHECK_REFERENCE_INT(self);

    /* Get the oid */
    len = py_str_to_git_oid(py_hex, &oid);
    TODO_SUPPORT_SHORT_HEXS(len)
    if (len == 0)
        return -1;

    /* Set the oid */
    err = git_reference_set_oid(self->reference, &oid);
    if (err < 0) {
        Error_set(err);
        return -1;
    }

    return 0;
}

static PyObject *
Reference_get_hex(Reference *self)
{
    const git_oid *oid;

    CHECK_REFERENCE(self);

    /* Get the oid (only for "direct" references) */
    oid = git_reference_oid(self->reference);
    if (oid == NULL) {
        PyErr_SetString(PyExc_ValueError,
                        "oid is only available if the reference is direct "
                        "(i.e. not symbolic)");
        return NULL;
    }

    /* Convert and return it */
    return git_oid_to_py_str(oid);
}

static PyObject *
Reference_get_type(Reference *self)
{
    git_rtype c_type;

    CHECK_REFERENCE(self);
    c_type = git_reference_type(self->reference);
    return PyInt_FromLong(c_type);
}

static PyMethodDef Reference_methods[] = {
    {"delete", (PyCFunction)Reference_delete, METH_NOARGS,
     "Delete this reference. It will no longer be valid!"},
    {"rename", (PyCFunction)Reference_rename, METH_O,
      "Rename the reference."},
    {"reload", (PyCFunction)Reference_reload, METH_NOARGS,
     "Reload the reference from the file-system."},
    {"resolve", (PyCFunction)Reference_resolve, METH_NOARGS,
      "Resolve a symbolic reference and return a direct reference."},
    {NULL}
};

static PyGetSetDef Reference_getseters[] = {
    {"name", (getter)Reference_get_name, NULL,
     "The full name of a reference.", NULL},
    {"oid", (getter)Reference_get_oid, (setter)Reference_set_oid, "object id",
     NULL},
    {"hex", (getter)Reference_get_hex, NULL, "hex oid", NULL},
    {"target", (getter)Reference_get_target, (setter)Reference_set_target,
     "target", NULL},
    {"type", (getter)Reference_get_type, NULL,
     "type (GIT_REF_OID, GIT_REF_SYMBOLIC or GIT_REF_PACKED).", NULL},
    {NULL}
};

static PyTypeObject ReferenceType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "pygit2.Reference",                        /* tp_name           */
    sizeof(Reference),                         /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)Reference_dealloc,             /* tp_dealloc        */
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
    Py_TPFLAGS_DEFAULT,                        /* tp_flags          */
    "Reference",                               /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    Reference_methods,                         /* tp_methods        */
    0,                                         /* tp_members        */
    Reference_getseters,                       /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    0,                                         /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};

static int
Signature_init(Signature *self, PyObject *args, PyObject *kwds)
{
    PyObject *py_name;
    char *name, *email, *encoding = NULL;
    long long time;
    int offset;
    int err;
    git_signature *signature;

    if (kwds) {
        PyErr_SetString(PyExc_TypeError,
                        "Signature takes no keyword arguments");
        return -1;
    }

    if (!PyArg_ParseTuple(args, "OsLi|s",
                          &py_name, &email, &time, &offset, &encoding))
        return -1;

    name = py_str_to_c_str(py_name, encoding);

    err = git_signature_new(&signature, name, email, time, offset);
    if (err < 0) {
        Error_set(err);
        return -1;
    }

    self->obj = NULL;
    self->signature = signature;

    if (encoding) {
        self->encoding = strdup(encoding);
        if (self->encoding == NULL) {
            PyErr_NoMemory();
            return -1;
        }
    }

    return 0;
}

static void
Signature_dealloc(Signature *self)
{
    if (self->obj)
        Py_DECREF(self->obj);
    else {
        git_signature_free((git_signature*)self->signature);
        free((void*)self->encoding);
    }
    Py_TYPE(self)->tp_free((PyObject*)self);
}

static PyObject *
Signature_get_encoding(Signature *self)
{
    const char *encoding;

    encoding = self->encoding;
    if (encoding == NULL)
        encoding = "utf-8";

    return to_encoding(encoding);
}

static PyObject *
Signature_get_raw_name(Signature *self)
{
    return to_bytes(self->signature->name);
}

static PyObject *
Signature_get_raw_email(Signature *self)
{
    return to_bytes(self->signature->email);
}

static PyObject *
Signature_get_name(Signature *self)
{
    return to_unicode(self->signature->name, self->encoding, "strict");
}

static PyObject *
Signature_get_email(Signature *self)
{
    return to_unicode(self->signature->email, self->encoding, "strict");
}

static PyObject *
Signature_get_time(Signature *self)
{
    return PyInt_FromLong(self->signature->when.time);
}

static PyObject *
Signature_get_offset(Signature *self)
{
    return PyInt_FromLong(self->signature->when.offset);
}

static PyGetSetDef Signature_getseters[] = {
    {"_encoding", (getter)Signature_get_encoding, NULL, "encoding", NULL},
    {"_name", (getter)Signature_get_raw_name, NULL, "Name (bytes)", NULL},
    {"_email", (getter)Signature_get_raw_email, NULL, "Email (bytes)", NULL},
    {"name", (getter)Signature_get_name, NULL, "Name", NULL},
    {"email", (getter)Signature_get_email, NULL, "Email", NULL},
    {"time", (getter)Signature_get_time, NULL, "Time", NULL},
    {"offset", (getter)Signature_get_offset, NULL, "Offset", NULL},
    {NULL}
};

static PyTypeObject SignatureType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "pygit2.Signature",                        /* tp_name           */
    sizeof(Signature),                         /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)Signature_dealloc,             /* tp_dealloc        */
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
    Py_TPFLAGS_DEFAULT,                        /* tp_flags          */
    "Signature",                               /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    0,                                         /* tp_methods        */
    0,                                         /* tp_members        */
    Signature_getseters,                       /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    (initproc)Signature_init,                  /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};

static PyObject *
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

static PyMethodDef module_methods[] = {
    {"init_repository", init_repository, METH_VARARGS,
     "Creates a new Git repository in the given folder."},
    {NULL}
};

PyObject*
moduleinit(PyObject* m)
{
    if (m == NULL)
        return NULL;

    GitError = PyErr_NewException("pygit2.GitError", NULL, NULL);

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

    TreeEntryType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&TreeEntryType) < 0)
        return NULL;
    IndexType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&IndexType) < 0)
        return NULL;
    IndexEntryType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&IndexEntryType) < 0)
        return NULL;
    WalkerType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&WalkerType) < 0)
        return NULL;
    ReferenceType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&ReferenceType) < 0)
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

    /** Git status flags **/
    PyModule_AddIntConstant(m, "GIT_STATUS_CURRENT", GIT_STATUS_CURRENT);

    /* Flags for index status */
    PyModule_AddIntConstant(m, "GIT_STATUS_INDEX_NEW", GIT_STATUS_INDEX_NEW);
    PyModule_AddIntConstant(m, "GIT_STATUS_INDEX_MODIFIED",
                            GIT_STATUS_INDEX_MODIFIED);
    PyModule_AddIntConstant(m, "GIT_STATUS_INDEX_DELETED" ,
                            GIT_STATUS_INDEX_DELETED);

    /* Flags for worktree status */
    PyModule_AddIntConstant(m, "GIT_STATUS_WT_NEW", GIT_STATUS_WT_NEW);
    PyModule_AddIntConstant(m, "GIT_STATUS_WT_MODIFIED" ,
                            GIT_STATUS_WT_MODIFIED);
    PyModule_AddIntConstant(m, "GIT_STATUS_WT_DELETED", GIT_STATUS_WT_DELETED);

    /* Flags for ignored files */
    PyModule_AddIntConstant(m, "GIT_STATUS_IGNORED", GIT_STATUS_IGNORED);

    return m;
}


#if PY_MAJOR_VERSION < 3
  PyMODINIT_FUNC
  initpygit2(void)
  {
      PyObject* m;
      m = Py_InitModule3("pygit2", module_methods,
                         "Python bindings for libgit2.");
      moduleinit(m);
  }
#else
  static struct PyModuleDef moduledef = {
      PyModuleDef_HEAD_INIT,
      "pygit2",                        /* m_name */
      "Python bindings for libgit2.",  /* m_doc */
      -1,                              /* m_size */
      module_methods,                  /* m_methods */
      NULL,                            /* m_reload */
      NULL,                            /* m_traverse */
      NULL,                            /* m_clear */
      NULL,                            /* m_free */
  };

  PyMODINIT_FUNC
  PyInit_pygit2(void)
  {
      PyObject* m;
      m = PyModule_Create(&moduledef);
      return moduleinit(m);
  }
#endif
