#ifndef INCLUDE_pygit2_repository_h
#define INCLUDE_pygit2_repository_h

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <git2.h>
#include <pygit2/types.h>

int  Repository_init(Repository *self, PyObject *args, PyObject *kwds);
int  Repository_traverse(Repository *self, visitproc visit, void *arg);
int  Repository_clear(Repository *self);
int  Repository_contains(Repository *self, PyObject *value);

git_odb_object* Repository_read_raw(git_repository *repo, const git_oid *oid, size_t len);

PyObject* Repository_getitem(Repository *self, PyObject *value);
PyObject* Repository_read(Repository *self, PyObject *py_hex);
PyObject* Repository_write(Repository *self, PyObject *args);
PyObject* Repository_get_index(Repository *self, void *closure);
PyObject* Repository_get_path(Repository *self, void *closure);
PyObject* Repository_get_workdir(Repository *self, void *closure);
PyObject* Repository_get_config(Repository *self, void *closure);
PyObject* Repository_walk(Repository *self, PyObject *args);
PyObject* Repository_create_blob(Repository *self, PyObject *args);
PyObject* Repository_create_commit(Repository *self, PyObject *args);
PyObject* Repository_create_tag(Repository *self, PyObject *args);
PyObject* Repository_listall_references(Repository *self, PyObject *args);
PyObject* Repository_lookup_reference(Repository *self, PyObject *py_name);
PyObject* Repository_create_reference(Repository *self,  PyObject *args);
PyObject* Repository_create_symbolic_reference(Repository *self,  PyObject *args);
PyObject* Repository_packall_references(Repository *self,  PyObject *args);
PyObject* Repository_status(Repository *self, PyObject *args);
PyObject* Repository_status_file(Repository *self, PyObject *value);
PyObject* Repository_TreeBuilder(Repository *self, PyObject *args);

#endif
