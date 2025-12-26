.PHONY: build html

build:
	OPENSSL_VERSION=3.5.4 LIBSSH2_VERSION=1.11.1 LIBGIT2_VERSION=1.9.2 sh build.sh

html: build
	make -C docs html
