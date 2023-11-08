.PHONY: build html

build:
	OPENSSL_VERSION=3.2.3 LIBSSH2_VERSION=1.11.1 LIBGIT2_VERSION=1.9.0 sh build.sh

html: build
	make -C docs html

meson:
	rm builddir -rf
	meson setup builddir
	cd builddir && meson compile

meson_build:
	python -m build

meson_install:
	python -m venv venv
	./venv/bin/pip install -U pip
	./venv/bin/pip install build
