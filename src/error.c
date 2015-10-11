/*
 * Copyright 2010-2015 The pygit2 contributors
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

#include "error.h"

PyObject *GitError;

PyObject *
Error_type(int type)
{
    const git_error* error;
    /* Expected */
    switch (type) {
        /* Input does not exist in the scope searched. */
        case GIT_ENOTFOUND:
            return PyExc_KeyError;

        /* A reference with this name already exists */
        case GIT_EEXISTS:
            return PyExc_ValueError;

        /* The given short oid is ambiguous */
        case GIT_EAMBIGUOUS:
            return PyExc_ValueError;

        /* The buffer is too short to satisfy the request */
        case GIT_EBUFS:
            return PyExc_ValueError;

        /* Invalid input spec */
        case GIT_EINVALIDSPEC:
            return PyExc_ValueError;

        /* Skip and passthrough the given ODB backend */
        case GIT_PASSTHROUGH:
            return GitError;

        /* No entries left in ref walker */
        case GIT_ITEROVER:
            return PyExc_StopIteration;
    }

    /* Critical */
    error = giterr_last();
    if (error != NULL) {
        switch (error->klass) {
            case GITERR_NOMEMORY:
                return PyExc_MemoryError;
            case GITERR_OS:
                return PyExc_OSError;
            case GITERR_INVALID:
                return PyExc_ValueError;
        }
    }
    return GitError;
}


PyObject *
Error_set(int err)
{
    assert(err < 0);

    return Error_set_exc(Error_type(err));
}

PyObject *
Error_set_exc(PyObject* exception)
{
    const git_error* error = giterr_last();
    char* message = (error == NULL) ?
            "(No error information given)" : error->message;
    PyErr_SetString(exception, message);

    return NULL;
}


PyObject *
Error_set_str(int err, const char *str)
{
    const git_error* error;
    if (err == GIT_ENOTFOUND) {
        /* KeyError expects the arg to be the missing key. */
        PyErr_SetString(PyExc_KeyError, str);
        return NULL;
    }

    error = giterr_last();
    if (error == NULL) /* Expected error - no error msg set */
        return PyErr_Format(Error_type(err), "%s", str);

    return PyErr_Format(Error_type(err), "%s: %s", str, error->message);
}

PyObject *
Error_set_oid(int err, const git_oid *oid, size_t len)
{
    char hex[GIT_OID_HEXSZ + 1];

    git_oid_fmt(hex, oid);
    hex[len] = '\0';
    return Error_set_str(err, hex);
}
