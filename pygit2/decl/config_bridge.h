/*
 * These C structs need to be constructible and usable in Python code using CFFI like all
 * other libgit2 structs. They follow a common pattern found throughout libgit2, where a
 * "private" struct "extends" a struct from the public API by placing that "public" struct
 * as the first member of the private struct. As long as pointers are used to access the
 * private struct, it can safely be cast to and from the public struct because of the way
 * the memory layout works.
 *
 * In support of this, these structs are both included in / compiled into pygit2._libgit2.c
 * and loaded into CFFI's runtime definitions.
 */

typedef struct _pygit_in_memory_backend _pygit_in_memory_backend;
struct _pygit_in_memory_backend {
    git_config_backend parent;
    void * self;
};

typedef struct _pygit_in_memory_backend_entry _pygit_in_memory_backend_entry;
struct _pygit_in_memory_backend_entry {
    git_config_backend_entry parent;
    _pygit_in_memory_backend * owner;
};

typedef struct _pygit_in_memory_backend_iterator _pygit_in_memory_backend_iterator;
struct _pygit_in_memory_backend_iterator {
    git_config_iterator parent;
    void * self;
};

typedef struct _pygit_in_memory_backend_iterator_entry _pygit_in_memory_backend_iterator_entry;
struct _pygit_in_memory_backend_iterator_entry {
    git_config_backend_entry parent;
    _pygit_in_memory_backend_iterator * owner;
};
