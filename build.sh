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
#   LIBGIT2_VERSION=<Version> - Build the given version of libgit2
#   OPENSSL_VERSION=<Version> - Build the given version of OpenSSL
#                               (only needed for Mac universal on CI)
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
# Build libgit2 1.3.0 (will use libssh2 if available), then build pygit2
# inplace:
#
#   LIBGIT2_VERSION=1.3.0 sh build.sh
#
# Build libssh2 1.10.0 and libgit2 1.3.0, then build pygit2 inplace:
#
#   LIBSSH2_VERSION=1.10.0 LIBGIT2_VERSION=1.3.0 sh build.sh
#
# Tell where libssh2 is installed, build libgit2 1.3.0, then build pygit2
# inplace:
#
#   LIBSSH2_PREFIX=/usr/local LIBGIT2_VERSION=1.3.0 sh build.sh
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

if [ "$CIBUILDWHEEL" != "1" ]; then
    PYTHON_TAG=$($PYTHON build_tag.py)
fi

PREFIX="${PREFIX:-$(pwd)/ci/$PYTHON_TAG}"
export LDFLAGS="-Wl,-rpath,$PREFIX/lib"

if [ "$CIBUILDWHEEL" = "1" ]; then
    rm -rf ci
    mkdir ci || true
    cd ci
    if [ "$KERNEL" = "Linux" ]; then
        yum install wget openssl-devel libssh2-devel zlib-devel -y
    fi
else
    # Create a virtual environment
    $PYTHON -m venv $PREFIX
fi

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
if [ -n "$OPENSSL_VERSION" ]; then
    if [ "$CIBUILDWHEEL" != "1" ] || [ "$KERNEL" != "Darwin" ]; then
        echo "OPENSSL_VERSION should only be set when building"
        echo "macOS universal2 wheels on GitHub!"
        echo "Please unset and try again"
        exit 1
    fi
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
fi

# Install libssh2
if [ -n "$LIBSSH2_VERSION" ]; then
    FILENAME=libssh2-$LIBSSH2_VERSION
    wget https://www.libssh2.org/download/$FILENAME.tar.gz -N --no-check-certificate
    tar xf $FILENAME.tar.gz
    cd $FILENAME
    if [ "$KERNEL" = "Darwin" ] && [ "$CIBUILDWHEEL" = "1" ]; then
        cmake . \
                -DCMAKE_INSTALL_PREFIX=$PREFIX \
                -DBUILD_SHARED_LIBS=ON \
                -DBUILD_EXAMPLES=OFF \
                -DCMAKE_OSX_ARCHITECTURES="arm64;x86_64" \
                -DOPENSSL_CRYPTO_LIBRARY="../openssl-universal/$LIBCRYPTO" \
                -DOPENSSL_SSL_LIBRARY="../openssl-universal/$LIBSSL" \
                -DOPENSSL_INCLUDE_DIR="../openssl-x86/include" \
                -DBUILD_TESTING=OFF
    else
        cmake . \
                -DCMAKE_INSTALL_PREFIX=$PREFIX \
                -DBUILD_SHARED_LIBS=ON \
                -DBUILD_EXAMPLES=OFF \
                -DBUILD_TESTING=OFF
    fi
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
    if [ "$KERNEL" = "Darwin" ] && [ "$CIBUILDWHEEL" = "1" ]; then
        CMAKE_PREFIX_PATH=$OPENSSL_PREFIX:$LIBSSH2_PREFIX cmake . \
                -DBUILD_SHARED_LIBS=ON \
                -DBUILD_CLAR=OFF \
                -DCMAKE_OSX_ARCHITECTURES="arm64;x86_64" \
                -DOPENSSL_CRYPTO_LIBRARY="../openssl-universal/$LIBCRYPTO" \
                -DOPENSSL_SSL_LIBRARY="../openssl-universal/$LIBSSL" \
                -DOPENSSL_INCLUDE_DIR="../openssl-x86/include" \
                -DCMAKE_BUILD_TYPE=$BUILD_TYPE
    else
        CMAKE_PREFIX_PATH=$OPENSSL_PREFIX:$LIBSSH2_PREFIX cmake . \
                -DCMAKE_INSTALL_PREFIX=$PREFIX \
                -DBUILD_SHARED_LIBS=ON \
                -DBUILD_CLAR=OFF \
                -DCMAKE_BUILD_TYPE=$BUILD_TYPE
    fi
    cmake --build . --target install
    cd ..
    export LIBGIT2=$PREFIX
fi

if [ "$CIBUILDWHEEL" = "1" ]; then
    # This is gross. auditwheel/delocate-wheel are not so good
    # at finding libraries in random places, so we have to
    # put them in the loader path.
    if [ "$KERNEL" = "Darwin" ]; then
        cp -r $OPENSSL_PREFIX/*.dylib /usr/local/lib
        cp -r $LIBSSH2_PREFIX/lib/*.dylib /usr/local/lib
        cp -r $FILENAME/*.dylib /usr/local/lib
    else
        cp -r $PREFIX/lib64/*.so* /usr/local/lib
    fi
    # we're done building dependencies, cibuildwheel action will take over
    exit 0
fi

# Build pygit2
$PREFIX/bin/pip install -U pip wheel
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
        $PREFIX/bin/pip install $WHEELDIR/pygit2*-$PYTHON_TAG-*.whl
    fi
    $PREFIX/bin/pip install -r requirements-test.txt
    $PREFIX/bin/pytest --cov=pygit2
fi
