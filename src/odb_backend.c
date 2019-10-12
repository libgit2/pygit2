/*
 * Copyright 2010-2019 The pygit2 contributors
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

static int
OdbBackend_build_as_iter(const git_oid *oid, void *accum)
{
    int err;

    PyObject *py_oid = git_oid_to_python(oid);
    if (py_oid == NULL)
        return GIT_EUSER;

    err = PyList_Append((PyObject*)accum, py_oid);
    Py_DECREF(py_oid);
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
    "read(oid) -> (type, data, size)\n"
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

    /* XXX: This assumes the default libgit2 allocator is in use and will
     * probably segfault and/or destroy the universe otherwise */
    free(data);

    return tuple;
}

PyMethodDef OdbBackend_methods[] = {
    METHOD(OdbBackend, read, METH_O),
    {NULL}
};

PyDoc_STRVAR(OdbBackend__doc__, "Object database backend.");

PyTypeObject OdbBackendType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.OdbBackend",                      /* tp_name           */
    sizeof(OdbBackend),                        /* tp_basicsize      */
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
    0,                                         /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};

PyObject *
wrap_odb_backend(git_odb_backend *c_odb_backend)
{
    OdbBackend *py_odb_backend = PyObject_New(OdbBackend, &OdbBackendType);

    if (py_odb_backend)
        py_odb_backend->odb_backend = c_odb_backend;

    return (PyObject *)py_odb_backend;
}

PyDoc_STRVAR(OdbBackendPack__doc__, "Object database backend for packfiles.");

int
OdbBackendPack_init(OdbBackendPack *self, PyObject *args, PyObject *kwds)
{
    PyObject *py_path;
    const char *path;
    int err;

    if (kwds && PyDict_Size(kwds) > 0) {
        PyErr_SetString(PyExc_TypeError,
                        "OdbBackendPack takes no keyword arguments");
        return -1;
    }

    if (!PyArg_ParseTuple(args, "O", &py_path))
        return -1;

    path = py_path_to_c_str(py_path);
    if (path == NULL)
        return -1;
    err = git_odb_backend_pack(&self->super.odb_backend, path);

    if (err < 0) {
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
        "OdbBackendLoose(objects_dir, compression_level,\n"
        "    do_fsync, dir_mode=0, file_mode=0)\n"
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
    PyObject *py_path;
    const char *path;
    int compression_level, do_fsync;
    unsigned int dir_mode = 0, file_mode = 0;
    int err;

    if (kwds && PyDict_Size(kwds) > 0) {
        PyErr_SetString(PyExc_TypeError,
                        "OdbBackendLoose takes no keyword arguments");
        return -1;
    }

    if (!PyArg_ParseTuple(args, "Oip|II", &py_path, &compression_level,
                &do_fsync, &dir_mode, &file_mode))
        return -1;

    path = py_path_to_c_str(py_path);
    if (path == NULL)
        return -1;
    err = git_odb_backend_loose(&self->super.odb_backend, path,
            compression_level, do_fsync, dir_mode, file_mode);

    if (err < 0) {
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
