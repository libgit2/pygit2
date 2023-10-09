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

/* Checkout */

extern "Python" int _checkout_notify_cb(
    git_checkout_notify_t why,
    const char *path,
    const git_diff_file *baseline,
    const git_diff_file *target,
    const git_diff_file *workdir,
    void *payload);

extern "Python" void _checkout_progress_cb(
    const char *path,
    size_t completed_steps,
    size_t total_steps,
    void *payload);

/* Stash */

extern "Python" int _stash_apply_progress_cb(
    git_stash_apply_progress_t progress,
    void *payload);

extern "Python" void _filter_shutdown_cb(git_filter *self);

extern "Python" int _filter_check_cb(
    git_filter *self,
    void **payload,
    const git_filter_source *src,
    const char **attr_values);

extern "Python" int _filter_stream_cb(
    git_writestream **out,
    git_filter *self,
    void **payload,
    const git_filter_source *src,
    git_writestream *next);

extern "Python" void _filter_cleanup_cb(
    git_filter *self,
    void *payload);

extern "Python" int _writestream_write_cb(
    git_writestream *stream,
    const char *buffer,
    size_t len);

extern "Python" int _writestream_close_cb(git_writestream *stream);

extern "Python" void _writestream_free_cb(git_writestream *stream);
