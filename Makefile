.PHONY: build html

build:
	OPENSSL_VERSION=3.0.9 LIBSSH2_VERSION=1.11.0 LIBGIT2_VERSION=1.6.4 sh build.sh

html: build
	make -C docs html
