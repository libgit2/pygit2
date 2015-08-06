#ifndef __PYGIT2_MARIADB_ODB_H
#define __PYGIT2_MARIADB_ODB_H

#include <stdint.h>

/* disable -Wstrict-prototypes because mysql's devs don't know C ... */
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wstrict-prototypes"
#include <mysql.h>
#pragma GCC diagnostic pop

#include <git2.h>
#include <git2/errors.h>
#include <git2/odb_backend.h>
#include <git2/sys/odb_backend.h>
#include <git2/types.h>

int git_odb_backend_mariadb(git_odb_backend **backend_out,
        MYSQL *db,
        const char *mariadb_table,
        uint32_t git_repository_id,
        int odb_partitions);

#endif