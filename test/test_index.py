# -*- coding: UTF-8 -*-
#
# Copyright 2011 Itaapy
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

"""Tests for Index files."""

from __future__ import absolute_import
from __future__ import unicode_literals
from binascii import b2a_hex
import os
import unittest

import pygit2
from . import utils


__author__ = 'jdavid@itaapy.com (J. David Ibáñez)'


class IndexBareTest(utils.BareRepoTestCase):

    def test_bare(self):
        index = self.repo.index
        self.assertEqual(len(index), 0)


class IndexTest(utils.RepoTestCase):

    def test_index(self):
        self.assertNotEqual(None, self.repo.index)

    def test_read(self):
        index = self.repo.index
        self.assertEqual(len(index), 2)

        self.assertRaises(TypeError, lambda: index[()])
        self.assertRaisesWithArg(ValueError, -4, lambda: index[-4])
        self.assertRaisesWithArg(KeyError, 'abc', lambda: index['abc'])

        sha = 'a520c24d85fbfc815d385957eed41406ca5a860b'
        self.assertTrue('hello.txt' in index)
        self.assertEqual(index['hello.txt'].hex, sha)
        self.assertEqual(index['hello.txt'].path, 'hello.txt')
        self.assertEqual(index[1].hex, sha)

    def test_add(self):
        index = self.repo.index

        sha = '0907563af06c7464d62a70cdd135a6ba7d2b41d8'
        self.assertFalse('bye.txt' in index)
        index.add('bye.txt')
        self.assertTrue('bye.txt' in index)
        self.assertEqual(len(index), 3)
        self.assertEqual(index['bye.txt'].hex, sha)

    def test_clear(self):
        index = self.repo.index
        self.assertEqual(len(index), 2)
        index.clear()
        self.assertEqual(len(index), 0)

    def test_write(self):
        index = self.repo.index
        index.add('bye.txt', 0)
        index.write()

        index.clear()
        self.assertFalse('bye.txt' in index)
        index.read()
        self.assertTrue('bye.txt' in index)


    def test_read_tree(self):
        tree_oid = '68aba62e560c0ebc3396e8ae9335232cd93a3f60'
        # Test reading first tree
        index = self.repo.index
        self.assertEqual(len(index), 2)
        index.read_tree(tree_oid)
        self.assertEqual(len(index), 1)
        # Test read-write returns the same oid
        oid = index.write_tree()
        oid = b2a_hex(oid).decode('ascii')
        self.assertEqual(oid, tree_oid)
        # Test the index is only modified in memory
        index.read()
        self.assertEqual(len(index), 2)


    def test_write_tree(self):
        oid = self.repo.index.write_tree()
        sha = b2a_hex(oid).decode('ascii')
        self.assertEqual(sha, 'fd937514cb799514d4b81bb24c5fcfeb6472b245')

    def test_iter(self):
        index = self.repo.index
        n = len(index)
        self.assertEqual(len(list(index)), n)

        # Compare SHAs, not IndexEntry object identity
        entries = [index[x].hex for x in range(n)]
        self.assertEqual(list(x.hex for x in index), entries)

    def test_mode(self):
        """
            Testing that we can access an index entry mode.
        """
        index = self.repo.index

        hello_mode = index['hello.txt'].mode
        self.assertEqual(hello_mode, 33188)

    def test_bare_index(self):
        index = pygit2.Index(os.path.join(self.repo.path, 'index'))
        self.assertEqual([x.hex for x in index],
                [x.hex for x in self.repo.index])

        self.assertRaises(pygit2.GitError, lambda: index.add('bye.txt', 0))

if __name__ == '__main__':
    unittest.main()
