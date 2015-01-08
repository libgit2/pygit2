typedef ... git_repository;
typedef ... git_remote;
typedef ... git_refspec;
typedef ... git_push;
typedef ... git_cred;
typedef ... git_object;
typedef ... git_tree;
typedef ... git_commit;
typedef ... git_index;
typedef ... git_diff;
typedef ... git_index_conflict_iterator;

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

typedef int64_t git_off_t;
typedef int64_t git_time_t;

typedef enum {
	GIT_REF_INVALID = 0,
	GIT_REF_OID = 1,
	GIT_REF_SYMBOLIC = 2,
	GIT_REF_LISTALL = 3,
} git_ref_t;

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

typedef struct git_time {
	git_time_t time;
	int offset;
} git_time;

typedef struct git_signature {
	char *name;
	char *email;
	git_time when;
} git_signature;

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
int git_remote_delete(git_remote *remote);
int git_repository_state_cleanup(git_repository *repo);

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
int git_remote_init_callbacks(git_remote_callbacks *opts, unsigned int version);
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
int git_cred_ssh_key_from_agent(
    git_cred **out,
    const char *username);

/*
 * git_diff
 */

typedef enum {
	GIT_SUBMODULE_IGNORE_RESET     = -1,

	GIT_SUBMODULE_IGNORE_NONE      = 1,
	GIT_SUBMODULE_IGNORE_UNTRACKED = 2,
	GIT_SUBMODULE_IGNORE_DIRTY     = 3,
	GIT_SUBMODULE_IGNORE_ALL       = 4,
	GIT_SUBMODULE_IGNORE_DEFAULT   = 0
} git_submodule_ignore_t;

typedef enum {
	GIT_DELTA_UNMODIFIED = 0,
	GIT_DELTA_ADDED = 1,
	GIT_DELTA_DELETED = 2,
	GIT_DELTA_MODIFIED = 3,
	GIT_DELTA_RENAMED = 4,
	GIT_DELTA_COPIED = 5,
	GIT_DELTA_IGNORED = 6,
	GIT_DELTA_UNTRACKED = 7,
	GIT_DELTA_TYPECHANGE = 8,
} git_delta_t;

typedef struct {
	git_oid     id;
	const char *path;
	git_off_t   size;
	uint32_t    flags;
	uint16_t    mode;
} git_diff_file;

typedef struct {
	git_delta_t   status;
	uint32_t      flags;
	uint16_t      similarity;
	uint16_t      nfiles;
	git_diff_file old_file;
	git_diff_file new_file;
} git_diff_delta;

typedef int (*git_diff_notify_cb)(
	const git_diff *diff_so_far,
	const git_diff_delta *delta_to_add,
	const char *matched_pathspec,
	void *payload);

typedef struct {
	unsigned int version;
	uint32_t flags;

	git_submodule_ignore_t ignore_submodules;
	git_strarray       pathspec;
	git_diff_notify_cb notify_cb;
	void              *notify_payload;

	uint16_t    context_lines;
	uint16_t    interhunk_lines;
	uint16_t    id_abbrev;
	git_off_t   max_size;
	const char *old_prefix;
	const char *new_prefix;
} git_diff_options;

typedef struct {
	int (*file_signature)(
		void **out, const git_diff_file *file,
		const char *fullpath, void *payload);
	int (*buffer_signature)(
		void **out, const git_diff_file *file,
		const char *buf, size_t buflen, void *payload);
	void (*free_signature)(void *sig, void *payload);
	int (*similarity)(int *score, void *siga, void *sigb, void *payload);
	void *payload;
} git_diff_similarity_metric;

int git_diff_init_options(git_diff_options *opts, unsigned int version);
int git_diff_index_to_workdir(git_diff **diff, git_repository *repo, git_index *index, const git_diff_options *opts);
int git_diff_tree_to_index(git_diff **diff, git_repository *repo, git_tree *old_tree, git_index *index, const git_diff_options *opts);

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

int git_checkout_init_options(git_checkout_options *opts, unsigned int version);
int git_checkout_tree(git_repository *repo, const git_object *treeish, const git_checkout_options *opts);
int git_checkout_head(git_repository *repo, const git_checkout_options *opts);
int git_checkout_index(git_repository *repo, git_index *index, const git_checkout_options *opts);

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

#define GIT_CLONE_OPTIONS_VERSION ...
int git_clone_init_options(git_clone_options *opts, unsigned int version);

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

#define GIT_REPOSITORY_INIT_OPTIONS_VERSION ...
int git_repository_init_init_options(git_repository_init_options *opts, int version);

int git_repository_init(
	git_repository **out,
	const char *path,
	unsigned is_bare);

int git_repository_init_ext(
	git_repository **out,
	const char *repo_path,
	git_repository_init_options *opts);

int git_repository_set_head(git_repository *repo, const char *refname, const git_signature *signature, const char *log_message);
int git_repository_set_head_detached(git_repository *repo, const git_oid *commitish, const git_signature *signature, const char *log_message);

/*
 * git_index
 */
typedef int64_t git_time_t;

typedef struct {
	git_time_t seconds;
	unsigned int nanoseconds;
} git_index_time;

typedef struct git_index_entry {
	git_index_time ctime;
	git_index_time mtime;

	unsigned int dev;
	unsigned int ino;
	unsigned int mode;
	unsigned int uid;
	unsigned int gid;
	git_off_t file_size;

	git_oid id;

	unsigned short flags;
	unsigned short flags_extended;

	const char *path;
} git_index_entry;

typedef int (*git_index_matched_path_cb)(
	const char *path, const char *matched_pathspec, void *payload);

void git_index_free(git_index *index);
int git_repository_index(git_index **out, git_repository *repo);
int git_index_open(git_index **out, const char *index_path);
int git_index_read(git_index *index, int force);
int git_index_write(git_index *index);
size_t git_index_entrycount(const git_index *index);
int git_index_find(size_t *at_pos, git_index *index, const char *path);
int git_index_add_bypath(git_index *index, const char *path);
int git_index_add(git_index *index, const git_index_entry *source_entry);
int git_index_remove(git_index *index, const char *path, int stage);
int git_index_read_tree(git_index *index, const git_tree *tree);
int git_index_clear(git_index *index);
int git_index_write_tree(git_oid *out, git_index *index);
int git_index_write_tree_to(git_oid *out, git_index *index, git_repository *repo);
const git_index_entry *git_index_get_bypath(git_index *index, const char *path, int stage);
const git_index_entry *git_index_get_byindex(git_index *index, size_t n);
int git_index_add_all(git_index *index,	const git_strarray *pathspec, unsigned int flags,
	git_index_matched_path_cb callback,	void *payload);
int git_index_has_conflicts(const git_index *index);
void git_index_conflict_iterator_free(git_index_conflict_iterator *iterator);
int git_index_conflict_iterator_new(git_index_conflict_iterator **iterator_out, git_index *index);
int git_index_conflict_get(const git_index_entry **ancestor_out, const git_index_entry **our_out, const git_index_entry **their_out, git_index *index, const char *path);
int git_index_conflict_next(const git_index_entry **ancestor_out, const git_index_entry **our_out, const git_index_entry **their_out, git_index_conflict_iterator *iterator);
int git_index_conflict_remove(git_index *index, const char *path);

/*
 * git_blame
 */

typedef ... git_blame;

typedef struct git_blame_options {
	unsigned int version;

	uint32_t flags;
	uint16_t min_match_characters;
	git_oid newest_commit;
	git_oid oldest_commit;
	uint32_t min_line;
	uint32_t max_line;
} git_blame_options;

#define GIT_BLAME_OPTIONS_VERSION ...

typedef struct git_blame_hunk {
	uint16_t lines_in_hunk;

	git_oid final_commit_id;
	uint16_t final_start_line_number;
	git_signature *final_signature;

	git_oid orig_commit_id;
	const char *orig_path;
	uint16_t orig_start_line_number;
	git_signature *orig_signature;

	char boundary;
} git_blame_hunk;

int git_blame_init_options(git_blame_options *opts, unsigned int version);
uint32_t git_blame_get_hunk_count(git_blame *blame);
const git_blame_hunk *git_blame_get_hunk_byindex(git_blame *blame, uint32_t index);
const git_blame_hunk *git_blame_get_hunk_byline(git_blame *blame, uint32_t lineno);
int git_blame_file(git_blame **out, git_repository *repo, const char *path, git_blame_options *options);
void git_blame_free(git_blame *blame);

/*
 * Merging
 */

typedef enum { ... } git_merge_tree_flag_t;

typedef enum {
	GIT_MERGE_FILE_FAVOR_NORMAL = 0,
	GIT_MERGE_FILE_FAVOR_OURS = 1,
	GIT_MERGE_FILE_FAVOR_THEIRS = 2,
	GIT_MERGE_FILE_FAVOR_UNION = 3,
} git_merge_file_favor_t;

typedef struct {
	unsigned int version;
	git_merge_tree_flag_t flags;
	unsigned int rename_threshold;
	unsigned int target_limit;
	git_diff_similarity_metric *metric;
	git_merge_file_favor_t file_favor;
} git_merge_options;

#define GIT_MERGE_OPTIONS_VERSION ...

int git_merge_init_options(git_merge_options *opts,	unsigned int version);
int git_merge_commits(git_index **out, git_repository *repo, const git_commit *our_commit, const git_commit *their_commit, const git_merge_options *opts);
