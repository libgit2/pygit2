# -*- coding: UTF-8 -*-
#
# Copyright 2010-2013 The pygit2 contributors
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

"""Tests for Remote objects."""


import unittest
import pygit2
from . import utils

REMOTE_NAME = 'origin'
REMOTE_URL = 'git://github.com/libgit2/pygit2.git'
REMOTE_FETCHSPEC_SRC = 'refs/heads/*'
REMOTE_FETCHSPEC_DST = 'refs/remotes/origin/*'
REMOTE_REPO_OBJECTS = 30
REMOTE_REPO_BYTES = 2758

class RepositoryTest(utils.RepoTestCase):
    def test_remote_create(self):
        name = 'upstream'
        url = 'git://github.com/libgit2/pygit2.git'

        remote = self.repo.create_remote(name, url);

        self.assertEqual(type(remote), pygit2.Remote)
        self.assertEqual(name, remote.name)
        self.assertEqual(url, remote.url)

        self.assertRaises(ValueError, self.repo.create_remote, *(name, url))


    def test_remote_rename(self):
        remote = self.repo.remotes[0]

        self.assertEqual(REMOTE_NAME, remote.name)
        remote.name = 'new'
        self.assertEqual('new', remote.name)

        self.assertRaisesAssign(ValueError, remote, 'name', '')


    def test_remote_set_url(self):
        remote = self.repo.remotes[0]

        self.assertEqual(REMOTE_URL, remote.url)
        new_url = 'git://github.com/cholin/pygit2.git'
        remote.url = new_url
        self.assertEqual(new_url, remote.url)

        self.assertRaisesAssign(ValueError, remote, 'url', '')


    def test_remote_fetchspec(self):
        remote = self.repo.remotes[0]

        self.assertEqual(REMOTE_FETCHSPEC_SRC, remote.fetchspec[0])
        self.assertEqual(REMOTE_FETCHSPEC_DST, remote.fetchspec[1])

        new_fetchspec = ('refs/foo/*', 'refs/remotes/foo/*')
        remote.fetchspec = new_fetchspec
        self.assertEqual(new_fetchspec[0], remote.fetchspec[0])
        self.assertEqual(new_fetchspec[1], remote.fetchspec[1])


    def test_remote_list(self):
        self.assertEqual(1, len(self.repo.remotes))
        remote = self.repo.remotes[0]
        self.assertEqual(REMOTE_NAME, remote.name)
        self.assertEqual(REMOTE_URL, remote.url)

        name = 'upstream'
        url = 'git://github.com/libgit2/pygit2.git'
        remote = self.repo.create_remote(name, url);
        self.assertTrue(remote.name in [x.name for x in self.repo.remotes])


class EmptyRepositoryTest(utils.EmptyRepoTestCase):
    def test_fetch(self):
        remote = self.repo.remotes[0]
        stats = remote.fetch()
        self.assertEqual(stats['received_bytes'], REMOTE_REPO_BYTES)
        self.assertEqual(stats['indexed_objects'], REMOTE_REPO_OBJECTS)
        self.assertEqual(stats['received_objects'], REMOTE_REPO_OBJECTS)


if __name__ == '__main__':
    unittest.main()
