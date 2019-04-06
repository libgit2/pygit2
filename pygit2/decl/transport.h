typedef struct git_cred git_cred;

typedef enum {
	GIT_CREDTYPE_USERPASS_PLAINTEXT = 1,
	GIT_CREDTYPE_SSH_KEY = 2,
	GIT_CREDTYPE_SSH_CUSTOM = 4,
	GIT_CREDTYPE_DEFAULT = 8,
	GIT_CREDTYPE_SSH_INTERACTIVE = 16,
	GIT_CREDTYPE_USERNAME = 32,
	GIT_CREDTYPE_SSH_MEMORY = 64,
} git_credtype_t;

typedef enum {
	GIT_CERT_SSH_MD5 = 1,
	GIT_CERT_SSH_SHA1 = 2,
} git_cert_ssh_t;

typedef struct {
	git_cert parent;
	git_cert_ssh_t type;
	unsigned char hash_md5[16];
	unsigned char hash_sha1[20];
} git_cert_hostkey;

typedef struct {
	git_cert parent;
	void *data;
	size_t len;
} git_cert_x509;

typedef int (*git_cred_acquire_cb)(
	git_cred **cred,
	const char *url,
	const char *username_from_url,
	unsigned int allowed_types,
	void *payload);

typedef int (*git_transport_cb)(git_transport **out, git_remote *owner, void *param);
int git_cred_username_new(git_cred **cred, const char *username);
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

int git_cred_ssh_key_memory_new(
	git_cred **out,
	const char *username,
	const char *publickey,
	const char *privatekey,
	const char *passphrase);

