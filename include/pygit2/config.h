#ifndef INCLUDE_pygit2_config_h
#define INCLUDE_pygit2_config_h

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <git2.h>

PyObject* Config_get_global_config(void);
PyObject* Config_get_system_config(void);
PyObject* Config_add_file(Config *self, PyObject *args);
PyObject* Config_getitem(Config *self, PyObject *key);
PyObject* Config_foreach(Config *self, PyObject *args);
int Config_setitem(Config *self, PyObject *key, PyObject *value);

#endif
