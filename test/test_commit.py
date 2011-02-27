#!/usr/bin/env python
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

__author__ = 'dborowitz@google.com (Dave Borowitz)'

import unittest

import pygit2
import utils

COMMIT_SHA = '5fe808e8953c12735680c257f56600cb0de44b10'


class CommitTest(utils.BareRepoTestCase):

    def test_read_commit(self):
        commit = self.repo[COMMIT_SHA]
        self.assertEqual(COMMIT_SHA, commit.sha)
        parents = commit.parents
        self.assertEqual(1, len(parents))
        self.assertEqual('c2792cfa289ae6321ecf2cd5806c2194b0fd070c',
                         parents[0].sha)
        self.assertEqual('Second test data commit.', commit.message_short)
        self.assertEqual(('Second test data commit.\n\n'
                          'This commit has some additional text.\n'),
                         commit.message)
        commit_time = 1288481576
        self.assertEqual(commit_time, commit.commit_time)
        self.assertEqual(('Dave Borowitz', 'dborowitz@google.com', commit_time),
                         commit.committer)
        self.assertEqual(('Dave Borowitz', 'dborowitz@google.com', 1288477363),
                         commit.author)

    def test_new_commit(self):
        message = 'New commit.\n\nMessage.\n'
        committer = ('John Doe', 'jdoe@example.com', 12346)
        author = ('Jane Doe', 'jdoe2@example.com', 12345)

        commit = pygit2.Commit(self.repo)
        commit.message = message
        commit.committer = committer
        commit.author = author

        self.assertEqual(None, commit.sha)
        self.assertEqual(pygit2.GIT_OBJ_COMMIT, commit.type)
        self.assertEqual(message, commit.message)
        self.assertEqual('New commit.', commit.message_short)
        self.assertEqual(12346, commit.commit_time)
        self.assertEqual(committer, commit.committer)
        self.assertEqual(author, commit.author)

    def test_modify_commit(self):
        message = 'New commit.\n\nMessage.\n'
        committer = ('John Doe', 'jdoe@example.com', 12346)
        author = ('Jane Doe', 'jdoe2@example.com', 12345)

        commit = self.repo[COMMIT_SHA]
        commit.message = message
        commit.committer = committer
        commit.author = author

        self.assertEqual(message, commit.message)
        self.assertEqual('New commit.', commit.message_short)
        self.assertEqual(12346, commit.commit_time)
        self.assertEqual(committer, commit.committer)
        self.assertEqual(author, commit.author)


if __name__ == '__main__':
  unittest.main()
