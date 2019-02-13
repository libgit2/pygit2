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

SRC_DIR=/io
BUILD_DIR=`mktemp -d "/tmp/${DIST_NAME}-manylinux1-build.XXXXXXXXXX"`
LIBGIT2_CLONE_DIR="${BUILD_DIR}/libgit2"
LIBGIT2_BUILD_DIR="${LIBGIT2_CLONE_DIR}/build"
export LIBGIT2="${LIBGIT2_CLONE_DIR}/_install"

ORIG_WHEEL_DIR="${BUILD_DIR}/original-wheelhouse"
WHEEL_DEP_DIR="${BUILD_DIR}/deps-wheelhouse"
WHEELHOUSE_DIR="${SRC_DIR}/dist"

mkdir -p "$WHEELHOUSE_DIR"

export PYCA_OPENSSL_PATH=/opt/pyca/cryptography/openssl
export OPENSSL_PATH=/opt/openssl

export CFLAGS="-I${PYCA_OPENSSL_PATH}/include -I${OPENSSL_PATH}/include"
export LDFLAGS="-L${PYCA_OPENSSL_PATH}/lib -L${OPENSSL_PATH}/lib -L/usr/local/lib/"
export LD_LIBRARY_PATH="${LIBGIT2}/lib:$LD_LIBRARY_PATH"

ARCH=`uname -m`


>&2 echo Installing system deps...
# Install a system package required by our library
# libgit2 needs cmake 2.8, which can be found in EPEL
yum -y install \
    git libssh2-devel libffi-devel \
    openssl-devel pkgconfig \
    cmake28

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

chown -R --reference=/io/.travis.yml ${WHEELHOUSE_DIR}
>&2 echo Final OS-specific wheels for ${DIST_NAME}:
ls -l ${WHEELHOUSE_DIR}
