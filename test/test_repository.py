# Copyright 2010-2019 The pygit2 contributors
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

# Import from the Standard Library
import binascii
import unittest
import shutil
import tempfile
import os
from os.path import join, realpath
import sys
from urllib.request import pathname2url

import pytest

# Import from pygit2
from pygit2 import GIT_OBJ_ANY, GIT_OBJ_BLOB, GIT_OBJ_COMMIT
from pygit2 import init_repository, clone_repository, discover_repository
from pygit2 import Oid, Reference, hashfile
import pygit2
from . import utils

try:
    import __pypy__
except ImportError:
    __pypy__ = None


HEAD_SHA = '784855caf26449a1914d2cf62d12b9374d76ae78'
PARENT_SHA = 'f5e5aa4e36ab0fe62ee1ccc6eb8f79b866863b87'  # HEAD^
BLOB_HEX = 'af431f20fc541ed6d5afede3e2dc7160f6f01f16'
BLOB_RAW = binascii.unhexlify(BLOB_HEX.encode('ascii'))
BLOB_OID = Oid(raw=BLOB_RAW)


class RepositoryTest(utils.BareRepoTestCase):

    def test_is_empty(self):
        assert not self.repo.is_empty

    def test_is_bare(self):
        assert self.repo.is_bare

    def test_head(self):
        head = self.repo.head
        assert HEAD_SHA == head.target.hex
        assert type(head) == Reference
        assert not self.repo.head_is_unborn
        assert not self.repo.head_is_detached

    def test_set_head(self):
        # Test setting a detatched HEAD.
        self.repo.set_head(Oid(hex=PARENT_SHA))
        assert self.repo.head.target.hex == PARENT_SHA
        # And test setting a normal HEAD.
        self.repo.set_head("refs/heads/master")
        assert self.repo.head.name == "refs/heads/master"
        assert self.repo.head.target.hex == HEAD_SHA

    def test_read(self):
        with pytest.raises(TypeError): self.repo.read(123)
        self.assertRaisesWithArg(KeyError, '1' * 40, self.repo.read, '1' * 40)

        ab = self.repo.read(BLOB_OID)
        a = self.repo.read(BLOB_HEX)
        assert ab == a
        assert (GIT_OBJ_BLOB, b'a contents\n') == a

        a2 = self.repo.read('7f129fd57e31e935c6d60a0c794efe4e6927664b')
        assert (GIT_OBJ_BLOB, b'a contents 2\n') == a2

        a_hex_prefix = BLOB_HEX[:4]
        a3 = self.repo.read(a_hex_prefix)
        assert (GIT_OBJ_BLOB, b'a contents\n') == a3

    def test_write(self):
        data = b"hello world"
        # invalid object type
        with pytest.raises(ValueError): self.repo.write(GIT_OBJ_ANY, data)

        oid = self.repo.write(GIT_OBJ_BLOB, data)
        assert type(oid) == Oid

    def test_contains(self):
        with pytest.raises(TypeError): 123 in self.repo
        assert BLOB_OID in self.repo
        assert BLOB_HEX in self.repo
        assert BLOB_HEX[:10] in self.repo
        assert ('a' * 40) not in self.repo
        assert ('a' * 20) not in self.repo

    def test_iterable(self):
        l = [obj for obj in self.repo]
        oid = Oid(hex=BLOB_HEX)
        assert oid in l

    def test_lookup_blob(self):
        with pytest.raises(TypeError): self.repo[123]
        assert self.repo[BLOB_OID].hex == BLOB_HEX
        a = self.repo[BLOB_HEX]
        assert b'a contents\n' == a.read_raw()
        assert BLOB_HEX == a.hex
        assert GIT_OBJ_BLOB == a.type

    def test_lookup_blob_prefix(self):
        a = self.repo[BLOB_HEX[:5]]
        assert b'a contents\n' == a.read_raw()
        assert BLOB_HEX == a.hex
        assert GIT_OBJ_BLOB == a.type

    def test_lookup_commit(self):
        commit_sha = '5fe808e8953c12735680c257f56600cb0de44b10'
        commit = self.repo[commit_sha]
        assert commit_sha == commit.hex
        assert GIT_OBJ_COMMIT == commit.type
        assert commit.message == ('Second test data commit.\n\n'
                                  'This commit has some additional text.\n')

    def test_lookup_commit_prefix(self):
        commit_sha = '5fe808e8953c12735680c257f56600cb0de44b10'
        commit_sha_prefix = commit_sha[:7]
        too_short_prefix = commit_sha[:3]
        commit = self.repo[commit_sha_prefix]
        assert commit_sha == commit.hex
        assert GIT_OBJ_COMMIT == commit.type
        assert 'Second test data commit.\n\n' 'This commit has some additional text.\n' == commit.message
        with pytest.raises(ValueError):
            self.repo.__getitem__(too_short_prefix)

    def test_expand_id(self):
        commit_sha = '5fe808e8953c12735680c257f56600cb0de44b10'
        expanded = self.repo.expand_id(commit_sha[:7])
        assert commit_sha == expanded.hex

    @unittest.skipIf(__pypy__ is not None, "skip refcounts checks in pypy")
    def test_lookup_commit_refcount(self):
        start = sys.getrefcount(self.repo)
        commit_sha = '5fe808e8953c12735680c257f56600cb0de44b10'
        commit = self.repo[commit_sha]
        del commit
        end = sys.getrefcount(self.repo)
        assert start == end

    def test_get_path(self):
        directory = realpath(self.repo.path)
        expected = realpath(self.repo_path)
        assert directory == expected

    def test_get_workdir(self):
        assert self.repo.workdir is None

    def test_revparse_single(self):
        parent = self.repo.revparse_single('HEAD^')
        assert parent.hex == PARENT_SHA

    def test_hash(self):
        data = "foobarbaz"
        hashed_sha1 = pygit2.hash(data)
        written_sha1 = self.repo.create_blob(data)
        assert hashed_sha1 == written_sha1

    def test_hashfile(self):
        data = "bazbarfoo"
        handle, tempfile_path = tempfile.mkstemp()
        with os.fdopen(handle, 'w') as fh:
            fh.write(data)
        hashed_sha1 = hashfile(tempfile_path)
        os.unlink(tempfile_path)
        written_sha1 = self.repo.create_blob(data)
        assert hashed_sha1 == written_sha1

    def test_conflicts_in_bare_repository(self):
        def create_conflict_file(repo, branch, content):
            oid = repo.create_blob(content.encode('utf-8'))
            tb = repo.TreeBuilder()
            tb.insert('conflict', oid, pygit2.GIT_FILEMODE_BLOB)
            tree = tb.write()

            sig = pygit2.Signature('Author', 'author@example.com')
            commit = repo.create_commit(branch.name, sig, sig,
                    'Conflict', tree, [branch.target])
            assert commit is not None
            return commit

        b1 = self.repo.create_branch('b1', self.repo.head.peel())
        c1 = create_conflict_file(self.repo, b1, 'ASCII - abc')
        b2 = self.repo.create_branch('b2', self.repo.head.peel())
        c2 = create_conflict_file(self.repo, b2, 'Unicode - äüö')

        index = self.repo.merge_commits(c1, c2)
        assert index.conflicts is not None

        # ConflictCollection does not allow calling len(...) on it directly so
        # we have to calculate length by iterating over its entries
        assert sum(1 for _ in index.conflicts) == 1

        (a, t, o) = index.conflicts['conflict']
        diff = self.repo.merge_file_from_index(a, t, o)
        assert diff == '''<<<<<<< conflict
ASCII - abc
=======
Unicode - äüö
>>>>>>> conflict
'''

class RepositoryTest_II(utils.RepoTestCase):

    def test_is_empty(self):
        assert not self.repo.is_empty

    def test_is_bare(self):
        assert not self.repo.is_bare

    def test_get_path(self):
        directory = realpath(self.repo.path)
        expected = realpath(join(self.repo_path, '.git'))
        assert directory == expected

    def test_get_workdir(self):
        directory = realpath(self.repo.workdir)
        expected = realpath(self.repo_path)
        assert directory == expected

    def test_set_workdir(self):
        directory = tempfile.mkdtemp()
        self.repo.workdir = directory
        assert realpath(self.repo.workdir) == realpath(directory)

    def test_checkout_ref(self):
        ref_i18n = self.repo.lookup_reference('refs/heads/i18n')

        # checkout i18n with conflicts and default strategy should
        # not be possible
        with pytest.raises(pygit2.GitError): self.repo.checkout(ref_i18n)

        # checkout i18n with GIT_CHECKOUT_FORCE
        head = self.repo.head
        head = self.repo[head.target]
        assert 'new' not in head.tree
        self.repo.checkout(ref_i18n, strategy=pygit2.GIT_CHECKOUT_FORCE)

        head = self.repo.head
        head = self.repo[head.target]
        assert head.hex == ref_i18n.target.hex
        assert 'new' in head.tree
        assert 'bye.txt' not in self.repo.status()

    def test_checkout_branch(self):
        branch_i18n = self.repo.lookup_branch('i18n')

        # checkout i18n with conflicts and default strategy should
        # not be possible
        with pytest.raises(pygit2.GitError): self.repo.checkout(branch_i18n)

        # checkout i18n with GIT_CHECKOUT_FORCE
        head = self.repo.head
        head = self.repo[head.target]
        assert 'new' not in head.tree
        self.repo.checkout(branch_i18n, strategy=pygit2.GIT_CHECKOUT_FORCE)

        head = self.repo.head
        head = self.repo[head.target]
        assert head.hex == branch_i18n.target.hex
        assert 'new' in head.tree
        assert 'bye.txt' not in self.repo.status()

    def test_checkout_index(self):
        # some changes to working dir
        with open(os.path.join(self.repo.workdir, 'hello.txt'), 'w') as f:
            f.write('new content')

        # checkout index
        assert 'hello.txt' in self.repo.status()
        self.repo.checkout(strategy=pygit2.GIT_CHECKOUT_FORCE)
        assert 'hello.txt' not in self.repo.status()

    def test_checkout_head(self):
        # some changes to the index
        with open(os.path.join(self.repo.workdir, 'bye.txt'), 'w') as f:
            f.write('new content')
        self.repo.index.add('bye.txt')

        # checkout from index should not change anything
        assert 'bye.txt' in self.repo.status()
        self.repo.checkout(strategy=pygit2.GIT_CHECKOUT_FORCE)
        assert 'bye.txt' in self.repo.status()

        # checkout from head will reset index as well
        self.repo.checkout('HEAD', strategy=pygit2.GIT_CHECKOUT_FORCE)
        assert 'bye.txt' not in self.repo.status()

    def test_checkout_alternative_dir(self):
        ref_i18n = self.repo.lookup_reference('refs/heads/i18n')
        extra_dir = os.path.join(self.repo.workdir, 'extra-dir')
        os.mkdir(extra_dir)
        assert len(os.listdir(extra_dir)) == 0
        self.repo.checkout(ref_i18n, directory=extra_dir)
        assert not len(os.listdir(extra_dir)) == 0

    def test_checkout_paths(self):
        ref_i18n = self.repo.lookup_reference('refs/heads/i18n')
        ref_master = self.repo.lookup_reference('refs/heads/master')
        self.repo.checkout(ref_master)
        self.repo.checkout(ref_i18n, paths=['new'])
        status = self.repo.status()
        assert status['new'] == pygit2.GIT_STATUS_INDEX_NEW

    def test_merge_base(self):
        commit = self.repo.merge_base(
            '5ebeeebb320790caf276b9fc8b24546d63316533',
            '4ec4389a8068641da2d6578db0419484972284c8')
        assert commit.hex == 'acecd5ea2924a4b900e7e149496e1f4b57976e51'

        # Create a commit without any merge base to any other
        sig = pygit2.Signature("me", "me@example.com")
        indep = self.repo.create_commit(None, sig, sig, "a new root commit",
                                        self.repo[commit].peel(pygit2.Tree).id, [])

        assert self.repo.merge_base(indep, commit) is None

    def test_descendent_of(self):
        assert not self.repo.descendant_of(
            '5ebeeebb320790caf276b9fc8b24546d63316533',
            '4ec4389a8068641da2d6578db0419484972284c8')
        assert not self.repo.descendant_of(
            '5ebeeebb320790caf276b9fc8b24546d63316533',
            '5ebeeebb320790caf276b9fc8b24546d63316533')
        assert self.repo.descendant_of(
            '5ebeeebb320790caf276b9fc8b24546d63316533',
            'acecd5ea2924a4b900e7e149496e1f4b57976e51')
        assert not self.repo.descendant_of(
            'acecd5ea2924a4b900e7e149496e1f4b57976e51',
            '5ebeeebb320790caf276b9fc8b24546d63316533')

        with pytest.raises(pygit2.GitError):
            self.repo.descendant_of(
                '2' * 40,  # a valid but inexistent SHA
                '5ebeeebb320790caf276b9fc8b24546d63316533')

    def test_ahead_behind(self):
        ahead, behind = self.repo.ahead_behind(
            '5ebeeebb320790caf276b9fc8b24546d63316533',
            '4ec4389a8068641da2d6578db0419484972284c8')
        assert 1 == ahead
        assert 2 == behind

        ahead, behind = self.repo.ahead_behind(
            '4ec4389a8068641da2d6578db0419484972284c8',
            '5ebeeebb320790caf276b9fc8b24546d63316533')
        assert 2 == ahead
        assert 1 == behind

    def test_reset_hard(self):
        ref = "5ebeeebb320790caf276b9fc8b24546d63316533"
        with open(os.path.join(self.repo.workdir, "hello.txt")) as f:
            lines = f.readlines()
        assert "hola mundo\n" in lines
        assert "bonjour le monde\n" in lines

        self.repo.reset(
            ref,
            pygit2.GIT_RESET_HARD)
        assert self.repo.head.target.hex == ref

        with open(os.path.join(self.repo.workdir, "hello.txt")) as f:
            lines = f.readlines()
        #Hard reset will reset the working copy too
        assert "hola mundo\n" not in lines
        assert "bonjour le monde\n" not in lines

    def test_reset_soft(self):
        ref = "5ebeeebb320790caf276b9fc8b24546d63316533"
        with open(os.path.join(self.repo.workdir, "hello.txt")) as f:
            lines = f.readlines()
        assert "hola mundo\n" in lines
        assert "bonjour le monde\n" in lines

        self.repo.reset(
            ref,
            pygit2.GIT_RESET_SOFT)
        assert self.repo.head.target.hex == ref
        with open(os.path.join(self.repo.workdir, "hello.txt")) as f:
            lines = f.readlines()
        #Soft reset will not reset the working copy
        assert "hola mundo\n" in lines
        assert "bonjour le monde\n" in lines

        #soft reset will keep changes in the index
        diff = self.repo.diff(cached=True)
        with pytest.raises(KeyError): diff[0]

    def test_reset_mixed(self):
        ref = "5ebeeebb320790caf276b9fc8b24546d63316533"
        with open(os.path.join(self.repo.workdir, "hello.txt")) as f:
            lines = f.readlines()
        assert "hola mundo\n" in lines
        assert "bonjour le monde\n" in lines

        self.repo.reset(
            ref,
            pygit2.GIT_RESET_MIXED)

        assert self.repo.head.target.hex == ref

        with open(os.path.join(self.repo.workdir, "hello.txt")) as f:
            lines = f.readlines()
        #mixed reset will not reset the working copy
        assert "hola mundo\n" in lines
        assert "bonjour le monde\n" in lines

        #mixed reset will set the index to match working copy
        diff = self.repo.diff(cached=True)
        assert "hola mundo\n" in diff.patch
        assert "bonjour le monde\n" in diff.patch

    def test_stash(self):
        # some changes to working dir
        with open(os.path.join(self.repo.workdir, 'hello.txt'), 'w') as f:
            f.write('new content')

        sig = pygit2.Signature('Stasher', 'stasher@example.com')
        self.repo.stash(sig, include_untracked=True)
        assert 'hello.txt' not in self.repo.status()
        self.repo.stash_apply()
        assert 'hello.txt' in self.repo.status()
        self.repo.stash_drop()
        with pytest.raises(KeyError): self.repo.stash_pop()

    def test_revert(self):
        master = self.repo.head.peel()
        commit_to_revert = self.repo['4ec4389a8068641da2d6578db0419484972284c8']
        parent = commit_to_revert.parents[0]
        commit_diff_stats = (
            parent.tree.diff_to_tree(commit_to_revert.tree).stats
        )

        revert_index = self.repo.revert_commit(commit_to_revert, master)
        revert_diff_stats = revert_index.diff_to_tree(master.tree).stats

        assert revert_diff_stats.insertions == commit_diff_stats.deletions
        assert revert_diff_stats.deletions == commit_diff_stats.insertions
        assert revert_diff_stats.files_changed == commit_diff_stats.files_changed

    def test_diff_patch(self):
        new_content = ['bye world', 'adiós', 'au revoir monde']
        new_content = ''.join(x + os.linesep for x in new_content)

        # create the patch
        with open(os.path.join(self.repo.workdir, 'hello.txt'), 'wb') as f:
            f.write(new_content.encode('utf-8'))

        patch = self.repo.diff().patch

        # rollback all changes
        self.repo.checkout('HEAD', strategy=pygit2.GIT_CHECKOUT_FORCE)

        # apply the patch and compare
        diff = pygit2.Diff.parse_diff(patch)
        self.repo.apply(diff)

        with open(os.path.join(self.repo.workdir, 'hello.txt'), 'rb') as f:
            content = f.read().decode('utf-8')

        self.assertEqual(content, new_content)


class RepositorySignatureTest(utils.RepoTestCase):

    def test_default_signature(self):
        config = self.repo.config
        config['user.name'] = 'Random J Hacker'
        config['user.email'] ='rjh@example.com'

        sig = self.repo.default_signature
        assert 'Random J Hacker' == sig.name
        assert 'rjh@example.com' == sig.email

class NewRepositoryTest(utils.NoRepoTestCase):

    def test_new_repo(self):
        repo = init_repository(self._temp_dir, False)

        oid = repo.write(GIT_OBJ_BLOB, "Test")
        assert type(oid) == Oid

        assert os.path.exists(os.path.join(self._temp_dir, '.git'))


class InitRepositoryTest(utils.NoRepoTestCase):
    # under the assumption that repo.is_bare works

    def test_no_arg(self):
        repo = init_repository(self._temp_dir)
        assert not repo.is_bare

    def test_pos_arg_false(self):
        repo = init_repository(self._temp_dir, False)
        assert not repo.is_bare

    def test_pos_arg_true(self):
        repo = init_repository(self._temp_dir, True)
        assert repo.is_bare

    def test_keyword_arg_false(self):
        repo = init_repository(self._temp_dir, bare=False)
        assert not repo.is_bare

    def test_keyword_arg_true(self):
        repo = init_repository(self._temp_dir, bare=True)
        assert repo.is_bare


class DiscoverRepositoryTest(utils.NoRepoTestCase):

    def test_discover_repo(self):
        repo = init_repository(self._temp_dir, False)
        subdir = os.path.join(self._temp_dir, "test1", "test2")
        os.makedirs(subdir)
        assert repo.path == discover_repository(subdir)

    def test_discover_repo_not_found(self):
        assert discover_repository(tempfile.tempdir) is None


class EmptyRepositoryTest(utils.EmptyRepoTestCase):

    def test_is_empty(self):
        assert self.repo.is_empty

    def test_is_base(self):
        assert not self.repo.is_bare

    def test_head(self):
        assert self.repo.head_is_unborn
        assert not self.repo.head_is_detached


class StringTypesRepositoryTest(utils.NoRepoTestCase):

    def test_bytes_string(self):
        repo_path = b'./test/data/testrepo.git/'
        pygit2.Repository(repo_path)

    def test_unicode_string(self):
        # String is unicode because of unicode_literals
        repo_path = './test/data/testrepo.git/'
        pygit2.Repository(repo_path)


class CloneRepositoryTest(utils.NoRepoTestCase):

    def test_clone_repository(self):
        repo_path = "./test/data/testrepo.git/"
        repo = clone_repository(repo_path, self._temp_dir)
        assert not repo.is_empty
        assert not repo.is_bare

    def test_clone_bare_repository(self):
        repo_path = "./test/data/testrepo.git/"
        repo = clone_repository(repo_path, self._temp_dir, bare=True)
        assert not repo.is_empty
        assert repo.is_bare

    def test_clone_repository_and_remote_callbacks(self):
        src_repo_relpath = "./test/data/testrepo.git/"
        repo_path = os.path.join(self._temp_dir, "clone-into")
        url = pathname2url(os.path.realpath(src_repo_relpath))

        if url.startswith('///'):
            url = 'file:' + url
        else:
            url = 'file://' + url

        def create_repository(path, bare):
            return init_repository(path, bare)

        # here we override the name
        def create_remote(repo, name, url):
            return repo.remotes.create("custom_remote", url)

        repo = clone_repository(url, repo_path, repository=create_repository, remote=create_remote)
        assert not repo.is_empty
        assert 'refs/remotes/custom_remote/master' in repo.listall_references()
        assert repo.remotes["custom_remote"] is not None

    @unittest.skipIf(utils.no_network(), "Requires network")
    def test_clone_with_credentials(self):
        url = 'https://github.com/libgit2/TestGitRepository'
        credentials = pygit2.UserPass("libgit2", "libgit2")
        callbacks = pygit2.RemoteCallbacks(credentials=credentials)
        repo = clone_repository(url, self._temp_dir, callbacks=callbacks)

        assert not repo.is_empty

    def test_clone_with_checkout_branch(self):
        # create a test case which isolates the remote
        test_repo = clone_repository('./test/data/testrepo.git',
                                     os.path.join(self._temp_dir, 'testrepo-orig.git'),
                                     bare=True)
        test_repo.create_branch('test', test_repo[test_repo.head.target])
        repo = clone_repository(test_repo.path,
                                os.path.join(self._temp_dir, 'testrepo.git'),
                                checkout_branch='test', bare=True)
        assert repo.lookup_reference('HEAD').target == 'refs/heads/test'

    # FIXME The tests below are commented because they are broken:
    #
    # - test_clone_push_url: Passes, but does nothing useful.
    #
    # - test_clone_fetch_spec: Segfaults because of a bug in libgit2 0.19,
    #   this has been fixed already, so wait for 0.20
    #
    # - test_clone_push_spec: Passes, but does nothing useful.
    #

#   def test_clone_push_url(self):
#       repo_path = "./test/data/testrepo.git/"
#       repo = clone_repository(
#           repo_path, self._temp_dir, push_url="custom_push_url"
#       )
#       assert not repo.is_empty
#       # FIXME: When pygit2 supports retrieving the pushurl parameter,
#       # enable this test
#       # assert repo.remotes[0].pushurl == "custom_push_url"

#   def test_clone_fetch_spec(self):
#       repo_path = "./test/data/testrepo.git/"
#       repo = clone_repository(repo_path, self._temp_dir,
#                               fetch_spec="refs/heads/test")
#       assert not repo.is_empty
#       # FIXME: When pygit2 retrieve the fetchspec we passed to git clone.
#       # fetchspec seems to be going through, but the Repository class is
#       # not getting it.
#       # assert repo.remotes[0].fetchspec == "refs/heads/test"

#   def test_clone_push_spec(self):
#       repo_path = "./test/data/testrepo.git/"
#       repo = clone_repository(repo_path, self._temp_dir,
#                               push_spec="refs/heads/test")
#       assert not repo.is_empty
#       # FIXME: When pygit2 supports retrieving the pushspec parameter,
#       # enable this test
#       # not sure how to test this either... couldn't find pushspec
#       # assert repo.remotes[0].fetchspec == "refs/heads/test"

class WorktreeTestCase(utils.RepoTestCase):

    def test_worktree(self):
        worktree_name = 'foo'
        worktree_dir = tempfile.mkdtemp()
        # Delete temp path so that it's not present when we attempt to add the
        # worktree later
        os.rmdir(worktree_dir)

        def _check_worktree(worktree):
            # Confirm the name attribute matches the specified name
            assert worktree.name == worktree_name
            # Confirm the path attribute points to the correct path
            assert os.path.realpath(worktree.path) == worktree_dir
            # The "gitdir" in a worktree should be a file with a reference to
            # the actual gitdir. Let's make sure that the path exists and is a
            # file.
            assert os.path.isfile(os.path.join(worktree_dir, '.git'))

        # We should have zero worktrees
        assert self.repo.list_worktrees() == []
        # Add a worktree
        worktree = self.repo.add_worktree(worktree_name, worktree_dir)
        # Check that the worktree was added properly
        _check_worktree(worktree)
        # We should have one worktree now
        assert self.repo.list_worktrees() == [worktree_name]
        # We should also have a branch of the same name
        assert worktree_name in self.repo.listall_branches()
        # Test that lookup_worktree() returns a properly-instantiated
        # pygit2._Worktree object
        _check_worktree(self.repo.lookup_worktree(worktree_name))
        # Remove the worktree dir
        shutil.rmtree(worktree_dir)
        # Prune the worktree. For some reason, libgit2 treats a worktree as
        # valid unless both the worktree directory and data dir under
        # $GIT_DIR/worktrees are gone. This doesn't make much sense since the
        # normal usage involves removing the worktree directory and then
        # pruning. So, for now we have to force the prune. This may be
        # something to take up with libgit2.
        worktree.prune(True)
        assert self.repo.list_worktrees() == []

    def test_worktree_custom_ref(self):
        worktree_name = 'foo'
        worktree_dir = tempfile.mkdtemp()
        branch_name = 'version1'

        # New branch based on head
        tip = self.repo.revparse_single('HEAD')
        worktree_ref = self.repo.branches.create(branch_name, tip)
        # Delete temp path so that it's not present when we attempt to add the
        # worktree later
        os.rmdir(worktree_dir)

        # Add a worktree for the given ref
        worktree = self.repo.add_worktree(worktree_name, worktree_dir, worktree_ref)
        # We should have one worktree now
        assert self.repo.list_worktrees() == [worktree_name]
        # We should not have a branch of the same name
        assert worktree_name not in self.repo.listall_branches()

        # The given ref is checked out in the "worktree repository"
        assert worktree_ref.is_checked_out()

        # Remove the worktree dir and prune the worktree
        shutil.rmtree(worktree_dir)
        worktree.prune(True)
        assert self.repo.list_worktrees() == []

        # The ref is no longer checked out
        assert worktree_ref.is_checked_out() == False

        # The branch still exists
        assert branch_name in self.repo.branches
