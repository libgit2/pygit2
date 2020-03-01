#! /usr/bin/env bash
if [ -n "$DEBUG" ]
then
  set -x
fi

LIBGIT2_VERSION="$1"

set -euo pipefail

if [ -z "$LIBGIT2_VERSION" ]
then
    >&2 echo "Please pass libgit2 version as first argument of this script ($0)"
    exit 1
fi

manylinux_image="quay.io/pypa/manylinux2010_x86_64"
manylinux_image="pyca/cryptography-manylinux2010:x86_64"

echo Waiting for docker pull to complete downloading container...
docker pull "${manylinux_image}" &
wait

echo Building wheel
docker run --rm -v `pwd`:/io "${manylinux_image}" /io/travis/build-manylinux-wheels.sh pygit2 "$LIBGIT2_VERSION" &
wait

set +u
