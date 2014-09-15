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

"""Tests for Blame objects."""

from __future__ import absolute_import
from __future__ import unicode_literals
import unittest
import pygit2
from pygit2 import Index, Oid, Tree, Object
import tarfile
import os
from . import utils
from time import time

TREE_HASH = 'fd937514cb799514d4b81bb24c5fcfeb6472b245'
COMMIT_HASH = '2be5719152d4f82c7302b1c0932d8e5f0a4a0e98'

class ArchiveTest(utils.RepoTestCase):

    def check_writing(self, treeish, timestamp=None):
        archive = tarfile.open('foo.tar', mode='w')
        self.repo.write_archive(treeish, archive)

        index = Index()
        if isinstance(treeish, Object):
            index.read_tree(treeish.peel(Tree))
        else:
            index.read_tree(self.repo[treeish].peel(Tree))

        self.assertEqual(len(index), len(archive.getmembers()))

        if timestamp:
            fileinfo = archive.getmembers()[0]
            self.assertEqual(timestamp, fileinfo.mtime)

        archive.close()
        self.assertTrue(os.path.isfile('foo.tar'))
        os.remove('foo.tar')

    def test_write_tree(self):
        self.check_writing(TREE_HASH)
        self.check_writing(Oid(hex=TREE_HASH))
        self.check_writing(self.repo[TREE_HASH])

    def test_write_commit(self):
        commit_timestamp = self.repo[COMMIT_HASH].committer.time
        self.check_writing(COMMIT_HASH, commit_timestamp)
        self.check_writing(Oid(hex=COMMIT_HASH), commit_timestamp)
        self.check_writing(self.repo[COMMIT_HASH], commit_timestamp)
