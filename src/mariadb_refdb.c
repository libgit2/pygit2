#include <stdlib.h>

#include <Python.h>
#include "error.h"

#include "mariadb_refdb.h"


typedef struct {
    git_refdb_backend parent;

    MYSQL *db;
    uint32_t repository_id;
} mariadb_refdb_backend_t;


typedef struct {
    git_reference_iterator parent;

    /* TODO */
} mariadb_reference_iterator_t;


extern PyObject *GitError;


static int mariadb_reference_iterator_next(git_reference **ref,
        git_reference_iterator *iter);
static int mariadb_reference_iterator_next_name(const char **ref_name,
        git_reference_iterator *iter);
static void mariadb_reference_iterator_free(git_reference_iterator *iter);


/*!
 * \brief Template for our mariadb_reference_iterator_t.
 * When creating, we can memcpy() this template, and just fill in the taggued
 * fields.
 */
static const mariadb_reference_iterator_t reference_iterator_template = {
    .parent = {
        .db = NULL,  /* To fill in */
        .next = mariadb_reference_iterator_next,
        .next_name = mariadb_reference_iterator_next_name,
        .free = mariadb_reference_iterator_free,
    },
};


static int mariadb_reference_iterator_next(git_reference **ref,
        git_reference_iterator *iter)
{
    /* TODO */
    return GIT_ERROR;
}


static int mariadb_reference_iterator_next_name(const char **ref_name,
        git_reference_iterator *iter)
{
    /* TODO */
    return GIT_ERROR;
}


static void mariadb_reference_iterator_free(git_reference_iterator *iter)
{
    /* TODO */
}


static int mariadb_refdb_exists(int *exists, git_refdb_backend *backend,
        const char *ref_name)
{
    /* TODO */
    return GIT_ERROR;
}


static int mariadb_refdb_lookup(git_reference **out, git_refdb_backend *backend,
        const char *ref_name)
{
    /* TODO */
    return GIT_ERROR;
}


static int mariadb_refdb_iterator(git_reference_iterator **iter,
        struct git_refdb_backend *backend, const char *glob)
{
    /* TODO */
    return GIT_ERROR;
}


static int mariadb_refdb_write(git_refdb_backend *backend,
        const git_reference *ref, int force,
        const git_signature *who, const char *message,
        const git_oid *old, const char *old_target)
{
    /* TODO */
    return GIT_ERROR;
}


static int mariadb_refdb_rename(git_reference **out, git_refdb_backend *backend,
        const char *old_name, const char *new_name, int force,
        const git_signature *who, const char *message)
{
    /* TODO */
    return GIT_ERROR;
}


static int mariadb_refdb_del(git_refdb_backend *backend, const char *ref_name,
        const git_oid *old_id, const char *old_target)
{
    /* TODO */
    return GIT_ERROR;
}


static int mariadb_refdb_compress(git_refdb_backend *backend)
{
    /* TODO */
    return GIT_ERROR;
}


static int mariadb_refdb_lock(void **payload_out, git_refdb_backend *backend,
        const char *refname)
{
    /* TODO */
    return GIT_ERROR;
}


static int mariadb_refdb_unlock(git_refdb_backend *backend, void *payload,
        int success, int update_reflog, const git_reference *ref,
        const git_signature *sig, const char *message)
{
    /* TODO */
    return GIT_ERROR;
}


static void mariadb_refdb_free(git_refdb_backend *backend)
{
    free(backend);
}


static int mariadb_refdb_has_log(git_refdb_backend *backend,
        const char *refname)
{
    /* We don't use reflogs, so we never have one */
    return 0;
}


static int mariadb_refdb_ensure_log(git_refdb_backend *backend,
        const char *refname)
{
    /* We don't use reflogs */
    return GIT_OK;
}



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

    backend->parent.exists = mariadb_refdb_exists;
    backend->parent.lookup = mariadb_refdb_lookup;
    backend->parent.iterator = mariadb_refdb_iterator;
    backend->parent.write = mariadb_refdb_write;
    backend->parent.rename = mariadb_refdb_rename;
    backend->parent.del = mariadb_refdb_del;
    backend->parent.compress = mariadb_refdb_compress;
    backend->parent.has_log = mariadb_refdb_has_log;
    backend->parent.ensure_log = mariadb_refdb_ensure_log;
    backend->parent.free = mariadb_refdb_free;
    backend->parent.reflog_read = NULL; /* unused */
    backend->parent.reflog_write = NULL; /* unused */
    backend->parent.reflog_rename = NULL; /* unused */
    backend->parent.reflog_delete = NULL; /* unused */
    backend->parent.lock = mariadb_refdb_lock;
    backend->parent.unlock = mariadb_refdb_unlock;

    return GIT_OK;
}