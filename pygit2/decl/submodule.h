#define GIT_SUBMODULE_UPDATE_OPTIONS_VERSION ...

typedef enum {
	GIT_SUBMODULE_STATUS_IN_HEAD           = (1u << 0),
	GIT_SUBMODULE_STATUS_IN_INDEX          = (1u << 1),
	GIT_SUBMODULE_STATUS_IN_CONFIG         = (1u << 2),
	GIT_SUBMODULE_STATUS_IN_WD             = (1u << 3),
	GIT_SUBMODULE_STATUS_INDEX_ADDED       = (1u << 4),
	GIT_SUBMODULE_STATUS_INDEX_DELETED     = (1u << 5),
	GIT_SUBMODULE_STATUS_INDEX_MODIFIED    = (1u << 6),
	GIT_SUBMODULE_STATUS_WD_UNINITIALIZED  = (1u << 7),
	GIT_SUBMODULE_STATUS_WD_ADDED          = (1u << 8),
	GIT_SUBMODULE_STATUS_WD_DELETED        = (1u << 9),
	GIT_SUBMODULE_STATUS_WD_MODIFIED       = (1u << 10),
	GIT_SUBMODULE_STATUS_WD_INDEX_MODIFIED = (1u << 11),
	GIT_SUBMODULE_STATUS_WD_WD_MODIFIED    = (1u << 12),
	GIT_SUBMODULE_STATUS_WD_UNTRACKED      = (1u << 13),
} git_submodule_status_t;

typedef struct git_submodule_update_options {
	unsigned int version;
	git_checkout_options checkout_opts;
	git_fetch_options fetch_opts;
	int allow_fetch;
} git_submodule_update_options;

int git_submodule_update_init_options(
	git_submodule_update_options *opts, unsigned int version);

int git_submodule_add_setup(
	git_submodule **out,
	git_repository *repo,
	const char *url,
	const char *path,
	int use_gitlink);
int git_submodule_clone(
	git_repository **out,
	git_submodule *submodule,
	const git_submodule_update_options *opts);
int git_submodule_add_finalize(git_submodule *submodule);

int git_submodule_update(git_submodule *submodule, int init, git_submodule_update_options *options);

int git_submodule_lookup(
	git_submodule **out,
	git_repository *repo,
	const char *name);

void git_submodule_free(git_submodule *submodule);
int git_submodule_open(
	git_repository **repo,
	git_submodule *submodule);

int git_submodule_init(git_submodule *submodule, int overwrite);
int git_submodule_sync(git_submodule *submodule);
int git_submodule_reload(git_submodule *submodule, int force);
int git_submodule_status(unsigned int *status, git_repository *repo, const char *name, git_submodule_ignore_t ignore);

int git_submodule_add_to_index(git_submodule *submodule, int write_index);

const char * git_submodule_name(git_submodule *submodule);
const char * git_submodule_path(git_submodule *submodule);
const char * git_submodule_url(git_submodule *submodule);
const char * git_submodule_branch(git_submodule *submodule);
git_submodule_ignore_t git_submodule_ignore(git_submodule *submodule);
git_submodule_recurse_t git_submodule_fetch_recurse_submodules(git_submodule *submodule);
const git_oid * git_submodule_head_id(git_submodule *submodule);
const git_oid * git_submodule_index_id(git_submodule *submodule);
const git_oid * git_submodule_wd_id(git_submodule *submodule);

int git_submodule_set_url(git_repository *repo, const char *name, const char *url);
int git_submodule_set_branch(git_repository *repo, const char *name, const char *branch);
int git_submodule_set_ignore(git_repository *repo, const char *name, git_submodule_ignore_t ignore);
int git_submodule_set_fetch_recurse_submodules(git_repository *repo, const char *name, git_submodule_recurse_t fetch_recurse_submodules);
