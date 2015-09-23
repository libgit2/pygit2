# -*- coding: UTF-8 -*-
#
# Copyright 2010-2014 The pygit2 contributors
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

import sys
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
        rmtree(self._temp_dir)

    def assertRaisesAssign(self, exc_class, instance, name, value):
        try:
            setattr(instance, name, value)
        except:
            self.assertEqual(exc_class, sys.exc_info()[0])

    def assertAll(self, func, entries):
        return self.assertTrue(all(func(x) for x in entries))

    def assertAny(self, func, entries):
        return self.assertTrue(any(func(x) for x in entries))

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


class AutoRepoTestCase(NoRepoTestCase):
    def setUp(self):
        super(AutoRepoTestCase, self).setUp()
        self.repo_ctxtmgr = TemporaryRepository(self.repo_spec)
        self.repo_path = self.repo_ctxtmgr.__enter__()
        self.repo = pygit2.Repository(self.repo_path)

    def tearDown(self):
        self.repo_ctxtmgr.__exit__(None, None, None)
        super(AutoRepoTestCase, self).tearDown()


class BareRepoTestCase(AutoRepoTestCase):

    repo_spec = 'git', 'testrepo.git'


class RepoTestCase(AutoRepoTestCase):

    repo_spec = 'tar', 'testrepo'


class RepoTestCaseForMerging(AutoRepoTestCase):

    repo_spec = 'tar', 'testrepoformerging'


class DirtyRepoTestCase(AutoRepoTestCase):

    repo_spec = 'tar', 'dirtyrepo'


class EmptyRepoTestCase(AutoRepoTestCase):

    repo_spec = 'tar', 'emptyrepo'


class SubmoduleRepoTestCase(AutoRepoTestCase):

    repo_spec = 'tar', 'submodulerepo'


class BinaryFileRepoTestCase(AutoRepoTestCase):

    repo_spec = 'tar', 'binaryfilerepo'
