/*
 * Copyright 2010-2013 The pygit2 contributors
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

#ifndef INCLUDE_pygit2_repository_h
#define INCLUDE_pygit2_repository_h

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <git2.h>
#include "types.h"

int  Repository_init(Repository *self, PyObject *args, PyObject *kwds);
int  Repository_traverse(Repository *self, visitproc visit, void *arg);
int  Repository_clear(Repository *self);
int  Repository_contains(Repository *self, PyObject *value);

git_odb_object*
Repository_read_raw(git_repository *repo, const git_oid *oid, size_t len);

PyObject* Repository_head(Repository *self);
PyObject* Repository_getitem(Repository *self, PyObject *value);
PyObject* Repository_read(Repository *self, PyObject *py_hex);
PyObject* Repository_write(Repository *self, PyObject *args);
PyObject* Repository_get_index(Repository *self, void *closure);
PyObject* Repository_get_path(Repository *self, void *closure);
PyObject* Repository_get_workdir(Repository *self, void *closure);
PyObject* Repository_get_config(Repository *self, void *closure);
PyObject* Repository_walk(Repository *self, PyObject *args);
PyObject* Repository_create_blob(Repository *self, PyObject *args);
PyObject* Repository_create_blob_fromfile(Repository *self, PyObject *args);
PyObject* Repository_create_commit(Repository *self, PyObject *args);
PyObject* Repository_create_tag(Repository *self, PyObject *args);
PyObject* Repository_create_branch(Repository *self, PyObject *args);
PyObject* Repository_listall_references(Repository *self, PyObject *args);
PyObject* Repository_listall_branches(Repository *self, PyObject *args);
PyObject* Repository_lookup_reference(Repository *self, PyObject *py_name);

PyObject*
Repository_create_reference(Repository *self, PyObject *args, PyObject* kw);

PyObject* Repository_packall_references(Repository *self,  PyObject *args);
PyObject* Repository_status(Repository *self, PyObject *args);
PyObject* Repository_status_file(Repository *self, PyObject *value);
PyObject* Repository_TreeBuilder(Repository *self, PyObject *args);

PyObject* Repository_blame(Repository *self, PyObject *args, PyObject *kwds);

#endif
