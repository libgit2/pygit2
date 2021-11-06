.PHONY: build html

build:
	LIBSSH2_VERSION=1.10.0 LIBGIT2_VERSION=1.3.0 sh build.sh

html: build
	make -C docs html
