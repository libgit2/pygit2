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
#include "utils.h"
#include "object.h"
#include "blob.h"

extern PyObject *GitError;

extern PyTypeObject BlobType;

PyDoc_STRVAR(Blob_size__doc__, "Size.");

PyObject *
Blob_size__get__(Blob *self)
{
    return PyLong_FromLongLong(git_blob_rawsize(self->blob));
}


PyDoc_STRVAR(Blob_is_binary__doc__, "True if binary data, False if not.");

PyObject *
Blob_is_binary__get__(Blob *self)
{
    if (git_blob_is_binary(self->blob))
        Py_RETURN_TRUE;
    Py_RETURN_FALSE;
}


PyDoc_STRVAR(Blob_data__doc__,
  "The contents of the blob, a bytes string. This is the same as\n"
  "Blob.read_raw()");

PyDoc_STRVAR(Blob__pointer__doc__, "Get the blob's pointer. For internal use only.");
PyObject *
Blob__pointer__get__(Blob *self)
{
    /* Bytes means a raw buffer */
    return PyBytes_FromStringAndSize((char *) &self->blob, sizeof(git_blob *));
}

PyGetSetDef Blob_getseters[] = {
    GETTER(Blob, size),
    GETTER(Blob, is_binary),
    {"data", (getter)Object_read_raw, NULL, Blob_data__doc__, NULL},
    GETTER(Blob, _pointer),
    {NULL}
};

static int
Blob_getbuffer(Blob *self, Py_buffer *view, int flags)
{
    return PyBuffer_FillInfo(view, (PyObject *) self,
                             (void *) git_blob_rawcontent(self->blob),
                             git_blob_rawsize(self->blob), 1, flags);
}

#if PY_MAJOR_VERSION == 2

static Py_ssize_t
Blob_getreadbuffer(Blob *self, Py_ssize_t index, const void **ptr)
{
    if (index != 0) {
        PyErr_SetString(PyExc_SystemError,
                        "accessing non-existent blob segment");
        return -1;
    }
    *ptr = (void *) git_blob_rawcontent(self->blob);
    return git_blob_rawsize(self->blob);
}

static Py_ssize_t
Blob_getsegcount(Blob *self, Py_ssize_t *lenp)
{
    if (lenp)
        *lenp = git_blob_rawsize(self->blob);

    return 1;
}

static PyBufferProcs Blob_as_buffer = {
    (readbufferproc)Blob_getreadbuffer,
    NULL,                       /* bf_getwritebuffer */
    (segcountproc)Blob_getsegcount,
    NULL,                       /* charbufferproc */
    (getbufferproc)Blob_getbuffer,
};

#else

static PyBufferProcs Blob_as_buffer = {
    (getbufferproc)Blob_getbuffer,
};

#endif  /* python 2 vs python 3 buffers */

PyDoc_STRVAR(Blob__doc__, "Blob object.\n"
  "\n"
  "Blobs implement the buffer interface, which means you can get access\n"
  "to its data via `memoryview(blob)` without the need to create a copy."
);

PyTypeObject BlobType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.Blob",                            /* tp_name           */
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
    &Blob_as_buffer,                           /* tp_as_buffer      */
#if PY_MAJOR_VERSION == 2
    Py_TPFLAGS_DEFAULT |                       /* tp_flags          */
    Py_TPFLAGS_HAVE_GETCHARBUFFER |
    Py_TPFLAGS_HAVE_NEWBUFFER,
#else
    Py_TPFLAGS_DEFAULT,                        /* tp_flags          */
#endif
    Blob__doc__,                               /* tp_doc            */
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
