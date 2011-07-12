#!/usr/bin/env python
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

__author__ = 'jdavid@itaapy.com (J. David Ibáñez)'

import unittest

import utils


class IndexBareTest(utils.BareRepoTestCase):

    def test_bare(self):
        self.assertEqual(None, self.repo.index)


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
        self.assertEqual(index['hello.txt'].sha, sha)
        self.assertEqual(index[1].sha, sha)

    def test_add(self):
        index = self.repo.index

        sha = '0907563af06c7464d62a70cdd135a6ba7d2b41d8'
        self.assertFalse('bye.txt' in index)
        index.add('bye.txt')
        self.assertTrue('bye.txt' in index)
        self.assertEqual(len(index), 3)
        self.assertEqual(index['bye.txt'].sha, sha)

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

    def test_create_tree(self):
        sha = self.repo.index.create_tree()
        self.assertEqual(sha, 'fd937514cb799514d4b81bb24c5fcfeb6472b245')

    def test_iter(self):
        index = self.repo.index
        n = len(index)
        self.assertEqual(len(list(index)), n)
        # FIXME This fails
        #entries = [index[x] for x in xrange(n)]
        #self.assertEqual(list(index), entries)

    def test_attributes(self):
        """
            Testing that we can access an index entry attributes.
        """
        index = self.repo.index

        hello_attributes = index['hello.txt'].attributes
        self.assertEqual(hello_attributes, 33188)


if __name__ == '__main__':
    unittest.main()
