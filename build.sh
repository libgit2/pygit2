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
#   AUDITWHEEL_PLAT           - Linux platform for auditwheel repair
#   LIBSSH2_OPENSSL           - Where to find openssl
#   LIBSSH2_VERSION=<Version> - Build the given version of libssh2
#   LIBGIT2_VERSION=<Version> - Build the given version of libgit2
#   OPENSSL_VERSION=<Version> - Build the given version of OpenSSL
#                               (only needed for Mac universal on CI)
#
# Examples.
#
# Build inplace, libgit2 must be available in the path:
#
#   sh build.sh
#
# Build libgit2 1.9.2 (will use libssh2 if available), then build pygit2
# inplace:
#
#   LIBGIT2_VERSION=1.9.2 sh build.sh
#
# Build libssh2 1.11.1 and libgit2 1.9.2, then build pygit2 inplace:
#
#   LIBSSH2_VERSION=1.11.1 LIBGIT2_VERSION=1.9.2 sh build.sh
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
    if [ -f /usr/bin/apt-get ]; then
        apt-get update
        apt-get install wget -y
        if [ -z "$OPENSSL_VERSION" ]; then
            apt-get install libssl-dev -y
        else
            apt-get install libtime-piece-perl -y
        fi
    elif [ -f /usr/bin/yum ]; then
        yum install wget zlib-devel -y
        if [ -z "$OPENSSL_VERSION" ]; then
            yum install openssl-devel -y
        else
            yum install perl-IPC-Cmd -y
            yum install perl-Pod-Html -y
            yum install perl-Time-Piece -y
        fi
    elif [ -f /sbin/apk ]; then
        apk add wget
        if [ -z "$OPENSSL_VERSION" ]; then
            apk add --no-cache openssl-dev
        else
            apk add --no-cache perl
        fi
    fi
    rm -rf ci
    mkdir ci || true
    cd ci
else
    # Create a virtual environment
    $PYTHON -m venv $PREFIX
    cd ci
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
    FILENAME=openssl-$OPENSSL_VERSION
    wget https://www.openssl.org/source/$FILENAME.tar.gz -N --no-check-certificate

    if [ "$KERNEL" = "Darwin" ]; then
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
    else
        # Linux
        tar xf $FILENAME.tar.gz
        cd $FILENAME
        ./Configure shared no-apps no-docs no-tests --prefix=$PREFIX --libdir=$PREFIX/lib
        make
        make install
        OPENSSL_PREFIX=$(pwd)
        cd ..
    fi
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
    USE_SSH=ON
else
    USE_SSH=OFF
fi

# Install libgit2
if [ -n "$LIBGIT2_VERSION" ]; then
    FILENAME=libgit2-$LIBGIT2_VERSION
    wget https://github.com/libgit2/libgit2/archive/refs/tags/v$LIBGIT2_VERSION.tar.gz -N -O $FILENAME.tar.gz
    tar xf $FILENAME.tar.gz
    cd $FILENAME
    mkdir -p build
    cd build
    if [ "$KERNEL" = "Darwin" ] && [ "$CIBUILDWHEEL" = "1" ]; then
        CMAKE_PREFIX_PATH=$OPENSSL_PREFIX:$PREFIX cmake .. \
                -DBUILD_SHARED_LIBS=ON \
                -DBUILD_TESTS=OFF \
                -DCMAKE_BUILD_TYPE=$BUILD_TYPE \
                -DCMAKE_OSX_ARCHITECTURES="arm64;x86_64" \
                -DOPENSSL_CRYPTO_LIBRARY="../openssl-universal/$LIBCRYPTO" \
                -DOPENSSL_SSL_LIBRARY="../openssl-universal/$LIBSSL" \
                -DOPENSSL_INCLUDE_DIR="../openssl-x86/include" \
                -DCMAKE_INSTALL_PREFIX=$PREFIX \
                -DUSE_SSH=$USE_SSH
    else
        export CFLAGS=-I$PREFIX/include
        CMAKE_PREFIX_PATH=$OPENSSL_PREFIX:$PREFIX cmake .. \
                -DBUILD_SHARED_LIBS=ON \
                -DBUILD_TESTS=OFF \
                -DCMAKE_BUILD_TYPE=$BUILD_TYPE \
                -DCMAKE_INSTALL_PREFIX=$PREFIX \
                -DUSE_SSH=$USE_SSH
    fi
    cmake --build . --target install
    cd ..
    cd ..
    export LIBGIT2=$PREFIX
fi

if [ "$CIBUILDWHEEL" = "1" ]; then
    if [ "$KERNEL" = "Darwin" ]; then
        cp $OPENSSL_PREFIX/*.dylib $PREFIX/lib/
        cp $OPENSSL_PREFIX/*.dylib $PREFIX/lib/
        echo "PREFIX        " $PREFIX
        echo "OPENSSL_PREFIX" $OPENSSL_PREFIX
        ls -l /Users/runner/work/pygit2/pygit2/ci/
        ls -l $PREFIX/lib
    fi
    # we're done building dependencies, cibuildwheel action will take over
    exit 0
fi

# Build pygit2
cd ..
$PREFIX/bin/pip install -U pip wheel
if [ "$1" = "wheel" ]; then
    shift
    $PREFIX/bin/pip install wheel
    $PREFIX/bin/python setup.py bdist_wheel
    WHEELDIR=dist
else
    # Install Python requirements & build inplace
    $PREFIX/bin/pip install -r requirements.txt
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
    shift
    if [ -n "$WHEELDIR" ]; then
        $PREFIX/bin/pip install $WHEELDIR/pygit2*-$PYTHON_TAG-*.whl
    fi
    $PREFIX/bin/pip install -r requirements-test.txt
    $PREFIX/bin/pytest --cov=pygit2
fi

# Type checking
if [ "$1" = "mypy" ]; then
    shift
    if [ -n "$WHEELDIR" ]; then
        $PREFIX/bin/pip install $WHEELDIR/pygit2*-$PYTHON_TAG-*.whl
    fi
    $PREFIX/bin/pip install -r requirements-test.txt -r requirements-typing.txt
    $PREFIX/bin/mypy pygit2 test
fi

# Test .pyi stub file
if [ "$1" = "stubtest" ]; then
    shift
    $PREFIX/bin/pip install mypy
    PYTHONPATH=. $PREFIX/bin/stubtest --mypy-config-file mypy-stubtest.ini pygit2._pygit2
    [ $? == 0 ] && echo "stubtest OK"
fi
