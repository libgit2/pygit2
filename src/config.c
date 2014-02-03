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
#include "types.h"
#include "utils.h"
#include "config.h"

extern PyTypeObject ConfigType;
extern PyTypeObject ConfigIterType;


PyObject *
wrap_config(char *c_path) {
    int err;
    PyObject *py_path;
    Config *py_config;

    py_path = Py_BuildValue("(s)", c_path);
    py_config = PyObject_New(Config, &ConfigType);

    err = Config_init(py_config, py_path, NULL);
    if (err < 0)
        return  NULL;

    return (PyObject*) py_config;
}


int
Config_init(Config *self, PyObject *args, PyObject *kwds)
{
    char *path = NULL;
    int err;

    if (kwds && PyDict_Size(kwds) > 0) {
        PyErr_SetString(PyExc_TypeError,
                        "Config takes no keyword arguments");
        return -1;
    }

    if (!PyArg_ParseTuple(args, "|s", &path))
        return -1;

    if (path == NULL)
        err = git_config_new(&self->config);
    else
        err = git_config_open_ondisk(&self->config, path);

    if (err < 0) {
        git_config_free(self->config);

        if (err == GIT_ENOTFOUND)
            Error_set_exc(PyExc_IOError);
        else
            Error_set(err);

        return -1;
    }

    return 0;
}


void
Config_dealloc(Config *self)
{
    git_config_free(self->config);
    PyObject_Del(self);
}

PyDoc_STRVAR(Config_get_global_config__doc__,
  "get_global_config() -> Config\n"
  "\n"
  "Return an object representing the global configuration file.");

PyObject *
Config_get_global_config(void)
{
    char path[GIT_PATH_MAX];
    int err;

    err = git_config_find_global(path, GIT_PATH_MAX);
    if (err < 0) {
        if (err == GIT_ENOTFOUND) {
            PyErr_SetString(PyExc_IOError, "Global config file not found.");
            return NULL;
        }

        return Error_set(err);
    }

    return wrap_config(path);
}


PyDoc_STRVAR(Config_get_system_config__doc__,
  "get_system_config() -> Config\n"
  "\n"
  "Return an object representing the system configuration file.");

PyObject *
Config_get_system_config(void)
{
    char path[GIT_PATH_MAX];
    int err;

    err = git_config_find_system(path, GIT_PATH_MAX);
    if (err < 0) {
        if (err == GIT_ENOTFOUND) {
            PyErr_SetString(PyExc_IOError, "System config file not found.");
            return NULL;
        }
        return Error_set(err);
    }

    return wrap_config(path);
}


int
Config_contains(Config *self, PyObject *py_key) {
    int err;
    const char *c_value, *c_key;
    PyObject *tkey;

    c_key = py_str_borrow_c_str(&tkey, py_key, NULL);
    if (c_key == NULL)
        return -1;

    err = git_config_get_string(&c_value, self->config, c_key);
    Py_DECREF(tkey);

    if (err < 0) {
        if (err == GIT_ENOTFOUND)
            return 0;

        Error_set(err);
        return -1;
    }

    return 1;
}


PyObject *
Config_getitem(Config *self, PyObject *py_key)
{
    int64_t value_int;
    int err, value_bool;
    const char *value_str;
    const char *key;
    PyObject* py_value, *tmp;

    key = py_str_borrow_c_str(&tmp, py_key, NULL);
    if (key == NULL)
        return NULL;

    err = git_config_get_string(&value_str, self->config, key);
    Py_CLEAR(tmp);
    if (err < 0)
        goto cleanup;

    if (git_config_parse_int64(&value_int, value_str) == 0)
        py_value = PyLong_FromLongLong(value_int);
    else if(git_config_parse_bool(&value_bool, value_str) == 0)
        py_value = PyBool_FromLong(value_bool);
    else
        py_value = to_unicode(value_str, NULL, NULL);

cleanup:
    if (err < 0) {
        if (err == GIT_ENOTFOUND) {
            PyErr_SetObject(PyExc_KeyError, py_key);
            return NULL;
        }

        return Error_set(err);
    }

    return py_value;
}

int
Config_setitem(Config *self, PyObject *py_key, PyObject *py_value)
{
    int err;
    const char *key, *value;
    PyObject *tkey, *tvalue;

    key = py_str_borrow_c_str(&tkey, py_key, NULL);
    if (key == NULL)
        return -1;

    if (py_value == NULL)
        err = git_config_delete_entry(self->config, key);
    else if (PyBool_Check(py_value)) {
        err = git_config_set_bool(self->config, key,
                (int)PyObject_IsTrue(py_value));
    } else if (PyLong_Check(py_value)) {
        err = git_config_set_int64(self->config, key,
                (int64_t)PyLong_AsLong(py_value));
    } else {
        value = py_str_borrow_c_str(&tvalue, py_value, NULL);
        err = git_config_set_string(self->config, key, value);
        Py_DECREF(tvalue);
    }

    Py_DECREF(tkey);
    if (err < 0) {
        Error_set(err);
        return -1;
    }
    return 0;
}

PyDoc_STRVAR(Config_add_file__doc__,
  "add_file(path, level=0, force=0)\n"
  "\n"
  "Add a config file instance to an existing config.");

PyObject *
Config_add_file(Config *self, PyObject *args, PyObject *kwds)
{
    char *keywords[] = {"path", "level", "force", NULL};
    int err;
    char *path;
    unsigned int level = 0;
    int force = 0;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "s|Ii", keywords,
                                     &path, &level, &force))
        return NULL;

    err = git_config_add_file_ondisk(self->config, path, level, force);
    if (err < 0)
        return Error_set_str(err, path);

    Py_RETURN_NONE;
}


PyDoc_STRVAR(Config_get_multivar__doc__,
  "get_multivar(name[, regex]) -> [str, ...]\n"
  "\n"
  "Get each value of a multivar ''name'' as a list. The optional ''regex''\n"
  "parameter is expected to be a regular expression to filter the variables\n"
  "we're interested in.");

PyObject *
Config_get_multivar(Config *self, PyObject *args)
{
    int err;
    PyObject *list;
    const char *name = NULL;
    const char *regex = NULL;
    git_config_iterator *iter;
    git_config_entry *entry;

    if (!PyArg_ParseTuple(args, "s|s", &name, &regex))
        return NULL;

    list = PyList_New(0);
    err = git_config_multivar_iterator_new(&iter, self->config, name, regex);
    if (err < 0)
        return Error_set(err);

    while ((err = git_config_next(&entry, iter)) == 0) {
        PyObject *item;

        item = to_unicode(entry->value, NULL, NULL);
        if (item == NULL) {
            git_config_iterator_free(iter);
            return NULL;
        }

        PyList_Append(list, item);
        Py_CLEAR(item);
    }

    git_config_iterator_free(iter);
    if (err == GIT_ITEROVER)
        err = 0;

    if (err < 0)
        return Error_set(err);

    return list;
}


PyDoc_STRVAR(Config_set_multivar__doc__,
  "set_multivar(name, regex, value)\n"
  "\n"
  "Set a multivar ''name'' to ''value''. ''regexp'' is a regular expression\n"
  "to indicate which values to replace");

PyObject *
Config_set_multivar(Config *self, PyObject *args)
{
    int err;
    const char *name = NULL;
    const char *regex = NULL;
    const char *value = NULL;

    if (!PyArg_ParseTuple(args, "sss", &name, &regex, &value))
        return NULL;

    err = git_config_set_multivar(self->config, name, regex, value);
    if (err < 0) {
        if (err == GIT_ENOTFOUND)
            Error_set(err);
        else
            PyErr_SetNone(PyExc_TypeError);
        return NULL;
    }

    Py_RETURN_NONE;
}

PyObject *
Config_iter(Config *self)
{
    ConfigIter *iter;
    int err;

    iter = PyObject_New(ConfigIter, &ConfigIterType);
    if (!iter)
        return NULL;

    if ((err = git_config_iterator_new(&iter->iter, self->config)) < 0)
        return Error_set(err);

    Py_INCREF(self);
    iter->owner = self;

    return (PyObject*)iter;
}

PyMethodDef Config_methods[] = {
    METHOD(Config, get_system_config, METH_NOARGS | METH_STATIC),
    METHOD(Config, get_global_config, METH_NOARGS | METH_STATIC),
    METHOD(Config, add_file, METH_VARARGS | METH_KEYWORDS),
    METHOD(Config, get_multivar, METH_VARARGS),
    METHOD(Config, set_multivar, METH_VARARGS),
    {NULL}
};

PySequenceMethods Config_as_sequence = {
    0,                               /* sq_length */
    0,                               /* sq_concat */
    0,                               /* sq_repeat */
    0,                               /* sq_item */
    0,                               /* sq_slice */
    0,                               /* sq_ass_item */
    0,                               /* sq_ass_slice */
    (objobjproc)Config_contains,     /* sq_contains */
};

PyMappingMethods Config_as_mapping = {
    0,                               /* mp_length */
    (binaryfunc)Config_getitem,      /* mp_subscript */
    (objobjargproc)Config_setitem,   /* mp_ass_subscript */
};


PyDoc_STRVAR(Config__doc__, "Configuration management.");

PyTypeObject ConfigType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.Config",                          /* tp_name           */
    sizeof(Config),                            /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)Config_dealloc,                /* tp_dealloc        */
    0,                                         /* tp_print          */
    0,                                         /* tp_getattr        */
    0,                                         /* tp_setattr        */
    0,                                         /* tp_compare        */
    0,                                         /* tp_repr           */
    0,                                         /* tp_as_number      */
    &Config_as_sequence,                       /* tp_as_sequence    */
    &Config_as_mapping,                        /* tp_as_mapping     */
    0,                                         /* tp_hash           */
    0,                                         /* tp_call           */
    0,                                         /* tp_str            */
    0,                                         /* tp_getattro       */
    0,                                         /* tp_setattro       */
    0,                                         /* tp_as_buffer      */
    Py_TPFLAGS_DEFAULT,                        /* tp_flags          */
    Config__doc__,                             /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    (getiterfunc)Config_iter,                  /* tp_iter           */
    0,                                         /* tp_iternext       */
    Config_methods,                            /* tp_methods        */
    0,                                         /* tp_members        */
    0,                                         /* tp_getset         */
    0,                                         /* tp_base           */
    0,                                         /* tp_dict           */
    0,                                         /* tp_descr_get      */
    0,                                         /* tp_descr_set      */
    0,                                         /* tp_dictoffset     */
    (initproc)Config_init,                     /* tp_init           */
    0,                                         /* tp_alloc          */
    0,                                         /* tp_new            */
};

void
ConfigIter_dealloc(ConfigIter *self)
{
    Py_CLEAR(self->owner);
    git_config_iterator_free(self->iter);
    PyObject_Del(self);
}

PyObject *
ConfigIter_iternext(ConfigIter *self)
{
    int err;
    git_config_entry *entry;

    if ((err = git_config_next(&entry, self->iter)) < 0)
        return Error_set(err);

    return Py_BuildValue("ss", entry->name, entry->value);
}

PyDoc_STRVAR(ConfigIter__doc__, "Configuration iterator.");

PyTypeObject ConfigIterType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "_pygit2.ConfigIter",                       /* tp_name           */
    sizeof(ConfigIter),                         /* tp_basicsize      */
    0,                                         /* tp_itemsize       */
    (destructor)ConfigIter_dealloc ,           /* tp_dealloc        */
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
    ConfigIter__doc__,                         /* tp_doc            */
    0,                                         /* tp_traverse       */
    0,                                         /* tp_clear          */
    0,                                         /* tp_richcompare    */
    0,                                         /* tp_weaklistoffset */
    PyObject_SelfIter,                         /* tp_iter           */
    (iternextfunc)ConfigIter_iternext,         /* tp_iternext       */

};
