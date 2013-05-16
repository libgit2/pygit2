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

#ifndef INCLUDE_pygit2_reference_h
#define INCLUDE_pygit2_reference_h

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <git2.h>

PyObject* Reference_delete(Reference *self, PyObject *args);
PyObject* Reference_rename(Reference *self, PyObject *py_name);
PyObject* Reference_reload(Reference *self);
PyObject* Reference_resolve(Reference *self, PyObject *args);
PyObject* Reference_get_target(Reference *self);
PyObject* Reference_get_name(Reference *self);
PyObject* Reference_get_oid(Reference *self);
PyObject* Reference_get_hex(Reference *self);
PyObject* Reference_get_type(Reference *self);
PyObject* wrap_reference(git_reference *c_reference, Repository *repo);

#endif
