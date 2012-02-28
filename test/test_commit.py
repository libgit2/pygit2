# -*- coding: UTF-8 -*-
#
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

"""Tests for Commit objects."""

from __future__ import absolute_import
from __future__ import unicode_literals
import unittest

from pygit2 import GIT_OBJ_COMMIT, Signature
from . import utils


__author__ = 'dborowitz@google.com (Dave Borowitz)'

COMMIT_SHA = '5fe808e8953c12735680c257f56600cb0de44b10'


class CommitTest(utils.BareRepoTestCase):

    def test_read_commit(self):
        commit = self.repo[COMMIT_SHA]
        self.assertEqual(COMMIT_SHA, commit.hex)
        parents = commit.parents
        self.assertEqual(1, len(parents))
        self.assertEqual('c2792cfa289ae6321ecf2cd5806c2194b0fd070c',
                         parents[0].hex)
        self.assertEqual(None, commit.message_encoding)
        self.assertEqual(('Second test data commit.\n\n'
                          'This commit has some additional text.\n'),
                         commit.message)
        commit_time = 1288481576
        self.assertEqual(commit_time, commit.commit_time)
        self.assertEqualSignature(
            commit.committer,
            Signature('Dave Borowitz', 'dborowitz@google.com',
                      commit_time, -420))
        self.assertEqualSignature(
            commit.author,
            Signature('Dave Borowitz', 'dborowitz@google.com', 1288477363,
                      -420))
        self.assertEqual(
            '967fce8df97cc71722d3c2a5930ef3e6f1d27b12', commit.tree.hex)

    def test_new_commit(self):
        repo = self.repo
        message = 'New commit.\n\nMessage with non-ascii chars: ééé.\n'
        committer = Signature('John Doe', 'jdoe@example.com', 12346, 0)
        author = Signature('J. David Ibáñez', 'jdavid@example.com', 12345, 0)
        tree = '967fce8df97cc71722d3c2a5930ef3e6f1d27b12'
        tree_prefix = tree[:5]
        too_short_prefix = tree[:3]

        parents = [COMMIT_SHA[:5]]
        self.assertRaises(ValueError, repo.create_commit, None, author,
                          committer, message, too_short_prefix, parents)

        sha = repo.create_commit(None, author, committer, message,
                                 tree_prefix, parents)
        commit = repo[sha]

        self.assertEqual(GIT_OBJ_COMMIT, commit.type)
        self.assertEqual('98286caaab3f1fde5bf52c8369b2b0423bad743b',
                         commit.hex)
        self.assertEqual(None, commit.message_encoding)
        self.assertEqual(message, commit.message)
        self.assertEqual(12346, commit.commit_time)
        self.assertEqualSignature(committer, commit.committer)
        self.assertEqualSignature(author, commit.author)
        self.assertEqual(tree, commit.tree.hex)
        self.assertEqual(1, len(commit.parents))
        self.assertEqual(COMMIT_SHA, commit.parents[0].hex)

    def test_new_commit_encoding(self):
        repo = self.repo
        encoding = 'iso-8859-1'
        message = 'New commit.\n\nMessage with non-ascii chars: ééé.\n'
        committer = Signature('John Doe', 'jdoe@example.com', 12346, 0,
                              encoding)
        author = Signature('J. David Ibáñez', 'jdavid@example.com', 12345, 0,
                           encoding)
        tree = '967fce8df97cc71722d3c2a5930ef3e6f1d27b12'
        tree_prefix = tree[:5]

        parents = [COMMIT_SHA[:5]]
        sha = repo.create_commit(None, author, committer, message,
                                 tree_prefix, parents, encoding)
        commit = repo[sha]

        self.assertEqual(GIT_OBJ_COMMIT, commit.type)
        self.assertEqual('iso-8859-1', commit.message_encoding)
        self.assertEqual(message, commit.message)
        self.assertEqual(12346, commit.commit_time)
        self.assertEqualSignature(committer, commit.committer)
        self.assertEqualSignature(author, commit.author)
        self.assertEqual(tree, commit.tree.hex)
        self.assertEqual(1, len(commit.parents))
        self.assertEqual(COMMIT_SHA, commit.parents[0].hex)

    def test_modify_commit(self):
        message = 'New commit.\n\nMessage.\n'
        committer = ('John Doe', 'jdoe@example.com', 12346)
        author = ('Jane Doe', 'jdoe2@example.com', 12345)

        commit = self.repo[COMMIT_SHA]
        self.assertRaises(AttributeError, setattr, commit, 'message', message)
        self.assertRaises(AttributeError, setattr, commit, 'committer',
                          committer)
        self.assertRaises(AttributeError, setattr, commit, 'author', author)
        self.assertRaises(AttributeError, setattr, commit, 'tree', None)
        self.assertRaises(AttributeError, setattr, commit, 'parents', None)


if __name__ == '__main__':
    unittest.main()
