#ifndef __PYGIT2_MARIADB_REFDB_H
#define __PYGIT2_MARIADB_REFDB_H

#include <mysql.h>

#include <git2.h>
#include <git2/errors.h>
#include <git2/refdb.h>
#include <git2/sys/refdb_backend.h>
#include <git2/types.h>

int git_refdb_backend_mariadb(git_refdb_backend **backend_out,
        MYSQL *db,
        const char *mariadb_table,
        uint32_t git_repository_id,
        int refdb_partitions);

#endif