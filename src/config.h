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

#ifndef INCLUDE_pygit2_config_h
#define INCLUDE_pygit2_config_h

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <git2.h>

PyObject* wrap_config(char *c_path);
PyObject* Config_get_global_config(void);
PyObject* Config_get_system_config(void);
PyObject* Config_add_file(Config *self, PyObject *args, PyObject *kwds);
PyObject* Config_getitem(Config *self, PyObject *key);
PyObject* Config_foreach(Config *self, PyObject *args);
PyObject* Config_get_multivar(Config *self, PyObject *args);
PyObject* Config_set_multivar(Config *self, PyObject *args);
int Config_init(Config *self, PyObject *args, PyObject *kwds);
int Config_setitem(Config *self, PyObject *key, PyObject *value);
#endif
