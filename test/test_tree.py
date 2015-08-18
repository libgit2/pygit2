# -*- coding: utf-8 -*-
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

"""Tests for Commit objects."""

from __future__ import absolute_import
from __future__ import unicode_literals
import operator
import unittest

from pygit2 import TreeEntry
from pygit2 import GIT_FILEMODE_BLOB
from pygit2 import GIT_OBJ_COMMIT, Signature, Oid
from pygit2.repository import Repository

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

    def test_equality(self):
        tree_a = self.repo['18e2d2e9db075f9eb43bcb2daa65a2867d29a15e']
        tree_b = self.repo['2ad1d3456c5c4a1c9e40aeeddb9cd20b409623c8']

        self.assertNotEqual(tree_a['a'], tree_b['a'])
        self.assertNotEqual(tree_a['a'], tree_b['b'])
        self.assertEqual(tree_a['b'], tree_b['b'])

    def test_sorting(self):
        tree_a = self.repo['18e2d2e9db075f9eb43bcb2daa65a2867d29a15e']
        self.assertEqual(list(tree_a), sorted(reversed(list(tree_a))))
        self.assertNotEqual(list(tree_a), reversed(list(tree_a)))

    def test_read_subtree(self):
        tree = self.repo[TREE_SHA]
        subtree_entry = tree['c']
        self.assertTreeEntryEqual(subtree_entry, SUBTREE_SHA, 'c', 0o0040000)

        subtree = self.repo[subtree_entry.id]
        self.assertEqual(1, len(subtree))
        sha = '297efb891a47de80be0cfe9c639e4b8c9b450989'
        self.assertTreeEntryEqual(subtree[0], sha, 'd', 0o0100644)


    def test_new_tree(self):
        repo = self.repo
        b0 = repo.create_blob('1')
        b1 = repo.create_blob('2')
        t = repo.TreeBuilder()
        t.insert('x', b0, 0o0100644)
        t.insert('y', b1, 0o0100755)
        tree = repo[t.write()]

        self.assertTrue('x' in tree)
        self.assertTrue('y' in tree)

        x = tree['x']
        y = tree['y']
        self.assertEqual(x.filemode, 0o0100644)
        self.assertEqual(y.filemode, 0o0100755)

        self.assertEqual(repo[x.id].id, b0)
        self.assertEqual(repo[y.id].id, b1)


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
            self.assertEqual(tree_entry, tree[tree_entry.name])

    def test_deep_contains(self):
        tree = self.repo[TREE_SHA]
        self.assertTrue('a' in tree)
        self.assertTrue('c' in tree)
        self.assertTrue('c/d' in tree)
        self.assertFalse('c/e' in tree)
        self.assertFalse('d' in tree)


class MariadbTreeTest(utils.MariadbRepositoryTestCase):
    def test_simple_tree_write(self):
        repo = Repository(None, 0,
                self.TEST_DB_USER, self.TEST_DB_PASSWD,
                self.TEST_DB_SOCKET, self.TEST_DB_DB,
                self.TEST_DB_TABLE_PREFIX,
                self.TEST_DB_REPO_ID,
                odb_partitions=2, refdb_partitions=2)
        try:
            blob_oid = repo.create_blob(b"abcdef\ntoto\n")

            committer = Signature('Cecil Committer', 'cecil@committers.tld')
            author = Signature('Alice Author 2', 'alice@authors.tld')
            tree = repo.TreeBuilder()
            tree.insert('toto.txt', blob_oid, GIT_FILEMODE_BLOB)
            tree = tree.write()
            oid = repo.create_commit(
                    'refs/heads/master',  # create the branch
                    author, committer, 'one line commit message\n\ndetails',
                    tree,  # binary string representing the tree object ID
                    []  # parents of the new commit
                )
            self.assertNotEqual(oid, None)
        finally:
            repo.close()

        repo = Repository(None, 0,
                self.TEST_DB_USER, self.TEST_DB_PASSWD,
                self.TEST_DB_SOCKET, self.TEST_DB_DB,
                self.TEST_DB_TABLE_PREFIX,
                self.TEST_DB_REPO_ID,
                odb_partitions=2, refdb_partitions=2)
        try:
            commit = repo[oid]
            self.assertNotEqual(commit, None)
            tree = commit.tree
            self.assertNotEqual(tree, None)
            tree_entry = tree['toto.txt']
            self.assertNotEqual(tree_entry, None)
            blob = repo.get(tree_entry.id)
            self.assertNotEqual(blob, None)
            self.assertEqual(blob.data, b"abcdef\ntoto\n")
        finally:
            repo.close()

if __name__ == '__main__':
    unittest.main()
