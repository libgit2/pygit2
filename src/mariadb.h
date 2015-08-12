#ifndef __PYGIT2_MARIADB_H
#define __PYGIT2_MARIADB_H

#include <Python.h>
#include "error.h"

#define RAISE_EXC(fmt, ...) \
    do { \
        PyErr_Format(GitError, fmt, __VA_ARGS__); \
        fprintf(stderr, fmt "\n", __VA_ARGS__); \
    } while(0);

#define RAISE_EXC_STR(fmt) \
    do { \
        PyErr_SetString(GitError, fmt); \
        fprintf(stderr, fmt "\n"); \
    } while(0);

#endif