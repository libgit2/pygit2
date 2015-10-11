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

#ifndef INCLUDE_pygit2_tree_h
#define INCLUDE_pygit2_tree_h

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <git2.h>
#include "types.h"

TreeEntry * wrap_tree_entry(const git_tree_entry *entry);
PyObject* TreeEntry_get_filemode(TreeEntry *self);
PyObject* TreeEntry_get_name(TreeEntry *self);
PyObject* TreeEntry_get_oid(TreeEntry *self);
PyObject* TreeEntry_get_hex(TreeEntry *self);

TreeEntry* Tree_getitem_by_index(Tree *self, PyObject *py_index);
TreeEntry* Tree_getitem(Tree *self, PyObject *value);
PyObject* Tree_diff_tree(Tree *self, PyObject *args);

#endif
