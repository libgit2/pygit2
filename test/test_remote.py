# Copyright 2010-2025 The pygit2 contributors
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
from unittest.mock import patch

import pytest

import pygit2
from pygit2 import Oid
from pygit2.ffi import ffi

from . import utils

REMOTE_NAME = 'origin'
REMOTE_URL = 'https://github.com/libgit2/pygit2.git'
REMOTE_FETCHSPEC_SRC = 'refs/heads/*'
REMOTE_FETCHSPEC_DST = 'refs/remotes/origin/*'
REMOTE_REPO_OBJECTS = 30
REMOTE_FETCHTEST_FETCHSPECS = ['refs/tags/v1.13.2']
REMOTE_REPO_FETCH_ALL_OBJECTS = 13276
REMOTE_REPO_FETCH_HEAD_COMMIT_OBJECTS = 238

ORIGIN_REFSPEC = '+refs/heads/*:refs/remotes/origin/*'


def test_remote_create(testrepo):
    name = 'upstream'
    url = 'https://github.com/libgit2/pygit2.git'

    remote = testrepo.remotes.create(name, url)

    assert type(remote) is pygit2.Remote
    assert name == remote.name
    assert url == remote.url
    assert remote.push_url is None

    with pytest.raises(ValueError):
        testrepo.remotes.create(*(name, url))


def test_remote_create_with_refspec(testrepo):
    name = 'upstream'
    url = 'https://github.com/libgit2/pygit2.git'
    fetch = '+refs/*:refs/*'

    remote = testrepo.remotes.create(name, url, fetch)

    assert type(remote) is pygit2.Remote
    assert name == remote.name
    assert url == remote.url
    assert [fetch] == remote.fetch_refspecs
    assert remote.push_url is None


def test_remote_create_anonymous(testrepo):
    url = 'https://github.com/libgit2/pygit2.git'

    remote = testrepo.remotes.create_anonymous(url)
    assert remote.name is None
    assert url == remote.url
    assert remote.push_url is None
    assert remote.fetch_refspecs == []
    assert remote.push_refspecs == []
    assert remote.fetch_refspecs == []
    assert remote.push_refspecs == []


def test_remote_delete(testrepo):
    name = 'upstream'
    url = 'https://github.com/libgit2/pygit2.git'

    testrepo.remotes.create(name, url)
    assert len(testrepo.remotes) == 2
    assert len(testrepo.remotes) == 2
    remote = testrepo.remotes[1]

    assert name == remote.name
    testrepo.remotes.delete(remote.name)
    assert len(testrepo.remotes) == 1
    assert len(testrepo.remotes) == 1


def test_remote_rename(testrepo):
    remote = testrepo.remotes[0]

    assert remote.name == REMOTE_NAME
    assert remote.name == REMOTE_NAME
    problems = testrepo.remotes.rename(remote.name, 'new')
    assert problems == []
    assert remote.name != 'new'
    assert problems == []
    assert remote.name != 'new'

    with pytest.raises(ValueError):
        testrepo.remotes.rename('', '')
    with pytest.raises(ValueError):
        testrepo.remotes.rename(None, None)


def test_remote_set_url(testrepo):
    remote = testrepo.remotes['origin']
    assert remote.url == REMOTE_URL
    assert remote.url == REMOTE_URL

    new_url = 'https://github.com/cholin/pygit2.git'
    testrepo.remotes.set_url('origin', new_url)
    remote = testrepo.remotes['origin']
    assert new_url == remote.url

    with pytest.raises(ValueError):
        testrepo.remotes.set_url('origin', '')

    testrepo.remotes.set_push_url('origin', new_url)
    remote = testrepo.remotes['origin']
    assert new_url == remote.push_url
    with pytest.raises(ValueError):
        testrepo.remotes.set_push_url('origin', '')


def test_refspec(testrepo):
    remote = testrepo.remotes['origin']

    assert remote.refspec_count == 1
    refspec = remote.get_refspec(0)
    assert refspec.src == REMOTE_FETCHSPEC_SRC
    assert refspec.dst == REMOTE_FETCHSPEC_DST
    assert refspec.force is True
    assert refspec.string == ORIGIN_REFSPEC
    assert refspec.string == ORIGIN_REFSPEC

    assert list is type(remote.fetch_refspecs)
    assert 1 == len(remote.fetch_refspecs)
    assert ORIGIN_REFSPEC == remote.fetch_refspecs[0]

    assert refspec.src_matches('refs/heads/master')
    assert refspec.dst_matches('refs/remotes/origin/master')
    assert refspec.transform('refs/heads/master') == 'refs/remotes/origin/master'
    assert refspec.rtransform('refs/remotes/origin/master') == 'refs/heads/master'
    assert refspec.transform('refs/heads/master') == 'refs/remotes/origin/master'
    assert refspec.rtransform('refs/remotes/origin/master') == 'refs/heads/master'

    assert list is type(remote.push_refspecs)
    assert 0 == len(remote.push_refspecs)

    push_specs = remote.push_refspecs
    assert list is type(push_specs)
    assert 0 == len(push_specs)

    testrepo.remotes.add_fetch('origin', '+refs/test/*:refs/test/remotes/*')
    remote = testrepo.remotes['origin']

    fetch_specs = remote.fetch_refspecs
    assert list is type(fetch_specs)
    assert 2 == len(fetch_specs)
    assert [
        '+refs/heads/*:refs/remotes/origin/*',
        '+refs/test/*:refs/test/remotes/*',
    ]
    ]

    testrepo.remotes.add_push('origin', '+refs/test/*:refs/test/remotes/*')

    with pytest.raises(TypeError):
        testrepo.remotes.add_fetch(['+refs/*:refs/*', 5])

    remote = testrepo.remotes['origin']
    assert remote.push_refspecs == ['+refs/test/*:refs/test/remotes/*']
    assert remote.push_refspecs == ['+refs/test/*:refs/test/remotes/*']


def test_remote_list(testrepo):
    assert len(testrepo.remotes) == 1
    assert len(testrepo.remotes) == 1
    remote = testrepo.remotes[0]
    assert remote.name == REMOTE_NAME
    assert remote.url == REMOTE_URL
    assert remote.name == REMOTE_NAME
    assert remote.url == REMOTE_URL

    name = 'upstream'
    url = 'https://github.com/libgit2/pygit2.git'
    remote = testrepo.remotes.create(name, url)
    assert remote.name in testrepo.remotes.names()
    assert remote.name in [x.name for x in testrepo.remotes]


@utils.requires_network
def test_ls_remotes(testrepo):
    assert len(testrepo.remotes) == 1
    assert len(testrepo.remotes) == 1
    remote = testrepo.remotes[0]

    refs = remote.ls_remotes()
    assert refs

    # Check that a known ref is returned.
    assert next(iter(r for r in refs if r['name'] == 'refs/tags/v0.28.2'))


def test_remote_collection(testrepo):
    remote = testrepo.remotes['origin']
    assert remote.name == REMOTE_NAME
    assert remote.url == REMOTE_URL
    assert remote.name == REMOTE_NAME
    assert remote.url == REMOTE_URL

    with pytest.raises(KeyError):
        testrepo.remotes['upstream']

    name = 'upstream'
    url = 'https://github.com/libgit2/pygit2.git'
    remote = testrepo.remotes.create(name, url)
    assert remote.name in testrepo.remotes.names()
    assert remote.name in [x.name for x in testrepo.remotes]


@utils.requires_refcount
def test_remote_refcount(testrepo):
    start = sys.getrefcount(testrepo)
    remote = testrepo.remotes[0]
    del remote
    end = sys.getrefcount(testrepo)
    assert start == end


def test_fetch(emptyrepo):
    remote = emptyrepo.remotes[0]
    stats = remote.fetch()
    assert stats.received_bytes > 2700
    assert stats.received_bytes < 3100
    assert stats.indexed_objects == REMOTE_REPO_OBJECTS
    assert stats.received_objects == REMOTE_REPO_OBJECTS


@utils.requires_network
def test_fetch_depth_zero(testrepo):
    remote = testrepo.remotes[0]
    stats = remote.fetch(REMOTE_FETCHTEST_FETCHSPECS, depth=0)
    assert stats.indexed_objects == REMOTE_REPO_FETCH_ALL_OBJECTS
    assert stats.received_objects == REMOTE_REPO_FETCH_ALL_OBJECTS


@utils.requires_network
def test_fetch_depth_one(testrepo):
    remote = testrepo.remotes[0]
    stats = remote.fetch(REMOTE_FETCHTEST_FETCHSPECS, depth=1)
    assert stats.indexed_objects == REMOTE_REPO_FETCH_HEAD_COMMIT_OBJECTS
    assert stats.received_objects == REMOTE_REPO_FETCH_HEAD_COMMIT_OBJECTS


def test_transfer_progress(emptyrepo):
    class MyCallbacks(pygit2.RemoteCallbacks):
        def transfer_progress(self, stats):
            self.tp = stats

    callbacks = MyCallbacks()
    remote = emptyrepo.remotes[0]
    stats = remote.fetch(callbacks=callbacks)
    assert stats.received_bytes == callbacks.tp.received_bytes
    assert stats.indexed_objects == callbacks.tp.indexed_objects
    assert stats.received_objects == callbacks.tp.received_objects


def test_update_tips(emptyrepo):
    remote = emptyrepo.remotes[0]
    tips = [
        (
            'refs/remotes/origin/master',
            pygit2.Oid(hex='0' * 40),
            pygit2.Oid(hex='784855caf26449a1914d2cf62d12b9374d76ae78'),
        ),
        (
            'refs/tags/root',
            pygit2.Oid(hex='0' * 40),
            pygit2.Oid(hex='3d2962987c695a29f1f80b6c3aa4ec046ef44369'),
        ),
    ]

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


@utils.requires_network
def test_ls_remotes_certificate_check():
    url = 'https://github.com/pygit2/empty.git'

    class MyCallbacks(pygit2.RemoteCallbacks):
        def __init__(self):
            self.i = 0

        def certificate_check(self, certificate, valid, host):
            self.i += 1

            assert certificate is None
            assert valid is True
            assert host == b'github.com'
            return True

    # We create an in-memory repository
    git = pygit2.Repository()
    remote = git.remotes.create_anonymous(url)

    callbacks = MyCallbacks()
    refs = remote.ls_remotes(callbacks=callbacks)

    # Sanity check that we indeed got some refs.
    assert len(refs) > 0

    # Make sure our certificate_check callback triggered.
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
        'refs/heads/master',
        tip.author,
        tip.author,
        'empty commit',
        tip.tree.id,
        [tip.id],
    )
    remote.push(['refs/heads/master'])
    assert origin[origin.head.target].id == oid


def test_push_when_up_to_date_succeeds(origin, clone, remote):
    remote.push(['refs/heads/master'])
    origin_tip = origin[origin.head.target].id
    clone_tip = clone[clone.head.target].id
    assert origin_tip == clone_tip


def test_push_transfer_progress(origin, clone, remote):
    tip = clone[clone.head.target]
    new_tip_id = clone.create_commit(
        'refs/heads/master',
        tip.author,
        tip.author,
        'empty commit',
        tip.tree.id,
        [tip.id],
    )

    # NOTE: We're currently not testing bytes_pushed due to a bug in libgit2
    # 1.9.0: it passes a junk value for bytes_pushed when pushing to a remote
    # on the local filesystem, as is the case in this unit test. (When pushing
    # to a remote over the network, the value is correct.)
    class MyCallbacks(pygit2.RemoteCallbacks):
        def push_transfer_progress(self, objects_pushed, total_objects, bytes_pushed):
            self.objects_pushed = objects_pushed
            self.total_objects = total_objects

    assert origin.branches['master'].target == tip.id

    callbacks = MyCallbacks()
    remote.push(['refs/heads/master'], callbacks=callbacks)
    assert callbacks.objects_pushed == 1
    assert callbacks.total_objects == 1
    assert origin.branches['master'].target == new_tip_id


def test_push_interrupted_from_callbacks(origin, clone, remote):
    tip = clone[clone.head.target]
    clone.create_commit(
        'refs/heads/master',
        tip.author,
        tip.author,
        'empty commit',
        tip.tree.id,
        [tip.id],
    )

    class MyCallbacks(pygit2.RemoteCallbacks):
        def push_transfer_progress(self, objects_pushed, total_objects, bytes_pushed):
            raise InterruptedError('retreat! retreat!')

    assert origin.branches['master'].target == tip.id

    callbacks = MyCallbacks()
    with pytest.raises(InterruptedError, match='retreat! retreat!'):
        remote.push(['refs/heads/master'], callbacks=callbacks)

    assert origin.branches['master'].target == tip.id


def test_push_non_fast_forward_commits_to_remote_fails(origin, clone, remote):
    tip = origin[origin.head.target]
    origin.create_commit(
        'refs/heads/master',
        tip.author,
        tip.author,
        'some commit',
        tip.tree.id,
        [tip.id],
    )
    tip = clone[clone.head.target]
    clone.create_commit(
        'refs/heads/master',
        tip.author,
        tip.author,
        'other commit',
        tip.tree.id,
        [tip.id],
    )

    with pytest.raises(pygit2.GitError):
        remote.push(['refs/heads/master'])


def test_push_options(origin, clone, remote):
    from pygit2 import RemoteCallbacks

    callbacks = RemoteCallbacks()
    remote.push(['refs/heads/master'], callbacks)
    remote_push_options = callbacks.push_options.remote_push_options
    assert remote_push_options.count == 0

    callbacks = RemoteCallbacks()
    remote.push(['refs/heads/master'], callbacks, push_options=[])
    remote_push_options = callbacks.push_options.remote_push_options
    assert remote_push_options.count == 0

    callbacks = RemoteCallbacks()
    # Local remotes don't support push_options, so pushing will raise an error.
    # However, push_options should still be set in RemoteCallbacks.
    with pytest.raises(pygit2.GitError, match='push-options not supported by remote'):
        remote.push(['refs/heads/master'], callbacks, push_options=['foo'])
    remote_push_options = callbacks.push_options.remote_push_options
    assert remote_push_options.count == 1
    # strings pointed to by remote_push_options.strings[] are already freed

    callbacks = RemoteCallbacks()
    with pytest.raises(pygit2.GitError, match='push-options not supported by remote'):
        remote.push(['refs/heads/master'], callbacks, push_options=['Opt A', 'Opt B'])
    remote_push_options = callbacks.push_options.remote_push_options
    assert remote_push_options.count == 2
    # strings pointed to by remote_push_options.strings[] are already freed


def test_push_threads(origin, clone, remote):
    from pygit2 import RemoteCallbacks

    callbacks = RemoteCallbacks()
    remote.push(['refs/heads/master'], callbacks)
    assert callbacks.push_options.pb_parallelism == 1

    callbacks = RemoteCallbacks()
    remote.push(['refs/heads/master'], callbacks, threads=0)
    assert callbacks.push_options.pb_parallelism == 0

    callbacks = RemoteCallbacks()
    remote.push(['refs/heads/master'], callbacks, threads=1)
    assert callbacks.push_options.pb_parallelism == 1
