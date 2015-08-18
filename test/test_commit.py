# -*- coding: UTF-8 -*-
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
import unittest
import sys

from pygit2 import GIT_FILEMODE_BLOB
from pygit2 import GIT_OBJ_COMMIT, Signature, Oid
from pygit2.repository import Repository

from . import utils

import mysql.connector

# pypy (in python2 mode) raises TypeError on writing to read-only, so
# we need to check and change the test accordingly
try:
    import __pypy__
    import __pypy__, sys
    pypy2 =  sys.version_info[0] < 3
except ImportError:
    __pypy__ = None
    pypy2 = False

COMMIT_SHA = '5fe808e8953c12735680c257f56600cb0de44b10'


class CommitTest(utils.BareRepoTestCase):

    @unittest.skipIf(__pypy__ is not None, "skip refcounts checks in pypy")
    def test_commit_refcount(self):
        commit = self.repo[COMMIT_SHA]
        start = sys.getrefcount(commit)
        tree = commit.tree
        del tree
        end = sys.getrefcount(commit)
        self.assertEqual(start, end)


    def test_read_commit(self):
        commit = self.repo[COMMIT_SHA]
        self.assertEqual(COMMIT_SHA, str(commit.id))
        parents = commit.parents
        self.assertEqual(1, len(parents))
        self.assertEqual('c2792cfa289ae6321ecf2cd5806c2194b0fd070c',
                         str(parents[0].id))
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
            '967fce8df97cc71722d3c2a5930ef3e6f1d27b12', str(commit.tree.id))

    def test_new_commit(self):
        repo = self.repo
        message = 'New commit.\n\nMessage with non-ascii chars: ééé.\n'
        committer = Signature('John Doe', 'jdoe@example.com', 12346, 0)
        author = Signature(
            'J. David Ibáñez', 'jdavid@example.com', 12345, 0,
            encoding='utf-8')
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
        self.assertEqual(Oid(hex=tree), commit.tree_id)
        self.assertEqual(1, len(commit.parents))
        self.assertEqual(COMMIT_SHA, commit.parents[0].hex)
        self.assertEqual(Oid(hex=COMMIT_SHA), commit.parent_ids[0])

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
        self.assertEqual(message.encode(encoding), commit.raw_message)
        self.assertEqual(12346, commit.commit_time)
        self.assertEqualSignature(committer, commit.committer)
        self.assertEqualSignature(author, commit.author)
        self.assertEqual(tree, commit.tree.hex)
        self.assertEqual(Oid(hex=tree), commit.tree_id)
        self.assertEqual(1, len(commit.parents))
        self.assertEqual(COMMIT_SHA, commit.parents[0].hex)
        self.assertEqual(Oid(hex=COMMIT_SHA), commit.parent_ids[0])

    def test_modify_commit(self):
        message = 'New commit.\n\nMessage.\n'
        committer = ('John Doe', 'jdoe@example.com', 12346)
        author = ('Jane Doe', 'jdoe2@example.com', 12345)

        commit = self.repo[COMMIT_SHA]

        error_type = AttributeError if not pypy2 else TypeError
        self.assertRaises(error_type, setattr, commit, 'message', message)
        self.assertRaises(error_type, setattr, commit, 'committer', committer)
        self.assertRaises(error_type, setattr, commit, 'author', author)
        self.assertRaises(error_type, setattr, commit, 'tree', None)
        self.assertRaises(error_type, setattr, commit, 'parents', None)


class MariadbCommitTest(utils.MariadbRepositoryTestCase):
    def test_new_commit(self):
        repo = Repository(None, 0,
                self.TEST_DB_USER, self.TEST_DB_PASSWD,
                None, self.TEST_DB_DB,
                self.TEST_DB_TABLE_PREFIX,
                self.TEST_DB_REPO_ID,
                odb_partitions=2, refdb_partitions=2)
        try:
            author = Signature('Alice Author', 'alice@authors.tld')
            committer = Signature('Cecil Committer', 'cecil@committers.tld')
            tree = repo.TreeBuilder().write()
            sha = repo.create_commit(
                    'refs/heads/master',  # create the branch
                    author, committer, 'one line commit message\n\ndetails',
                    tree,  # binary string representing the tree object ID
                    []  # parents of the new commit
                )
            self.assertNotEqual(sha, None)
        finally:
            repo.close()

    def test_fetch_commit(self):
        repo = Repository(None, 0,
                self.TEST_DB_USER, self.TEST_DB_PASSWD,
                self.TEST_DB_SOCKET, self.TEST_DB_DB,
                self.TEST_DB_TABLE_PREFIX,
                self.TEST_DB_REPO_ID,
                odb_partitions=2, refdb_partitions=2)
        try:
            author = Signature('Alice Author', 'alice@authors.tld')
            committer = Signature('Cecil Committer', 'cecil@committers.tld')
            tree = repo.TreeBuilder().write()
            sha = repo.create_commit(
                    'refs/heads/master',  # create the branch
                    author, committer, 'one line commit message\n\ndetails',
                    tree,  # binary string representing the tree object ID
                    []  # parents of the new commit
                )
            self.assertNotEqual(sha, None)

            # fetch
            commit = repo[sha]
            self.assertNotEqual(commit, None)
            self.assertEqual(commit.author.name, author.name)
        finally:
            repo.close()

    def test_reopen_fetch_commit(self):
        repo = Repository(None, 0,
                self.TEST_DB_USER, self.TEST_DB_PASSWD,
                self.TEST_DB_SOCKET, self.TEST_DB_DB,
                self.TEST_DB_TABLE_PREFIX,
                self.TEST_DB_REPO_ID,
                odb_partitions=2, refdb_partitions=2)
        try:
            author = Signature('Alice Author', 'alice@authors.tld')
            committer = Signature('Cecil Committer', 'cecil@committers.tld')
            tree = repo.TreeBuilder().write()
            sha = repo.create_commit(
                    'refs/heads/master',  # create the branch
                    author, committer, 'one line commit message\n\ndetails',
                    tree,  # binary string representing the tree object ID
                    []  # parents of the new commit
                )
            self.assertNotEqual(sha, None)
        finally:
            repo.close()

        # reopen
        repo = Repository(None, 0,
                self.TEST_DB_USER, self.TEST_DB_PASSWD,
                self.TEST_DB_SOCKET, self.TEST_DB_DB,
                self.TEST_DB_TABLE_PREFIX,
                self.TEST_DB_REPO_ID,
                odb_partitions=2, refdb_partitions=2)
        try:
            # invalid oid
            self.assertRaises(KeyError, repo.__getitem__,
                Oid(hex='abcdef012345'))
            # invalid short id
            self.assertRaises(KeyError, repo.__getitem__, 'abcdef012345')

            # fetch
            commit = repo[sha]
            self.assertNotEqual(commit, None)
            self.assertEqual(commit.author.name, author.name)
        finally:
            repo.close()

    def test_double_commit(self):
        repo = Repository(None, 0,
                self.TEST_DB_USER, self.TEST_DB_PASSWD,
                self.TEST_DB_SOCKET, self.TEST_DB_DB,
                self.TEST_DB_TABLE_PREFIX,
                self.TEST_DB_REPO_ID,
                odb_partitions=2, refdb_partitions=2)
        try:
            author = Signature('Alice Author', 'alice@authors.tld')
            committer = Signature('Cecil Committer', 'cecil@committers.tld')
            tree = repo.TreeBuilder().write()
            oid_parent = repo.create_commit(
                    'refs/heads/master',  # create the branch
                    author, committer, 'one line commit message\n\ndetails',
                    tree,  # binary string representing the tree object ID
                    []  # parents of the new commit
                )
            self.assertNotEqual(oid_parent, None)

            hex_parent = oid_parent.hex[:12]

            commit_parent = repo[oid_parent]

            oid_child = repo.create_commit(
                    'refs/heads/master',
                    author, committer, 'one line commit message\n\ndetails',
                    tree,  # binary string representing the tree object ID
                    [hex_parent]  # parents of the new commit
                )
            self.assertNotEqual(oid_child, None)
        finally:
            repo.close()

        # reopen
        repo = Repository(None, 0,
                self.TEST_DB_USER, self.TEST_DB_PASSWD,
                self.TEST_DB_SOCKET, self.TEST_DB_DB,
                self.TEST_DB_TABLE_PREFIX,
                self.TEST_DB_REPO_ID,
                odb_partitions=2, refdb_partitions=2)
        try:
            # fetch
            commit_parent = repo[oid_parent]
            self.assertNotEqual(commit_parent, None)
            self.assertEqual(commit_parent.parents, [])
            self.assertEqual(commit_parent.parent_ids, [])

            commit_child = repo[oid_child]
            self.assertNotEqual(commit_child, None)
            self.assertEqual(len(commit_child.parents), 1)
            self.assertEqual(commit_child.parents[0].id, commit_parent.id)
            self.assertEqual(commit_child.parent_ids, [oid_parent])
        finally:
            repo.close()

    def test_conflicting_oid(self):
        repo = Repository(None, 0,
                self.TEST_DB_USER, self.TEST_DB_PASSWD,
                self.TEST_DB_SOCKET, self.TEST_DB_DB,
                self.TEST_DB_TABLE_PREFIX,
                self.TEST_DB_REPO_ID,
                odb_partitions=2, refdb_partitions=2)
        try:
            author = Signature('Alice Author', 'alice@authors.tld')
            committer = Signature('Cecil Committer', 'cecil@committers.tld')
            tree = repo.TreeBuilder().write()
            oid_parent = repo.create_commit(
                    'refs/heads/master',  # create the branch
                    author, committer, 'one line commit message\n\ndetails',
                    tree,  # binary string representing the tree object ID
                    []  # parents of the new commit
                )
            self.assertNotEqual(oid_parent, None)
        finally:
            repo.close()

        short_oid = oid_parent.hex[:12]

        ## create a commit with a fake sha starting like the oid_parent
        ## so we can have a conflict

        cnx = mysql.connector.connect(user=self.TEST_DB_USER,
            password=self.TEST_DB_PASSWD,
            host=self.TEST_DB_HOST, database=self.TEST_DB_DB)
        try:
            cursor = cnx.cursor()
            try:
                query = ("INSERT INTO `%s_odb`"
                            " (`repository_id`, `oid`, `oid_hex`, `type`,"
                            " `size`, `data`)"
                            " VALUES (%d, UNHEX('%sABCDEF'), '%sABCDEF', 1, 0,"
                            "  UNHEX('0000'));"
                            % (self.TEST_DB_TABLE_PREFIX, self.TEST_DB_REPO_ID,
                                short_oid.upper(), short_oid.upper()))
                cursor.execute(query)
            finally:
                cursor.close()
            cnx.commit()
        finally:
            cnx.close()

        # reopen
        repo = Repository(None, 0,
                self.TEST_DB_USER, self.TEST_DB_PASSWD,
                self.TEST_DB_SOCKET, self.TEST_DB_DB,
                self.TEST_DB_TABLE_PREFIX,
                self.TEST_DB_REPO_ID,
                odb_partitions=2, refdb_partitions=2)
        try:
            commit = repo[oid_parent]
            self.assertNotEqual(commit, None)
            self.assertRaises(ValueError, repo.__getitem__, short_oid)
            commit = repo[oid_parent.hex[:16]]
            self.assertNotEqual(commit, None)
        finally:
            repo.close()


class MariadbParrallelCommitTest(utils.MariadbRepositoryTestCase):
    def test_two_repos_two_commits(self):
        repo1 = Repository(None, 0,
                self.TEST_DB_USER, self.TEST_DB_PASSWD,
                self.TEST_DB_SOCKET, self.TEST_DB_DB,
                self.TEST_DB_TABLE_PREFIX,
                self.TEST_DB_REPO_ID,
                odb_partitions=2, refdb_partitions=2)
        try:
            repo2 = Repository(None, 0,
                self.TEST_DB_USER, self.TEST_DB_PASSWD,
                self.TEST_DB_SOCKET, self.TEST_DB_DB,
                self.TEST_DB_TABLE_PREFIX,
                self.TEST_DB_REPO_ID + 1,
                odb_partitions=2, refdb_partitions=2)
            try:
                blob_oid2 = repo2.create_blob("abcdef\ntoto\n")

                author = Signature('Alice Author', 'alice@authors.tld')
                committer = Signature('Cecil Committer', 'cecil@committers.tld')
                tree1 = repo1.TreeBuilder().write()
                oid_1 = repo1.create_commit(
                        'refs/heads/master',  # create the branch
                        author, committer, 'one line commit message\n\ndetails',
                        tree1,  # binary string representing the tree object ID
                        []  # parents of the new commit
                    )
                self.assertNotEqual(oid_1, None)

                author = Signature('Alice Author 2', 'alice@authors.tld')
                tree2 = repo2.TreeBuilder()
                tree2.insert('toto.txt', blob_oid2, GIT_FILEMODE_BLOB)
                tree2 = tree2.write()
                oid_2 = repo2.create_commit(
                        'refs/heads/master',  # create the branch
                        author, committer, 'one line commit message\n\ndetails',
                        tree2,  # binary string representing the tree object ID
                        []  # parents of the new commit
                    )
                self.assertNotEqual(oid_2, None)
            finally:
                repo2.close()
        finally:
            repo1.close()

        # reopen
        repo1 = Repository(None, 0,
                self.TEST_DB_USER, self.TEST_DB_PASSWD,
                self.TEST_DB_SOCKET, self.TEST_DB_DB,
                self.TEST_DB_TABLE_PREFIX,
                self.TEST_DB_REPO_ID,
                odb_partitions=2, refdb_partitions=2)
        try:
            repo2 = Repository(None, 0,
                self.TEST_DB_USER, self.TEST_DB_PASSWD,
                self.TEST_DB_SOCKET, self.TEST_DB_DB,
                self.TEST_DB_TABLE_PREFIX,
                self.TEST_DB_REPO_ID + 1,
                odb_partitions=2, refdb_partitions=2)
            try:
                # fetch
                commit_1 = repo1[oid_1]
                self.assertNotEqual(commit_1, None)

                commit_2 = repo2[oid_2]
                self.assertNotEqual(commit_2, None)
            finally:
                repo2.close()
        finally:
            repo1.close()


if __name__ == '__main__':
    unittest.main()
