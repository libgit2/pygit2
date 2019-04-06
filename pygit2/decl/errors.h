typedef enum {
	GIT_OK         =  0,

	GIT_ERROR      = -1,
	GIT_ENOTFOUND  = -3,
	GIT_EEXISTS    = -4,
	GIT_EAMBIGUOUS = -5,
	GIT_EBUFS      = -6,

	GIT_EUSER      = -7,

	GIT_EBAREREPO       =  -8,
	GIT_EUNBORNBRANCH   =  -9,
	GIT_EUNMERGED       = -10,
	GIT_ENONFASTFORWARD = -11,
	GIT_EINVALIDSPEC    = -12,
	GIT_ECONFLICT       = -13,
	GIT_ELOCKED         = -14,
	GIT_EMODIFIED       = -15,
	GIT_EAUTH           = -16,
	GIT_ECERTIFICATE    = -17,
	GIT_EAPPLIED        = -18,
	GIT_EPEEL           = -19,
	GIT_EEOF            = -20,
	GIT_EINVALID        = -21,
	GIT_EUNCOMMITTED    = -22,
	GIT_EDIRECTORY      = -23,
	GIT_EMERGECONFLICT  = -24,

	GIT_PASSTHROUGH     = -30,
	GIT_ITEROVER        = -31,
	GIT_RETRY           = -32,
	GIT_EMISMATCH       = -33,
	GIT_EINDEXDIRTY     = -34,
	GIT_EAPPLYFAIL      = -35,
} git_error_code;


typedef struct {
	char *message;
	int klass;
} git_error;


const git_error * git_error_last(void);
