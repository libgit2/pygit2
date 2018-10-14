# -*- coding: UTF-8 -*-
#
# Copyright 2010-2017 The pygit2 contributors
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

"""Tests for Remote objects."""


import gc
import os.path
import sys
import unittest

import pytest

import pygit2
from pygit2 import Oid
from . import utils

try:
    import __pypy__
except ImportError:
    __pypy__ = None

REMOTE_NAME = 'origin'
REMOTE_URL = 'git://github.com/libgit2/pygit2.git'
REMOTE_FETCHSPEC_SRC = 'refs/heads/*'
REMOTE_FETCHSPEC_DST = 'refs/remotes/origin/*'
REMOTE_REPO_OBJECTS = 30
REMOTE_REPO_BYTES = 2758

ORIGIN_REFSPEC = '+refs/heads/*:refs/remotes/origin/*'

class RepositoryTest(utils.RepoTestCase):
    def test_remote_create(self):
        name = 'upstream'
        url = 'git://github.com/libgit2/pygit2.git'

        remote = self.repo.create_remote(name, url)

        assert type(remote) == pygit2.Remote
        assert name == remote.name
        assert url == remote.url
        assert remote.push_url is None

        with pytest.raises(ValueError): self.repo.create_remote(*(name, url))

    def test_remote_create_with_refspec(self):
        name = 'upstream'
        url = 'git://github.com/libgit2/pygit2.git'
        fetch = "+refs/*:refs/*"

        remote = self.repo.remotes.create(name, url, fetch)

        assert type(remote) == pygit2.Remote
        assert name == remote.name
        assert url == remote.url
        assert [fetch] == remote.fetch_refspecs
        assert remote.push_url is None

    def test_remote_delete(self):
        name = 'upstream'
        url = 'git://github.com/libgit2/pygit2.git'

        self.repo.create_remote(name, url)
        assert 2 == len(self.repo.remotes)
        remote = self.repo.remotes[1]

        assert name == remote.name
        self.repo.remotes.delete(remote.name)
        assert 1 == len(self.repo.remotes)

    def test_remote_rename(self):
        remote = self.repo.remotes[0]

        assert REMOTE_NAME == remote.name
        problems = self.repo.remotes.rename(remote.name, "new")
        assert [] == problems
        assert 'new' != remote.name

        with pytest.raises(ValueError): self.repo.remotes.rename('', '')
        with pytest.raises(ValueError): self.repo.remotes.rename(None, None)


    def test_remote_set_url(self):
        remote = self.repo.remotes["origin"]
        assert REMOTE_URL == remote.url

        new_url = 'git://github.com/cholin/pygit2.git'
        self.repo.remotes.set_url("origin", new_url)
        remote = self.repo.remotes["origin"]
        assert new_url == remote.url

        with pytest.raises(ValueError):
            self.repo.remotes.set_url("origin", "")

        self.repo.remotes.set_push_url("origin", new_url)
        remote = self.repo.remotes["origin"]
        assert new_url == remote.push_url
        with pytest.raises(ValueError):
            self.repo.remotes.set_push_url("origin", "")

    def test_refspec(self):
        remote = self.repo.remotes["origin"]

        assert remote.refspec_count == 1
        refspec = remote.get_refspec(0)
        assert refspec.src == REMOTE_FETCHSPEC_SRC
        assert refspec.dst == REMOTE_FETCHSPEC_DST
        assert True == refspec.force
        assert ORIGIN_REFSPEC == refspec.string

        assert list == type(remote.fetch_refspecs)
        assert 1 == len(remote.fetch_refspecs)
        assert ORIGIN_REFSPEC == remote.fetch_refspecs[0]

        assert refspec.src_matches('refs/heads/master')
        assert refspec.dst_matches('refs/remotes/origin/master')
        assert 'refs/remotes/origin/master' == refspec.transform('refs/heads/master')
        assert 'refs/heads/master' == refspec.rtransform('refs/remotes/origin/master')

        assert list == type(remote.push_refspecs)
        assert 0 == len(remote.push_refspecs)

        push_specs = remote.push_refspecs
        assert list == type(push_specs)
        assert 0 == len(push_specs)

        self.repo.remotes.add_fetch("origin", '+refs/test/*:refs/test/remotes/*')
        remote = self.repo.remotes["origin"]

        fetch_specs = remote.fetch_refspecs
        assert list == type(fetch_specs)
        assert 2 == len(fetch_specs)
        assert ['+refs/heads/*:refs/remotes/origin/*', '+refs/test/*:refs/test/remotes/*'] == fetch_specs

        self.repo.remotes.add_push("origin", '+refs/test/*:refs/test/remotes/*')

        with pytest.raises(TypeError):
            self.repo.remotes.add_fetch(['+refs/*:refs/*', 5])

        remote = self.repo.remotes["origin"]
        assert ['+refs/test/*:refs/test/remotes/*'] == remote.push_refspecs

    def test_remote_list(self):
        assert 1 == len(self.repo.remotes)
        remote = self.repo.remotes[0]
        assert REMOTE_NAME == remote.name
        assert REMOTE_URL == remote.url

        name = 'upstream'
        url = 'git://github.com/libgit2/pygit2.git'
        remote = self.repo.create_remote(name, url)
        assert remote.name in [x.name for x in self.repo.remotes]

    def test_remote_collection(self):
        remote = self.repo.remotes['origin']
        assert REMOTE_NAME == remote.name
        assert REMOTE_URL == remote.url

        with pytest.raises(KeyError):
            self.repo.remotes['upstream']

        name = 'upstream'
        url = 'git://github.com/libgit2/pygit2.git'
        remote = self.repo.remotes.create(name, url)
        assert remote.name in [x.name for x in self.repo.remotes]

    @unittest.skipIf(__pypy__ is not None, "skip refcounts checks in pypy")
    def test_remote_refcount(self):
        start = sys.getrefcount(self.repo)
        remote = self.repo.remotes[0]
        del remote
        end = sys.getrefcount(self.repo)
        assert start == end

class EmptyRepositoryTest(utils.EmptyRepoTestCase):
    def test_fetch(self):
        remote = self.repo.remotes[0]
        stats = remote.fetch()
        assert stats.received_bytes == REMOTE_REPO_BYTES
        assert stats.indexed_objects == REMOTE_REPO_OBJECTS
        assert stats.received_objects == REMOTE_REPO_OBJECTS

    def test_transfer_progress(self):
        class MyCallbacks(pygit2.RemoteCallbacks):
            def transfer_progress(self, stats):
                self.tp = stats

        callbacks = MyCallbacks()
        remote = self.repo.remotes[0]
        stats = remote.fetch(callbacks=callbacks)
        assert stats.received_bytes == callbacks.tp.received_bytes
        assert stats.indexed_objects == callbacks.tp.indexed_objects
        assert stats.received_objects == callbacks.tp.received_objects

    def test_update_tips(self):
        remote = self.repo.remotes[0]
        tips = [('refs/remotes/origin/master', Oid(hex='0'*40),
                 Oid(hex='784855caf26449a1914d2cf62d12b9374d76ae78')),
                ('refs/tags/root', Oid(hex='0'*40),
                 Oid(hex='3d2962987c695a29f1f80b6c3aa4ec046ef44369'))]

        class MyCallbacks(pygit2.RemoteCallbacks):
            def __init__(self, test_self, tips):
                self.test = test_self
                self.tips = tips
                self.i = 0

            def update_tips(self, name, old, new):
                self.test.assertEqual(self.tips[self.i], (name, old, new))
                self.i += 1

        callbacks = MyCallbacks(self, tips)
        remote.fetch(callbacks=callbacks)
        assert callbacks.i > 0


class PruneTestCase(utils.RepoTestCase):
    def setUp(self):
        super(PruneTestCase, self).setUp()
        cloned_repo_path = os.path.join(self.repo_ctxtmgr.temp_dir, 'test_remote_prune')
        pygit2.clone_repository(self.repo_path, cloned_repo_path)
        self.clone_repo = pygit2.Repository(cloned_repo_path)
        self.repo.branches.delete('i18n')

    def tearDown(self):
        self.clone_repo = None
        super(PruneTestCase, self).tearDown()
        
    def test_fetch_remote_default(self):
        self.clone_repo.remotes[0].fetch()
        assert 'origin/i18n' in self.clone_repo.branches

    def test_fetch_remote_prune(self):
        self.clone_repo.remotes[0].fetch(prune=pygit2.GIT_FETCH_PRUNE)
        assert 'origin/i18n' not in self.clone_repo.branches

    def test_fetch_no_prune(self):
        self.clone_repo.remotes[0].fetch(prune=pygit2.GIT_FETCH_NO_PRUNE)
        assert 'origin/i18n' in self.clone_repo.branches

    def test_remote_prune(self):
        pruned = []
        class MyCallbacks(pygit2.RemoteCallbacks):
            def update_tips(self, name, old, new):
                pruned.append(name)

        callbacks = MyCallbacks()
        remote = self.clone_repo.remotes['origin']
        # We do a fetch in order to establish the connection to the remote.
        # Prune operation requires an active connection.
        remote.fetch(prune=pygit2.GIT_FETCH_NO_PRUNE)
        assert 'origin/i18n' in self.clone_repo.branches
        remote.prune(callbacks)
        assert pruned == ['refs/remotes/origin/i18n']
        assert 'origin/i18n' not in self.clone_repo.branches

class Utf8BranchTest(utils.Utf8BranchRepoTestCase):
    def test_fetch(self):
        remote = self.repo.remotes.create('origin', self.repo.workdir)
        remote.fetch()


class PushTestCase(unittest.TestCase):
    def setUp(self):
        self.origin_ctxtmgr = utils.TemporaryRepository(('git', 'testrepo.git'))
        self.clone_ctxtmgr = utils.TemporaryRepository(('git', 'testrepo.git'))
        self.origin = pygit2.Repository(self.origin_ctxtmgr.__enter__())
        self.clone = pygit2.Repository(self.clone_ctxtmgr.__enter__())
        self.remote = self.clone.create_remote('origin', self.origin.path)

    def tearDown(self):
        self.origin = None
        self.clone = None
        self.remote = None
        gc.collect()

        self.origin_ctxtmgr.__exit__(None, None, None)
        self.clone_ctxtmgr.__exit__(None, None, None)

    def test_push_fast_forward_commits_to_remote_succeeds(self):
        tip = self.clone[self.clone.head.target]
        oid = self.clone.create_commit(
            'refs/heads/master', tip.author, tip.author, 'empty commit',
            tip.tree.id, [tip.id]
        )
        self.remote.push(['refs/heads/master'])
        assert self.origin[self.origin.head.target].id == oid

    def test_push_when_up_to_date_succeeds(self):
        self.remote.push(['refs/heads/master'])
        origin_tip = self.origin[self.origin.head.target].id
        clone_tip = self.clone[self.clone.head.target].id
        assert origin_tip == clone_tip

    def test_push_non_fast_forward_commits_to_remote_fails(self):
        tip = self.origin[self.origin.head.target]
        self.origin.create_commit(
            'refs/heads/master', tip.author, tip.author, 'some commit',
            tip.tree.id, [tip.id]
        )
        tip = self.clone[self.clone.head.target]
        self.clone.create_commit(
            'refs/heads/master', tip.author, tip.author, 'other commit',
            tip.tree.id, [tip.id]
        )

        with pytest.raises(pygit2.GitError):
            self.remote.push(['refs/heads/master'])
