#!/usr/bin/env bash

set -xe

ARCH=`uname -m`
PYTHONS="cp36-cp36m cp37-cp37m cp38-cp38 cp39-cp39 cp310-cp310"
export PYCA_OPENSSL_PATH=/opt/pyca/cryptography/openssl
export OPENSSL_PATH=/opt/openssl
export CFLAGS="-fPIC"
export PKG_CONFIG_PATH="${OPENSSL_PATH}/lib/pkgconfig:${PYCA_OPENSSL_PATH}/lib/pkgconfig"

# Install requirements
yum -y install git libffi-devel
yum -y install openssl wget
if [ ${ARCH} == 'aarch64' ]; then
  yum -y install cmake
else
  yum -y install cmake3
fi

# Copy source directory so we don't mangle with it
SRC_DIR=/io/src
TMP_DIR=/io/tmp
rm $TMP_DIR -rf
cp -a $SRC_DIR $TMP_DIR

# Build
pushd $TMP_DIR
export OPENSSL_PREFIX=/opt/pyca/cryptography/openssl
export ZLIB_VERSION=1.2.11
export LIBSSH2_VERSION=1.10.0
export LIBGIT2_VERSION=1.3.0
export BUILD_TYPE=Release
for PY in $PYTHONS; do
    PYTHON=/opt/python/${PY}/bin/python sh build.sh wheel bundle test
done
popd

# Copy wheels to source dist folder
ls -l $TMP_DIR/wheelhouse
mkdir -p $SRC_DIR/dist
cp $TMP_DIR/wheelhouse/pygit2-*_$ARCH.whl $SRC_DIR/dist
chown -R --reference="${SRC_DIR}/setup.py" ${SRC_DIR}/dist
