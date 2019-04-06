typedef struct {
	char   *ptr;
	size_t asize, size;
} git_buf;

void git_buf_dispose(git_buf *buffer);
