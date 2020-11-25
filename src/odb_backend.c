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
#include "error.h"
#include "object.h"
#include "oid.h"
#include "types.h"
#include "utils.h"
#include <git2/odb_backend.h>
#include <git2/sys/alloc.h>
#include <git2/sys/odb_backend.h>

/*
 * pygit2_odb_backend is a container for the state associated with a custom
 * implementation of git_odb_backend. It holds a list of callable references
 * which represent the Python class's implementations of each git_odb_backend
 * function. The git_odb_backend field's function pointers are assigned to the
 * pygit2_odb_backend_* functions, which handle translating between the libgit2
 * ABI and the Python ABI.
 */
struct pygit2_odb_backend
{
    git_odb_backend backend;
    PyObject *OdbBackend;
    PyObject *read,
             *read_prefix,
             *read_header,
             *write,
             *writestream,
             *readstream,
             *exists,
             *exists_prefix,
             *refresh,
             *writepack,
             *freshen;
};

static int
pygit2_odb_backend_read(void **ptr, size_t *sz,
        git_object_t *type, git_odb_backend *_be, const git_oid *oid)
{
    PyObject *args, *py_oid, *result;
    struct pygit2_odb_backend *be = (struct pygit2_odb_backend *)_be;

    py_oid = git_oid_to_python(oid);
    if (py_oid == NULL)
        return GIT_EUSER;

    args = Py_BuildValue("(N)", py_oid);
    result = PyObject_CallObject(be->read, args);
    Py_DECREF(args);

    if (result == NULL)
        return git_error_for_exc();

    const char *bytes;
    if (!PyArg_ParseTuple(result, "ny#", type, &bytes, sz) || !bytes) {
        Py_DECREF(result);
        return GIT_EUSER;
    }

    *ptr = git_odb_backend_data_alloc(_be, *sz);
    if (!*ptr) {
        Py_DECREF(result);
        return GIT_EUSER;
    }

    memcpy(*ptr, bytes, *sz);
    Py_DECREF(result);
    return 0;
}

static int
pygit2_odb_backend_read_prefix(git_oid *oid_out, void **ptr, size_t *sz,
        git_object_t *type, git_odb_backend *_be,
        const git_oid *short_oid, size_t len)
{
    PyObject *args, *py_oid, *py_oid_out, *result;
    struct pygit2_odb_backend *be = (struct pygit2_odb_backend *)_be;

    py_oid = git_oid_to_python(short_oid);
    if (py_oid == NULL)
        return GIT_EUSER;

    args = Py_BuildValue("(N)", py_oid);
    result = PyObject_CallObject(be->read_prefix, args);
    Py_DECREF(args);

    if (result == NULL)
        return git_error_for_exc();

    const char *bytes;
    if (!PyArg_ParseTuple(result, "Ony#",
                &py_oid_out, type, &bytes, sz) || !bytes) {
        Py_DECREF(result);
        return GIT_EUSER;
    }


    *ptr = git_odb_backend_data_alloc(_be, *sz);
    if (!*ptr) {
        Py_DECREF(result);
        return GIT_EUSER;
    }

    memcpy(*ptr, bytes, *sz);
    py_oid_to_git_oid(py_oid_out, oid_out);
    Py_DECREF(result);
    return 0;
}

static int
pygit2_odb_backend_read_header(size_t *len, git_object_t *type,
        git_odb_backend *_be, const git_oid *oid)
{
    PyObject *args, *py_oid, *result;
    struct pygit2_odb_backend *be = (struct pygit2_odb_backend *)_be;

    py_oid = git_oid_to_python(oid);
    if (py_oid == NULL)
        return GIT_EUSER;

    args = Py_BuildValue("(N)", py_oid);
    result = PyObject_CallObject(be->read_header, args);
    Py_DECREF(args);

    if (result == NULL)
        return git_error_for_exc();

    if (!PyArg_ParseTuple(result, "nn", type, len)) {
        Py_DECREF(result);
        return GIT_EUSER;
    }

    Py_DECREF(result);
    return 0;
}

static int
pygit2_odb_backend_write(git_odb_backend *_be, const git_oid *oid,
        const void *data, size_t sz, git_object_t typ)
{
    PyObject *args, *py_oid, *result;
    struct pygit2_odb_backend *be = (struct pygit2_odb_backend *)_be;

    py_oid = git_oid_to_python(oid);
    if (py_oid == NULL)
        return GIT_EUSER;

    args = Py_BuildValue("(Ny#n)", py_oid, data, sz, typ);
    result = PyObject_CallObject(be->write, args);
    Py_DECREF(args);

    if (result == NULL)
        return git_error_for_exc();

    Py_DECREF(result);
    return 0;
}

static int
pygit2_odb_backend_exists(git_odb_backend *_be, const git_oid *oid)
{
    PyObject *args, *py_oid, *result;
    struct pygit2_odb_backend *be = (struct pygit2_odb_backend *)_be;

    py_oid = git_oid_to_python(oid);
    if (py_oid == NULL)
        return GIT_EUSER;

    args = Py_BuildValue("(N)", py_oid);
    result = PyObject_CallObject(be->exists, args);
    Py_DECREF(args);

    if (result == NULL)
        return git_error_for_exc();

    int r = PyObject_IsTrue(result);
    Py_DECREF(result);
    return r;
}

static int
pygit2_odb_backend_exists_prefix(git_oid *out, git_odb_backend *_be,
        const git_oid *partial, size_t len)
{
    PyObject *args, *py_oid, *py_oid_out, *result;
    struct pygit2_odb_backend *be = (struct pygit2_odb_backend *)_be;

    py_oid = git_oid_to_python(partial);
    if (py_oid == NULL)
        return GIT_EUSER;

    args = Py_BuildValue("(N)", py_oid);
    result = PyObject_CallObject(be->exists_prefix, args);
    Py_DECREF(args);

    if (result == NULL)
        return git_error_for_exc();

    if (!PyArg_ParseTuple(result, "O", &py_oid_out)) {
        Py_DECREF(result);
        return GIT_EUSER;
    }

    Py_DECREF(result);

    if (py_oid_out == Py_None) {
        return GIT_ENOTFOUND;
    }

    py_oid_to_git_oid(py_oid_out, out);
    Py_DECREF(py_oid_out);
    return 0;
}

static int
pygit2_odb_backend_refresh(git_odb_backend *_be)
{
    struct pygit2_odb_backend *be = (struct pygit2_odb_backend *)_be;
    PyObject_CallObject(be->exists_prefix, NULL);
    return git_error_for_exc();
}

static int
pygit2_odb_backend_foreach(git_odb_backend *_be,
        git_odb_foreach_cb cb, void *payload)
{
    PyObject *item;
    git_oid oid;
    struct pygit2_odb_backend *be = (struct pygit2_odb_backend *)_be;
    PyObject *iterator = PyObject_GetIter((PyObject *)be->OdbBackend);
    assert(iterator);

    while ((item = PyIter_Next(iterator))) {
        py_oid_to_git_oid(item, &oid);
        cb(&oid, payload);
        Py_DECREF(item);
    }

    return git_error_for_exc();
}

static void
pygit2_odb_backend_free(git_odb_backend *_be)
{
    struct pygit2_odb_backend *be = (struct pygit2_odb_backend *)_be;
    Py_DECREF(be->OdbBackend);
}

int
OdbBackend_init(OdbBackend *self, PyObject *args, PyObject *kwds)
{
    if (args && PyTuple_Size(args) > 0) {
        PyErr_SetString(PyExc_TypeError,
                        "OdbBackend takes no arguments");
        return -1;
    }

    if (kwds && PyDict_Size(kwds) > 0) {
        PyErr_SetString(PyExc_TypeError,
                        "OdbBackend takes no keyword arguments");
        return -1;
    }

    struct pygit2_odb_backend *be = calloc(1, sizeof(struct pygit2_odb_backend));
    be->backend.version = GIT_ODB_BACKEND_VERSION;
    be->OdbBackend = (PyObject *)self;

    if (PyObject_HasAttrString((PyObject *)self, "read")) {
        be->read = PyObject_GetAttrString((PyObject *)self, "read");
        be->backend.read = pygit2_odb_backend_read;
    }

    if (PyObject_HasAttrString((PyObject *)self, "read_prefix")) {
        be->read_prefix = PyObject_GetAttrString(
                (PyObject *)self, "read_prefix");
        be->backend.read_prefix = pygit2_odb_backend_read_prefix;
    }

    if (PyObject_HasAttrString((PyObject *)self, "read_header")) {
        be->read_header = PyObject_GetAttrString(
                (PyObject *)self, "read_header");
        be->backend.read_header = pygit2_odb_backend_read_header;
    }

    if (PyObject_HasAttrString((PyObject *)self, "write")) {
        be->write = PyObject_GetAttrString(
                (PyObject *)self, "write");
        be->backend.write = pygit2_odb_backend_write;
    }

    /* TODO: Stream-based read/write
    if (PyObject_HasAttrString((PyObject *)self, "writestream")) {
        be->writestream = PyObject_GetAttrString(
                (PyObject *)self, "writestream");
        be->backend.writestream = pygit2_odb_backend_writestream;
    }

    if (PyObject_HasAttrString((PyObject *)self, "readstream")) {
        be->readstream = PyObject_GetAttrString(
                (PyObject *)self, "readstream");
        be->backend.readstream = pygit2_odb_backend_readstream;
    }
    */

    if (PyObject_HasAttrString((PyObject *)self, "exists")) {
        be->exists = PyObject_GetAttrString(
                (PyObject *)self, "exists");
        be->backend.exists = pygit2_odb_backend_exists;
    }

    if (PyObject_HasAttrString((PyObject *)self, "exists_prefix")) {
        be->exists_prefix = PyObject_GetAttrString(
                (PyObject *)self, "exists_prefix");
        be->backend.exists_prefix = pygit2_odb_backend_exists_prefix;
    }

    if (PyObject_HasAttrString((PyObject *)self, "refresh")) {
        be->refresh = PyObject_GetAttrString(
                (PyObject *)self, "refresh");
        be->backend.refresh = pygit2_odb_backend_refresh;
    }

    if (PyIter_Check((PyObject *)self)) {
        be->backend.foreach = pygit2_odb_backend_foreach;
    }

    /* TODO:
    if (PyObject_HasAttrString((PyObject *)self, "writepack")) {
        be->writepack = PyObject_GetAttrString(
                (PyObject *)self, "writepack");
        be->backend.writepack = pygit2_odb_backend_writepack;
        Py_INCREF(be->writepack);
    }

    if (PyObject_HasAttrString((PyObject *)self, "freshen")) {
        be->freshen = PyObject_GetAttrString(
                (PyObject *)self, "freshen");
        be->backend.freshen = pygit2_odb_backend_freshen;
        Py_INCREF(be->freshen);
    }
    */

    Py_INCREF((PyObject *)self);
    be->backend.free = pygit2_odb_backend_free;

    self->odb_backend = (git_odb_backend *)be;
    return 0;
}

void
OdbBackend_dealloc(OdbBackend *self)
{
    if (self->odb_backend && self->odb_backend->read == pygit2_odb_backend_read) {
        struct pygit2_odb_backend *be = (struct pygit2_odb_backend *)self->odb_backend;
        Py_CLEAR(be->read);
        Py_CLEAR(be->read_prefix);
        Py_CLEAR(be->read_header);
        Py_CLEAR(be->write);
        Py_CLEAR(be->writestream);
        Py_CLEAR(be->readstream);
        Py_CLEAR(be->exists);
        Py_CLEAR(be->exists_prefix);
        Py_CLEAR(be->refresh);
        Py_CLEAR(be->writepack);
        Py_CLEAR(be->freshen);
        free(be);
    }

    Py_TYPE(self)->tp_free((PyObject *) self);
}

static int
OdbBackend_build_as_iter(const git_oid *oid, void *accum)
{
    int err;

    PyObject *py_oid = git_oid_to_python(oid);
    if (py_oid == NULL)
        return GIT_EUSER;

    err = PyList_Append((PyObject*)accum, py_oid);
    if (err < 0)
        return GIT_EUSER;

    return 0;
}

PyObject *
OdbBackend_as_iter(OdbBackend *self)
{
    int err;
    PyObject *accum = PyList_New(0);
    PyObject *ret = NULL;

    err = self->odb_backend->foreach(self->odb_backend,
            OdbBackend_build_as_iter, (void*)accum);
    if (err == GIT_EUSER)
        goto exit;
    if (err < 0) {
        ret = Error_set(err);
        goto exit;
    }

    ret = PyObject_GetIter(accum);

exit:
    Py_DECREF(accum);
    return ret;
}

PyDoc_STRVAR(OdbBackend_read__doc__,
    "read(oid) -> (type, data)\n"
    "\n"
    "Read raw object data from this odb backend.\n");

PyObject *
OdbBackend_read(OdbBackend *self, PyObject *py_hex)
{
    int err;
    git_oid oid;
    git_object_t type;
    size_t len, sz;
    void *data;
    PyObject* tuple;

    if (self->odb_backend->read == NULL) {
        Py_INCREF(Py_NotImplemented);
        return Py_NotImplemented;
    }

    len = py_oid_to_git_oid(py_hex, &oid);
    if (len == 0)
        return NULL;

    err = self->odb_backend->read(&data, &sz, &type, self->odb_backend, &oid);
    if (err != 0) {
        Error_set_oid(err, &oid, len);
        return NULL;
    }

    tuple = Py_BuildValue("(ny#)", type, data, sz);

    git_odb_backend_data_free(self->odb_backend, data);

    return tuple;
}

PyDoc_STRVAR(OdbBackend_read_prefix__doc__,
    "read_prefix(oid) -> (oid, type, data)\n"
    "\n"
    "Read raw object data from this odb backend based on an oid prefix.\n");

PyObject *
OdbBackend_read_prefix(OdbBackend *self, PyObject *py_hex)
{
    int err;
    git_oid oid, oid_out;
    git_object_t type;
    size_t len, sz;
    void *data;
    PyObject *tuple, *py_oid_out;

    if (self->odb_backend->read_prefix == NULL) {
        Py_INCREF(Py_NotImplemented);
        return Py_NotImplemented;
    }

    len = py_oid_to_git_oid(py_hex, &oid);
    if (len == 0)
        return NULL;

    err = self->odb_backend->read_prefix(&oid_out,
            &data, &sz, &type, self->odb_backend, &oid, len);
    if (err != 0) {
        Error_set_oid(err, &oid, len);
        return NULL;
    }

    py_oid_out = git_oid_to_python(&oid_out);
    if (py_oid_out == NULL) {
        return Error_set_exc(PyExc_MemoryError);
    }
    tuple = Py_BuildValue("(ny#O)", type, data, sz, py_oid_out);

    git_odb_backend_data_free(self->odb_backend, data);

    return tuple;
}

PyDoc_STRVAR(OdbBackend_read_header__doc__,
    "read_header(oid) -> (type, len)\n"
    "\n"
    "Read raw object header from this odb backend.");

PyObject *
OdbBackend_read_header(OdbBackend *self, PyObject *py_hex)
{
    int err;
    size_t len;
    git_object_t type;
    git_oid oid;

    if (self->odb_backend->read_header == NULL) {
        Py_INCREF(Py_NotImplemented);
        return Py_NotImplemented;
    }

    len = py_oid_to_git_oid(py_hex, &oid);
    if (len == 0)
        return NULL;

    err = self->odb_backend->read_header(&len, &type, self->odb_backend, &oid);
    if (err != 0) {
        Error_set_oid(err, &oid, len);
        return NULL;
    }

    return Py_BuildValue("(ni)", type, len);
}

PyDoc_STRVAR(OdbBackend_exists__doc__,
    "exists(oid) -> bool\n"
    "\n"
    "Returns true if the given oid can be found in this odb.");

PyObject *
OdbBackend_exists(OdbBackend *self, PyObject *py_hex)
{
    int result;
    size_t len;
    git_oid oid;

    if (self->odb_backend->exists == NULL) {
        Py_INCREF(Py_NotImplemented);
        return Py_NotImplemented;
    }

    len = py_oid_to_git_oid(py_hex, &oid);
    if (len == 0)
        return NULL;

    result = self->odb_backend->exists(self->odb_backend, &oid);
    if (result < 0)
        return Error_set(result);
    else if (result == 0)
        Py_RETURN_FALSE;
    else
        Py_RETURN_TRUE;
}

PyDoc_STRVAR(OdbBackend_exists_prefix__doc__,
    "exists_prefix(partial oid) -> complete oid\n"
    "\n"
    "Given a partial oid, returns the full oid. Raises KeyError if not found,\n"
    "or ValueError if ambiguous.");

PyObject *
OdbBackend_exists_prefix(OdbBackend *self, PyObject *py_hex)
{
    int result;
    size_t len;
    git_oid oid;

    if (self->odb_backend->exists_prefix == NULL) {
        Py_INCREF(Py_NotImplemented);
        return Py_NotImplemented;
    }

    len = py_oid_to_git_oid(py_hex, &oid);
    if (len == 0)
        return NULL;

    git_oid out;
    result = self->odb_backend->exists_prefix(&out,
            self->odb_backend, &oid, len);

    if (result < 0)
        return Error_set(result);

    return git_oid_to_python(&out);
}

PyDoc_STRVAR(OdbBackend_refresh__doc__,
    "refresh()\n"
    "\n"
    "If the backend supports a refreshing mechanism, this function will invoke\n"
    "it. However, the backend implementation should try to stay up-to-date as\n"
    "much as possible by itself as libgit2 will not automatically invoke this\n"
    "function. For instance, a potential strategy for the backend\n"
    "implementation to utilize this could be internally calling the refresh\n"
    "function on failed lookups.");

PyObject *
OdbBackend_refresh(OdbBackend *self)
{
    if (self->odb_backend->refresh == NULL) {
        /* XXX: Should we no-op instead? */
        Py_INCREF(Py_NotImplemented);
        return Py_NotImplemented;
    }
    self->odb_backend->refresh(self->odb_backend);
    Py_RETURN_NONE;
}

/*
 * TODO:
 * - write
 * - writepack
 * - writestream
 * - readstream
 * - freshen
 */
PyMethodDef OdbBackend_methods[] = {
    METHOD(OdbBackend, read, METH_O),
    METHOD(OdbBackend, read_prefix, METH_O),
    METHOD(OdbBackend, read_header, METH_O),
    METHOD(OdbBackend, exists, METH_O),
    METHOD(OdbBackend, exists_prefix, METH_O),
    METHOD(OdbBackend, refresh, METH_NOARGS),
    {NULL}
};

PyDoc_STRVAR(OdbBackend__doc__, "Object database backend.");

PyTypeObject OdbBackendType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.OdbBackend",                      /* tp_name           */
    sizeof(OdbBackend),                        /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)OdbBackend_dealloc,            /* tp_dealloc        */
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
    OdbBackend__doc__,                         /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    (getiterfunc)OdbBackend_as_iter,           /* tp_iter           */
    0,                                         /* tp_iternext       */
    OdbBackend_methods,                        /* tp_methods        */
    0,                                         /* tp_members        */
    0,                                         /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    (initproc)OdbBackend_init,                 /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};

PyObject *
wrap_odb_backend(git_odb_backend *c_odb_backend)
{
    OdbBackend *pygit2_odb_backend = PyObject_New(OdbBackend, &OdbBackendType);

    if (pygit2_odb_backend)
        pygit2_odb_backend->odb_backend = c_odb_backend;

    return (PyObject *)pygit2_odb_backend;
}

PyDoc_STRVAR(OdbBackendPack__doc__, "Object database backend for packfiles.");

int
OdbBackendPack_init(OdbBackendPack *self, PyObject *args, PyObject *kwds)
{
    if (kwds && PyDict_Size(kwds) > 0) {
        PyErr_SetString(PyExc_TypeError, "OdbBackendPack takes no keyword arguments");
        return -1;
    }

    PyObject *py_path;
    if (!PyArg_ParseTuple(args, "O", &py_path))
        return -1;

    char *path = pgit_encode_fsdefault(py_path);
    if (path == NULL)
        return -1;

    int err = git_odb_backend_pack(&self->super.odb_backend, path);
    free(path);
    if (err) {
        Error_set(err);
        return -1;
    }

    return 0;
}

PyTypeObject OdbBackendPackType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.OdbBackendPack",                  /* tp_name           */
    sizeof(OdbBackendPack),                    /* tp_basicsize      */
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
    Py_TPFLAGS_DEFAULT,                        /* tp_flags          */
    OdbBackendPack__doc__,                     /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    0,                                         /* tp_methods        */
    0,                                         /* tp_members        */
    0,                                         /* tp_getset         */
    &OdbBackendType,                           /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    (initproc)OdbBackendPack_init,             /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};

PyDoc_STRVAR(OdbBackendLoose__doc__,
        "OdbBackendLoose(objects_dir, compression_level,"
        " do_fsync, dir_mode=0, file_mode=0)\n"
        "\n"
        "Object database backend for loose objects.\n"
        "\n"
        "Parameters:\n"
        "\n"
        "objects_dir\n"
        "    path to top-level object dir on disk\n"
        "\n"
        "compression_level\n"
        "    zlib compression level to use\n"
        "\n"
        "do_fsync\n"
        "    true to fsync() after writing\n"
        "\n"
        "dir_mode\n"
        "    mode for new directories, or 0 for default\n"
        "\n"
        "file_mode\n"
        "    mode for new files, or 0 for default");

int
OdbBackendLoose_init(OdbBackendLoose *self, PyObject *args, PyObject *kwds)
{
    if (kwds && PyDict_Size(kwds) > 0) {
        PyErr_SetString(PyExc_TypeError, "OdbBackendLoose takes no keyword arguments");
        return -1;
    }

    PyObject *py_path;
    int compression_level, do_fsync;
    unsigned int dir_mode = 0, file_mode = 0;
    if (!PyArg_ParseTuple(args, "Oip|II", &py_path, &compression_level,
                          &do_fsync, &dir_mode, &file_mode))
        return -1;

    char *path = pgit_encode_fsdefault(py_path);
    if (path == NULL)
        return -1;

    int err = git_odb_backend_loose(&self->super.odb_backend, path, compression_level,
                                    do_fsync, dir_mode, file_mode);
    free(path);
    if (err) {
        Error_set(err);
        return -1;
    }

    return 0;
}

PyTypeObject OdbBackendLooseType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.OdbBackendLoose",                 /* tp_name           */
    sizeof(OdbBackendLoose),                   /* tp_basicsize      */
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
    Py_TPFLAGS_DEFAULT,                        /* tp_flags          */
    OdbBackendLoose__doc__,                    /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter           */
    0,                                         /* tp_iternext       */
    0,                                         /* tp_methods        */
    0,                                         /* tp_members        */
    0,                                         /* tp_getset         */
    &OdbBackendType,                           /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    (initproc)OdbBackendLoose_init,            /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};
