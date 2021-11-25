#!/bin/sh
set -x # Print every command and variable
set -e # Fail fast

# Variables
ARCH=`uname -m`
KERNEL=`uname -s`
BUILD_TYPE=${BUILD_TYPE:-Debug}
PYTHON=${PYTHON:-python3}

PREFIX="${PREFIX:-$(pwd)/ci/}"
export LDFLAGS="-Wl,-rpath,$PREFIX/lib"

OPENSSL_VERSION=3.0.0

rm -rf ci
mkdir ci || true
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

# Install openssl
FILENAME=openssl-$OPENSSL_VERSION
wget https://www.openssl.org/source/$FILENAME.tar.gz -N --no-check-certificate

tar xf $FILENAME.tar.gz
mv $FILENAME openssl-x86

tar xf $FILENAME.tar.gz
mv $FILENAME openssl-arm

cd openssl-x86
./Configure darwin64-x86_64-cc shared
make
cd ../openssl-arm
./Configure enable-rc5 zlib darwin64-arm64-cc no-asm
make
cd ..

mkdir openssl-universal

LIBSSL=$(basename openssl-x86/libssl.*.dylib)
lipo -create openssl-x86/libssl.*.dylib openssl-arm/libssl.*.dylib -output openssl-universal/$LIBSSL
LIBCRYPTO=$(basename openssl-x86/libcrypto.*.dylib)
lipo -create openssl-x86/libcrypto.*.dylib openssl-arm/libcrypto.*.dylib -output openssl-universal/$LIBCRYPTO
cd openssl-universal
install_name_tool -id "@rpath/$LIBSSL" $LIBSSL
install_name_tool -id "@rpath/$LIBCRYPTO" $LIBCRYPTO
OPENSSL_PREFIX=$(pwd)
cd ..


# Install libssh2
if [ -n "$LIBSSH2_VERSION" ]; then
    FILENAME=libssh2-$LIBSSH2_VERSION
    wget https://www.libssh2.org/download/$FILENAME.tar.gz -N --no-check-certificate
    tar xf $FILENAME.tar.gz
    cd $FILENAME
    cmake . \
            -DCMAKE_INSTALL_PREFIX=$PREFIX \
            -DBUILD_SHARED_LIBS=ON \
            -DBUILD_EXAMPLES=OFF \
            -DCMAKE_OSX_ARCHITECTURES="arm64;x86_64" \
            -DOPENSSL_CRYPTO_LIBRARY="../openssl-universal/$LIBCRYPTO" \
            -DOPENSSL_SSL_LIBRARY="../openssl-universal/$LIBSSL" \
            -DOPENSSL_INCLUDE_DIR="../openssl-x86/include" \
            -DBUILD_TESTING=OFF
    cmake --build . --target install
    cd ..
    LIBSSH2_PREFIX=$PREFIX
fi

# Install libgit2
if [ -n "$LIBGIT2_VERSION" ]; then
    FILENAME=libgit2-$LIBGIT2_VERSION
    wget https://github.com/libgit2/libgit2/archive/refs/tags/v$LIBGIT2_VERSION.tar.gz -N -O $FILENAME.tar.gz
    tar xf $FILENAME.tar.gz
    cd $FILENAME
    CMAKE_PREFIX_PATH=$OPENSSL_PREFIX:$LIBSSH2_PREFIX cmake . \
            -DBUILD_SHARED_LIBS=ON \
            -DBUILD_CLAR=OFF \
            -DCMAKE_OSX_ARCHITECTURES="arm64;x86_64" \
            -DCMAKE_BUILD_TYPE=$BUILD_TYPE \
            -DOPENSSL_CRYPTO_LIBRARY="../openssl-universal/$LIBCRYPTO" \
            -DOPENSSL_SSL_LIBRARY="../openssl-universal/$LIBSSL" \
            -DOPENSSL_INCLUDE_DIR="../openssl-x86/include"
    cmake --build . --target install
    cd ..
fi

# This is gross
cp -r $OPENSSL_PREFIX/*.dylib /usr/local/lib
cp -r $LIBSSH2_PREFIX/lib/*.dylib /usr/local/lib
cp -r $FILENAME/*.dylib /usr/local/lib
