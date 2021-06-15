.PHONY: build html

build:
	LIBSSH2_VERSION=1.9.0 LIBGIT2_VERSION=1.1.0 sh build.sh

html:
	cd docs && find . -name "*rst" | entr make html
