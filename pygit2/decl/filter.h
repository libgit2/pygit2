typedef enum {
	GIT_FILTER_TO_WORKTREE = ...,
	GIT_FILTER_TO_ODB = ...,
} git_filter_mode_t;

typedef enum {
	GIT_FILTER_DEFAULT = ...,
	GIT_FILTER_ALLOW_UNSAFE = ...,
	GIT_FILTER_NO_SYSTEM_ATTRIBUTES = ...,
	GIT_FILTER_ATTRIBUTES_FROM_HEAD = ...,
	GIT_FILTER_ATTRIBUTES_FROM_COMMIT = ...,
} git_filter_flag_t;

int git_filter_list_load(
	git_filter_list **filters,
	git_repository *repo,
	git_blob *blob,
	const char *path,
	git_filter_mode_t mode,
	uint32_t flags);

int git_filter_list_contains(
	git_filter_list *filters,
	const char *name);

size_t git_filter_list_length(
	const git_filter_list *fl);

void git_filter_list_free(git_filter_list *filters);
