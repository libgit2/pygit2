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

"""Tests for Repository objects."""

from __future__ import absolute_import
from __future__ import unicode_literals
import binascii
import unittest
import os
from os.path import join, realpath

from pygit2 import GIT_OBJ_ANY, GIT_OBJ_BLOB, GIT_OBJ_COMMIT, init_repository
from . import utils


__author__ = 'dborowitz@google.com (Dave Borowitz)'

A_HEX_SHA = 'af431f20fc541ed6d5afede3e2dc7160f6f01f16'
A_BIN_SHA = binascii.unhexlify(A_HEX_SHA.encode('ascii'))


class RepositoryTest(utils.BareRepoTestCase):

    def test_read(self):
        self.assertRaises(TypeError, self.repo.read, 123)
        self.assertRaisesWithArg(KeyError, '1' * 40, self.repo.read, '1' * 40)

        ab = self.repo.read(A_BIN_SHA)
        a = self.repo.read(A_HEX_SHA)
        self.assertEqual(ab, a)
        self.assertEqual((GIT_OBJ_BLOB, 'a contents\n'), a)

        a2 = self.repo.read('7f129fd57e31e935c6d60a0c794efe4e6927664b')
        self.assertEqual((GIT_OBJ_BLOB, 'a contents 2\n'), a2)
        
        a_hex_prefix = A_HEX_SHA[:4]
        a3 = self.repo.read(a_hex_prefix)
        self.assertEqual((GIT_OBJ_BLOB, 'a contents\n'), a3)

    def test_write(self):
        data = b"hello world"
        # invalid object type
        self.assertRaises(ValueError, self.repo.write, GIT_OBJ_ANY, data)

        oid = self.repo.write(GIT_OBJ_BLOB, data)
        self.assertEqual(type(oid), bytes)
        self.assertEqual(len(oid), 20)

    def test_contains(self):
        self.assertRaises(TypeError, lambda: 123 in self.repo)
        self.assertTrue(A_BIN_SHA in self.repo)
        self.assertTrue(A_HEX_SHA in self.repo)
        self.assertFalse('a' * 40 in self.repo)

    def test_lookup_blob(self):
        self.assertRaises(TypeError, lambda: self.repo[123])
        self.assertEqual(self.repo[A_BIN_SHA].hex, A_HEX_SHA)
        a = self.repo[A_HEX_SHA]
        self.assertEqual(b'a contents\n', a.read_raw())
        self.assertEqual(A_HEX_SHA, a.hex)
        self.assertEqual(GIT_OBJ_BLOB, a.type)

    def test_lookup_blob_prefix(self):
        a = self.repo[A_HEX_SHA[:5]]
        self.assertEqual(b'a contents\n', a.read_raw())
        self.assertEqual(A_HEX_SHA, a.hex)
        self.assertEqual(GIT_OBJ_BLOB, a.type)

    def test_lookup_commit(self):
        commit_sha = '5fe808e8953c12735680c257f56600cb0de44b10'
        commit = self.repo[commit_sha]
        self.assertEqual(commit_sha, commit.hex)
        self.assertEqual(GIT_OBJ_COMMIT, commit.type)
        self.assertEqual(('Second test data commit.\n\n'
                          'This commit has some additional text.\n'),
                         commit.message)

    def test_lookup_commit_prefix(self):
        commit_sha = '5fe808e8953c12735680c257f56600cb0de44b10'
        commit_sha_prefix = commit_sha[:7]
        too_short_prefix = commit_sha[:3]
        commit = self.repo[commit_sha_prefix]
        self.assertEqual(commit_sha, commit.hex)
        self.assertEqual(GIT_OBJ_COMMIT, commit.type)
        self.assertEqual(('Second test data commit.\n\n'
                    'This commit has some additional text.\n'),
                   commit.message)
        self.assertRaises(ValueError, self.repo.__getitem__, too_short_prefix)

    def test_get_path(self):
        directory = realpath(self.repo.path)
        expected = realpath(join(self._temp_dir, 'testrepo.git'))
        self.assertEqual(directory, expected)

    def test_get_workdir(self):
        self.assertEqual(self.repo.workdir, None)



class RepositoryTest_II(utils.RepoTestCase):

    def test_get_path(self):
        directory = realpath(self.repo.path)
        expected = realpath(join(self._temp_dir, 'testrepo', '.git'))
        self.assertEqual(directory, expected)

    def test_get_workdir(self):
        directory = realpath(self.repo.workdir)
        expected = realpath(join(self._temp_dir, 'testrepo'))
        self.assertEqual(directory, expected)


class NewRepositoryTest(utils.NoRepoTestCase):
    def test_new_repo(self):
        repo = init_repository(self._temp_dir, False)

        oid = repo.write(GIT_OBJ_BLOB, "Test")
        self.assertEqual(type(oid), bytes)
        self.assertEqual(len(oid), 20)

        assert os.path.exists(os.path.join(self._temp_dir, '.git'))

if __name__ == '__main__':
    unittest.main()
