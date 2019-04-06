typedef int (*git_packbuilder_progress)(
	int stage,
	uint32_t current,
	uint32_t total,
	void *payload);
