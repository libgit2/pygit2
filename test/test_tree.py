# -*- coding: utf-8 -*-
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

"""Tests for Commit objects."""

from __future__ import absolute_import
from __future__ import unicode_literals
import operator
import unittest

from . import utils


TREE_SHA = '967fce8df97cc71722d3c2a5930ef3e6f1d27b12'
SUBTREE_SHA = '614fd9a3094bf618ea938fffc00e7d1a54f89ad0'


class TreeTest(utils.BareRepoTestCase):

    def assertTreeEntryEqual(self, entry, sha, name, filemode):
        self.assertEqual(entry.hex, sha)
        self.assertEqual(entry.name, name)
        self.assertEqual(entry.filemode, filemode,
                         '0%o != 0%o' % (entry.filemode, filemode))

    def test_read_tree(self):
        tree = self.repo[TREE_SHA]
        self.assertRaises(TypeError, lambda: tree[()])
        self.assertRaisesWithArg(KeyError, 'abcd', lambda: tree['abcd'])
        self.assertRaisesWithArg(IndexError, -4, lambda: tree[-4])
        self.assertRaisesWithArg(IndexError, 3, lambda: tree[3])

        self.assertEqual(3, len(tree))
        sha = '7f129fd57e31e935c6d60a0c794efe4e6927664b'
        self.assertTrue('a' in tree)
        self.assertTreeEntryEqual(tree[0], sha, 'a', 0o0100644)
        self.assertTreeEntryEqual(tree[-3], sha, 'a', 0o0100644)
        self.assertTreeEntryEqual(tree['a'], sha, 'a', 0o0100644)

        sha = '85f120ee4dac60d0719fd51731e4199aa5a37df6'
        self.assertTrue('b' in tree)
        self.assertTreeEntryEqual(tree[1], sha, 'b', 0o0100644)
        self.assertTreeEntryEqual(tree[-2], sha, 'b', 0o0100644)
        self.assertTreeEntryEqual(tree['b'], sha, 'b', 0o0100644)

        sha = '297efb891a47de80be0cfe9c639e4b8c9b450989'
        self.assertTreeEntryEqual(tree['c/d'], sha, 'd', 0o0100644)
        self.assertRaisesWithArg(KeyError, 'ab/cd', lambda: tree['ab/cd'])

    def test_read_subtree(self):
        tree = self.repo[TREE_SHA]
        subtree_entry = tree['c']
        self.assertTreeEntryEqual(subtree_entry, SUBTREE_SHA, 'c', 0o0040000)

        subtree = subtree_entry.to_object()
        self.assertEqual(1, len(subtree))
        sha = '297efb891a47de80be0cfe9c639e4b8c9b450989'
        self.assertTreeEntryEqual(subtree[0], sha, 'd', 0o0100644)

    def test_new_tree(self):
        b0 = self.repo.create_blob('1')
        b1 = self.repo.create_blob('2')
        t = self.repo.TreeBuilder()
        t.insert('x', b0, 0o0100644)
        t.insert('y', b1, 0o0100755)
        tree = self.repo[t.write()]

        self.assertTrue('x' in tree)
        self.assertTrue('y' in tree)

        x = tree['x']
        y = tree['y']
        self.assertEqual(x.filemode, 0o0100644)
        self.assertEqual(y.filemode, 0o0100755)

        self.assertEqual(x.to_object().oid, b0)
        self.assertEqual(y.to_object().oid, b1)



    def test_modify_tree(self):
        tree = self.repo[TREE_SHA]
        self.assertRaises(TypeError, operator.setitem, 'c', tree['a'])
        self.assertRaises(TypeError, operator.delitem, 'c')

    def test_iterate_tree(self):
        """
            Testing that we're able to iterate of a Tree object and that the
            resulting sha strings are consitent with the sha strings we could
            get with other Tree access methods.
        """
        tree = self.repo[TREE_SHA]
        for tree_entry in tree:
            self.assertEqual(tree_entry.hex, tree[tree_entry.name].hex)


if __name__ == '__main__':
    unittest.main()
