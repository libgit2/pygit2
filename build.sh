#!/bin/sh

#
# Synopsis:
#
#   sh build.sh               - Build inplace
#   sh build.sh test          - Build inplace, and run the tests
#   sh build.sh wheel         - Build a wheel, install, and run the tests
#
# Environment variables:
#
#   LIBSSH2_OPENSSL           - Where to find openssl
#   LIBSSH2_PREFIX            - Where to find libssh2
#   LIBSSH2_VERSION=<Version> - Build the given version of libssh2
#   LIBGIT2_VERSION=<Versoin> - Build the given version of libgit2
#
# Either use LIBSSH2_PREFIX, or LIBSSH2_VERSION, or none (if libssh2 is already
# in the path, or if you don't want to use it).
#
# Examples.
#
# Build inplace, libgit2 must be available in the path:
#
#   sh build.sh
#
# Build libgit2 1.1.0 (will use libssh2 if available), then build pygit2
# inplace:
#
#   LIBGIT2_VERSION=1.1.0 sh build.sh
#
# Build libssh2 1.9.0 and libgit2 1.1.0, then build pygit2 inplace:
#
#   LIBSSH2_VERSION=1.9.0 LIBGIT2_VERSION=1.1.0 sh build.sh
#
# Tell where libssh2 is installed, build libgit2 1.1.0, then build pygit2
# inplace:
#
#   LIBSSH2_PREFIX=/usr/local LIBGIT2_VERSION=1.1.0 sh build.sh
#
# Build inplace and run the tests:
#
#   sh build.sh test
#
# Build a wheel:
#
#   sh build.sh wheel
#

set -x # Print every command and variable
set -e # Fail fast

# Variables
ARCH=`uname -m`
KERNEL=`uname -s`
BUILD_TYPE=${BUILD_TYPE:-Debug}
PYTHON=${PYTHON:-python3}

PYTHON_TAG=$($PYTHON build_tag.py)
PREFIX="${PREFIX:-$(pwd)/ci/$PYTHON_TAG}"
export LDFLAGS="-Wl,-rpath,$PREFIX/lib"

# Create a virtual environment
$PYTHON -m venv $PREFIX
cd ci

# Install zlib
# XXX Build libgit2 with USE_BUNDLED_ZLIB instead?
if [ -n "$ZLIB_VERSION" ]; then
    FILENAME=zlib-$ZLIB_VERSION
    wget https://www.zlib.net/$FILENAME.tar.gz -N
    tar xf $FILENAME.tar.gz
    cd $FILENAME
    ./configure --prefix=$PREFIX
    make
    make install
    cd ..
fi

# Install libssh2
if [ -n "$LIBSSH2_VERSION" ]; then
    FILENAME=libssh2-$LIBSSH2_VERSION
    wget https://www.libssh2.org/download/$FILENAME.tar.gz -N
    tar xf $FILENAME.tar.gz
    cd $FILENAME
    cmake . \
            -DCMAKE_INSTALL_PREFIX=$PREFIX \
            -DBUILD_SHARED_LIBS=ON \
            -DBUILD_EXAMPLES=OFF \
            -DBUILD_TESTING=OFF
    cmake --build . --target install
    cd ..
    LIBSSH2_PREFIX=$PREFIX
fi

# Install libgit2
if [ -n "$LIBGIT2_VERSION" ]; then
    FILENAME=libgit2-$LIBGIT2_VERSION
    wget https://github.com/libgit2/libgit2/releases/download/v$LIBGIT2_VERSION/$FILENAME.tar.gz -N
    tar xf $FILENAME.tar.gz
    cd $FILENAME
    CMAKE_PREFIX_PATH=$OPENSSL_PREFIX:$LIBSSH2_PREFIX cmake . \
            -DCMAKE_INSTALL_PREFIX=$PREFIX \
            -DBUILD_SHARED_LIBS=ON \
            -DBUILD_CLAR=OFF \
            -DCMAKE_BUILD_TYPE=$BUILD_TYPE
    cmake --build . --target install
    cd ..
    export LIBGIT2=$PREFIX
fi

# Build pygit2
cd ..
$PREFIX/bin/pip install -U pip
if [ "$1" = "wheel" ]; then
    shift
    $PREFIX/bin/pip install wheel
    $PREFIX/bin/python setup.py bdist_wheel
    WHEELDIR=dist
else
    # Install Python requirements & build inplace
    $PREFIX/bin/python setup.py egg_info
    $PREFIX/bin/pip install -r pygit2.egg-info/requires.txt
    $PREFIX/bin/python setup.py build_ext --inplace
fi

# Bundle libraries
if [ "$1" = "bundle" ]; then
    shift
    WHEELDIR=wheelhouse
    case "${KERNEL}" in
        Darwin*)
            $PREFIX/bin/pip install delocate
            $PREFIX/bin/delocate-listdeps dist/pygit2-*macosx*.whl
            $PREFIX/bin/delocate-wheel -v -w $WHEELDIR dist/pygit2-*macosx*.whl
            $PREFIX/bin/delocate-listdeps $WHEELDIR/pygit2-*macosx*.whl
            ;;
        *) # LINUX
            $PREFIX/bin/pip install auditwheel
            $PREFIX/bin/auditwheel repair dist/pygit2*-$PYTHON_TAG-*_$ARCH.whl
            $PREFIX/bin/auditwheel show $WHEELDIR/pygit2*-$PYTHON_TAG-*_$ARCH.whl
            ;;
    esac
fi

# Tests
if [ "$1" = "test" ]; then
    if [ -n "$WHEELDIR" ]; then
        $PREFIX/bin/pip install $WHEELDIR/pygit2*-$PYTHON_TAG-*_$ARCH.whl
    fi
    $PREFIX/bin/pip install -r requirements-test.txt
    $PREFIX/bin/pytest --cov=pygit2
fi
