typedef ... git_repository;
typedef ... git_remote;
typedef ... git_refspec;
typedef ... git_push;
typedef ... git_cred;
typedef ... git_diff_file;
typedef ... git_tree;
typedef ... git_signature;

#define GIT_OID_RAWSZ ...
#define GIT_PATH_MAX ...

typedef struct git_oid {
	unsigned char id[20];
} git_oid;

typedef struct {
	char   *ptr;
	size_t asize, size;
} git_buf;
void git_buf_free(git_buf *buffer);

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
void git_repository_free(git_repository *repo);

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
	GIT_CREDTYPE_USERPASS_PLAINTEXT,
	GIT_CREDTYPE_SSH_KEY,
	GIT_CREDTYPE_SSH_CUSTOM,
	GIT_CREDTYPE_DEFAULT,
	...
} git_credtype_t;

typedef int (*git_transport_message_cb)(const char *str, int len, void *data);
typedef int (*git_cred_acquire_cb)(
	git_cred **cred,
	const char *url,
	const char *username_from_url,
	unsigned int allowed_types,
	void *payload);
typedef int (*git_transfer_progress_cb)(const git_transfer_progress *stats, void *payload);

struct git_remote_callbacks {
	unsigned int version;
	git_transport_message_cb sideband_progress;
	int (*completion)(git_remote_completion_type type, void *data);
	git_cred_acquire_cb credentials;
	git_transfer_progress_cb transfer_progress;
	int (*update_tips)(const char *refname, const git_oid *a, const git_oid *b, void *data);
	void *payload;
};

typedef struct git_remote_callbacks git_remote_callbacks;

int git_remote_list(git_strarray *out, git_repository *repo);
int git_remote_load(git_remote **out, git_repository *repo, const char *name);
int git_remote_create(
	git_remote **out,
	git_repository *repo,
	const char *name,
	const char *url);

const char * git_remote_name(const git_remote *remote);

int git_remote_rename(
	git_strarray *problems,
	git_remote *remote,
	const char *new_name);
const char * git_remote_url(const git_remote *remote);
int git_remote_set_url(git_remote *remote, const char* url);
const char * git_remote_pushurl(const git_remote *remote);
int git_remote_set_pushurl(git_remote *remote, const char* url);
int git_remote_fetch(git_remote *remote, const git_signature *signature, const char *reflog_message);
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

int git_push_status_foreach(
	git_push *push,
	int (*cb)(const char *ref, const char *msg, void *data),
	void *data);

int git_push_update_tips(
		git_push *push,
		const git_signature *signature,
		const char *reflog_message);
void git_push_free(git_push *push);

const char * git_refspec_src(const git_refspec *refspec);
const char * git_refspec_dst(const git_refspec *refspec);
int git_refspec_force(const git_refspec *refspec);
const char * git_refspec_string(const git_refspec *refspec);
git_direction git_refspec_direction(const git_refspec *spec);

int git_refspec_src_matches(const git_refspec *refspec, const char *refname);
int git_refspec_dst_matches(const git_refspec *refspec, const char *refname);

int git_refspec_transform(git_buf *buf, const git_refspec *spec, const char *name);
int git_refspec_rtransform(git_buf *buf, const git_refspec *spec, const char *name);

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

/*
 * git_checkout
 */

typedef enum { ... } git_checkout_notify_t;

typedef int (*git_checkout_notify_cb)(
	git_checkout_notify_t why,
	const char *path,
	const git_diff_file *baseline,
	const git_diff_file *target,
	const git_diff_file *workdir,
	void *payload);

typedef void (*git_checkout_progress_cb)(
	const char *path,
	size_t completed_steps,
	size_t total_steps,
	void *payload);

typedef struct git_checkout_options {
	unsigned int version;

	unsigned int checkout_strategy;

	int disable_filters;
	unsigned int dir_mode;
	unsigned int file_mode;
	int file_open_flags;

	unsigned int notify_flags;
	git_checkout_notify_cb notify_cb;
	void *notify_payload;

	git_checkout_progress_cb progress_cb;
	void *progress_payload;

	git_strarray paths;

	git_tree *baseline;

	const char *target_directory;

	const char *ancestor_label;
	const char *our_label;
	const char *their_label;
} git_checkout_options;

typedef enum {
	GIT_CLONE_LOCAL_AUTO,
	GIT_CLONE_LOCAL,
	GIT_CLONE_NO_LOCAL,
	GIT_CLONE_LOCAL_NO_LINKS,
} git_clone_local_t;

/*
 * git_clone
 */

typedef struct git_clone_options {
	unsigned int version;

	git_checkout_options checkout_opts;
	git_remote_callbacks remote_callbacks;

	int bare;
	int ignore_cert_errors;
	git_clone_local_t local;
	const char *remote_name;
	const char* checkout_branch;
	git_signature *signature;
} git_clone_options;

int git_clone(git_repository **out,
	const char *url,
	const char *local_path,
	const git_clone_options *options);

int git_clone_into(
	git_repository *repo,
	git_remote *remote,
	const git_checkout_options *co_opts,
	const char *branch,
	const git_signature *signature);

/*
 * git_config
 */

typedef ... git_config;
typedef ... git_config_iterator;

typedef enum {
	GIT_CONFIG_LEVEL_SYSTEM = 1,
	GIT_CONFIG_LEVEL_XDG = 2,
	GIT_CONFIG_LEVEL_GLOBAL = 3,
	GIT_CONFIG_LEVEL_LOCAL = 4,
	GIT_CONFIG_LEVEL_APP = 5,
	GIT_CONFIG_HIGHEST_LEVEL = -1,
} git_config_level_t;

typedef struct {
	const char *name;
	const char *value;
	git_config_level_t level;
} git_config_entry;

int git_repository_config(git_config **out, git_repository *repo);
int git_repository_config_snapshot(git_config **out, git_repository *repo);
void git_config_free(git_config *cfg);

int git_config_get_string(const char **out, const git_config *cfg, const char *name);
int git_config_set_string(git_config *cfg, const char *name, const char *value);
int git_config_set_bool(git_config *cfg, const char *name, int value);
int git_config_set_int64(git_config *cfg, const char *name, int64_t value);

int git_config_parse_bool(int *out, const char *value);
int git_config_parse_int64(int64_t *out, const char *value);

int git_config_delete_entry(git_config *cfg, const char *name);
int git_config_add_file_ondisk(git_config *cfg,
	const char *path,
	git_config_level_t level,
	int force);

int git_config_iterator_new(git_config_iterator **out, const git_config *cfg);
int git_config_next(git_config_entry **entry, git_config_iterator *iter);
void git_config_iterator_free(git_config_iterator *iter);

int git_config_multivar_iterator_new(
	git_config_iterator **out,
	const git_config *cfg,
	const char *name,
	const char *regexp);

int git_config_set_multivar(
	git_config *cfg,
	const char *name,
	const char *regexp,
	const char *value);

int git_config_new(git_config **out);
int git_config_snapshot(git_config **out, git_config *config);
int git_config_open_ondisk(git_config **out, const char *path);
int git_config_find_system(git_buf *out);
int git_config_find_global(git_buf *out);
int git_config_find_xdg(git_buf *out);

/*
 * git_repository_init
 */
typedef enum {
	GIT_REPOSITORY_INIT_BARE,
	GIT_REPOSITORY_INIT_NO_REINIT,
	GIT_REPOSITORY_INIT_NO_DOTGIT_DIR,
	GIT_REPOSITORY_INIT_MKDIR,
	GIT_REPOSITORY_INIT_MKPATH,
	GIT_REPOSITORY_INIT_EXTERNAL_TEMPLATE,
	...
} git_repository_init_flag_t;

typedef enum {
	GIT_REPOSITORY_INIT_SHARED_UMASK,
	GIT_REPOSITORY_INIT_SHARED_GROUP,
	GIT_REPOSITORY_INIT_SHARED_ALL,
	...
} git_repository_init_mode_t;

typedef struct {
	unsigned int version;
	uint32_t    flags;
	uint32_t    mode;
	const char *workdir_path;
	const char *description;
	const char *template_path;
	const char *initial_head;
	const char *origin_url;
} git_repository_init_options;

int git_repository_init(
	git_repository **out,
	const char *path,
	unsigned is_bare);

int git_repository_init_ext(
	git_repository **out,
	const char *repo_path,
	git_repository_init_options *opts);
