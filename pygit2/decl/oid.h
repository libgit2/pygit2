typedef struct git_oid {
	unsigned char id[20];
} git_oid;

typedef struct git_remote_head {
        int local;
        git_oid oid;
        git_oid loid;
        char *name;
        char *symref_target;
} git_remote_head;
