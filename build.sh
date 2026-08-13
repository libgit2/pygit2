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
#                               (used on Linux and macOS CI builds)
#
# Examples.
#
# Build inplace, libgit2 must be available in the path:
#
#   sh build.sh
#
# Build libgit2 1.9.6 (will use libssh2 if available), then build pygit2
# inplace:
#
#   LIBGIT2_VERSION=1.9.6 sh build.sh
#
# Build libssh2 1.11.1 and libgit2 1.9.6, then build pygit2 inplace:
#
#   LIBSSH2_VERSION=1.11.1 LIBGIT2_VERSION=1.9.6 sh build.sh
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

    # Use cached dependencies if they match the requested versions.
    if [ -f ci/versions.txt ] && \
       grep -q "^LIBGIT2_VERSION=$LIBGIT2_VERSION$" ci/versions.txt && \
       grep -q "^LIBSSH2_VERSION=$LIBSSH2_VERSION$" ci/versions.txt && \
       grep -q "^OPENSSL_VERSION=$OPENSSL_VERSION$" ci/versions.txt; then
        echo "Using cached dependencies"
        exit 0
    fi

    # The ci directory may be a bind-mount (e.g. inside cibuildwheel), so
    # remove its contents but keep the directory itself.
    rm -rf ci/* ci/.[!.]* ci/..?* 2>/dev/null || true
    mkdir -p ci
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
        # Build OpenSSL for the host architecture only.
        tar xf $FILENAME.tar.gz
        cd $FILENAME
        if [ "$ARCH" = "arm64" ]; then
            ./Configure enable-rc5 zlib darwin64-arm64-cc no-asm shared --prefix=$PREFIX --libdir=$PREFIX/lib
        else
            ./Configure darwin64-x86_64-cc shared --prefix=$PREFIX --libdir=$PREFIX/lib
        fi
        make
        make install
        OPENSSL_PREFIX=$PREFIX
        # Set install names so delocate can bundle the libraries.
        cd $PREFIX/lib
        LIBSSL=$(find . -maxdepth 1 -name 'libssl.*.dylib' -type f | head -n1 | sed 's|^\./||')
        LIBCRYPTO=$(find . -maxdepth 1 -name 'libcrypto.*.dylib' -type f | head -n1 | sed 's|^\./||')
        install_name_tool -id "@rpath/$LIBSSL" "$LIBSSL"
        install_name_tool -id "@rpath/$LIBCRYPTO" "$LIBCRYPTO"
        cd ../..
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
        CMAKE_PREFIX_PATH=$PREFIX cmake . \
                -DCMAKE_INSTALL_PREFIX=$PREFIX \
                -DBUILD_SHARED_LIBS=ON \
                -DBUILD_EXAMPLES=OFF \
                -DCMAKE_OSX_ARCHITECTURES="$ARCH" \
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
        CMAKE_PREFIX_PATH=$PREFIX cmake .. \
                -DBUILD_SHARED_LIBS=ON \
                -DBUILD_TESTS=OFF \
                -DCMAKE_BUILD_TYPE=$BUILD_TYPE \
                -DCMAKE_OSX_ARCHITECTURES="$ARCH" \
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
    # Record versions so the cache can be reused.
    cat > $PREFIX/versions.txt <<EOF
LIBGIT2_VERSION=$LIBGIT2_VERSION
LIBSSH2_VERSION=$LIBSSH2_VERSION
OPENSSL_VERSION=$OPENSSL_VERSION
EOF
    if [ "$KERNEL" = "Darwin" ]; then
        echo "PREFIX        " $PREFIX
        echo "OPENSSL_PREFIX" $OPENSSL_PREFIX
        ls -l $PREFIX
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
