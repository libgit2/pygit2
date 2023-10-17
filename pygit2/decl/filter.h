typedef enum {
	GIT_FILTER_TO_WORKTREE = 0,
	GIT_FILTER_SMUDGE = GIT_FILTER_TO_WORKTREE,
	GIT_FILTER_TO_ODB = 1,
	GIT_FILTER_CLEAN = GIT_FILTER_TO_ODB
} git_filter_mode_t;

typedef enum {
	GIT_FILTER_DEFAULT = 0u,
	GIT_FILTER_ALLOW_UNSAFE = (1u << 0),
	GIT_FILTER_NO_SYSTEM_ATTRIBUTES = (1u << 1),
	GIT_FILTER_ATTRIBUTES_FROM_HEAD = (1u << 2),
	GIT_FILTER_ATTRIBUTES_FROM_COMMIT = (1u << 3)
} git_filter_flag_t;



#define GIT_FILTER_VERSION ...

#define GIT_FILTER_DRIVER_PRIORITY 200

typedef struct git_filter_source git_filter_source;
typedef struct git_filter git_filter;

typedef int (*git_filter_init_fn)(git_filter *self);
typedef void (*git_filter_shutdown_fn)(git_filter *self);
typedef int (*git_filter_check_fn)(
	git_filter              *self,
	void                   **payload, /* NULL on entry, may be set */
	const git_filter_source *src,
	const char             **attr_values);
typedef int (*git_filter_apply_fn)(
	git_filter              *self,
	void                   **payload, /* may be read and/or set */
	git_buf                 *to,
	const git_buf           *from,
	const git_filter_source *src);
typedef int (*git_filter_stream_fn)(
	git_writestream        **out,
	git_filter              *self,
	void                   **payload,
	const git_filter_source *src,
	git_writestream         *next);
typedef void (*git_filter_cleanup_fn)(
	git_filter              *self,
	void                    *payload);

struct git_filter {
	unsigned int           version;
	const char            *attributes;
	git_filter_init_fn     initialize;
	git_filter_shutdown_fn shutdown;
	git_filter_check_fn    check;
	git_filter_apply_fn    apply; /* deprecated in favor of stream */
	git_filter_stream_fn   stream;
	git_filter_cleanup_fn  cleanup;
};

int git_filter_init(git_filter *filter, unsigned int version);
int git_filter_register(
	const char *name, git_filter *filter, int priority);
int git_filter_unregister(const char *name);
git_repository *git_filter_source_repo(const git_filter_source *src);
const char *git_filter_source_path(const git_filter_source *src);
uint16_t git_filter_source_filemode(const git_filter_source *src);
const git_oid *git_filter_source_id(const git_filter_source *src);
git_filter_mode_t git_filter_source_mode(const git_filter_source *src);
uint32_t git_filter_source_flags(const git_filter_source *src);
