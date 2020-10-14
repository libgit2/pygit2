#!/bin/sh

LIBGIT2_VERSION="$1"
if [ -z "$LIBGIT2_VERSION" ]
then
    >&2 echo "Please pass libgit2 version as a first argument of this script ($0)"
    exit 1
fi

PREFIX=/home/travis/install

# Build libssh2 1.9.0 (Ubuntu only has 1.8.0, which doesn't work)
cd ~
wget https://www.libssh2.org/download/libssh2-1.9.0.tar.gz
tar xf libssh2-1.9.0.tar.gz
cd libssh2-1.9.0
./configure --prefix=/usr --disable-static && make
sudo make install

# Build libgit2
cd ~
git clone --depth=1 -b "ethomson/v${LIBGIT2_VERSION}" https://github.com/libgit2/libgit2.git
cd libgit2/

mkdir build && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=$PREFIX -DBUILD_CLAR=OFF
cmake --build . --target install

ls -la ..
