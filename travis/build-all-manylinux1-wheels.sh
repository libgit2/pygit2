#! /usr/bin/env bash
if [ -n "$DEBUG" ]
then
  set -x
fi

package_name="$1"
LIBGIT2_VERSION="$2"

set -euo pipefail

if [ -z "$package_name" ]
then
    >&2 echo "Please pass package name as a first argument of this script ($0)"
    exit 1
fi

if [ -z "$LIBGIT2_VERSION" ]
then
    >&2 echo "Please pass libgit2 version as a second argument of this script ($0)"
    exit 1
fi

manylinux1_image_prefix="quay.io/pypa/manylinux1_"
manylinux1_image_prefix="pyca/cryptography-manylinux1:"
dock_ext_args=""
declare -A docker_pull_pids=()  # This syntax requires at least bash v4

for arch in x86_64
do
    docker pull "${manylinux1_image_prefix}${arch}" &
    docker_pull_pids[$arch]=$!
done

for arch in x86_64
do
    echo
    echo
    arch_pull_pid=${docker_pull_pids[$arch]}
    echo Waiting for docker pull PID $arch_pull_pid to complete downloading container for $arch arch...
    wait $arch_pull_pid  # await for docker image for current arch to be pulled from hub
    [ $arch == "i686" ] && dock_ext_args="linux32"

    echo Building wheel for $arch arch
    docker run --rm -v `pwd`:/io "${manylinux1_image_prefix}${arch}" $dock_ext_args /io/travis/build-manylinux1-wheels.sh "$package_name" "$LIBGIT2_VERSION" &

    dock_ext_args=""  # Reset docker args, just in case
done
wait

set +u
