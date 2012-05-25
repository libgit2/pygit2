#ifndef INCLUDE_pygit2_tree_h
#define INCLUDE_pygit2_tree_h

#include <Python.h>
#include <git2.h>
#include <pygit2/types.h>

PyObject* TreeEntry_get_attributes(TreeEntry *self);
PyObject* TreeEntry_get_name(TreeEntry *self);
PyObject* TreeEntry_get_oid(TreeEntry *self);
PyObject* TreeEntry_get_hex(TreeEntry *self);
PyObject* TreeEntry_to_object(TreeEntry *self);

TreeEntry* Tree_getitem_by_index(Tree *self, PyObject *py_index);
TreeEntry* Tree_getitem(Tree *self, PyObject *value);

PyObject* TreeBuilder_insert(TreeBuilder *self, PyObject *args);
PyObject* TreeBuilder_write(TreeBuilder *self);
PyObject* TreeBuilder_remove(TreeBuilder *self, PyObject *py_filename);
PyObject* TreeBuilder_clear(TreeBuilder *self);
#endif
