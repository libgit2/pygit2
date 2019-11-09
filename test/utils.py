# Copyright 2010-2019 The pygit2 contributors
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

import gc
import hashlib
import os
import shutil
import socket
import stat
import tarfile
import tempfile
import unittest

import pytest

import pygit2


_no_network = None
def no_network():
    global _no_network
    if _no_network is None:
        try:
            socket.gethostbyname('github.com')
        except socket.gaierror:
            _no_network = True
        else:
            _no_network = False

    return _no_network


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


class TemporaryRepository(object):
    def __init__(self, repo_spec):
        self.repo_spec = repo_spec

    def __enter__(self):
        container, name = self.repo_spec
        repo_path = os.path.join(os.path.dirname(__file__), 'data', name)
        self.temp_dir = tempfile.mkdtemp()
        temp_repo_path = os.path.join(self.temp_dir, name)
        if container == 'tar':
            tar = tarfile.open('.'.join((repo_path, 'tar')))
            tar.extractall(self.temp_dir)
            tar.close()
        else:
            shutil.copytree(repo_path, temp_repo_path)
        return temp_repo_path

    def __exit__(self, exc_type, exc_value, traceback):
        rmtree(self.temp_dir)


class NoRepoTestCase(unittest.TestCase):

    def setUp(self):
        self._temp_dir = tempfile.mkdtemp()
        self.repo = None

    def tearDown(self):
        del self.repo
        gc.collect()
        rmtree(self._temp_dir)

    def assertRaisesWithArg(self, exc_class, arg, func, *args, **kwargs):
        with pytest.raises(exc_class) as excinfo:
            func(*args, **kwargs)
        assert excinfo.value.args == (arg,)
        
        # Explicitly clear the Exception Info. Citing https://docs.pytest.org/en/latest/reference.html#pytest-raises:
        #
        # Clearing those references breaks a reference cycle 
        # (ExceptionInfo –> caught exception –> frame stack raising the exception 
        # –> current frame stack –> local variables –> ExceptionInfo) which makes 
        # Python keep all objects referenced from that cycle (including all local 
        # variables in the current frame) alive until the next cyclic garbage collection 
        # run. See the official Python try statement documentation for more detailed 
        # information.
        del excinfo


class AutoRepoTestCase(NoRepoTestCase):
    def setUp(self):
        super().setUp()
        self.repo_ctxtmgr = TemporaryRepository(self.repo_spec)
        self.repo_path = self.repo_ctxtmgr.__enter__()
        self.repo = pygit2.Repository(self.repo_path)

    def tearDown(self):
        super().tearDown()
        self.repo_ctxtmgr.__exit__(None, None, None)


class BareRepoTestCase(AutoRepoTestCase):

    repo_spec = 'git', 'testrepo.git'


class RepoTestCase(AutoRepoTestCase):

    repo_spec = 'tar', 'testrepo'


class RepoTestCaseForMerging(AutoRepoTestCase):

    repo_spec = 'tar', 'testrepoformerging'


class Utf8BranchRepoTestCase(AutoRepoTestCase):

    repo_spec = 'tar', 'utf8branchrepo'


class DirtyRepoTestCase(AutoRepoTestCase):

    repo_spec = 'tar', 'dirtyrepo'


class EmptyRepoTestCase(AutoRepoTestCase):

    repo_spec = 'tar', 'emptyrepo'


class SubmoduleRepoTestCase(AutoRepoTestCase):

    repo_spec = 'tar', 'submodulerepo'


class BinaryFileRepoTestCase(AutoRepoTestCase):

    repo_spec = 'tar', 'binaryfilerepo'


class GpgSignedRepoTestCase(AutoRepoTestCase):

    repo_spec = 'tar', 'gpgsigned'
