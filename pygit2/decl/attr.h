#define GIT_ATTR_CHECK_FILE_THEN_INDEX	0
#define GIT_ATTR_CHECK_INDEX_THEN_FILE	1
#define GIT_ATTR_CHECK_INDEX_ONLY		2
#define GIT_ATTR_CHECK_NO_SYSTEM		4

typedef enum {
	GIT_ATTR_VALUE_UNSPECIFIED = 0, /**< The attribute has been left unspecified */
	GIT_ATTR_VALUE_TRUE,   /**< The attribute has been set */
	GIT_ATTR_VALUE_FALSE,  /**< The attribute has been unset */
	GIT_ATTR_VALUE_STRING  /**< This attribute has a value */
} git_attr_value_t;

int git_attr_get(
	const char **value_out,
	git_repository *repo,
	uint32_t flags,
	const char *path,
	const char *name);

git_attr_value_t git_attr_value(const char *attr);
