#!/bin/sh

LIBGIT2_VERSION="$1"
if [ -z "$LIBGIT2_VERSION" ]
then
    >&2 echo "Please pass libgit2 version as a first argument of this script ($0)"
    exit 1
fi

cd ~

git clone --depth=1 -b "maint/v${LIBGIT2_VERSION}" https://github.com/libgit2/libgit2.git
cd libgit2/

mkdir build && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=../_install -DBUILD_CLAR=OFF
cmake --build . --target install

ls -la ..
