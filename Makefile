.PHONY: build html

build:
	OPENSSL_VERSION=3.0.7 LIBSSH2_VERSION=1.10.0 LIBGIT2_VERSION=1.5.1 sh build.sh

html: build
	make -C docs html
