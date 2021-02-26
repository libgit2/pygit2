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
set -e # Exit script on any command failure

# Arguments
WHAT=${1:-inplace}

# Variables
PYTHON=${PYTHON:-python3}
PYTHON_VERSION=$($PYTHON -c "import platform; print(f'{platform.python_implementation()}-{platform.python_version()}')")
PREFIX="${PREFIX:-$(pwd)/ci/$PYTHON_VERSION}"
export LDFLAGS="-Wl,-rpath,$PREFIX/lib"

# Linux or macOS
case "$(uname -s)" in
    Darwin*)
        LDD="otool -L"
        SOEXT="dylib"
        ;;
    *) # LINUX
        LDD="ldd"
        SOEXT="so"
        ;;
esac

# Create a virtual environment
$PYTHON -m venv $PREFIX
cd ci

# Install libssh2
if [ -n "$LIBSSH2_VERSION" ]; then
    FILENAME=libssh2-$LIBSSH2_VERSION
    wget https://www.libssh2.org/download/$FILENAME.tar.gz -N
    tar xf $FILENAME.tar.gz
    cd $FILENAME
    ./configure --prefix=$PREFIX --disable-static
    make
    make install
    cd ..
    $LDD $PREFIX/lib/libssh2.$SOEXT
    LIBSSH2_PREFIX=$PREFIX
fi

# Install libgit2
if [ -n "$LIBGIT2_VERSION" ]; then
    FILENAME=libgit2-$LIBGIT2_VERSION
    wget https://github.com/libgit2/libgit2/releases/download/v$LIBGIT2_VERSION/$FILENAME.tar.gz -N
    tar xf $FILENAME.tar.gz
    cd $FILENAME
    CMAKE_PREFIX_PATH=$OPENSSL_PREFIX:$LIBSSH2_PREFIX cmake . -DBUILD_CLAR=OFF -DCMAKE_INSTALL_PREFIX=$PREFIX
    cmake --build . --target install
    cd ..
    $LDD $PREFIX/lib/libgit2.$SOEXT
    export LIBGIT2=$PREFIX
fi

# Build pygit2
cd ..
$PREFIX/bin/pip install -U pip
if [ $WHAT = "wheel" ]; then
    $PREFIX/bin/pip install wheel
    $PREFIX/bin/python setup.py bdist_wheel
else
    # Install Python requirements & build inplace
    $PREFIX/bin/python setup.py egg_info
    $PREFIX/bin/pip install -r pygit2.egg-info/requires.txt
    $PREFIX/bin/python setup.py build_ext --inplace
fi

# Tests
if [ $WHAT = "test" ]; then
    $PREFIX/bin/pip install -r requirements-test.txt
    $PREFIX/bin/pytest --cov=pygit2
fi
