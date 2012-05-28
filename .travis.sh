#!/bin/sh

cd ~

git clone -b master https://github.com/libgit2/libgit2.git
cd libgit2/

mkdir build && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=../_install
cmake --build . --target install

ls -la ..
