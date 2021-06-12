.PHONY: build html

build:
	LIBGIT2_VERSION=1.1.0 sh build.sh

html:
	cd docs && find . -name "*rst" | entr make html
