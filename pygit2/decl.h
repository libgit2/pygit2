typedef ... git_repository;
typedef ... git_remote;
typedef ... git_refspec;
typedef ... git_push;
typedef ... git_cred;

#define GIT_OID_RAWSZ ...

typedef struct git_oid {
	unsigned char id[20];
} git_oid;

typedef struct git_strarray {
	char **strings;
	size_t count;
} git_strarray;

typedef enum {
	GIT_OK = 0,
	GIT_ERROR = -1,
	GIT_ENOTFOUND = -3,
	GIT_EEXISTS = -4,
	GIT_EAMBIGUOUS = -5,
	GIT_EBUFS = -6,
	GIT_EUSER = -7,
	GIT_EBAREREPO = -8,
	GIT_EUNBORNBRANCH = -9,
	GIT_EUNMERGED = -10,
	GIT_ENONFASTFORWARD = -11,
	GIT_EINVALIDSPEC = -12,
	GIT_EMERGECONFLICT = -13,
	GIT_ELOCKED = -14,

	GIT_PASSTHROUGH = -30,
	GIT_ITEROVER = -31,
} git_error_code;

typedef struct {
	char *message;
	int klass;
} git_error;

const git_error * giterr_last(void);

void git_strarray_free(git_strarray *array);

typedef struct git_transfer_progress {
	unsigned int total_objects;
	unsigned int indexed_objects;
	unsigned int received_objects;
	unsigned int local_objects;
	unsigned int total_deltas;
	unsigned int indexed_deltas;
	size_t received_bytes;
} git_transfer_progress;

typedef enum git_remote_completion_type {
	GIT_REMOTE_COMPLETION_DOWNLOAD,
	GIT_REMOTE_COMPLETION_INDEXING,
	GIT_REMOTE_COMPLETION_ERROR,
} git_remote_completion_type;

typedef enum {
	GIT_DIRECTION_FETCH = 0,
	GIT_DIRECTION_PUSH  = 1
} git_direction;

typedef enum {
	GIT_CREDTYPE_USERPASS_PLAINTEXT = ...,
	GIT_CREDTYPE_SSH_KEY = ...,
	GIT_CREDTYPE_SSH_CUSTOM = ...,
	GIT_CREDTYPE_DEFAULT = ...,
} git_credtype_t;

typedef struct git_remote_callbacks {
	unsigned int version;
	int (*progress)(const char *str, int len, void *data);
	int (*completion)(git_remote_completion_type type, void *data);
	int (*credentials)(git_cred **cred, const char *url, const char *username_from_url, unsigned int allowed_types,	void *data);
	int (*transfer_progress)(const git_transfer_progress *stats, void *data);
	int (*update_tips)(const char *refname, const git_oid *a, const git_oid *b, void *data);
	void *payload;
} git_remote_callbacks ;

int git_remote_list(git_strarray *out, git_repository *repo);
int git_remote_load(git_remote **out, git_repository *repo, const char *name);
int git_remote_create(git_remote **out,
		git_repository *repo,
		const char *name,
		const char *url);
const char * git_remote_name(const git_remote *remote);
typedef int (*git_remote_rename_problem_cb)(const char *problematic_refspec, void *payload);
int git_remote_rename(git_remote *remote,
	const char *new_name,
	git_remote_rename_problem_cb callback,
	void *payload);
const char * git_remote_url(const git_remote *remote);
int git_remote_set_url(git_remote *remote, const char* url);
const char * git_remote_pushurl(const git_remote *remote);
int git_remote_set_pushurl(git_remote *remote, const char* url);
int git_remote_fetch(git_remote *remote);
const git_transfer_progress * git_remote_stats(git_remote *remote);
int git_remote_add_push(git_remote *remote, const char *refspec);
int git_remote_add_fetch(git_remote *remote, const char *refspec);
int git_remote_save(const git_remote *remote);
int git_remote_set_callbacks(git_remote *remote, const git_remote_callbacks *callbacks);
size_t git_remote_refspec_count(git_remote *remote);
const git_refspec * git_remote_get_refspec(git_remote *remote, size_t n);

int git_remote_get_fetch_refspecs(git_strarray *array, git_remote *remote);
int git_remote_set_fetch_refspecs(git_remote *remote, git_strarray *array);
int git_remote_get_push_refspecs(git_strarray *array, git_remote *remote);
int git_remote_set_push_refspecs(git_remote *remote, git_strarray *array);

void git_remote_free(git_remote *remote);

int git_push_new(git_push **push, git_remote *remote);
int git_push_add_refspec(git_push *push, const char *refspec);
int git_push_finish(git_push *push);
int git_push_unpack_ok(git_push *push);

int git_push_status_foreach(git_push *push,
			int (*cb)(const char *ref, const char *msg, void *data),
			void *data);

int git_push_update_tips(git_push *push);
void git_push_free(git_push *push);

const char * git_refspec_src(const git_refspec *refspec);
const char * git_refspec_dst(const git_refspec *refspec);
int git_refspec_force(const git_refspec *refspec);
const char * git_refspec_string(const git_refspec *refspec);
git_direction git_refspec_direction(const git_refspec *spec);

int git_refspec_src_matches(const git_refspec *refspec, const char *refname);
int git_refspec_dst_matches(const git_refspec *refspec, const char *refname);

int git_refspec_transform(char *out, size_t outlen, const git_refspec *spec, const char *name);
int git_refspec_rtransform(char *out, size_t outlen, const git_refspec *spec, const char *name);

int git_cred_userpass_plaintext_new(
	git_cred **out,
	const char *username,
	const char *password);
int git_cred_ssh_key_new(
	git_cred **out,
	const char *username,
	const char *publickey,
	const char *privatekey,
	const char *passphrase);
