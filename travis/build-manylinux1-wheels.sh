#!/usr/bin/env bash

set -e -x
CURDIR=`pwd`

# Install a system package required by our library
yum -y install git libssh2-devel libffi-devel openssl-devel pkgconfig

# libgit2 needs cmake 2.8, which can be found in EPEL

yum -y install cmake28

git clone --depth=1 -b maint/v0.24 https://github.com/libgit2/libgit2.git
cd libgit2/


mkdir build && cd build
cmake28 .. -DCMAKE_INSTALL_PREFIX=../_install -DBUILD_CLAR=OFF
cmake28 --build . --target install
export LIBGIT2=$CURDIR/libgit2/_install/
export LD_LIBRARY_PATH=$CURDIR/libgit2/_install/lib

mkdir -p wheelhouse

# Compile wheels
for PYBIN in /opt/python/*/bin; do
    ${PYBIN}/pip wheel /io/ -w wheelhouse/
done

# Bundle external shared libraries into the wheels
for whl in wheelhouse/pygit*.whl; do
    auditwheel repair $whl -w /io/wheelhouse/
done

# Install packages
for PYBIN in /opt/python/*/bin/; do
    ${PYBIN}/pip install pygit2 --no-index -f /io/wheelhouse
done

chmod 0777 wheelhouse/*.whl