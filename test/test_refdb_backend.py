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

"""Tests for Refdb objects."""

from collections.abc import Generator, Iterator
from pathlib import Path

import pytest

import pygit2
from pygit2 import Commit, Oid, Reference, Repository, Signature


# Note: the refdb abstraction from libgit2 is meant to provide information
# which libgit2 transforms into something more useful, and in general YMMV by
# using the backend directly. So some of these tests are a bit vague or
# incomplete, to avoid hitting the semi-valid states that refdbs produce by
# design.
class ProxyRefdbBackend(pygit2.RefdbBackend):
    def __init__(self, source: pygit2.RefdbBackend) -> None:
        self.source = source

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
        self, old_name: str, new_name: str, force: bool, who: Signature, message: str
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

    def __iter__(self) -> Iterator[Reference]:
        return iter(self.source)


@pytest.fixture
def repo(testrepo: Repository) -> Generator[Repository, None, None]:
    testrepo.backend = ProxyRefdbBackend(pygit2.RefdbFsBackend(testrepo))
    yield testrepo


def test_exists(repo: Repository) -> None:
    assert not repo.backend.exists('refs/heads/does-not-exist')
    assert repo.backend.exists('refs/heads/master')


def test_lookup(repo: Repository) -> None:
    assert repo.backend.lookup('refs/heads/does-not-exist') is None
    assert repo.backend.lookup('refs/heads/master').name == 'refs/heads/master'


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
