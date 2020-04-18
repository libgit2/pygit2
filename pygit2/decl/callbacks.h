extern "Python" int _certificate_cb(
    git_cert *cert,
    int valid,
    const char *host,
    void *payload);

extern "Python" int _credentials_cb(
    git_credential **out,
    const char *url,
    const char *username_from_url,
    unsigned int allowed_types,
    void *payload);

extern "Python" int _push_update_reference_cb(
    const char *refname,
    const char *status,
    void *data);

extern "Python" int _remote_create_cb(
	git_remote **out,
	git_repository *repo,
	const char *name,
	const char *url,
	void *payload);

extern "Python" int _repository_create_cb(
	git_repository **out,
	const char *path,
	int bare,
	void *payload);

extern "Python" int _sideband_progress_cb(
    const char *str,
    int len,
    void *payload);

extern "Python" int _transfer_progress_cb(
    const git_indexer_progress *stats,
    void *payload);

extern "Python" int _update_tips_cb(
	const char *refname,
	const git_oid *a,
	const git_oid *b,
	void *data);
