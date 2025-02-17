/*
 * Copyright 2010-2025 The pygit2 contributors
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

    py_path = to_unicode_n(buf.ptr, buf.size, NULL, NULL);
    git_buf_dispose(&buf);

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
        return Error_type_error(
            "option should be an integer, got %.200s", py_option);

    option = PyLong_AsLong(py_option);

    switch (option) {

        case GIT_OPT_GET_MWINDOW_FILE_LIMIT:
        case GIT_OPT_GET_MWINDOW_MAPPED_LIMIT:
        case GIT_OPT_GET_MWINDOW_SIZE:
        {
            size_t value;

            error = git_libgit2_opts(option, &value);
            if (error < 0)
                return Error_set(error);

            return PyLong_FromSize_t(value);
        }

        case GIT_OPT_SET_MWINDOW_FILE_LIMIT:
        case GIT_OPT_SET_MWINDOW_MAPPED_LIMIT:
        case GIT_OPT_SET_MWINDOW_SIZE:
        {
            PyObject *py_value = PyTuple_GetItem(args, 1);
            if (!py_value)
                return NULL;

            if (!PyLong_Check(py_value))
                return Error_type_error("expected integer, got %.200s", py_value);

            size_t value = PyLong_AsSize_t(py_value);
            error = git_libgit2_opts(option, value);
            if (error  < 0)
                return Error_set(error);

            Py_RETURN_NONE;
        }

        case GIT_OPT_GET_SEARCH_PATH:
        {
            PyObject *py_level = PyTuple_GetItem(args, 1);
            if (!py_level)
                return NULL;

            if (!PyLong_Check(py_level))
                return Error_type_error("level should be an integer, got %.200s", py_level);

            return get_search_path(PyLong_AsLong(py_level));
        }

        case GIT_OPT_SET_SEARCH_PATH:
        {
            PyObject *py_level = PyTuple_GetItem(args, 1);
            if (!py_level)
                return NULL;

            PyObject *py_path = PyTuple_GetItem(args, 2);
            if (!py_path)
                return NULL;

            if (!PyLong_Check(py_level))
                return Error_type_error("level should be an integer, got %.200s", py_level);

            const char *path = pgit_borrow(py_path);
            if (!path)
                return NULL;

            int err = git_libgit2_opts(option, PyLong_AsLong(py_level), path);
            if (err < 0)
                return Error_set(err);

            Py_RETURN_NONE;
        }

        case GIT_OPT_SET_CACHE_OBJECT_LIMIT:
        {
            size_t limit;
            int object_type;
            PyObject *py_object_type, *py_limit;

            py_object_type = PyTuple_GetItem(args, 1);
            if (!py_object_type)
                return NULL;

            py_limit = PyTuple_GetItem(args, 2);
            if (!py_limit)
                return NULL;

            if (!PyLong_Check(py_limit))
                return Error_type_error(
                    "limit should be an integer, got %.200s", py_limit);

            object_type = PyLong_AsLong(py_object_type);
            limit = PyLong_AsSize_t(py_limit);
            error = git_libgit2_opts(option, object_type, limit);

            if (error < 0)
                return Error_set(error);

            Py_RETURN_NONE;
        }

        case GIT_OPT_SET_CACHE_MAX_SIZE:
        {
            size_t max_size;
            PyObject *py_max_size;

            py_max_size = PyTuple_GetItem(args, 1);
            if (!py_max_size)
                return NULL;

            if (!PyLong_Check(py_max_size))
                return Error_type_error(
                    "max_size should be an integer, got %.200s", py_max_size);

            max_size = PyLong_AsSize_t(py_max_size);
            error = git_libgit2_opts(option, max_size);
            if (error < 0)
                return Error_set(error);

            Py_RETURN_NONE;
        }

        case GIT_OPT_GET_CACHED_MEMORY:
        {
            size_t current;
            size_t allowed;
            PyObject* tup = PyTuple_New(2);

            error = git_libgit2_opts(option, &current, &allowed);
            if (error < 0)
                return Error_set(error);

            PyTuple_SetItem(tup, 0, PyLong_FromLong(current));
            PyTuple_SetItem(tup, 1, PyLong_FromLong(allowed));

            return tup;
        }

        case GIT_OPT_GET_TEMPLATE_PATH:
        case GIT_OPT_SET_TEMPLATE_PATH:
        {
            Py_INCREF(Py_NotImplemented);
            return Py_NotImplemented;
        }

        case GIT_OPT_SET_SSL_CERT_LOCATIONS:
        {
            PyObject *py_file, *py_dir;
            char *file_path=NULL, *dir_path=NULL;
            int err;

            py_file = PyTuple_GetItem(args, 1);
            if (!py_file)
                return NULL;
            py_dir = PyTuple_GetItem(args, 2);
            if (!py_dir)
                return NULL;

            /* py_file and py_dir are only valid if they are strings */
            PyObject *tvalue_file = NULL;
            if (PyUnicode_Check(py_file) || PyBytes_Check(py_file))
                file_path = pgit_borrow_fsdefault(py_file, &tvalue_file);

            PyObject *tvalue_dir = NULL;
            if (PyUnicode_Check(py_dir) || PyBytes_Check(py_dir))
                dir_path = pgit_borrow_fsdefault(py_dir, &tvalue_dir);

            err = git_libgit2_opts(option, file_path, dir_path);
            Py_XDECREF(tvalue_file);
            Py_XDECREF(tvalue_dir);

            if (err)
                return Error_set(err);

            Py_RETURN_NONE;
        }

        case GIT_OPT_SET_USER_AGENT:
        {
            Py_INCREF(Py_NotImplemented);
            return Py_NotImplemented;
        }

        // int enabled
        case GIT_OPT_ENABLE_CACHING:
        case GIT_OPT_ENABLE_STRICT_OBJECT_CREATION:
        case GIT_OPT_ENABLE_STRICT_SYMBOLIC_REF_CREATION:
        case GIT_OPT_ENABLE_OFS_DELTA:
        case GIT_OPT_ENABLE_FSYNC_GITDIR:
        case GIT_OPT_ENABLE_STRICT_HASH_VERIFICATION:
        case GIT_OPT_ENABLE_UNSAVED_INDEX_SAFETY:
        case GIT_OPT_DISABLE_PACK_KEEP_FILE_CHECKS:
        case GIT_OPT_SET_OWNER_VALIDATION:
        {
            PyObject *py_value = PyTuple_GetItem(args, 1);
            if (!py_value)
                return NULL;

            if (!PyLong_Check(py_value))
                return Error_type_error("expected integer, got %.200s", py_value);

            int value = PyLong_AsSize_t(py_value);
            error = git_libgit2_opts(option, value);
            if (error < 0)
                return Error_set(error);

            Py_RETURN_NONE;
        }

        // int enabled getter
        case GIT_OPT_GET_OWNER_VALIDATION:
        {
            int enabled;

            error = git_libgit2_opts(option, &enabled);
            if (error < 0)
                return Error_set(error);

            return PyLong_FromLong(enabled);
        }

        // Not implemented
        case GIT_OPT_SET_SSL_CIPHERS:
        case GIT_OPT_GET_USER_AGENT:
        case GIT_OPT_GET_WINDOWS_SHAREMODE:
        case GIT_OPT_SET_WINDOWS_SHAREMODE:
        case GIT_OPT_SET_ALLOCATOR:
        case GIT_OPT_GET_PACK_MAX_OBJECTS:
        case GIT_OPT_SET_PACK_MAX_OBJECTS:
        {
            Py_INCREF(Py_NotImplemented);
            return Py_NotImplemented;
        }

    }

    PyErr_SetString(PyExc_ValueError, "unknown/unsupported option value");
    return NULL;
}
