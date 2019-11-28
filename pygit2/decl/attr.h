#define GIT_ATTR_CHECK_FILE_THEN_INDEX	0
#define GIT_ATTR_CHECK_INDEX_THEN_FILE	1
#define GIT_ATTR_CHECK_INDEX_ONLY		2
#define GIT_ATTR_CHECK_NO_SYSTEM		4

typedef enum {
	GIT_ATTR_UNSPECIFIED_T = 0,
	GIT_ATTR_TRUE_T,
	GIT_ATTR_FALSE_T,
	GIT_ATTR_VALUE_T,
} git_attr_value_t;

int git_attr_get(
	const char **value_out,
	git_repository *repo,
	uint32_t flags,
	const char *path,
	const char *name);

git_attr_value_t git_attr_value(const char *attr);
