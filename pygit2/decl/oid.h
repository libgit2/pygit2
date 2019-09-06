typedef struct git_oid {
	unsigned char id[20];
} git_oid;

// This should go to net.h but due to h_order in _run.py, ffi won't compile properly.
typedef struct git_remote_head {
        int local;
        git_oid oid;
        git_oid loid;
        char *name;
        char *symref_target;
} git_remote_head;
