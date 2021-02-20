#!/bin/sh

set -x # Print every command and variable
set -e # Exit script on any command failure

# Variables
LIBSSH2_VERSION=${LIBSSH2_VERSION:-1.9.0}
LIBGIT2_VERSION=${LIBGIT2_VERSION:-1.1.0}
PYTHON=${PYTHON:-python3}

PYTHON_VERSION=$($PYTHON -c "import platform; print(f'{platform.python_implementation()}-{platform.python_version()}')")
PREFIX="${PREFIX:-$(pwd)/ci/$PYTHON_VERSION}"

# Create a virtual environment
$PYTHON -m venv $PREFIX
cd ci

# Install libssh2
wget https://www.libssh2.org/download/libssh2-$LIBSSH2_VERSION.tar.gz -N
tar xf libssh2-$LIBSSH2_VERSION.tar.gz
cd libssh2-$LIBSSH2_VERSION
./configure --prefix=$PREFIX --disable-static
make
make install
cd ..

# Install libgit2
wget https://github.com/libgit2/libgit2/releases/download/v$LIBGIT2_VERSION/libgit2-$LIBGIT2_VERSION.tar.gz -N
tar xf libgit2-$LIBGIT2_VERSION.tar.gz
cd libgit2-$LIBGIT2_VERSION
CMAKE_PREFIX_PATH=$PREFIX cmake . -DBUILD_CLAR=OFF -DCMAKE_INSTALL_PREFIX=$PREFIX
cmake --build . --target install
cd ..

# Install Python requirements
cd ..
$PREFIX/bin/python setup.py egg_info
$PREFIX/bin/pip install -U pip
$PREFIX/bin/pip install -r pygit2.egg-info/requires.txt
$PREFIX/bin/pip install -r requirements-test.txt

# Build locally
LIBGIT2=$PREFIX $PREFIX/bin/python setup.py build_ext --inplace

# Check
SUFFIX=$($PYTHON -c "import imp; print(imp.get_suffixes()[0][0])")
export LD_LIBRARY_PATH=$PREFIX/lib:$LD_LIBRARY_PATH
case "$(uname -s)" in
    Darwin*)    LDD="otool -L";;
    *)          LDD="ldd" # Defaults to Linux
esac
$LDD pygit2/_pygit2$SUFFIX

# Tests
$PREFIX/bin/pytest --cov=pygit2
