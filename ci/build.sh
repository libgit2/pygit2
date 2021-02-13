#!/bin/sh

LIBSSH2_VERSION=1.9.0
LIBGIT2_VERSION=1.1.0

PREFIX=`realpath install`

wget https://www.libssh2.org/download/libssh2-$LIBSSH2_VERSION.tar.gz
tar xf libssh2-$LIBSSH2_VERSION.tar.gz
cd libssh2-$LIBSSH2_VERSION
./configure --prefix=$PREFIX --disable-static
make
make install
cd ..

wget https://github.com/libgit2/libgit2/releases/download/v$LIBGIT2_VERSION/libgit2-$LIBGIT2_VERSION.tar.gz
tar xf libgit2-$LIBGIT2_VERSION.tar.gz
cd libgit2-$LIBGIT2_VERSION
CMAKE_PREFIX_PATH=$PREFIX cmake . -DBUILD_CLAR=OFF -DCMAKE_INSTALL_PREFIX=$PREFIX
cmake --build . --target install
cd ..
