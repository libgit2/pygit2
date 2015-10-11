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

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <structmember.h>
#include "error.h"
#include "types.h"
#include "utils.h"

extern PyObject *GitError;

static PyObject *
get_search_path(long level)
{
    git_buf buf = {NULL};
    PyObject *py_path;
    int err;

    err = git_libgit2_opts(GIT_OPT_GET_SEARCH_PATH, level, &buf);
    if (err < 0)
        return Error_set(err);

    py_path = to_unicode(buf.ptr, NULL, NULL);
    git_buf_free(&buf);

    if (!py_path)
        return NULL;

    return py_path;
}

PyObject *
option(PyObject *self, PyObject *args)
{
    long option;
    int error;
    PyObject *py_option;

    py_option = PyTuple_GetItem(args, 0);
    if (!py_option)
        return NULL;

    if (!PyLong_Check(py_option))
        goto on_non_integer;

    option = PyLong_AsLong(py_option);

    switch (option) {
        case GIT_OPT_GET_SEARCH_PATH:
        {
            PyObject *py_level;

            py_level = PyTuple_GetItem(args, 1);
            if (!py_level)
                return NULL;

            if (!PyLong_Check(py_level))
                goto on_non_integer;

            return get_search_path(PyLong_AsLong(py_level));
            break;
        }

        case GIT_OPT_SET_SEARCH_PATH:
        {
            PyObject *py_level, *py_path, *tpath;
            const char *path;
            int err;

            py_level = PyTuple_GetItem(args, 1);
            if (!py_level)
                return NULL;

            py_path = PyTuple_GetItem(args, 2);
            if (!py_path)
                return NULL;

            if (!PyLong_Check(py_level))
                goto on_non_integer;

            path = py_str_borrow_c_str(&tpath, py_path, NULL);
            if (!path)
                return NULL;

            err = git_libgit2_opts(GIT_OPT_SET_SEARCH_PATH, PyLong_AsLong(py_level), path);
            Py_DECREF(tpath);

            if (err < 0) {
                Error_set(err);
                return NULL;
            }

            Py_RETURN_NONE;
            break;
        }

        case GIT_OPT_GET_MWINDOW_SIZE:
        {
            size_t size;

            error = git_libgit2_opts(GIT_OPT_GET_MWINDOW_SIZE, &size);
            if (error < 0) {
                Error_set(error);
                return NULL;
            }

            return PyLong_FromSize_t(size);

            break;
        }

        case GIT_OPT_SET_MWINDOW_SIZE:
        {
            size_t size;
            PyObject *py_size;

            py_size = PyTuple_GetItem(args, 1);
            if (!py_size)
                return NULL;

            if (!PyLong_Check(py_size))
                goto on_non_integer;

            size = PyLong_AsSize_t(py_size);
            error = git_libgit2_opts(GIT_OPT_SET_MWINDOW_SIZE, size);
            if (error  < 0) {
                Error_set(error);
                return NULL;
            }

            Py_RETURN_NONE;
            break;
        }
    }

    PyErr_SetString(PyExc_ValueError, "unknown/unsupported option value");
    return NULL;

on_non_integer:
    PyErr_SetString(PyExc_TypeError, "option is not an integer");
    return NULL;
}
