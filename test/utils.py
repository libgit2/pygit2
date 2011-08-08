# Copyright 2010 Google, Inc.
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

__author__ = 'dborowitz@google.com (Dave Borowitz)'

import os
import shutil
import tarfile
import tempfile
import unittest

import pygit2


class BaseTestCase(unittest.TestCase):

    def tearDown(self):
        shutil.rmtree(self._temp_dir)

    def assertRaisesWithArg(self, exc_class, arg, func, *args, **kwargs):
        try:
            func(*args, **kwargs)
        except exc_class, e:
            self.assertEqual((arg,), e.args)
        else:
            self.fail('%s(%r) not raised' % (exc_class.__name__, arg))


def open_repo(repo_dir):
    repo_path = os.path.join(os.path.dirname(__file__), 'data', repo_dir)
    temp_dir = tempfile.mkdtemp()
    temp_repo_path = os.path.join(temp_dir, repo_dir)
    shutil.copytree(repo_path, temp_repo_path)
    return temp_dir, pygit2.Repository(temp_repo_path)


class BareRepoTestCase(BaseTestCase):

    def setUp(self):
        self._temp_dir, self.repo = open_repo('testrepo.git')


class RepoTestCase(BaseTestCase):

    repo_dir = 'testrepo'

    def setUp(self):
        repo_dir = self.repo_dir
        repo_path = os.path.join(os.path.dirname(__file__), 'data', repo_dir)
        temp_dir = tempfile.mkdtemp()
        tar = tarfile.open(repo_path + '.tar')
        tar.extractall(temp_dir)
        tar.close()
        self._temp_dir = temp_dir
        temp_repo_path = os.path.join(temp_dir, repo_dir, '.git')
        self.repo = pygit2.Repository(temp_repo_path)

class NoRepoTestCase(BaseTestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self._temp_dir = self.temp_dir

class DirtyRepoTestCase(RepoTestCase):

    repo_dir = 'dirtyrepo'
