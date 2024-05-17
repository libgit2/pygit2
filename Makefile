.PHONY: build html

build:
	OPENSSL_VERSION=3.1.5 LIBSSH2_VERSION=1.11.0 LIBGIT2_VERSION=1.8.1 sh build.sh

html: build
	make -C docs html
