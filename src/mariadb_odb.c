#include <assert.h>
#include <stdio.h>
#include <string.h>

#include <Python.h>
#include "error.h"

#include "mariadb_odb.h"


#define GIT2_STORAGE_ENGINE "InnoDB"
#define MAX_QUERY_LEN 1024 /* without the values */


#define SQL_CREATE \
        "CREATE TABLE IF NOT EXISTS `%s` (" /* %s = table name */ \
        "  `repository_id` INTEGER UNSIGNED NOT NULL," \
        "  `oid` binary(20) NOT NULL DEFAULT ''," \
        "  `type` tinyint(1) unsigned NOT NULL," \
        "  `size` bigint(20) unsigned NOT NULL," \
        "  `data` longblob NOT NULL," \
        "  PRIMARY KEY (`repository_id`, `oid`)," \
        "  KEY `type` (`type`)," \
        "  KEY `size` (`size`)" \
        ") ENGINE=" GIT2_STORAGE_ENGINE \
        " DEFAULT CHARSET=utf8" \
        " COLLATE=utf8_bin" \
        " PARTITION BY KEY(`repository_id`)" \
        " PARTITIONS %d" \
        ";"

#define SQL_READ \
        "SELECT `type`, `size`, UNCOMPRESS(`data`) FROM `%s`" \
        " WHERE `repository_id` = ? AND `oid` = ?" \
        " LIMIT 1;"

/* We set limit to 2 here, because we must detect hash prefix collision.
 */
#define SQL_READ_PREFIX \
        "SELECT `oid`, `type`, `size`, UNCOMPRESS(`data`) FROM `%s`" \
        " WHERE `repository_id` = ? AND `oid` LIKE CONCAT(?, '%%')" \
        " LIMIT 2"

#define SQL_READ_HEADER \
        "SELECT `type`, `size` FROM `%s`" \
        " WHERE `repository_id` = ? AND `oid` = ? LIMIT 1;"

/* We set limit to 2 here, because we must detect hash prefix collision.
 */
#define SQL_READ_HEADER_PREFIX \
        "SELECT `oid` FROM `%s`" \
        " WHERE `repository_id` = ? AND `oid` LIKE CONCAT(?, '%%')" \
        " LIMIT 2;"

#define SQL_WRITE \
        "INSERT IGNORE INTO `%s` VALUES (?, ?, ?, ?, COMPRESS(?));"

#define LEN(x) (sizeof(x) / sizeof(x[0]))

#define UNIMPLEMENTED_CALLBACK(cb_name) static int cb_name() \
{ \
    fprintf(stderr, \
        "MariaDB ODB: WARNING: %s called but not implemented !\n", \
        __FUNCTION__); \
    assert(0); \
    return GIT_EUSER; \
}

typedef struct {
    git_odb_backend parent;

    uint32_t git_repository_id;

    MYSQL *db;
    MYSQL_STMT *st_read;
    MYSQL_STMT *st_read_prefix;
    MYSQL_STMT *st_write;
    MYSQL_STMT *st_read_header;
    MYSQL_STMT *st_read_header_prefix;
} mariadb_odb_backend_t;


extern PyObject *GitError;


static int mariadb_odb_backend__read_header(size_t *len_p, git_otype *type_p,
        git_odb_backend *_backend, const git_oid *oid)
{
    mariadb_odb_backend_t *backend;
    int error;
    MYSQL_BIND bind_buffers[2];
    MYSQL_BIND result_buffers[2];

    assert(len_p && type_p && _backend && oid);

    backend = (mariadb_odb_backend_t *)_backend;

    memset(bind_buffers, 0, sizeof(bind_buffers));
    memset(result_buffers, 0, sizeof(result_buffers));

    /* bind the repository_id */
    bind_buffers[0].buffer = &backend->git_repository_id;
    bind_buffers[0].buffer_type = MYSQL_TYPE_LONG;

    /* bind the oid passed to the statement */
    bind_buffers[1].buffer = (void*)oid->id;
    bind_buffers[1].buffer_length = 20;
    bind_buffers[1].length = &bind_buffers[1].buffer_length;
    bind_buffers[1].buffer_type = MYSQL_TYPE_BLOB;
    if (mysql_stmt_bind_param(backend->st_read_header, bind_buffers) != 0) {
        PyErr_Format(GitError, __FILE__ ": %s: L%d: "
                "mysql_stmt_bind_param() failed: %s",
                __FUNCTION__, __LINE__,
                mysql_error(backend->db));
        return GIT_EUSER;
    }

    /* execute the statement */
    if (mysql_stmt_execute(backend->st_read_header) != 0) {
        PyErr_Format(GitError, __FILE__ ": %s: L%d: "
                "mysql_stmt_execute() failed: %s",
                __FUNCTION__, __LINE__,
                mysql_error(backend->db));
        return GIT_EUSER;
    }

    if (mysql_stmt_store_result(backend->st_read_header) != 0) {
        PyErr_Format(GitError, __FILE__ ": %s: L%d: "
                "mysql_stmt_store_result() failed: %s",
                __FUNCTION__, __LINE__,
                mysql_error(backend->db));
        return GIT_EUSER;
    }

    /*
    this should either be 0 or 1
    if it's > 1 MySQL's unique index failed and we should all fear for our lives
    */
    if (mysql_stmt_num_rows(backend->st_read_header) == 1) {
        result_buffers[0].buffer_type = MYSQL_TYPE_TINY;
        result_buffers[0].buffer = type_p;
        result_buffers[0].buffer_length = sizeof(*type_p);
        memset(type_p, 0, sizeof(*type_p));

        result_buffers[1].buffer_type = MYSQL_TYPE_LONGLONG;
        result_buffers[1].buffer = len_p;
        result_buffers[1].buffer_length = sizeof(*len_p);
        memset(len_p, 0, sizeof(*len_p));

        if(mysql_stmt_bind_result(backend->st_read_header, result_buffers) != 0) {
            PyErr_Format(GitError, __FILE__ ": %s: L%d: "
                "mysql_stmt_bind_result() failed: %s",
                __FUNCTION__, __LINE__,
                mysql_error(backend->db));
            return GIT_EUSER;
        }

        /* this should populate the buffers at *type_p and *len_p */
        if(mysql_stmt_fetch(backend->st_read_header) != 0) {
            PyErr_Format(GitError, __FILE__ ": %s: L%d: "
                "mysql_stmt_fetch() failed: %s",
                __FUNCTION__, __LINE__,
                mysql_stmt_error(backend->st_read_header));
            return GIT_EUSER;
        }

        error = GIT_OK;
    } else {
        error = GIT_ENOTFOUND;
    }

    /* reset the statement for further use */
    if (mysql_stmt_reset(backend->st_read_header) != 0) {
        PyErr_Format(GitError, __FILE__ ": %s: L%d: "
                "mysql_stmt_reset() failed: %s",
                __FUNCTION__, __LINE__,
                mysql_error(backend->db));
        return GIT_EUSER;
    }

    return error;
}


static int mariadb_odb_backend__read(void **data_p, size_t *len_p,
    git_otype *type_p, git_odb_backend *_backend, const git_oid *oid)
{
    mariadb_odb_backend_t *backend;
    int error;
    MYSQL_BIND bind_buffers[2];
    MYSQL_BIND result_buffers[3];
    unsigned long data_len;
    int fetch_result;

    assert(len_p && type_p && _backend && oid);

    backend = (mariadb_odb_backend_t *)_backend;

    memset(bind_buffers, 0, sizeof(bind_buffers));
    memset(result_buffers, 0, sizeof(result_buffers));

    /* bind the repository_id */
    bind_buffers[0].buffer = &backend->git_repository_id;
    bind_buffers[0].buffer_type = MYSQL_TYPE_LONG;

    /* bind the oid passed to the statement */
    bind_buffers[1].buffer = (void*)oid->id;
    bind_buffers[1].buffer_length = GIT_OID_RAWSZ;
    bind_buffers[1].length = &bind_buffers[1].buffer_length;
    bind_buffers[1].buffer_type = MYSQL_TYPE_BLOB;
    if (mysql_stmt_bind_param(backend->st_read, bind_buffers) != 0) {
        PyErr_Format(GitError, __FILE__ ": %s: L%d: "
                "mysql_stmt_bind_param() failed: %s",
                __FUNCTION__, __LINE__,
                mysql_error(backend->db));
        return GIT_EUSER;
    }

    /* execute the statement */
    if (mysql_stmt_execute(backend->st_read) != 0) {
        PyErr_Format(GitError, __FILE__ ": %s: L%d: "
                "mysql_stmt_execute() failed: %s",
                __FUNCTION__, __LINE__,
                mysql_error(backend->db));
        return GIT_EUSER;
    }

    if (mysql_stmt_store_result(backend->st_read) != 0) {
        PyErr_Format(GitError, __FILE__ ": %s: L%d: "
                "mysql_stmt_store_result() failed: %s",
                __FUNCTION__, __LINE__,
                mysql_error(backend->db));
        return GIT_EUSER;
    }

    /*
     this should either be 0 or 1
     if it's > 1 MySQL's unique index failed and we should all fear for our lives
    */
    if (mysql_stmt_num_rows(backend->st_read) == 1) {
        result_buffers[0].buffer_type = MYSQL_TYPE_TINY;
        result_buffers[0].buffer = type_p;
        result_buffers[0].buffer_length = sizeof(*type_p);
        memset(type_p, 0, sizeof(*type_p));

        result_buffers[1].buffer_type = MYSQL_TYPE_LONGLONG;
        result_buffers[1].buffer = len_p;
        result_buffers[1].buffer_length = sizeof(*len_p);
        memset(len_p, 0, sizeof(*len_p));

        /*
        by setting buffer and buffer_length to 0, this tells libmysql
        we want it to set data_len to the *actual* length of that field
        this way we can malloc exactly as much memory as we need for the buffer

        come to think of it, we can probably just use the length set in *len_p
        once we fetch the result ?
        */
        result_buffers[2].buffer_type = MYSQL_TYPE_LONG_BLOB;
        result_buffers[2].buffer = 0;
        result_buffers[2].buffer_length = 0;
        result_buffers[2].length = &data_len;

        if(mysql_stmt_bind_result(backend->st_read, result_buffers) != 0) {
            PyErr_Format(GitError, __FILE__ ": %s: L%d: "
                "mysql_stmt_bind_result() failed: %s",
                __FUNCTION__, __LINE__,
                mysql_error(backend->db));
            return GIT_EUSER;
        }

        /* this should populate the buffers at *type_p, *len_p and &data_len */
        fetch_result = mysql_stmt_fetch(backend->st_read);
        if (fetch_result != 0 && fetch_result != MYSQL_DATA_TRUNCATED) {
            fprintf(stderr, __FILE__ ": %s: L%d: "
                        "mysql_stmt_fetch() failed: %s\n",
                        __FUNCTION__, __LINE__,
                        mysql_stmt_error(backend->st_read));
            PyErr_Format(GitError, __FILE__ ": %s: L%d: "
                "mysql_stmt_fetch() failed: %s",
                __FUNCTION__, __LINE__,
                mysql_stmt_error(backend->st_read));
            return GIT_EUSER;
        }

        if (data_len > 0) {
            *data_p = malloc(data_len);
            result_buffers[2].buffer = *data_p;
            result_buffers[2].buffer_length = data_len;

            if (mysql_stmt_fetch_column(backend->st_read,
                    &result_buffers[2], 2, 0) != 0) {
                PyErr_Format(GitError, __FILE__ ": %s: L%d: "
                        "mysql_stmt_fetch_column() failed: %s",
                        __FUNCTION__, __LINE__,
                        mysql_error(backend->db));
                return GIT_EUSER;
            }
        }

        error = GIT_OK;
    } else {
        error = GIT_ENOTFOUND;
    }

    /* reset the statement for further use */
    if (mysql_stmt_reset(backend->st_read) != 0) {
        PyErr_Format(GitError, __FILE__ ": %s: L%d: "
                "mysql_stmt_reset() failed: %s",
                __FUNCTION__, __LINE__,
                mysql_error(backend->db));
        return GIT_EUSER;
    }

    return error;
}


static int mariadb_odb_backend__read_prefix(
        git_oid *out_oid, void **data_p, size_t *len_p, git_otype *type_p,
        git_odb_backend *_backend, const git_oid *short_oid, size_t len) {

    mariadb_odb_backend_t *backend;
    int error;
    MYSQL_BIND bind_buffers[2];
    MYSQL_BIND result_buffers[4];
    unsigned long data_len;
    int fetch_result;

    assert(out_oid && len_p && type_p && _backend && short_oid);

    backend = (mariadb_odb_backend_t *)_backend;

    memset(bind_buffers, 0, sizeof(bind_buffers));
    memset(result_buffers, 0, sizeof(result_buffers));

    /* bind the repository_id */
    bind_buffers[0].buffer = &backend->git_repository_id;
    bind_buffers[0].buffer_type = MYSQL_TYPE_LONG;

    /* bind the oid passed to the statement */
    bind_buffers[1].buffer = (void*)short_oid->id;
    bind_buffers[1].buffer_length = len;
    bind_buffers[1].length = &bind_buffers[1].buffer_length;
    bind_buffers[1].buffer_type = MYSQL_TYPE_BLOB;
    if (mysql_stmt_bind_param(backend->st_read_prefix, bind_buffers) != 0) {
        PyErr_Format(GitError, __FILE__ ": %s: L%d: "
                "mysql_stmt_bind_param() failed: %s",
                __FUNCTION__, __LINE__,
                mysql_error(backend->db));
        return GIT_EUSER;
    }

    /* execute the statement */
    if (mysql_stmt_execute(backend->st_read_prefix) != 0) {
        PyErr_Format(GitError, __FILE__ ": %s: L%d: "
                "mysql_stmt_execute() failed: %s",
                __FUNCTION__, __LINE__,
                mysql_error(backend->db));
        return GIT_EUSER;
    }

    if (mysql_stmt_store_result(backend->st_read_prefix) != 0) {
        PyErr_Format(GitError, __FILE__ ": %s: L%d: "
                "mysql_stmt_store_result() failed: %s",
                __FUNCTION__, __LINE__,
                mysql_error(backend->db));
        return GIT_EUSER;
    }

    if (mysql_stmt_num_rows(backend->st_read_prefix) > 1) {
        error = GIT_EAMBIGUOUS;
    } else if (mysql_stmt_num_rows(backend->st_read_prefix) < 1) {
        error = GIT_ENOTFOUND;
    } else {
        result_buffers[0].buffer_type = MYSQL_TYPE_BLOB;
        result_buffers[0].buffer = (void*)out_oid->id,
        result_buffers[0].buffer_length = GIT_OID_RAWSZ;
        result_buffers[0].length = &result_buffers[0].buffer_length;

        result_buffers[1].buffer_type = MYSQL_TYPE_TINY;
        result_buffers[1].buffer = type_p;
        result_buffers[1].buffer_length = sizeof(*type_p);
        memset(type_p, 0, sizeof(*type_p));

        result_buffers[2].buffer_type = MYSQL_TYPE_LONGLONG;
        result_buffers[2].buffer = len_p;
        result_buffers[2].buffer_length = sizeof(*len_p);
        memset(len_p, 0, sizeof(*len_p));

        /*
        by setting buffer and buffer_length to 0, this tells libmysql
        we want it to set data_len to the *actual* length of that field
        this way we can malloc exactly as much memory as we need for the buffer

        come to think of it, we can probably just use the length set in *len_p
        once we fetch the result ?
        */
        result_buffers[3].buffer_type = MYSQL_TYPE_LONG_BLOB;
        result_buffers[3].buffer = 0;
        result_buffers[3].buffer_length = 0;
        result_buffers[3].length = &data_len;


        if(mysql_stmt_bind_result(backend->st_read_prefix, result_buffers) != 0) {
            PyErr_Format(GitError, __FILE__ ": %s: L%d: "
                "mysql_stmt_bind_result() failed: %s",
                __FUNCTION__, __LINE__,
                mysql_error(backend->db));
            return GIT_EUSER;
        }

        /* this should populate the buffers at *type_p, *len_p and &data_len */
        fetch_result = mysql_stmt_fetch(backend->st_read_prefix);
        if (fetch_result != 0 && fetch_result != MYSQL_DATA_TRUNCATED) {
            fprintf(stderr, __FILE__ ": %s: L%d: "
                        "mysql_stmt_fetch() failed: %s\n",
                        __FUNCTION__, __LINE__,
                        mysql_stmt_error(backend->st_read_prefix));
            PyErr_Format(GitError, __FILE__ ": %s: L%d: "
                "mysql_stmt_fetch() failed: %s",
                __FUNCTION__, __LINE__,
                mysql_stmt_error(backend->st_read_prefix));
            return GIT_EUSER;
        }

        if (data_len > 0) {
            *data_p = malloc(data_len);
            result_buffers[2].buffer = *data_p;
            result_buffers[2].buffer_length = data_len;

            if (mysql_stmt_fetch_column(backend->st_read_prefix,
                    &result_buffers[2], 2, 0) != 0) {
                PyErr_Format(GitError, __FILE__ ": %s: L%d: "
                        "mysql_stmt_fetch_column() failed: %s",
                        __FUNCTION__, __LINE__,
                        mysql_error(backend->db));
                return GIT_EUSER;
            }
        }

        error = GIT_OK;
    }

    /* reset the statement for further use */
    if (mysql_stmt_reset(backend->st_read_prefix) != 0) {
        PyErr_Format(GitError, __FILE__ ": %s: L%d: "
                "mysql_stmt_reset() failed: %s",
                __FUNCTION__, __LINE__,
                mysql_error(backend->db));
        return GIT_EUSER;
    }
    return error;
}


static int mariadb_odb_backend__exists(git_odb_backend *_backend, const git_oid *oid)
{
    mariadb_odb_backend_t *backend;
    int found;
    MYSQL_BIND bind_buffers[2];

    assert(_backend && oid);

    backend = (mariadb_odb_backend_t *)_backend;
    found = 0;

    memset(bind_buffers, 0, sizeof(bind_buffers));

    /* bind the repository_id */
    bind_buffers[0].buffer = &backend->git_repository_id;
    bind_buffers[0].buffer_type = MYSQL_TYPE_LONG;

    /* bind the oid passed to the statement */
    bind_buffers[1].buffer = (void*)oid->id;
    bind_buffers[1].buffer_length = 20;
    bind_buffers[1].length = &bind_buffers[1].buffer_length;
    bind_buffers[1].buffer_type = MYSQL_TYPE_BLOB;
    if (mysql_stmt_bind_param(backend->st_read_header, bind_buffers) != 0) {
        PyErr_Format(GitError, __FILE__ ": %s: L%d: "
                "mysql_stmt_bind_param() failed: %s",
                __FUNCTION__, __LINE__,
                mysql_error(backend->db));
        return 0;
    }

    /* execute the statement */
    if (mysql_stmt_execute(backend->st_read_header) != 0) {
        PyErr_Format(GitError, __FILE__ ": %s: L%d: "
                "mysql_stmt_execute() failed: %s",
                __FUNCTION__, __LINE__,
                mysql_error(backend->db));
        return 0;
    }

    if (mysql_stmt_store_result(backend->st_read_header) != 0) {
        PyErr_Format(GitError, __FILE__ ": %s: L%d: "
                "mysql_stmt_store_result() failed: %s",
                __FUNCTION__, __LINE__,
                mysql_error(backend->db));
        return 0;
    }

    /*
    now lets see if any rows matched our query
    this should either be 0 or 1
    if it's > 1 MySQL's unique index failed and we should all fear for our lives
    */
    if (mysql_stmt_num_rows(backend->st_read_header) == 1) {
        found = 1;
    }

    /* reset the statement for further use */
    if (mysql_stmt_reset(backend->st_read_header) != 0) {
        PyErr_Format(GitError, __FILE__ ": %s: L%d: "
                "mysql_stmt_reset() failed: %s",
                __FUNCTION__, __LINE__,
                mysql_error(backend->db));
        return 0;
    }

    return found;
}


static int mariadb_odb_backend__exists_prefix(
        git_oid *out_oid, git_odb_backend *_backend,
        const git_oid *short_oid, size_t len)
{
    mariadb_odb_backend_t *backend;
    int error;
    MYSQL_BIND bind_buffers[2];
    MYSQL_BIND result_buffers[1];
    int fetch_result;

    assert(out_oid && _backend && short_oid);

    backend = (mariadb_odb_backend_t *)_backend;

    memset(bind_buffers, 0, sizeof(bind_buffers));
    memset(result_buffers, 0, sizeof(result_buffers));

    /* bind the repository_id */
    bind_buffers[0].buffer = &backend->git_repository_id;
    bind_buffers[0].buffer_type = MYSQL_TYPE_LONG;

    /* bind the oid passed to the statement */
    bind_buffers[1].buffer = (void*)short_oid->id;
    bind_buffers[1].buffer_length = len;
    bind_buffers[1].length = &bind_buffers[1].buffer_length;
    bind_buffers[1].buffer_type = MYSQL_TYPE_BLOB;
    if (mysql_stmt_bind_param(backend->st_read_prefix, bind_buffers) != 0) {
        PyErr_Format(GitError, __FILE__ ": %s: L%d: "
                "mysql_stmt_bind_param() failed: %s",
                __FUNCTION__, __LINE__,
                mysql_error(backend->db));
        return GIT_EUSER;
    }

    /* execute the statement */
    if (mysql_stmt_execute(backend->st_read_prefix) != 0) {
        PyErr_Format(GitError, __FILE__ ": %s: L%d: "
                "mysql_stmt_execute() failed: %s",
                __FUNCTION__, __LINE__,
                mysql_error(backend->db));
        return GIT_EUSER;
    }

    if (mysql_stmt_store_result(backend->st_read_prefix) != 0) {
        PyErr_Format(GitError, __FILE__ ": %s: L%d: "
                "mysql_stmt_store_result() failed: %s",
                __FUNCTION__, __LINE__,
                mysql_error(backend->db));
        return GIT_EUSER;
    }

    if (mysql_stmt_num_rows(backend->st_read_prefix) > 1) {
        error = GIT_EAMBIGUOUS;
    } else if (mysql_stmt_num_rows(backend->st_read_prefix) < 1) {
        error = GIT_ENOTFOUND;
    } else {
        result_buffers[0].buffer_type = MYSQL_TYPE_BLOB;
        result_buffers[0].buffer = (void*)out_oid->id,
        result_buffers[0].buffer_length = GIT_OID_RAWSZ;
        result_buffers[0].length = &result_buffers[0].buffer_length;

        if(mysql_stmt_bind_result(backend->st_read_prefix, result_buffers) != 0) {
            PyErr_Format(GitError, __FILE__ ": %s: L%d: "
                "mysql_stmt_bind_result() failed: %s",
                __FUNCTION__, __LINE__,
                mysql_error(backend->db));
            return GIT_EUSER;
        }

        /* this should populate the buffers */
        fetch_result = mysql_stmt_fetch(backend->st_read_prefix);
        if (fetch_result != 0 && fetch_result != MYSQL_DATA_TRUNCATED) {
            fprintf(stderr, __FILE__ ": %s: L%d: "
                        "mysql_stmt_fetch() failed: %s\n",
                        __FUNCTION__, __LINE__,
                        mysql_stmt_error(backend->st_read_prefix));
            PyErr_Format(GitError, __FILE__ ": %s: L%d: "
                "mysql_stmt_fetch() failed: %s",
                __FUNCTION__, __LINE__,
                mysql_stmt_error(backend->st_read_prefix));
            return GIT_EUSER;
        }

        error = GIT_OK;
    }

    /* reset the statement for further use */
    if (mysql_stmt_reset(backend->st_read_prefix) != 0) {
        PyErr_Format(GitError, __FILE__ ": %s: L%d: "
                "mysql_stmt_reset() failed: %s",
                __FUNCTION__, __LINE__,
                mysql_error(backend->db));
        return GIT_EUSER;
    }
    return error;
}


static int mariadb_odb_backend__write(git_odb_backend *_backend, const git_oid *oid,
    const void *data, size_t len, git_otype type)
{
    mariadb_odb_backend_t *backend;
    MYSQL_BIND bind_buffers[5];
    my_ulonglong affected_rows;

    assert(oid && _backend && data);

    backend = (mariadb_odb_backend_t *)_backend;

    memset(bind_buffers, 0, sizeof(bind_buffers));

    /* bind the repository_id */
    bind_buffers[0].buffer = &backend->git_repository_id;
    bind_buffers[0].buffer_type = MYSQL_TYPE_LONG;

    /* bind the oid */
    bind_buffers[1].buffer = (void*)oid->id;
    bind_buffers[1].buffer_length = 20;
    bind_buffers[1].length = &bind_buffers[1].buffer_length;
    bind_buffers[1].buffer_type = MYSQL_TYPE_BLOB;

    /* bind the type */
    bind_buffers[2].buffer = &type;
    bind_buffers[2].buffer_type = MYSQL_TYPE_TINY;

    /* bind the size of the data */
    bind_buffers[3].buffer = &len;
    bind_buffers[3].buffer_type = MYSQL_TYPE_LONG;

    /* bind the data */
    bind_buffers[4].buffer = (void*)data;
    bind_buffers[4].buffer_length = len;
    bind_buffers[4].length = &bind_buffers[4].buffer_length;
    bind_buffers[4].buffer_type = MYSQL_TYPE_BLOB;

    if (mysql_stmt_bind_param(backend->st_write, bind_buffers) != 0) {
        PyErr_Format(GitError, __FILE__ ": %s: L%d: "
                "mysql_stmt_bind_param() failed: %s",
                __FUNCTION__, __LINE__,
                mysql_error(backend->db));
        return GIT_EUSER;
    }

    /*
    TODO: use the streaming backend API so this actually makes sense to use :P
    once we want to use this we should comment out
    if (mysql_stmt_send_long_data(backend->st_write, 2, data, len) != 0)
       return GIT_EUSER;
    */

    /* execute the statement */
    if (mysql_stmt_execute(backend->st_write) != 0) {
        PyErr_Format(GitError, __FILE__ ": %s: L%d: "
                "mysql_stmt_execute() failed: %s",
                __FUNCTION__, __LINE__,
                mysql_error(backend->db));
        return GIT_EUSER;
    }

    /* now lets see if the insert worked */
    affected_rows = mysql_stmt_affected_rows(backend->st_write);
    if (affected_rows != 1) {
        PyErr_Format(GitError, __FILE__ ": %s: L%d: "
                "mysql_stmt_affected_rows() failed: %s",
                __FUNCTION__, __LINE__,
                mysql_error(backend->db));
        return GIT_EUSER;
    }

    /* reset the statement for further use */
    if (mysql_stmt_reset(backend->st_write) != 0) {
        PyErr_Format(GitError, __FILE__ ": %s: L%d: "
                "mysql_stmt_reset() failed: %s",
                __FUNCTION__, __LINE__,
                mysql_error(backend->db));
        return GIT_EUSER;
    }

    return GIT_OK;
}


static int mariadb_odb_backend__refresh(git_odb_backend *backend) {
    /* no-op here */
    return GIT_OK;
}


/* disable -Wstrict-prototype: we are actually in one of the only cases
 * where it is handy to have functions with an undefined list of
 * arguments.
 */
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wstrict-prototypes"

UNIMPLEMENTED_CALLBACK(mariadb_odb_backend__writestream)
UNIMPLEMENTED_CALLBACK(mariadb_odb_backend__readstream)
UNIMPLEMENTED_CALLBACK(mariadb_odb_backend__foreach)
UNIMPLEMENTED_CALLBACK(mariadb_odb_backend__writepack)

#pragma GCC diagnostic pop

static void mariadb_odb_backend__free(git_odb_backend *_backend)
{
    mariadb_odb_backend_t *backend;

    assert(_backend);
    backend = (mariadb_odb_backend_t *)_backend;

    if (backend->st_read)
        mysql_stmt_close(backend->st_read);
    if (backend->st_read_prefix)
        mysql_stmt_close(backend->st_read_prefix);
    if (backend->st_read_header)
        mysql_stmt_close(backend->st_read_header);
    if (backend->st_read_header_prefix);
        mysql_stmt_close(backend->st_read_header_prefix);
    if (backend->st_write)
        mysql_stmt_close(backend->st_write);

    free(backend);
}


static int init_db(MYSQL *db, const char *table_name, int odb_partitions)
{
    char sql_create[MAX_QUERY_LEN];

    snprintf(sql_create, sizeof(sql_create), SQL_CREATE, table_name,
        odb_partitions);

    if (mysql_real_query(db, sql_create, strlen(sql_create)) != 0) {
        PyErr_Format(GitError, __FILE__ ": %s: L%d: "
                "mysql_real_query() failed: %s",
                __FUNCTION__, __LINE__,
                mysql_error(db));
        return GIT_EUSER;
    }

    return GIT_OK;
}


static int init_statements(mariadb_odb_backend_t *backend, const char *mysql_table)
{
    my_bool truth = 1;

    char buffer[MAX_QUERY_LEN];

    struct {
        const char *query;
        const char *short_name;
        MYSQL_STMT **stmt;
    } statements[] = {
        {
            .query = SQL_READ,
            .short_name = "read",
            .stmt = &backend->st_read,
        },
        {
            .query = SQL_READ_PREFIX,
            .short_name = "read_prefix",
            .stmt = &backend->st_read_prefix,
        },
        {
            .query = SQL_READ_HEADER,
            .short_name = "read_header",
            .stmt = &backend->st_read_header,
        },
        {
            .query = SQL_READ_HEADER_PREFIX,
            .short_name = "read_header_prefix",
            .stmt = &backend->st_read_header_prefix,
        },
        {
            .query = SQL_WRITE,
            .short_name = "write",
            .stmt = &backend->st_write,
        },
    };

    size_t st_idx;

    for (st_idx = 0 ; st_idx < LEN(statements); st_idx++) {
        snprintf(buffer, sizeof(buffer),
            statements[st_idx].query, mysql_table);

        *(statements[st_idx].stmt) = mysql_stmt_init(backend->db);
        if (*(statements[st_idx].stmt) == NULL) {
            PyErr_Format(GitError, __FILE__ ": mysql_stmt_init(%s) failed: %s",
                statements[st_idx].short_name, mysql_error(backend->db));
            return GIT_EUSER;
        }

        if (mysql_stmt_attr_set(*(statements[st_idx].stmt),
                    STMT_ATTR_UPDATE_MAX_LENGTH, &truth) != 0) {
            PyErr_Format(GitError, __FILE__
                ": mysql_stmt_attr_set(%s) failed: %s",
                statements[st_idx].short_name, mysql_error(backend->db));
            return GIT_EUSER;
        }

        if (mysql_stmt_prepare(*(statements[st_idx].stmt),
                    buffer, strlen(buffer)) != 0) {
            PyErr_Format(GitError, __FILE__
                ": mysql_stmt_prepare(%s) failed: %s",
                statements[st_idx].short_name,
                mysql_error(backend->db));
            return GIT_EUSER;
        }
    }

    return GIT_OK;
}


int git_odb_backend_mariadb(git_odb_backend **backend_out,
        MYSQL *db,
        const char *mariadb_table,
        uint32_t git_repository_id,
        int odb_partitions)
{
    mariadb_odb_backend_t *backend;
    int error;

    backend = calloc(1, sizeof(mariadb_odb_backend_t));
    if (backend == NULL) {
        PyErr_SetString(GitError, "Out of memory");
        return GIT_EUSER;
    }

    git_odb_init_backend(&backend->parent, GIT_ODB_BACKEND_VERSION);

    backend->git_repository_id = git_repository_id;

    backend->db = db;

    /* check for and possibly create the database */
    error = init_db(db, mariadb_table, odb_partitions);
    if (error < 0) {
        goto cleanup;
    }

    error = init_statements(backend, mariadb_table);
    if (error < 0) {
        goto cleanup;
    }

    backend->parent.read = mariadb_odb_backend__read;
    backend->parent.read_prefix = mariadb_odb_backend__read_prefix;
    backend->parent.read_header = mariadb_odb_backend__read_header;
    backend->parent.write = mariadb_odb_backend__write;
    backend->parent.writestream = mariadb_odb_backend__writestream;
    backend->parent.readstream = mariadb_odb_backend__readstream;
    backend->parent.exists = mariadb_odb_backend__exists;
    backend->parent.exists_prefix = mariadb_odb_backend__exists_prefix;
    backend->parent.refresh = mariadb_odb_backend__refresh;
    backend->parent.free = mariadb_odb_backend__free;
    backend->parent.foreach = mariadb_odb_backend__foreach;
    backend->parent.writepack = mariadb_odb_backend__writepack;


    *backend_out = &backend->parent;
    return GIT_OK;

cleanup:
    mariadb_odb_backend__free(&backend->parent);
    return GIT_EUSER;
}