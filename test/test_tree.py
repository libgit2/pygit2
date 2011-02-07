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

TREE_SHA = '967fce8df97cc71722d3c2a5930ef3e6f1d27b12'
SUBTREE_SHA = '614fd9a3094bf618ea938fffc00e7d1a54f89ad0'


class TreeTest(utils.BareRepoTestCase):

    def assertTreeEntryEqual(self, entry, sha, name, attributes):
        self.assertEqual(entry.sha, sha)
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
        a_sha = '7f129fd57e31e935c6d60a0c794efe4e6927664b'
        self.assertTrue('a' in tree)
        self.assertTreeEntryEqual(tree[0], a_sha, 'a', 0100644)
        self.assertTreeEntryEqual(tree[-3], a_sha, 'a', 0100644)
        self.assertTreeEntryEqual(tree['a'], a_sha, 'a', 0100644)

        b_sha = '85f120ee4dac60d0719fd51731e4199aa5a37df6'
        self.assertTrue('b' in tree)
        self.assertTreeEntryEqual(tree[1], b_sha, 'b', 0100644)
        self.assertTreeEntryEqual(tree[-2], b_sha, 'b', 0100644)
        self.assertTreeEntryEqual(tree['b'], b_sha, 'b', 0100644)

    def test_read_subtree(self):
        tree = self.repo[TREE_SHA]
        subtree_entry = tree['c']
        self.assertTreeEntryEqual(subtree_entry, SUBTREE_SHA, 'c', 0040000)

        subtree = subtree_entry.to_object()
        self.assertEqual(1, len(subtree))
        self.assertTreeEntryEqual(
          subtree[0], '297efb891a47de80be0cfe9c639e4b8c9b450989', 'd', 0100644)

    def test_new_tree(self):
        tree = pygit2.Tree(self.repo)
        self.assertEqual(0, len(tree))
        tree.add_entry('1' * 40, 'x', 0100644)
        tree.add_entry('2' * 40, 'y', 0100755)
        self.assertEqual(2, len(tree))
        self.assertTrue('x' in tree)
        self.assertTrue('y' in tree)
        self.assertRaisesWithArg(KeyError, '1' * 40, tree['x'].to_object)

        tree.add_entry('3' * 40, 'z1', 0100644)
        tree.add_entry('4' * 40, 'z2', 0100644)
        self.assertEqual(4, len(tree))
        del tree['z1']
        del tree[2]
        self.assertEqual(2, len(tree))

        self.assertEqual(None, tree.sha)
        tree.write()
        contents = '100644 x\0%s100755 y\0%s' % ('\x11' * 20, '\x22' * 20)
        self.assertEqual((pygit2.GIT_OBJ_TREE, contents),
                         self.repo.read(tree.sha))

    def test_modify_tree(self):
        tree = self.repo[TREE_SHA]

        def fail_set():
            tree['c'] = tree['a']
        self.assertRaises(ValueError, fail_set)

        def fail_del_by_name():
            del tree['asdf']
        self.assertRaisesWithArg(KeyError, 'asdf', fail_del_by_name)

        def fail_del_by_index():
            del tree[99]
        self.assertRaisesWithArg(IndexError, 99, fail_del_by_index)

        self.assertTrue('c' in tree)
        self.assertEqual(3, len(tree))
        del tree['c']
        self.assertEqual(2, len(tree))
        self.assertFalse('c' in tree)

        tree.add_entry('1' * 40, 'c', 0100644)
        self.assertTrue('c' in tree)
        self.assertEqual(3, len(tree))

        old_sha = tree.sha
        tree.write()
        self.assertNotEqual(tree.sha, old_sha)
        self.assertEqual(tree.sha, self.repo[tree.sha].sha)


if __name__ == '__main__':
  unittest.main()
