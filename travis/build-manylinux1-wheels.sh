#!/usr/bin/env bash
if [ -n "$DEBUG" ]
then
  set -x
fi

DIST_NAME="$1"
LIBGIT2_VERSION="$2"

set -euo pipefail

if [ -z "$DIST_NAME" ]
then
    >&2 echo "Please pass package name as a first argument of this script ($0)"
    exit 1
fi

if [ -z "$LIBGIT2_VERSION" ]
then
    >&2 echo "Please pass libgit2 version as a second argument of this script ($0)"
    exit 1
fi

PYTHONS=`ls /opt/python/`

# Avoid creation of __pycache__/*.py[c|o]
export PYTHONDONTWRITEBYTECODE=1

SRC_DIR=/io
GIT_GLOBAL_ARGS="--git-dir=${SRC_DIR}/.git --work-tree=${SRC_DIR}"
TESTS_DIR="${SRC_DIR}/test"
BUILD_DIR=`mktemp -d "/tmp/${DIST_NAME}-manylinux1-build.XXXXXXXXXX"`
LIBGIT2_CLONE_DIR="${BUILD_DIR}/libgit2"
LIBGIT2_BUILD_DIR="${LIBGIT2_CLONE_DIR}/build"
export LIBGIT2="${LIBGIT2_CLONE_DIR}/_install"

LIBSSH2_VERSION=1.8.0
LIBSSH2_CLONE_DIR="${BUILD_DIR}/libssh2"
LIBSSH2_BUILD_DIR="${LIBSSH2_CLONE_DIR}/build"

ORIG_WHEEL_DIR="${BUILD_DIR}/original-wheelhouse"
WHEEL_DEP_DIR="${BUILD_DIR}/deps-wheelhouse"
WHEELHOUSE_DIR="${SRC_DIR}/dist"

# clear python cache
>&2 echo Cleaninig up python bytecode cache files...
find "${SRC_DIR}" \
    -type f \
    -name *.pyc -o -name *.pyo \
    -print0 | xargs -0 rm -fv
find "${SRC_DIR}" \
    -type d \
    -name __pycache__ \
    -print0 | xargs -0 rm -rfv

# clear python cache
>&2 echo Cleaninig up files untracked by Git...
git ${GIT_GLOBAL_ARGS} clean -fxd --exclude dist/

mkdir -p "$WHEELHOUSE_DIR"

export PYCA_OPENSSL_PATH=/opt/pyca/cryptography/openssl
export OPENSSL_PATH=/opt/openssl

export CFLAGS="-I${PYCA_OPENSSL_PATH}/include -I${OPENSSL_PATH}/include -I/usr/include"
export LDFLAGS="-L${PYCA_OPENSSL_PATH}/lib -L${OPENSSL_PATH}/lib -L/usr/local/lib -L/usr/lib64"
export LD_LIBRARY_PATH="${LIBGIT2}/lib:$LD_LIBRARY_PATH"
export PKG_CONFIG_PATH="/usr/local/lib64/pkgconfig:${PYCA_OPENSSL_PATH}/lib/pkgconfig:${OPENSSL_PATH}/lib/pkgconfig:$PKG_CONFIG_PATH"

ARCH=`uname -m`


>&2 echo Installing system deps...
# Install a system package required by our library
# libgit2 needs cmake 2.8, which can be found in EPEL
yum -y install \
    git libffi-devel \
    openssl-devel pkgconfig \
    cmake28

>&2 echo downloading source of libssh2 v${LIBSSH2_VERSION}:
git clone \
    --depth=1 \
    -b "libssh2-${LIBSSH2_VERSION}" \
    https://github.com/libssh2/libssh2 \
    "${LIBSSH2_CLONE_DIR}"

mkdir -p "${LIBSSH2_BUILD_DIR}"
pushd "${LIBSSH2_BUILD_DIR}"
cmake28 "${LIBSSH2_CLONE_DIR}" \
    -DBUILD_SHARED_LIBS=ON \
    -DBUILD_EXAMPLES=OFF \
    -DBUILD_TESTING=OFF \
    -DCRYPTO_BACKEND=OpenSSL \
    -DENABLE_ZLIB_COMPRESSION=ON
cmake28 --build "${LIBSSH2_BUILD_DIR}" --target install
popd

>&2 echo downloading source of libgit2 v${LIBGIT2_VERSION}:
git clone \
    --depth=1 \
    -b "maint/v${LIBGIT2_VERSION}" \
    https://github.com/libgit2/libgit2.git \
    "${LIBGIT2_CLONE_DIR}"

>&2 echo Building libgit2...
mkdir -p "${LIBGIT2_BUILD_DIR}"
pushd "${LIBGIT2_BUILD_DIR}"
# Ref https://libgit2.org/docs/guides/build-and-link/
cmake28 "${LIBGIT2_CLONE_DIR}" \
    -DCMAKE_INSTALL_PREFIX="${LIBGIT2}" \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_CLAR=OFF \
    -DTHREADSAFE=ON
cmake28 --build "${LIBGIT2_BUILD_DIR}" --target install
popd

>&2 echo Building wheels:
for PIP_BIN in /opt/python/*/bin/pip; do
    >&2 echo Using "${PIP_BIN}"...
    ${PIP_BIN} wheel "${SRC_DIR}" -w "${ORIG_WHEEL_DIR}"
done

>&2 echo Reparing wheels:
# Bundle external shared libraries into the wheels
for PY in $PYTHONS; do
    for whl in ${ORIG_WHEEL_DIR}/${DIST_NAME}-*-${PY}-linux_${ARCH}.whl; do
        >&2 echo Reparing "${whl}"...
        auditwheel repair "${whl}" -w ${WHEELHOUSE_DIR}
    done
done

# Download deps
>&2 echo Downloading dependencies:
for PY in $PYTHONS; do
    PIP_BIN="/opt/python/${PY}/bin/pip"
    WHEEL_FILE=`ls ${WHEELHOUSE_DIR}/${DIST_NAME}-*-${PY}-manylinux1_${ARCH}.whl`
    >&2 echo Downloading ${WHEEL_FILE} deps using ${PIP_BIN}...
    ${PIP_BIN} download -d "${WHEEL_DEP_DIR}" "${WHEEL_FILE}"
done

# Install packages
>&2 echo Testing wheels installation:
for PIP_BIN in /opt/python/*/bin/pip; do
    >&2 echo Using ${PIP_BIN}...
    ${PIP_BIN} install "${DIST_NAME}" --no-index -f ${WHEEL_DEP_DIR} &
done
wait

# clear python cache
>&2 echo Cleaninig up non-artifact files untracked by Git...
git ${GIT_GLOBAL_ARGS} clean -fxd --exclude dist/

>&2 echo Running test suite against wheels:
for PY_BIN in /opt/python/*/bin/python; do
    $PY_BIN -m pip install pytest
    $PY_BIN -m pytest "${TESTS_DIR}" &
done
wait

>&2 echo
>&2 echo ==================
>&2 echo SELF-TEST COMPLETE
>&2 echo ==================
>&2 echo

# Running analysis
>&2 echo
>&2 echo ==============
>&2 echo WHEEL ANALYSIS
>&2 echo ==============
>&2 echo
for PY in $PYTHONS; do
    WHEEL_BIN="/opt/python/${PY}/bin/wheel"
    WHEEL_FILE=`ls ${WHEELHOUSE_DIR}/${DIST_NAME}-*-${PY}-manylinux1_${ARCH}.whl`
    >&2 echo Analysing ${WHEEL_FILE}...
    auditwheel show "${WHEEL_FILE}"
    ${WHEEL_BIN} unpack -d "${BUILD_DIR}/${PY}-${DIST_NAME}" "${WHEEL_FILE}"
    ! ldd ${BUILD_DIR}/${PY}-${DIST_NAME}/${DIST_NAME}-*/${DIST_NAME}/.libs/lib* | grep '=> not found'
done

chown -R --reference="${SRC_DIR}/.travis.yml" "${SRC_DIR}"
>&2 echo Final OS-specific wheels for ${DIST_NAME}:
ls -l ${WHEELHOUSE_DIR}
