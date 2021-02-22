#!/bin/sh

set -x # Print every command and variable
set -e # Exit script on any command failure

echo $LIBSSH2_PREFIX

# Variables
#LIBSSH2_VERSION=${LIBSSH2_VERSION:-1.9.0}
#LIBGIT2_VERSION=${LIBGIT2_VERSION:-1.1.0}
PYTHON=${PYTHON:-python3}

PYTHON_VERSION=$($PYTHON -c "import platform; print(f'{platform.python_implementation()}-{platform.python_version()}')")
PREFIX="${PREFIX:-$(pwd)/ci/$PYTHON_VERSION}"

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
fi

# Install Python requirements
cd ..
$PREFIX/bin/python setup.py egg_info
$PREFIX/bin/pip install -U pip
$PREFIX/bin/pip install -r pygit2.egg-info/requires.txt
$PREFIX/bin/pip install -r requirements-test.txt

# Build locally
LIBGIT2=$PREFIX $PREFIX/bin/python setup.py build_ext --inplace

# Tests
export LD_LIBRARY_PATH=$PREFIX/lib:$LD_LIBRARY_PATH
$PREFIX/bin/pytest --cov=pygit2
