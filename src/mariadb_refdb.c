#include <stdlib.h>

#include <Python.h>
#include "error.h"

#include "mariadb_refdb.h"

typedef struct {
    git_refdb_backend parent;

    MYSQL *db;
    uint32_t repository_id;
} mariadb_refdb_backend_t;


extern PyObject *GitError;


int git_refdb_backend_mariadb(git_refdb_backend **backend_out,
        MYSQL *db,
        const char *mariadb_table,
        uint32_t git_repository_id)
{
    mariadb_refdb_backend_t *backend;

    backend = calloc(1, sizeof(mariadb_refdb_backend_t));
    if (backend == NULL) {
        PyErr_SetString(GitError, "out of memory");
        return GIT_ERROR;
    }

    *backend_out = &backend->parent;

    backend->db = db;
    backend->repository_id = git_repository_id;

    backend->parent.exists = NULL; /* TODO */
    backend->parent.lookup = NULL; /* TODO */
    backend->parent.iterator = NULL; /* TODO */
    backend->parent.write = NULL; /* TODO */
    backend->parent.rename = NULL; /* TODO */
    backend->parent.del = NULL; /* TODO */
    backend->parent.compress = NULL; /* TODO */
    backend->parent.has_log = NULL; /* TODO */
    backend->parent.ensure_log = NULL; /* TODO */
    backend->parent.free = NULL; /* TODO */
    backend->parent.reflog_read = NULL; /* TODO */
    backend->parent.reflog_write = NULL; /* TODO */
    backend->parent.reflog_rename = NULL; /* TODO */
    backend->parent.reflog_delete = NULL; /* TODO */
    backend->parent.lock = NULL; /* TODO */
    backend->parent.unlock = NULL; /* TODO */

    return GIT_OK;
}