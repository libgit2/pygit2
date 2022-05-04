# Copyright 2010-2021 The pygit2 contributors
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

import sys

import pytest

import pygit2
from pygit2 import Oid
from . import utils


REMOTE_NAME = 'origin'
REMOTE_URL = 'https://github.com/libgit2/pygit2.git'
REMOTE_FETCHSPEC_SRC = 'refs/heads/*'
REMOTE_FETCHSPEC_DST = 'refs/remotes/origin/*'
REMOTE_REPO_OBJECTS = 30
REMOTE_REPO_BYTES = 2758

ORIGIN_REFSPEC = '+refs/heads/*:refs/remotes/origin/*'

def test_remote_create(testrepo):
    name = 'upstream'
    url = 'https://github.com/libgit2/pygit2.git'

    remote = testrepo.remotes.create(name, url)

    assert type(remote) == pygit2.Remote
    assert name == remote.name
    assert url == remote.url
    assert remote.push_url is None

    with pytest.raises(ValueError): testrepo.remotes.create(*(name, url))

def test_remote_create_with_refspec(testrepo):
    name = 'upstream'
    url = 'https://github.com/libgit2/pygit2.git'
    fetch = "+refs/*:refs/*"

    remote = testrepo.remotes.create(name, url, fetch)

    assert type(remote) == pygit2.Remote
    assert name == remote.name
    assert url == remote.url
    assert [fetch] == remote.fetch_refspecs
    assert remote.push_url is None

def test_remote_delete(testrepo):
    name = 'upstream'
    url = 'https://github.com/libgit2/pygit2.git'

    testrepo.remotes.create(name, url)
    assert 2 == len(testrepo.remotes)
    remote = testrepo.remotes[1]

    assert name == remote.name
    testrepo.remotes.delete(remote.name)
    assert 1 == len(testrepo.remotes)

def test_remote_rename(testrepo):
    remote = testrepo.remotes[0]

    assert REMOTE_NAME == remote.name
    problems = testrepo.remotes.rename(remote.name, "new")
    assert [] == problems
    assert 'new' != remote.name

    with pytest.raises(ValueError): testrepo.remotes.rename('', '')
    with pytest.raises(ValueError): testrepo.remotes.rename(None, None)


def test_remote_set_url(testrepo):
    remote = testrepo.remotes["origin"]
    assert REMOTE_URL == remote.url

    new_url = 'https://github.com/cholin/pygit2.git'
    testrepo.remotes.set_url("origin", new_url)
    remote = testrepo.remotes["origin"]
    assert new_url == remote.url

    with pytest.raises(ValueError):
        testrepo.remotes.set_url("origin", "")

    testrepo.remotes.set_push_url("origin", new_url)
    remote = testrepo.remotes["origin"]
    assert new_url == remote.push_url
    with pytest.raises(ValueError):
        testrepo.remotes.set_push_url("origin", "")

def test_refspec(testrepo):
    remote = testrepo.remotes["origin"]

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

    testrepo.remotes.add_fetch("origin", '+refs/test/*:refs/test/remotes/*')
    remote = testrepo.remotes["origin"]

    fetch_specs = remote.fetch_refspecs
    assert list == type(fetch_specs)
    assert 2 == len(fetch_specs)
    assert ['+refs/heads/*:refs/remotes/origin/*', '+refs/test/*:refs/test/remotes/*'] == fetch_specs

    testrepo.remotes.add_push("origin", '+refs/test/*:refs/test/remotes/*')

    with pytest.raises(TypeError):
        testrepo.remotes.add_fetch(['+refs/*:refs/*', 5])

    remote = testrepo.remotes["origin"]
    assert ['+refs/test/*:refs/test/remotes/*'] == remote.push_refspecs

def test_remote_list(testrepo):
    assert 1 == len(testrepo.remotes)
    remote = testrepo.remotes[0]
    assert REMOTE_NAME == remote.name
    assert REMOTE_URL == remote.url

    name = 'upstream'
    url = 'https://github.com/libgit2/pygit2.git'
    remote = testrepo.remotes.create(name, url)
    assert remote.name in [x.name for x in testrepo.remotes]

@utils.requires_network
def test_ls_remotes(testrepo):
    assert 1 == len(testrepo.remotes)
    remote = testrepo.remotes[0]

    refs = remote.ls_remotes()

    assert refs

    # Check that a known ref is returned.
    assert next(iter(r for r in refs if r['name'] == 'refs/tags/v0.28.2'))

def test_remote_collection(testrepo):
    remote = testrepo.remotes['origin']
    assert REMOTE_NAME == remote.name
    assert REMOTE_URL == remote.url

    with pytest.raises(KeyError):
        testrepo.remotes['upstream']

    name = 'upstream'
    url = 'https://github.com/libgit2/pygit2.git'
    remote = testrepo.remotes.create(name, url)
    assert remote.name in [x.name for x in testrepo.remotes]

@utils.refcount
def test_remote_refcount(testrepo):
    start = sys.getrefcount(testrepo)
    remote = testrepo.remotes[0]
    del remote
    end = sys.getrefcount(testrepo)
    assert start == end


def test_fetch(emptyrepo):
    remote = emptyrepo.remotes[0]
    stats = remote.fetch()
    assert stats.received_bytes == REMOTE_REPO_BYTES
    assert stats.indexed_objects == REMOTE_REPO_OBJECTS
    assert stats.received_objects == REMOTE_REPO_OBJECTS

def test_transfer_progress(emptyrepo):
    class MyCallbacks(pygit2.RemoteCallbacks):
        def transfer_progress(emptyrepo, stats):
            emptyrepo.tp = stats

    callbacks = MyCallbacks()
    remote = emptyrepo.remotes[0]
    stats = remote.fetch(callbacks=callbacks)
    assert stats.received_bytes == callbacks.tp.received_bytes
    assert stats.indexed_objects == callbacks.tp.indexed_objects
    assert stats.received_objects == callbacks.tp.received_objects

def test_update_tips(emptyrepo):
    remote = emptyrepo.remotes[0]
    tips = [('refs/remotes/origin/master', Oid(hex='0'*40),
             Oid(hex='784855caf26449a1914d2cf62d12b9374d76ae78')),
            ('refs/tags/root', Oid(hex='0'*40),
             Oid(hex='3d2962987c695a29f1f80b6c3aa4ec046ef44369'))]

    class MyCallbacks(pygit2.RemoteCallbacks):
        def __init__(self, tips):
            self.tips = tips
            self.i = 0

        def update_tips(self, name, old, new):
            assert self.tips[self.i] == (name, old, new)
            self.i += 1

    callbacks = MyCallbacks(tips)
    remote.fetch(callbacks=callbacks)
    assert callbacks.i > 0


@pytest.fixture
def origin(tmp_path):
    with utils.TemporaryRepository('barerepo.zip', tmp_path) as path:
        yield pygit2.Repository(path)

@pytest.fixture
def clone(tmp_path):
    clone = tmp_path / 'clone'
    clone.mkdir()
    with utils.TemporaryRepository('barerepo.zip', clone) as path:
        yield pygit2.Repository(path)

@pytest.fixture
def remote(origin, clone):
    yield clone.remotes.create('origin', origin.path)


def test_push_fast_forward_commits_to_remote_succeeds(origin, clone, remote):
    tip = clone[clone.head.target]
    oid = clone.create_commit(
        'refs/heads/master', tip.author, tip.author, 'empty commit',
        tip.tree.id, [tip.id]
    )
    remote.push(['refs/heads/master'])
    assert origin[origin.head.target].id == oid

def test_push_when_up_to_date_succeeds(origin, clone, remote):
    remote.push(['refs/heads/master'])
    origin_tip = origin[origin.head.target].id
    clone_tip = clone[clone.head.target].id
    assert origin_tip == clone_tip

def test_push_non_fast_forward_commits_to_remote_fails(origin, clone, remote):
    tip = origin[origin.head.target]
    origin.create_commit(
        'refs/heads/master', tip.author, tip.author, 'some commit',
        tip.tree.id, [tip.id]
    )
    tip = clone[clone.head.target]
    clone.create_commit(
        'refs/heads/master', tip.author, tip.author, 'other commit',
        tip.tree.id, [tip.id]
    )

    with pytest.raises(pygit2.GitError):
        remote.push(['refs/heads/master'])
