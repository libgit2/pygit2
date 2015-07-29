#include <stdlib.h>

#include <Python.h>

#include <git2/sys/refs.h>

#include "error.h"
#include "mariadb_refdb.h"


#define GIT2_STORAGE_ENGINE "InnoDB"
#define MAX_QUERY_LEN 1024 /* without the values */


#define SQL_CREATE \
    "CREATE TABLE IF NOT EXISTS `%s` (" /* %s = table name */ \
    "  `repository_id` INTEGER UNSIGNED NOT NULL," \
    "  `refname` VARCHAR(255) NOT NULL," \
    "  `target_oid` binary(20) NULL," \
    "  `target_symbolic` VARCHAR(255) NULL," \
    "  `peel_oid` binary(20) NULL," \
    "  PRIMARY KEY (`repository_id`, `refname`)" \
    ") ENGINE=" GIT2_STORAGE_ENGINE \
    " DEFAULT CHARSET=utf8" \
    " COLLATE=utf8_bin" \
    " PARTITION BY KEY(`repository_id`)" \
    " PARTITIONS 4" \
    ";"


#define SQL_EXISTS \
    "SELECT refname FROM `%s`" /* %s = table name */ \
    " WHERE `repository_id` = ? AND `refname` = ?" \
    " LIMIT 1;"


#define SQL_LOOKUP \
    "SELECT `target_oid`, `target_symbolic`, `peel_oid`" \
    " FROM `%s`" /* %s = table name */ \
    " WHERE `repository_id` = ? AND `refname` = ?" \
    " LIMIT 1;"


/* for the iterator, we have to use the custom p_fnmatch() on each ref
 * so we must go through all of them. Hopefully there won't be too many
 */
#define SQL_ITERATOR \
    "SELECT `target_oid`, `target_symbolic`, `peel_oid`" \
    " FROM `%s`" /* %s = table name */ \
    " WHERE `repository_id` = ?;"


/* will automatically fail if the primary key is already used */
#define SQL_WRITE_NO_FORCE \
    "INSERT INTO `%s`" /* %s = table name */ \
    " (`repository_id`, `refname`, `target_oid`, `target_symbolic`," \
    " `peel_oid`)" \
    " VALUES (?, ?, ?, ?, ?);"


/* try to insert ; if there is a primary key conflict, tell it to update
 * the existing entry instead */
#define SQL_WRITE_FORCE \
    "INSERT INTO `%s`" /* %s = table name */ \
    " (`repository_id`, `refname`, `target_oid`, `target_symbolic`," \
    " `peel_oid`)" \
    " VALUES (?, ?, ?, ?, ?)" \
    " ON DUPLICATE KEY" \
    " UPDATE `target_oid`=?, `target_symbolic`=?, `peel_oid`=?;"


#define SQL_RENAME \
    "UPDATE `%s`" /* %s = table name */ \
    " SET `refname`=?" \
    " WHERE `repository_id` = ? AND `refname` = ?" \
    " LIMIT 1;"


#define SQL_DELETE \
    "DELETE FROM `%s`" /* %s = table name */ \
    " WHERE `repository_id` = ? AND `refname` = ?" \
    " LIMIT 1;"


/****
 * XXX(Jflesch):
 * For the write() operation, we need to access the content of git_reference
 * (typedef-ed from (struct git_reference)).
 * There doesn't seem to be any accessor available, and the structure
 * definition is not in the public #include of libgit2.
 * So we have to make this really ugly copy-and-pasta from the private header
 * libgit2/src/refs.h
 ****/

/*
 * See if our compiler is known to support flexible array members.
 */
#ifndef GIT_FLEX_ARRAY
#    if defined(__STDC_VERSION__) && (__STDC_VERSION__ >= 199901L)
#        define GIT_FLEX_ARRAY /* empty */
#    elif defined(__GNUC__)
#        if (__GNUC__ >= 3)
#            define GIT_FLEX_ARRAY /* empty */
#        else
#            define GIT_FLEX_ARRAY 0 /* older GNU extension */
#        endif
#    endif

/* Default to safer but a bit wasteful traditional style */
#    ifndef GIT_FLEX_ARRAY
#        define GIT_FLEX_ARRAY 1
#    endif
#endif

struct git_reference {
    git_refdb *db;
    git_ref_t type;

    union {
        git_oid oid;
        char *symbolic;
    } target;

    git_oid peel;
    char name[GIT_FLEX_ARRAY];
};

/***
 * End of ugly copy-and-pasta
 ***/


typedef struct {
    git_refdb_backend parent;

    MYSQL *db;
    uint32_t repository_id;

    MYSQL_STMT *st_exists;
    MYSQL_STMT *st_lookup;
    MYSQL_STMT *st_iterator;
    MYSQL_STMT *st_write_no_force;
    MYSQL_STMT *st_write_force;
    MYSQL_STMT *st_rename;
    MYSQL_STMT *st_delete;
} mariadb_refdb_backend_t;


typedef struct {
    git_reference_iterator parent;
    /* TODO */
} mariadb_reference_iterator_t;


extern PyObject *GitError;

/*!
 * \brief libgit2's custom internal implementation of fnmatch()
 * see man fnmatch()
 */
extern int p_fnmatch(const char *pattern, const char *string, int flags);


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


/*!
 * \param ref ref to add to the db
 * \param force if TRUE (1), smash any previously ref with the same name ;
 *   if FALSE (0), fail if there is already a ref with this name
 * \param who used for reflog ; ignored in this implementation
 * \param message used for reflog ; ignore in this implementation
 * \param old used for reflog ; ignored in this implementation
 * \param old_target used for reflog ; ignored in this implementation
 */
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
    /* Meh, who needs locking ? :P */
    return GIT_OK;
}


static int mariadb_refdb_unlock(git_refdb_backend *backend, void *payload,
        int success, int update_reflog, const git_reference *ref,
        const git_signature *sig, const char *message)
{
    /* Meh, who needs locking ? :P */
    return GIT_OK;
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


static int mariadb_refdb_reflog_read(git_reflog **out,
        git_refdb_backend *backend, const char *name)
{
    /* We don't use reflogs */
    return GIT_ERROR;
}


static int mariadb_refdb_reflog_write(git_refdb_backend *backend,
        git_reflog *reflog)
{
    /* We don't use reflogs */
    return GIT_OK;
}


static int mariadb_refdb_reflog_rename(git_refdb_backend *_backend,
        const char *old_name, const char *new_name)
{
    /* We don't use reflogs */
    return GIT_OK;
}


static int mariadb_refdb_reflog_delete(git_refdb_backend *backend,
        const char *name)
{
    /* We don't use reflogs */
    return GIT_OK;
}


static int init_db(MYSQL *db, const char *table_name)
{
    char sql_create[MAX_QUERY_LEN];

    snprintf(sql_create, sizeof(sql_create), SQL_CREATE, table_name);

    if (mysql_real_query(db, sql_create, strlen(sql_create)) != 0) {
        PyErr_Format(GitError, __FILE__ ": %s: L%d: "
                "mysql_real_query() failed: %s",
                __FUNCTION__, __LINE__,
                mysql_error(db));
        return GIT_ERROR;
    }

    return GIT_OK;
}


static int init_statement(MYSQL *db,
    const char *sql_query_short_name,
    const char *sql_statement,
    const char *mysql_table,
    MYSQL_STMT **statement)
{
    my_bool truth = 1;
    char sql_query[MAX_QUERY_LEN];

    snprintf(sql_query, sizeof(sql_query), sql_statement, mysql_table);

    *statement = mysql_stmt_init(db);
    if (*statement == NULL) {
        PyErr_SetString(GitError, __FILE__ ": mysql_stmt_init() failed");
        return GIT_ERROR;
    }

    if (mysql_stmt_attr_set(*statement, STMT_ATTR_UPDATE_MAX_LENGTH,
            &truth) != 0) {
        PyErr_SetString(GitError, __FILE__ ": mysql_stmt_attr_set() failed");
        return GIT_ERROR;
    }

    if (mysql_stmt_prepare(*statement, sql_query, strlen(sql_query)) != 0) {
        PyErr_Format(GitError, __FILE__ ": mysql_stmt_prepare(%s) failed: %s",
            sql_query_short_name,
            mysql_error(db));
        return GIT_ERROR;
    }

    return GIT_OK;
}


static int init_statements(mariadb_refdb_backend_t *backend,
        const char *mysql_table)
{
    if (init_statement(backend->db, "exists", SQL_EXISTS, mysql_table,
            &backend->st_exists) != GIT_OK)
        return GIT_ERROR;

    if (init_statement(backend->db, "lookup", SQL_LOOKUP, mysql_table,
            &backend->st_lookup) != GIT_OK)
        return GIT_ERROR;

    if (init_statement(backend->db, "iterator", SQL_ITERATOR, mysql_table,
            &backend->st_iterator) != GIT_OK)
        return GIT_ERROR;

    if (init_statement(backend->db, "write no force", SQL_WRITE_NO_FORCE,
            mysql_table, &backend->st_write_no_force) != GIT_OK)
        return GIT_ERROR;

    if (init_statement(backend->db, "write force", SQL_WRITE_FORCE,
            mysql_table, &backend->st_write_force) != GIT_OK)
        return GIT_ERROR;

    if (init_statement(backend->db, "rename", SQL_RENAME, mysql_table,
            &backend->st_rename) != GIT_OK)
        return GIT_ERROR;

    if (init_statement(backend->db, "delete", SQL_DELETE, mysql_table,
            &backend->st_delete) != GIT_OK)
        return GIT_ERROR;

    return GIT_OK;
}


int git_refdb_backend_mariadb(git_refdb_backend **backend_out,
        MYSQL *db,
        const char *mariadb_table,
        uint32_t git_repository_id)
{
    mariadb_refdb_backend_t *backend;
    int error;

    backend = calloc(1, sizeof(mariadb_refdb_backend_t));
    if (backend == NULL) {
        PyErr_SetString(GitError, "out of memory");
        return GIT_ERROR;
    }

    *backend_out = &backend->parent;
    backend->db = db;

    error = init_db(db, mariadb_table);
    if (error < 0) {
        goto error;
    }

    error = init_statements(backend, mariadb_table);
    if (error < 0) {
        goto error;
    }

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
    backend->parent.reflog_read = mariadb_refdb_reflog_read;
    backend->parent.reflog_write = mariadb_refdb_reflog_write;
    backend->parent.reflog_rename = mariadb_refdb_reflog_rename;
    backend->parent.reflog_delete = mariadb_refdb_reflog_delete;
    backend->parent.lock = mariadb_refdb_lock;
    backend->parent.unlock = mariadb_refdb_unlock;

    return GIT_OK;

error:
    mariadb_refdb_free(&backend->parent);
    return GIT_ERROR;
}