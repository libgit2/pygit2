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

"""Tests for Repository objects."""

__author__ = 'dborowitz@google.com (Dave Borowitz)'

import binascii
import unittest

import pygit2
import utils

A_HEX_SHA = 'af431f20fc541ed6d5afede3e2dc7160f6f01f16'
A_BIN_SHA = binascii.unhexlify(A_HEX_SHA)


class RepositoryTest(utils.BareRepoTestCase):

    def test_read(self):
        self.assertRaises(TypeError, self.repo.read, 123)
        self.assertRaises(ValueError, self.repo.read, A_BIN_SHA)
        self.assertRaisesWithArg(KeyError, '1' * 40, self.repo.read, '1' * 40)

        a = self.repo.read(A_HEX_SHA)
        self.assertEqual((pygit2.GIT_OBJ_BLOB, 'a contents\n'), a)

        a2 = self.repo.read('7f129fd57e31e935c6d60a0c794efe4e6927664b')
        self.assertEqual((pygit2.GIT_OBJ_BLOB, 'a contents 2\n'), a2)

    def test_contains(self):
        self.assertRaises(TypeError, lambda: 123 in self.repo)
        self.assertRaises(ValueError, lambda: A_BIN_SHA in self.repo)
        self.assertTrue(A_HEX_SHA in self.repo)
        self.assertFalse('a' * 40 in self.repo)

    def test_lookup_blob(self):
        self.assertRaises(TypeError, lambda: self.repo[123])
        self.assertRaises(ValueError, lambda: self.repo[A_BIN_SHA])
        a = self.repo[A_HEX_SHA]
        self.assertEqual('a contents\n', a.read_raw())
        self.assertEqual(A_HEX_SHA, a.sha)
        self.assertEqual(pygit2.GIT_OBJ_BLOB, a.type)

    def test_lookup_commit(self):
        commit_sha = '5fe808e8953c12735680c257f56600cb0de44b10'
        commit = self.repo[commit_sha]
        self.assertEqual(commit_sha, commit.sha)
        self.assertEqual(pygit2.GIT_OBJ_COMMIT, commit.type)
        self.assertEqual(('Second test data commit.\n\n'
                          'This commit has some additional text.\n'),
                         commit.message)


if __name__ == '__main__':
  unittest.main()
