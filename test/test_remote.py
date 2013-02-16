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

"""Tests for Remote objects."""


import pygit2
from . import utils

REMOTE_NAME = 'origin'
REMOTE_URL = 'git://github.com/libgit2/pygit2.git'

class RepositoryTest(utils.RepoTestCase):
    def test_remote_create(self):
        name = 'upstream'
        url = 'git://github.com/libgit2/pygit2.git'

        remote = self.repo.remote_create(name, url);

        self.assertEqual(type(remote), pygit2.Remote)
        self.assertEqual(name, remote.name)
        self.assertEqual(url, remote.url)

        self.assertRaises(ValueError,self.repo.remote_create, *(name, url))


    def test_remote_rename(self):
        remote = self.repo.remotes[0]

        self.assertEqual(REMOTE_NAME, remote.name)
        remote.name = 'new'
        self.assertEqual('new', remote.name)

        self.assertRaisesAssign(ValueError, remote, 'name', '')


    def test_remote_list(self):
        self.assertEqual(1, len(self.repo.remotes))
        remote = self.repo.remotes[0]
        self.assertEqual(REMOTE_NAME, remote.name)
        self.assertEqual(REMOTE_URL, remote.url)

        name = 'upstream'
        url = 'git://github.com/libgit2/pygit2.git'
        remote = self.repo.remote_create(name, url);
        self.assertTrue(remote.name in [x.name for x in self.repo.remotes])
