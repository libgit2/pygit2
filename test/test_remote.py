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

import sys
from collections.abc import Generator
from pathlib import Path

import pytest

import pygit2
from pygit2 import Remote, Repository
from pygit2.remotes import PushUpdate, TransferProgress

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


def test_remote_create(testrepo: Repository) -> None:
    name = 'upstream'
    url = 'https://github.com/libgit2/pygit2.git'

    remote = testrepo.remotes.create(name, url)

    assert type(remote) is pygit2.Remote
    assert name == remote.name
    assert url == remote.url
    assert remote.push_url is None

    with pytest.raises(ValueError):
        testrepo.remotes.create(*(name, url))


def test_remote_create_with_refspec(testrepo: Repository) -> None:
    name = 'upstream'
    url = 'https://github.com/libgit2/pygit2.git'
    fetch = '+refs/*:refs/*'

    remote = testrepo.remotes.create(name, url, fetch)

    assert type(remote) is pygit2.Remote
    assert name == remote.name
    assert url == remote.url
    assert [fetch] == remote.fetch_refspecs
    assert remote.push_url is None


def test_remote_create_anonymous(testrepo: Repository) -> None:
    url = 'https://github.com/libgit2/pygit2.git'

    remote = testrepo.remotes.create_anonymous(url)
    assert remote.name is None
    assert url == remote.url
    assert remote.push_url is None
    assert [] == remote.fetch_refspecs
    assert [] == remote.push_refspecs


def test_remote_delete(testrepo: Repository) -> None:
    name = 'upstream'
    url = 'https://github.com/libgit2/pygit2.git'

    testrepo.remotes.create(name, url)
    assert 2 == len(testrepo.remotes)
    remote = testrepo.remotes[1]

    assert name == remote.name
    testrepo.remotes.delete(remote.name)
    assert 1 == len(testrepo.remotes)


def test_remote_rename(testrepo: Repository) -> None:
    remote = testrepo.remotes[0]

    assert REMOTE_NAME == remote.name
    problems = testrepo.remotes.rename(remote.name, 'new')
    assert [] == problems
    assert 'new' != remote.name

    with pytest.raises(ValueError):
        testrepo.remotes.rename('', '')
    with pytest.raises(ValueError):
        testrepo.remotes.rename(None, None)  # type: ignore


def test_remote_set_url(testrepo: Repository) -> None:
    remote = testrepo.remotes['origin']
    assert REMOTE_URL == remote.url

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


def test_refspec(testrepo: Repository) -> None:
    remote = testrepo.remotes['origin']

    assert remote.refspec_count == 1
    refspec = remote.get_refspec(0)
    assert refspec.src == REMOTE_FETCHSPEC_SRC
    assert refspec.dst == REMOTE_FETCHSPEC_DST
    assert refspec.force is True
    assert ORIGIN_REFSPEC == refspec.string

    assert list is type(remote.fetch_refspecs)
    assert 1 == len(remote.fetch_refspecs)
    assert ORIGIN_REFSPEC == remote.fetch_refspecs[0]

    assert refspec.src_matches('refs/heads/master')
    assert refspec.dst_matches('refs/remotes/origin/master')
    assert 'refs/remotes/origin/master' == refspec.transform('refs/heads/master')
    assert 'refs/heads/master' == refspec.rtransform('refs/remotes/origin/master')

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
    ] == fetch_specs

    testrepo.remotes.add_push('origin', '+refs/test/*:refs/test/remotes/*')

    with pytest.raises(TypeError):
        testrepo.remotes.add_fetch(['+refs/*:refs/*', 5])  # type: ignore

    remote = testrepo.remotes['origin']
    assert ['+refs/test/*:refs/test/remotes/*'] == remote.push_refspecs


def test_remote_list(testrepo: Repository) -> None:
    assert 1 == len(testrepo.remotes)
    remote = testrepo.remotes[0]
    assert REMOTE_NAME == remote.name
    assert REMOTE_URL == remote.url

    name = 'upstream'
    url = 'https://github.com/libgit2/pygit2.git'
    remote = testrepo.remotes.create(name, url)
    assert remote.name in testrepo.remotes.names()
    assert remote.name in [x.name for x in testrepo.remotes]


@utils.requires_network
def test_list_heads(testrepo: Repository) -> None:
    assert 1 == len(testrepo.remotes)
    remote = testrepo.remotes[0]

    refs = remote.list_heads()
    assert refs

    # Check that a known ref is returned.
    assert next(iter(r for r in refs if r.name == 'refs/tags/v0.28.2'))


@utils.requires_network
def test_ls_remotes_deprecated(testrepo: Repository) -> None:
    assert 1 == len(testrepo.remotes)
    remote = testrepo.remotes[0]

    new_refs = remote.list_heads()

    with pytest.warns(DeprecationWarning, match='Use list_heads'):
        old_refs = remote.ls_remotes()

    assert new_refs
    assert old_refs

    for new, old in zip(new_refs, old_refs, strict=True):
        assert new.name == old['name']
        assert new.oid == old['oid']
        assert new.local == old['local']
        assert new.symref_target == old['symref_target']
        if new.local:
            assert new.loid == old['loid']
        else:
            assert new.loid == pygit2.Oid(b'')
            assert old['loid'] is None


@utils.requires_network
def test_list_heads_without_implicit_connect(testrepo: Repository) -> None:
    assert 1 == len(testrepo.remotes)
    remote = testrepo.remotes[0]

    with pytest.raises(pygit2.GitError, match='this remote has never connected'):
        remote.list_heads(connect=False)

    remote.connect()
    refs = remote.list_heads(connect=False)
    assert refs

    # Check that a known ref is returned.
    assert next(iter(r for r in refs if r.name == 'refs/tags/v0.28.2'))


def test_remote_collection(testrepo: Repository) -> None:
    remote = testrepo.remotes['origin']
    assert REMOTE_NAME == remote.name
    assert REMOTE_URL == remote.url

    with pytest.raises(KeyError):
        testrepo.remotes['upstream']

    name = 'upstream'
    url = 'https://github.com/libgit2/pygit2.git'
    remote = testrepo.remotes.create(name, url)
    assert remote.name in testrepo.remotes.names()
    assert remote.name in [x.name for x in testrepo.remotes]


@utils.requires_refcount
def test_remote_refcount(testrepo: Repository) -> None:
    start = sys.getrefcount(testrepo)
    remote = testrepo.remotes[0]
    del remote
    end = sys.getrefcount(testrepo)
    assert start == end


def test_fetch(emptyrepo: Repository) -> None:
    remote = emptyrepo.remotes[0]
    stats = remote.fetch()
    assert stats.received_bytes > 2700
    assert stats.received_bytes < 3100
    assert stats.indexed_objects == REMOTE_REPO_OBJECTS
    assert stats.received_objects == REMOTE_REPO_OBJECTS


@utils.requires_network
def test_fetch_depth_zero(testrepo: Repository) -> None:
    remote = testrepo.remotes[0]
    stats = remote.fetch(REMOTE_FETCHTEST_FETCHSPECS, depth=0)
    assert stats.indexed_objects == REMOTE_REPO_FETCH_ALL_OBJECTS
    assert stats.received_objects == REMOTE_REPO_FETCH_ALL_OBJECTS


@utils.requires_network
def test_fetch_depth_one(testrepo: Repository) -> None:
    remote = testrepo.remotes[0]
    stats = remote.fetch(REMOTE_FETCHTEST_FETCHSPECS, depth=1)
    assert stats.indexed_objects == REMOTE_REPO_FETCH_HEAD_COMMIT_OBJECTS
    assert stats.received_objects == REMOTE_REPO_FETCH_HEAD_COMMIT_OBJECTS


def test_transfer_progress(emptyrepo: Repository) -> None:
    class MyCallbacks(pygit2.RemoteCallbacks):
        def transfer_progress(self, stats: TransferProgress) -> None:
            self.tp = stats

    callbacks = MyCallbacks()
    remote = emptyrepo.remotes[0]
    stats = remote.fetch(callbacks=callbacks)
    assert stats.received_bytes == callbacks.tp.received_bytes
    assert stats.indexed_objects == callbacks.tp.indexed_objects
    assert stats.received_objects == callbacks.tp.received_objects


def test_update_tips(emptyrepo: Repository) -> None:
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
        tips: list[tuple[str, pygit2.Oid, pygit2.Oid]]

        def __init__(self, tips: list[tuple[str, pygit2.Oid, pygit2.Oid]]) -> None:
            self.tips = tips
            self.i = 0

        def update_tips(self, name: str, old: pygit2.Oid, new: pygit2.Oid) -> None:
            assert self.tips[self.i] == (name, old, new)
            self.i += 1

    callbacks = MyCallbacks(tips)
    remote.fetch(callbacks=callbacks)
    assert callbacks.i > 0


@utils.requires_network
def test_list_heads_certificate_check() -> None:
    url = 'https://github.com/pygit2/empty.git'

    class MyCallbacks(pygit2.RemoteCallbacks):
        def __init__(self) -> None:
            self.i = 0

        def certificate_check(
            self, certificate: None, valid: bool, host: str | bytes
        ) -> bool:
            self.i += 1

            assert certificate is None
            assert valid is True
            assert host == b'github.com'
            return True

    # We create an in-memory repository
    git = pygit2.Repository()
    remote = git.remotes.create_anonymous(url)

    callbacks = MyCallbacks()
    refs = remote.list_heads(callbacks=callbacks)

    # Sanity check that we indeed got some refs.
    assert len(refs) > 0

    # Make sure our certificate_check callback triggered.
    assert callbacks.i > 0


@pytest.fixture
def origin(tmp_path: Path) -> Generator[Repository, None, None]:
    with utils.TemporaryRepository('barerepo.zip', tmp_path) as path:
        yield pygit2.Repository(path)


@pytest.fixture
def clone(tmp_path: Path) -> Generator[Repository, None, None]:
    clone = tmp_path / 'clone'
    clone.mkdir()
    with utils.TemporaryRepository('barerepo.zip', clone) as path:
        yield pygit2.Repository(path)


@pytest.fixture
def remote(origin: Repository, clone: Repository) -> Generator[Remote, None, None]:
    yield clone.remotes.create('origin', origin.path)


def test_push_fast_forward_commits_to_remote_succeeds(
    origin: Repository, clone: Repository, remote: Remote
) -> None:
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


def test_push_when_up_to_date_succeeds(
    origin: Repository, clone: Repository, remote: Remote
) -> None:
    remote.push(['refs/heads/master'])
    origin_tip = origin[origin.head.target].id
    clone_tip = clone[clone.head.target].id
    assert origin_tip == clone_tip


def test_push_transfer_progress(
    origin: Repository, clone: Repository, remote: Remote
) -> None:
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
        def push_transfer_progress(
            self, objects_pushed: int, total_objects: int, bytes_pushed: int
        ) -> None:
            self.objects_pushed = objects_pushed
            self.total_objects = total_objects

    assert origin.branches['master'].target == tip.id

    callbacks = MyCallbacks()
    remote.push(['refs/heads/master'], callbacks=callbacks)
    assert callbacks.objects_pushed == 1
    assert callbacks.total_objects == 1
    assert origin.branches['master'].target == new_tip_id


@pytest.mark.parametrize('reject_from', ['push_transfer_progress', 'push_negotiation'])
def test_push_interrupted_from_callbacks(
    origin: Repository, clone: Repository, remote: Remote, reject_from: str
) -> None:
    reject_message = 'retreat! retreat!'

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
        def push_negotiation(self, updates: list[PushUpdate]) -> None:
            if reject_from == 'push_negotiation':
                raise InterruptedError(reject_message)

        def push_transfer_progress(
            self, objects_pushed: int, total_objects: int, bytes_pushed: int
        ) -> None:
            if reject_from == 'push_transfer_progress':
                raise InterruptedError(reject_message)

    assert origin.branches['master'].target == tip.id

    callbacks = MyCallbacks()
    with pytest.raises(InterruptedError, match='retreat! retreat!'):
        remote.push(['refs/heads/master'], callbacks=callbacks)

    assert origin.branches['master'].target == tip.id


def test_push_non_fast_forward_commits_to_remote_fails(
    origin: Repository, clone: Repository, remote: Remote
) -> None:
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


def test_push_options(origin: Repository, clone: Repository, remote: Remote) -> None:
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


def test_push_threads(origin: Repository, clone: Repository, remote: Remote) -> None:
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


def test_push_negotiation(
    origin: Repository, clone: Repository, remote: Remote
) -> None:
    old_tip = clone[clone.head.target]
    new_tip_id = clone.create_commit(
        'refs/heads/master',
        old_tip.author,
        old_tip.author,
        'empty commit',
        old_tip.tree.id,
        [old_tip.id],
    )

    the_updates: list[PushUpdate] = []

    class MyCallbacks(pygit2.RemoteCallbacks):
        def push_negotiation(self, updates: list[PushUpdate]) -> None:
            the_updates.extend(updates)

    assert origin.branches['master'].target == old_tip.id
    assert 'new_branch' not in origin.branches

    callbacks = MyCallbacks()
    remote.push(['refs/heads/master'], callbacks=callbacks)

    assert len(the_updates) == 1
    assert the_updates[0].src_refname == 'refs/heads/master'
    assert the_updates[0].dst_refname == 'refs/heads/master'
    assert the_updates[0].src == old_tip.id
    assert the_updates[0].dst == new_tip_id

    assert origin.branches['master'].target == new_tip_id
