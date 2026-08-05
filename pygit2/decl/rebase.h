typedef struct git_rebase git_rebase;

#define GIT_REBASE_OPTIONS_VERSION ...
#define GIT_REBASE_NO_OPERATION ...

typedef enum {
	GIT_REBASE_OPERATION_PICK = 0,
	GIT_REBASE_OPERATION_REWORD,
	GIT_REBASE_OPERATION_EDIT,
	GIT_REBASE_OPERATION_SQUASH,
	GIT_REBASE_OPERATION_FIXUP,
	GIT_REBASE_OPERATION_EXEC
} git_rebase_operation_t;

typedef struct {
	unsigned int version;
	int quiet;
	int inmemory;
	const char *rewrite_notes_ref;
	git_merge_options merge_options;
	git_checkout_options checkout_options;
	...;
} git_rebase_options;

typedef struct {
	git_rebase_operation_t type;
	const git_oid id;
	const char *exec;
	...;
} git_rebase_operation;

int git_rebase_options_init(git_rebase_options *opts, unsigned int version);

int git_rebase_init(
	git_rebase **out,
	git_repository *repo,
	const git_annotated_commit *branch,
	const git_annotated_commit *upstream,
	const git_annotated_commit *onto,
	const git_rebase_options *opts);

int git_rebase_open(
	git_rebase **out,
	git_repository *repo,
	const git_rebase_options *opts);

const char *git_rebase_orig_head_name(git_rebase *rebase);
const git_oid *git_rebase_orig_head_id(git_rebase *rebase);
const char *git_rebase_onto_name(git_rebase *rebase);
const git_oid *git_rebase_onto_id(git_rebase *rebase);

size_t git_rebase_operation_entrycount(git_rebase *rebase);
size_t git_rebase_operation_current(git_rebase *rebase);
git_rebase_operation *git_rebase_operation_byindex(
	git_rebase *rebase,
	size_t idx);

int git_rebase_next(
	git_rebase_operation **operation,
	git_rebase *rebase);

int git_rebase_inmemory_index(
	git_index **index,
	git_rebase *rebase);

int git_rebase_commit(
	git_oid *id,
	git_rebase *rebase,
	const git_signature *author,
	const git_signature *committer,
	const char *message_encoding,
	const char *message);

int git_rebase_abort(git_rebase *rebase);

int git_rebase_finish(
	git_rebase *rebase,
	const git_signature *signature);

void git_rebase_free(git_rebase *rebase);
