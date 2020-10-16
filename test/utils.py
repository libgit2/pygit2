# Copyright 2010-2020 The pygit2 contributors
#
# This file is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License, version 2,
# as published by the Free Software Foundation.
#
# In addition to the permissions in the GNU General Public License,
# the authors give you unlimited permission to link the compiled
# version of this file into combinations with other programs,
# and to distribute those combinations without any restriction
# coming from the use of this file.  (The General Public License
# restrictions do apply in other respects; for example, they cover
# modification of the file, and distribution when not linked into
# a combined executable.)
#
# This file is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING.  If not, write to
# the Free Software Foundation, 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301, USA.

# Standard library
import hashlib
import os
import shutil
import socket
import stat
import sys
import tarfile

import pygit2
import pytest



try:
    socket.gethostbyname('github.com')
except socket.gaierror:
    has_network = False
else:
    has_network = True

requires_network = pytest.mark.skipif(
    not has_network,
    reason='Requires network'
)


requires_ssh = pytest.mark.skipif(
    not (pygit2.features & pygit2.GIT_FEATURE_SSH),
    reason='Requires SSH'
)


is_pypy = '__pypy__' in sys.builtin_module_names

fspath = pytest.mark.skipif(is_pypy, reason=
    "PyPy doesn't fully support fspath, see https://foss.heptapod.net/pypy/pypy/-/issues/3168")

refcount = pytest.mark.skipif(is_pypy, reason='skip refcounts checks in pypy')


def force_rm_handle(remove_path, path, excinfo):
    os.chmod(
        path,
        os.stat(path).st_mode | stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH
    )
    remove_path(path)


def gen_blob_sha1(data):
    # http://stackoverflow.com/questions/552659/assigning-git-sha1s-without-git
    m = hashlib.sha1()
    m.update(('blob %d\0' % len(data)).encode())
    m.update(data)
    return m.hexdigest()


def rmtree(path):
    """In Windows a read-only file cannot be removed, and shutil.rmtree fails.
    So we implement our own version of rmtree to address this issue.
    """
    if os.path.exists(path):
        onerror = lambda func, path, e: force_rm_handle(func, path, e)
        shutil.rmtree(path, onerror=onerror)


class TemporaryRepository:

    def __init__(self, name, tmp_path):
        self.name = name
        self.tmp_path = tmp_path

    def __enter__(self):
        name = self.name
        basename, extension = os.path.splitext(name)
        path = os.path.join(os.path.dirname(__file__), 'data', name)

        temp_repo_path = os.path.join(self.tmp_path, basename)

        if extension == '.tar':
            tar = tarfile.open(path)
            tar.extractall(self.tmp_path)
            tar.close()
        elif extension == '.git':
            shutil.copytree(path, temp_repo_path)
        else:
            raise ValueError(f'Unexpected {extension} extension')

        return temp_repo_path

    def __exit__(self, exc_type, exc_value, traceback):
        pass


def assertRaisesWithArg(exc_class, arg, func, *args, **kwargs):
    with pytest.raises(exc_class) as excinfo:
        func(*args, **kwargs)
    assert excinfo.value.args == (arg,)

    # Explicitly clear the Exception Info. Citing
    # https://docs.pytest.org/en/latest/reference.html#pytest-raises:
    #
    # Clearing those references breaks a reference cycle
    # (ExceptionInfo –> caught exception –> frame stack raising the exception
    # –> current frame stack –> local variables –> ExceptionInfo) which makes
    # Python keep all objects referenced from that cycle (including all local
    # variables in the current frame) alive until the next cyclic garbage
    # collection run. See the official Python try statement documentation for
    # more detailed information.
    del excinfo
