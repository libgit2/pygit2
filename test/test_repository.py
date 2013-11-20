# -*- coding: UTF-8 -*-
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

"""Tests for Repository objects."""

# Import from the future
from __future__ import absolute_import
from __future__ import unicode_literals

# Import from the Standard Library
import binascii
import unittest
import tempfile
import os
from os.path import join, realpath

# Import from pygit2
from pygit2 import GIT_OBJ_ANY, GIT_OBJ_BLOB, GIT_OBJ_COMMIT
from pygit2 import init_repository, clone_repository, discover_repository
from pygit2 import Oid, Reference, hashfile
import pygit2
from . import utils


HEAD_SHA = '784855caf26449a1914d2cf62d12b9374d76ae78'
PARENT_SHA = 'f5e5aa4e36ab0fe62ee1ccc6eb8f79b866863b87'  # HEAD^
BLOB_HEX = 'af431f20fc541ed6d5afede3e2dc7160f6f01f16'
BLOB_RAW = binascii.unhexlify(BLOB_HEX.encode('ascii'))
BLOB_OID = Oid(raw=BLOB_RAW)


class RepositoryTest(utils.BareRepoTestCase):

    def test_is_empty(self):
        self.assertFalse(self.repo.is_empty)

    def test_is_bare(self):
        self.assertTrue(self.repo.is_bare)

    def test_head(self):
        head = self.repo.head
        self.assertEqual(HEAD_SHA, head.target.hex)
        self.assertEqual(type(head), Reference)
        self.assertFalse(self.repo.head_is_unborn)
        self.assertFalse(self.repo.head_is_detached)

    def test_read(self):
        self.assertRaises(TypeError, self.repo.read, 123)
        self.assertRaisesWithArg(KeyError, '1' * 40, self.repo.read, '1' * 40)

        ab = self.repo.read(BLOB_OID)
        a = self.repo.read(BLOB_HEX)
        self.assertEqual(ab, a)
        self.assertEqual((GIT_OBJ_BLOB, b'a contents\n'), a)

        a2 = self.repo.read('7f129fd57e31e935c6d60a0c794efe4e6927664b')
        self.assertEqual((GIT_OBJ_BLOB, b'a contents 2\n'), a2)

        a_hex_prefix = BLOB_HEX[:4]
        a3 = self.repo.read(a_hex_prefix)
        self.assertEqual((GIT_OBJ_BLOB, b'a contents\n'), a3)

    def test_write(self):
        data = b"hello world"
        # invalid object type
        self.assertRaises(ValueError, self.repo.write, GIT_OBJ_ANY, data)

        oid = self.repo.write(GIT_OBJ_BLOB, data)
        self.assertEqual(type(oid), Oid)

    def test_contains(self):
        self.assertRaises(TypeError, lambda: 123 in self.repo)
        self.assertTrue(BLOB_OID in self.repo)
        self.assertTrue(BLOB_HEX in self.repo)
        self.assertTrue(BLOB_HEX[:10] in self.repo)
        self.assertFalse('a' * 40 in self.repo)
        self.assertFalse('a' * 20 in self.repo)

    def test_iterable(self):
        l = [obj for obj in self.repo]
        oid = Oid(hex=BLOB_HEX)
        self.assertTrue(oid in l)

    def test_lookup_blob(self):
        self.assertRaises(TypeError, lambda: self.repo[123])
        self.assertEqual(self.repo[BLOB_OID].hex, BLOB_HEX)
        a = self.repo[BLOB_HEX]
        self.assertEqual(b'a contents\n', a.read_raw())
        self.assertEqual(BLOB_HEX, a.hex)
        self.assertEqual(GIT_OBJ_BLOB, a.type)

    def test_lookup_blob_prefix(self):
        a = self.repo[BLOB_HEX[:5]]
        self.assertEqual(b'a contents\n', a.read_raw())
        self.assertEqual(BLOB_HEX, a.hex)
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
        self.assertEqual(
            ('Second test data commit.\n\n'
             'This commit has some additional text.\n'),
            commit.message)
        self.assertRaises(ValueError, self.repo.__getitem__, too_short_prefix)

    def test_get_path(self):
        directory = realpath(self.repo.path)
        expected = realpath(self.repo_path)
        self.assertEqual(directory, expected)

    def test_get_workdir(self):
        self.assertEqual(self.repo.workdir, None)

    def test_revparse_single(self):
        parent = self.repo.revparse_single('HEAD^')
        self.assertEqual(parent.hex, PARENT_SHA)

    def test_hash(self):
        data = "foobarbaz"
        hashed_sha1 = pygit2.hash(data)
        written_sha1 = self.repo.create_blob(data)
        self.assertEqual(hashed_sha1, written_sha1)

    def test_hashfile(self):
        data = "bazbarfoo"
        tempfile_path = tempfile.mkstemp()[1]
        with open(tempfile_path, 'w') as fh:
            fh.write(data)
        hashed_sha1 = hashfile(tempfile_path)
        written_sha1 = self.repo.create_blob(data)
        self.assertEqual(hashed_sha1, written_sha1)


class RepositoryTest_II(utils.RepoTestCase):

    def test_is_empty(self):
        self.assertFalse(self.repo.is_empty)

    def test_is_bare(self):
        self.assertFalse(self.repo.is_bare)

    def test_get_path(self):
        directory = realpath(self.repo.path)
        expected = realpath(join(self.repo_path, '.git'))
        self.assertEqual(directory, expected)

    def test_get_workdir(self):
        directory = realpath(self.repo.workdir)
        expected = realpath(self.repo_path)
        self.assertEqual(directory, expected)

    def test_checkout_ref(self):
        ref_i18n = self.repo.lookup_reference('refs/heads/i18n')

        # checkout i18n with conflicts and default strategy should
        # not be possible
        self.assertRaises(pygit2.GitError, self.repo.checkout, ref_i18n)

        # checkout i18n with GIT_CHECKOUT_FORCE
        head = self.repo.head
        head = self.repo[head.target]
        self.assertTrue('new' not in head.tree)
        self.repo.checkout(ref_i18n, pygit2.GIT_CHECKOUT_FORCE)

        head = self.repo.head
        head = self.repo[head.target]
        self.assertEqual(head.hex, ref_i18n.target.hex)
        self.assertTrue('new' in head.tree)
        self.assertTrue('bye.txt' not in self.repo.status())

    def test_checkout_index(self):
        # some changes to working dir
        with open(os.path.join(self.repo.workdir, 'hello.txt'), 'w') as f:
            f.write('new content')

        # checkout index
        self.assertTrue('hello.txt' in self.repo.status())
        self.repo.checkout(strategy=pygit2.GIT_CHECKOUT_FORCE)
        self.assertTrue('hello.txt' not in self.repo.status())

    def test_checkout_head(self):
        # some changes to the index
        with open(os.path.join(self.repo.workdir, 'bye.txt'), 'w') as f:
            f.write('new content')
        self.repo.index.add('bye.txt')

        # checkout from index should not change anything
        self.assertTrue('bye.txt' in self.repo.status())
        self.repo.checkout(strategy=pygit2.GIT_CHECKOUT_FORCE)
        self.assertTrue('bye.txt' in self.repo.status())

        # checkout from head will reset index as well
        self.repo.checkout('HEAD', pygit2.GIT_CHECKOUT_FORCE)
        self.assertTrue('bye.txt' not in self.repo.status())

    def test_merge_base(self):
        commit = self.repo.merge_base(
            '5ebeeebb320790caf276b9fc8b24546d63316533',
            '4ec4389a8068641da2d6578db0419484972284c8')
        self.assertEqual(commit.hex,
                         'acecd5ea2924a4b900e7e149496e1f4b57976e51')


class NewRepositoryTest(utils.NoRepoTestCase):

    def test_new_repo(self):
        repo = init_repository(self._temp_dir, False)

        oid = repo.write(GIT_OBJ_BLOB, "Test")
        self.assertEqual(type(oid), Oid)

        assert os.path.exists(os.path.join(self._temp_dir, '.git'))


class InitRepositoryTest(utils.NoRepoTestCase):
    # under the assumption that repo.is_bare works

    def test_no_arg(self):
        repo = init_repository(self._temp_dir)
        self.assertFalse(repo.is_bare)

    def test_pos_arg_false(self):
        repo = init_repository(self._temp_dir, False)
        self.assertFalse(repo.is_bare)

    def test_pos_arg_true(self):
        repo = init_repository(self._temp_dir, True)
        self.assertTrue(repo.is_bare)

    def test_keyword_arg_false(self):
        repo = init_repository(self._temp_dir, bare=False)
        self.assertFalse(repo.is_bare)

    def test_keyword_arg_true(self):
        repo = init_repository(self._temp_dir, bare=True)
        self.assertTrue(repo.is_bare)



class DiscoverRepositoryTest(utils.NoRepoTestCase):

    def test_discover_repo(self):
        repo = init_repository(self._temp_dir, False)
        subdir = os.path.join(self._temp_dir, "test1", "test2")
        os.makedirs(subdir)
        self.assertEqual(repo.path, discover_repository(subdir))



class EmptyRepositoryTest(utils.EmptyRepoTestCase):

    def test_is_empty(self):
        self.assertTrue(self.repo.is_empty)

    def test_is_base(self):
        self.assertFalse(self.repo.is_bare)

    def test_head(self):
        self.assertTrue(self.repo.head_is_unborn)
        self.assertFalse(self.repo.head_is_detached)



class CloneRepositoryTest(utils.NoRepoTestCase):

    def test_clone_repository(self):
        repo_path = "./test/data/testrepo.git/"
        repo = clone_repository(repo_path, self._temp_dir)
        self.assertFalse(repo.is_empty)
        self.assertFalse(repo.is_bare)

    def test_clone_bare_repository(self):
        repo_path = "./test/data/testrepo.git/"
        repo = clone_repository(repo_path, self._temp_dir, bare=True)
        self.assertFalse(repo.is_empty)
        self.assertTrue(repo.is_bare)

    def test_clone_remote_name(self):
        repo_path = "./test/data/testrepo.git/"
        repo = clone_repository(
            repo_path, self._temp_dir, remote_name="custom_remote"
        )
        self.assertFalse(repo.is_empty)
        self.assertEqual(repo.remotes[0].name, "custom_remote")


    # FIXME The tests below are commented because they are broken:
    #
    # - test_clone_push_url: Passes, but does nothing useful.
    #
    # - test_clone_fetch_spec: Segfaults because of a bug in libgit2 0.19,
    #   this has been fixed already, so wait for 0.20
    #
    # - test_clone_push_spec: Passes, but does nothing useful.
    #
    # - test_clone_checkout_branch: Fails, because the test fixture does not
    #   have any branch named "test"

#   def test_clone_push_url(self):
#       repo_path = "./test/data/testrepo.git/"
#       repo = clone_repository(
#           repo_path, self._temp_dir, push_url="custom_push_url"
#       )
#       self.assertFalse(repo.is_empty)
#       # FIXME: When pygit2 supports retrieving the pushurl parameter,
#       # enable this test
#       # self.assertEqual(repo.remotes[0].pushurl, "custom_push_url")

#   def test_clone_fetch_spec(self):
#       repo_path = "./test/data/testrepo.git/"
#       repo = clone_repository(repo_path, self._temp_dir,
#                               fetch_spec="refs/heads/test")
#       self.assertFalse(repo.is_empty)
#       # FIXME: When pygit2 retrieve the fetchspec we passed to git clone.
#       # fetchspec seems to be going through, but the Repository class is
#       # not getting it.
#       # self.assertEqual(repo.remotes[0].fetchspec, "refs/heads/test")

#   def test_clone_push_spec(self):
#       repo_path = "./test/data/testrepo.git/"
#       repo = clone_repository(repo_path, self._temp_dir,
#                               push_spec="refs/heads/test")
#       self.assertFalse(repo.is_empty)
#       # FIXME: When pygit2 supports retrieving the pushspec parameter,
#       # enable this test
#       # not sure how to test this either... couldn't find pushspec
#       # self.assertEqual(repo.remotes[0].fetchspec, "refs/heads/test")

#   def test_clone_checkout_branch(self):
#       repo_path = "./test/data/testrepo.git/"
#       repo = clone_repository(repo_path, self._temp_dir,
#                               checkout_branch="test")
#       self.assertFalse(repo.is_empty)
#       # FIXME: When pygit2 supports retrieving the current branch,
#       # enable this test
#       # self.assertEqual(repo.remotes[0].current_branch, "test")


if __name__ == '__main__':
    unittest.main()
