#define GIT_PATH_MAX ...


typedef enum {
	GIT_FEATURE_THREADS	= 1,
	GIT_FEATURE_HTTPS	= 2,
	GIT_FEATURE_SSH		= 4,
	GIT_FEATURE_NSEC	= 8,
} git_feature_t;

int git_libgit2_features(void);
