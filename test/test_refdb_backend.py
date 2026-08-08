# Copyright 2010-2026 The pygit2 contributors
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

"""Tests for Refdb objects."""

import sys
from collections.abc import Generator, Iterator
from pathlib import Path

import pytest

import pygit2
from pygit2 import Commit, Oid, Reference, Repository, Signature

from . import utils


# Note: the refdb abstraction from libgit2 is meant to provide information
# which libgit2 transforms into something more useful, and in general YMMV by
# using the backend directly. So some of these tests are a bit vague or
# incomplete, to avoid hitting the semi-valid states that refdbs produce by
# design.
class ProxyRefdbBackend(pygit2.RefdbBackend):
    def __init__(self, source: pygit2.RefdbBackend) -> None:
        super().__init__()
        self.source = source

    def __iter__(self) -> 'ProxyRefdbBackend':
        return self

    def __next__(self) -> Reference:
        raise StopIteration

    def exists(self, ref: str) -> bool:
        return self.source.exists(ref)

    def lookup(self, ref: str) -> Reference:
        return self.source.lookup(ref)

    def write(
        self,
        ref: Reference,
        force: bool,
        who: Signature,
        message: str,
        old: None | str | Oid,
        old_target: None | str,
    ) -> None:
        return self.source.write(ref, force, who, message, old, old_target)

    def rename(
        self,
        old_name: str,
        new_name: str,
        force: bool,
        who: Signature,
        message: str | None,
    ) -> Reference:
        return self.source.rename(old_name, new_name, force, who, message)

    def delete(self, ref_name: str, old_id: Oid | str, old_target: str | None) -> None:
        return self.source.delete(ref_name, old_id, old_target)

    def compress(self) -> None:
        return self.source.compress()

    def has_log(self, ref_name: str) -> bool:
        return self.source.has_log(ref_name)

    def ensure_log(self, ref_name: str) -> bool:
        return self.source.ensure_log(ref_name)


@pytest.fixture
def repo(testrepo: Repository) -> Generator[Repository, None, None]:
    testrepo.backend = ProxyRefdbBackend(pygit2.RefdbFsBackend(testrepo))
    yield testrepo


class CachedRefdbBackend(ProxyRefdbBackend):
    """A backend that caches and reuses the Reference objects it returns."""

    def __init__(self, source: pygit2.RefdbBackend) -> None:
        super().__init__(source)
        self.cache: dict[str, Reference] = {}

    def lookup(self, ref: str) -> Reference:
        if ref not in self.cache:
            self.cache[ref] = self.source.lookup(ref)
        return self.cache[ref]


class IterRefdbBackend(ProxyRefdbBackend):
    """A backend whose iterator yields cached Reference objects."""

    def __init__(self, source: pygit2.RefdbBackend) -> None:
        super().__init__(source)
        self.cache: list[Reference] | None = None
        self.refs: Iterator[Reference] = iter([])

    def __iter__(self) -> 'IterRefdbBackend':
        if self.cache is None:
            self.cache = [
                self.source.lookup('refs/heads/master'),
                self.source.lookup('refs/heads/i18n'),
                Reference('refs/heads/symbolic', 'refs/heads/master'),
            ]
        self.refs = iter(self.cache)
        return self

    def __next__(self) -> Reference:
        return next(self.refs)


def test_exists(repo: Repository) -> None:
    assert not repo.backend.exists('refs/heads/does-not-exist')
    assert repo.backend.exists('refs/heads/master')


class RaisingRefdbBackend(ProxyRefdbBackend):
    """A backend whose exists callback always raises."""

    def exists(self, ref: str) -> bool:
        raise RuntimeError('boom')


def test_exists_callback_raises(testrepo: Repository) -> None:
    # Regression test (issue #1476): when the exists callback raises, the C
    # wrapper must not crash on a NULL result, and must propagate the error.
    backend = RaisingRefdbBackend(pygit2.RefdbFsBackend(testrepo))
    # Call the unbound C method so the call goes through the C wrapper
    # (pygit2_refdb_backend_exists), not directly to the Python override.
    # The error propagates as GitError, or as OSError/ValueError when a stale
    # libgit2 error (with a matching class) is left over from an earlier call.
    with pytest.raises((pygit2.GitError, OSError)):
        pygit2.RefdbBackend.exists(backend, 'refs/heads/master')


def test_lookup(repo: Repository) -> None:
    assert repo.backend.lookup('refs/heads/does-not-exist') is None
    assert repo.backend.lookup('refs/heads/master').name == 'refs/heads/master'


def test_lookup_cached_callback(testrepo: Repository) -> None:
    # Regression test: a backend may cache and return the same Reference
    # object on every lookup; the callback must not invalidate it, and
    # repeated lookups through libgit2 must keep working.
    backend = CachedRefdbBackend(pygit2.RefdbFsBackend(testrepo))
    refdb = pygit2.Refdb.new(testrepo)
    refdb.set_backend(backend)
    testrepo.set_refdb(refdb)

    target = testrepo.references['refs/heads/master'].target
    assert testrepo.references['refs/heads/master'].target == target
    assert backend.cache['refs/heads/master'].name == 'refs/heads/master'


def test_iterator_callback(testrepo: Repository) -> None:
    # Exercise the custom backend's iterator callback through libgit2's
    # git_reference_iterator; the Python attribute alone doesn't install it.
    backend = IterRefdbBackend(pygit2.RefdbFsBackend(testrepo))
    refdb = pygit2.Refdb.new(testrepo)
    refdb.set_backend(backend)
    testrepo.set_refdb(refdb)

    names = sorted(ref.name for ref in testrepo.references.iterator())
    assert names == ['refs/heads/i18n', 'refs/heads/master', 'refs/heads/symbolic']

    # The backend's cached objects must still be usable after iteration.
    assert backend.cache is not None
    assert [ref.name for ref in backend.cache] == [
        'refs/heads/master',
        'refs/heads/i18n',
        'refs/heads/symbolic',
    ]


@utils.requires_refcount
def test_iterator_callback_no_leak(testrepo: Repository) -> None:
    # Iterating must not leak the Reference objects the backend yields.
    backend = IterRefdbBackend(pygit2.RefdbFsBackend(testrepo))
    refdb = pygit2.Refdb.new(testrepo)
    refdb.set_backend(backend)
    testrepo.set_refdb(refdb)

    list(testrepo.references.iterator())
    assert backend.cache is not None
    refcount = sys.getrefcount(backend.cache[0])
    list(testrepo.references.iterator())
    # Keep the getrefcount call out of the assert: pytest's assertion
    # rewriting holds the subscript result in a frame temporary, which
    # inflates the refcount on some Python versions (e.g. 3.11).
    new_refcount = sys.getrefcount(backend.cache[0])
    assert new_refcount == refcount


def test_write(repo: Repository) -> None:
    master = repo.backend.lookup('refs/heads/master')
    commit = repo[master.target]
    ref = pygit2.Reference('refs/heads/test-write', master.target, None)
    repo.backend.write(ref, False, commit.author, 'Create test-write', None, None)
    assert repo.backend.lookup('refs/heads/test-write').target == master.target


def test_rename(repo: Repository) -> None:
    old_ref = repo.backend.lookup('refs/heads/i18n')
    target = repo.get(old_ref.target)
    assert isinstance(target, Commit)
    repo.backend.rename(
        'refs/heads/i18n', 'refs/heads/intl', False, target.committer, target.message
    )
    assert repo.backend.lookup('refs/heads/intl').target == target.id


def test_rename_callback(repo: Repository) -> None:
    # Exercise the custom backend's rename callback through libgit2's
    # git_reference_rename; calling repo.backend.rename() directly bypasses it.
    refdb = pygit2.Refdb.new(repo)
    refdb.set_backend(repo.backend)
    repo.set_refdb(refdb)
    ref = repo.references['refs/heads/i18n']
    target = ref.target
    ref.rename('refs/heads/intl')
    assert repo.references['refs/heads/intl'].target == target


def test_write_callback(repo: Repository) -> None:
    # Exercise the custom backend's write callback through libgit2's
    # git_reference_set_target; calling repo.backend.write() directly
    # bypasses it.
    refdb = pygit2.Refdb.new(repo)
    refdb.set_backend(repo.backend)
    repo.set_refdb(refdb)
    master = repo.references['refs/heads/master']
    i18n = repo.references['refs/heads/i18n']
    i18n.set_target(master.target)
    assert repo.references['refs/heads/i18n'].target == master.target


def test_write_callback_create(repo: Repository) -> None:
    # Exercise the custom backend's write callback through libgit2's
    # git_reference_create, which passes old=NULL for new references.
    refdb = pygit2.Refdb.new(repo)
    refdb.set_backend(repo.backend)
    repo.set_refdb(refdb)
    master = repo.references['refs/heads/master']
    repo.references.create('refs/heads/test-write', master.target)
    assert repo.references['refs/heads/test-write'].target == master.target


def test_delete(repo: Repository) -> None:
    old = repo.backend.lookup('refs/heads/i18n')
    repo.backend.delete('refs/heads/i18n', old.target, None)
    assert not repo.backend.lookup('refs/heads/i18n')


def test_compress(repo: Repository) -> None:
    repo = repo
    packed_refs_file = Path(repo.path) / 'packed-refs'
    assert not packed_refs_file.exists()
    repo.backend.compress()
    assert packed_refs_file.exists()


def test_has_log(repo: Repository) -> None:
    assert repo.backend.has_log('refs/heads/master')
    assert not repo.backend.has_log('refs/heads/does-not-exist')


def test_ensure_log(repo: Repository) -> None:
    assert not repo.backend.has_log('refs/heads/new-log')
    repo.backend.ensure_log('refs/heads/new-log')
    assert repo.backend.has_log('refs/heads/new-log')
