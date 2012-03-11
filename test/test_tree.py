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
import operator
import unittest

import pygit2
from . import utils


__author__ = 'dborowitz@google.com (Dave Borowitz)'

TREE_SHA = '967fce8df97cc71722d3c2a5930ef3e6f1d27b12'
SUBTREE_SHA = '614fd9a3094bf618ea938fffc00e7d1a54f89ad0'


class TreeTest(utils.BareRepoTestCase):

    def assertTreeEntryEqual(self, entry, sha, name, attributes):
        self.assertEqual(entry.hex, sha)
        self.assertEqual(entry.name, name)
        self.assertEqual(entry.attributes, attributes,
                         '0%o != 0%o' % (entry.attributes, attributes))

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

    def test_read_subtree(self):
        tree = self.repo[TREE_SHA]
        subtree_entry = tree['c']
        self.assertTreeEntryEqual(subtree_entry, SUBTREE_SHA, 'c', 0o0040000)

        subtree = subtree_entry.to_object()
        self.assertEqual(1, len(subtree))
        sha = '297efb891a47de80be0cfe9c639e4b8c9b450989'
        self.assertTreeEntryEqual(subtree[0], sha, 'd', 0o0100644)

    # XXX Creating new trees was removed from libgit2 by v0.11.0, we
    # deactivate this test temporarily, since the feature may come back in
    # a near feature (if it does not this test will be removed).
    def xtest_new_tree(self):
        tree = pygit2.Tree(self.repo)
        self.assertEqual(0, len(tree))
        tree.add_entry('1' * 40, 'x', 0o0100644)
        tree.add_entry('2' * 40, 'y', 0o0100755)
        self.assertEqual(2, len(tree))
        self.assertTrue('x' in tree)
        self.assertTrue('y' in tree)
        self.assertRaisesWithArg(KeyError, '1' * 40, tree['x'].to_object)

        tree.add_entry('3' * 40, 'z1', 0o0100644)
        tree.add_entry('4' * 40, 'z2', 0o0100644)
        self.assertEqual(4, len(tree))
        del tree['z1']
        del tree[2]
        self.assertEqual(2, len(tree))

        self.assertEqual(None, tree.hex)
        tree.write()
        contents = '100644 x\0%s100755 y\0%s' % ('\x11' * 20, '\x22' * 20)
        self.assertEqual((pygit2.GIT_OBJ_TREE, contents),
                         self.repo.read(tree.hex))

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
