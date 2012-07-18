# -*- coding: UTF-8 -*-
#
# Copyright 2010-2012 The pygit2 contributors
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

"""Test utilities for libgit2."""

from binascii import b2a_hex
import os
import shutil
import stat
import tarfile
import tempfile
import unittest
import hashlib

import pygit2


def force_rm_handle(remove_path, path, excinfo):
    os.chmod(
        path,
        os.stat(path).st_mode | stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH
    )
    remove_path(path)

def oid_to_hex(oid):
    return b2a_hex(oid).decode('ascii')

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
        shutil.rmtree(path, onerror=lambda func, path, e: force_rm_handle(func, path, e))


class NoRepoTestCase(unittest.TestCase):

    def setUp(self):
        self._temp_dir = tempfile.mkdtemp()
        self.repo = None

    def tearDown(self):
        del self.repo
        rmtree(self._temp_dir)

    def assertRaisesWithArg(self, exc_class, arg, func, *args, **kwargs):
        try:
            func(*args, **kwargs)
        except exc_class as exc_value:
            self.assertEqual((arg,), exc_value.args)
        else:
            self.fail('%s(%r) not raised' % (exc_class.__name__, arg))

    def assertEqualSignature(self, a, b):
        # XXX Remove this once equality test is supported by Signature
        self.assertEqual(a.name, b.name)
        self.assertEqual(a.email, b.email)
        self.assertEqual(a.time, b.time)
        self.assertEqual(a.offset, b.offset)


class BareRepoTestCase(NoRepoTestCase):

    repo_dir = 'testrepo.git'

    def setUp(self):
        super(BareRepoTestCase, self).setUp()

        repo_dir = self.repo_dir
        repo_path = os.path.join(os.path.dirname(__file__), 'data', repo_dir)
        temp_repo_path = os.path.join(self._temp_dir, repo_dir)

        shutil.copytree(repo_path, temp_repo_path)

        self.repo = pygit2.Repository(temp_repo_path)


class RepoTestCase(NoRepoTestCase):

    repo_dir = 'testrepo'

    def setUp(self):
        super(RepoTestCase, self).setUp()

        repo_dir = self.repo_dir
        repo_path = os.path.join(os.path.dirname(__file__), 'data', repo_dir)
        temp_repo_path = os.path.join(self._temp_dir, repo_dir, '.git')

        tar = tarfile.open(repo_path + '.tar')
        tar.extractall(self._temp_dir)
        tar.close()

        self.repo = pygit2.Repository(temp_repo_path)


class DirtyRepoTestCase(RepoTestCase):

    repo_dir = 'dirtyrepo'
