#ifndef INCLUDE_pygit2_config_h
#define INCLUDE_pygit2_config_h

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <git2.h>

PyObject* Config_get_global_config(void);
PyObject* Config_get_system_config(void);

#endif
