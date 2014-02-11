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

"""Tests for Object objects."""

from __future__ import absolute_import
from __future__ import unicode_literals
from os.path import dirname, join
import unittest

import pygit2
from pygit2 import GIT_OBJ_TREE, GIT_OBJ_TAG, Tree, Tag
from . import utils


BLOB_SHA = 'a520c24d85fbfc815d385957eed41406ca5a860b'
BLOB_CONTENT = """hello world
hola mundo
bonjour le monde
""".encode()
BLOB_NEW_CONTENT = b'foo bar\n'
BLOB_FILE_CONTENT = b'bye world\n'

class ObjectTest(utils.RepoTestCase):

    def test_peel_commit(self):
        # start by looking up the commit
        commit_id = self.repo.lookup_reference('refs/heads/master').target
        commit = self.repo[commit_id]
        # and peel to the tree
        tree = commit.peel(GIT_OBJ_TREE)

        self.assertEqual(type(tree), Tree)
        self.assertEqual(str(tree.id), 'fd937514cb799514d4b81bb24c5fcfeb6472b245')

    def test_peel_commit_type(self):
        commit_id = self.repo.lookup_reference('refs/heads/master').target
        commit = self.repo[commit_id]
        tree = commit.peel(Tree)

        self.assertEqual(type(tree), Tree)
        self.assertEqual(str(tree.id), 'fd937514cb799514d4b81bb24c5fcfeb6472b245')


    def test_invalid(self):
        commit_id = self.repo.lookup_reference('refs/heads/master').target
        commit = self.repo[commit_id]

        self.assertRaises(ValueError, commit.peel, GIT_OBJ_TAG)

    def test_invalid_type(self):
        commit_id = self.repo.lookup_reference('refs/heads/master').target
        commit = self.repo[commit_id]

        self.assertRaises(ValueError, commit.peel, Tag)

if __name__ == '__main__':
    unittest.main()
