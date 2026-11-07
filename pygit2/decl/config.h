typedef struct git_config_iterator git_config_iterator;
typedef struct git_config_backend git_config_backend;
typedef struct git_config_backend_entry git_config_backend_entry;
typedef struct git_config_backend_memory_options git_config_backend_memory_options;

typedef enum {
	GIT_CONFIG_LEVEL_PROGRAMDATA = 1,
	GIT_CONFIG_LEVEL_SYSTEM = 2,
	GIT_CONFIG_LEVEL_XDG = 3,
	GIT_CONFIG_LEVEL_GLOBAL = 4,
	GIT_CONFIG_LEVEL_LOCAL = 5,
	GIT_CONFIG_LEVEL_WORKTREE = 6,
	GIT_CONFIG_LEVEL_APP = 7,
	GIT_CONFIG_HIGHEST_LEVEL = -1
} git_config_level_t;

typedef struct git_config_entry {
	const char *name;
	const char *value;
	const char *backend_type;
	const char *origin_path;
	unsigned int include_depth;
	git_config_level_t level;
} git_config_entry;

struct git_config_backend_entry {
	struct git_config_entry entry;
    void (*free)(struct git_config_backend_entry *);
};

struct git_config_backend {
	unsigned int version;
	int readonly;
	struct git_config *cfg;
	int (*open)(struct git_config_backend *, git_config_level_t, const git_repository *);
	int (*get)(struct git_config_backend *, const char *, git_config_backend_entry **);
	int (*set)(struct git_config_backend *, const char *, const char *);
	int (*set_multivar)(git_config_backend *, const char *, const char *, const char *);
	int (*del)(struct git_config_backend *, const char *);
	int (*del_multivar)(struct git_config_backend *, const char *, const char *);
	int (*iterator)(git_config_iterator **, struct git_config_backend *);
	int (*snapshot)(struct git_config_backend **, struct git_config_backend *);
	int (*lock)(struct git_config_backend *);
	int (*unlock)(struct git_config_backend *, int);
	void (*free)(struct git_config_backend *);
};


struct git_config_backend_memory_options {
	unsigned int version;
	const char *backend_type;
	const char *origin_path;
};

struct git_config_iterator {
	git_config_backend *backend;
	unsigned int flags;
	int (*next)(git_config_backend_entry **, git_config_iterator *);
    void (*free)(git_config_iterator *);
};

void git_config_entry_free(git_config_entry *);
void git_config_free(git_config *cfg);
int git_config_get_entry(
	git_config_entry **out,
	const git_config *cfg,
	const char *name);

int git_config_get_string(const char **out, const git_config *cfg, const char *name);
int git_config_set_string(git_config *cfg, const char *name, const char *value);
int git_config_set_bool(git_config *cfg, const char *name, int value);
int git_config_set_int64(git_config *cfg, const char *name, int64_t value);
int git_config_parse_bool(int *out, const char *value);
int git_config_parse_int64(int64_t *out, const char *value);
int git_config_delete_entry(git_config *cfg, const char *name);
int git_config_add_file_ondisk(
	git_config *cfg,
	const char *path,
	git_config_level_t level,
	const git_repository *repo,
	int force);
int git_config_iterator_new(git_config_iterator **out, const git_config *cfg);
int git_config_next(git_config_entry **entry, git_config_iterator *iter);
void git_config_iterator_free(git_config_iterator *iter);
int git_config_multivar_iterator_new(git_config_iterator **out, const git_config *cfg, const char *name, const char *regexp);
int git_config_set_multivar(git_config *cfg, const char *name, const char *regexp, const char *value);
int git_config_delete_multivar(git_config *cfg, const char *name, const char *regexp);
int git_config_new(git_config **out);
int git_config_snapshot(git_config **out, git_config *config);
int git_config_open_ondisk(git_config **out, const char *path);
int git_config_open_default(git_config **out);
int git_config_find_system(git_buf *out);
int git_config_find_global(git_buf *out);
int git_config_find_xdg(git_buf *out);
int git_config_set_writeorder(git_config *config, git_config_level_t *levels, size_t len);

int git_config_init_backend(git_config_backend *backend, unsigned int version);
int git_config_add_backend(
    git_config *config,
    git_config_backend *backend,
    git_config_level_t level,
    const git_repository *repo,
    int force);

// Python functions invocable from C in support of the in-memory APP level backend provided
// by PyGit2. See config.py for more details.
extern "Python" int _config_memory_backend_open(
    struct git_config_backend *backend,
    git_config_level_t level,
    const git_repository *repo);

extern "Python" int _config_memory_backend_get(
    struct git_config_backend * backend,
    const char *name,
    git_config_backend_entry **out);

extern "Python" int _config_memory_backend_set(
    struct git_config_backend *backend,
    const char *name,
    const char *value);

extern "Python" int _config_memory_backend_set_multivar(
    git_config_backend *backend,
    const char *name,
    const char *regexp,
    const char *value);

extern "Python" int _config_memory_backend_del(
    struct git_config_backend *backend,
    const char *name);

extern "Python" int _config_memory_backend_del_multivar(
    struct git_config_backend *backend,
    const char *name,
    const char *regexp);

extern "Python" int _config_memory_backend_iterator(
    git_config_iterator **out,
    struct git_config_backend *backend);

extern "Python" int _config_memory_backend_snapshot(
    struct git_config_backend **out,
    struct git_config_backend *backend);

extern "Python" int _config_memory_backend_lock(
    struct git_config_backend *backend);

extern "Python" int _config_memory_backend_unlock(
    struct git_config_backend *backend,
    int success);

extern "Python" void _config_memory_backend_free(
    struct git_config_backend *backend);

extern "Python" void _config_memory_backend_entry_free(
    struct git_config_backend_entry *entry);

extern "Python" int _config_memory_iterator_next(
    git_config_backend_entry **out,
    git_config_iterator *iter);

extern "Python" void _config_memory_iterator_free(
    git_config_iterator *iter);

extern "Python" void _config_memory_iterator_entry_free(
    struct git_config_backend_entry *entry);
