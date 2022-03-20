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

"""Tests for Refdb objects."""

from pathlib import Path

import pygit2
import pytest


# Note: the refdb abstraction from libgit2 is meant to provide information
# which libgit2 transforms into something more useful, and in general YMMV by
# using the backend directly. So some of these tests are a bit vague or
# incomplete, to avoid hitting the semi-valid states that refdbs produce by
# design.
class ProxyRefdbBackend(pygit2.RefdbBackend):
    def __init__(testrepo, source):
        testrepo.source = source

    def exists(testrepo, ref):
        return testrepo.source.exists(ref)

    def lookup(testrepo, ref):
        return testrepo.source.lookup(ref)

    def write(testrepo, ref, force, who, message, old, old_target):
        return testrepo.source.write(ref, force, who, message, old, old_target)

    def rename(testrepo, old_name, new_name, force, who, message):
        return testrepo.source.rename(old_name, new_name, force, who, message)

    def delete(testrepo, ref_name, old_id, old_target):
        return testrepo.source.delete(ref_name, old_id, old_target)

    def compress(testrepo):
        return testrepo.source.compress()

    def has_log(testrepo, ref_name):
        return testrepo.source.has_log(ref_name)

    def ensure_log(testrepo, ref_name):
        return testrepo.source.ensure_log(ref_name)

    def __iter__(testrepo):
        return iter(testrepo.source)


@pytest.fixture
def repo(testrepo):
    testrepo.backend = ProxyRefdbBackend(pygit2.RefdbFsBackend(testrepo))
    yield testrepo


def test_exists(repo):
    assert not repo.backend.exists('refs/heads/does-not-exist')
    assert repo.backend.exists('refs/heads/master')

def test_lookup(repo):
    assert repo.backend.lookup('refs/heads/does-not-exist') is None
    assert repo.backend.lookup('refs/heads/master').name == 'refs/heads/master'

def test_write(repo):
    master = repo.backend.lookup('refs/heads/master')
    commit = repo.get(master.target)
    ref = pygit2.Reference("refs/heads/test-write", master.target, None)
    repo.backend.write(ref, False, commit.author,
            "Create test-write", None, None)
    assert repo.backend.lookup("refs/heads/test-write").target == master.target

def test_rename(repo):
    old_ref = repo.backend.lookup('refs/heads/i18n')
    target = repo.get(old_ref.target)
    repo.backend.rename('refs/heads/i18n', 'refs/heads/intl',
            False, target.committer, target.message)
    assert repo.backend.lookup('refs/heads/intl').target == target.id

def test_delete(repo):
    old = repo.backend.lookup('refs/heads/i18n')
    repo.backend.delete('refs/heads/i18n', old.target, None)
    assert not repo.backend.lookup('refs/heads/i18n')

def test_compress(repo):
    repo = repo
    packed_refs_file = Path(repo.path) / 'packed-refs'
    assert not packed_refs_file.exists()
    repo.backend.compress()
    assert packed_refs_file.exists()

def test_has_log(repo):
    assert repo.backend.has_log('refs/heads/master')
    assert not repo.backend.has_log('refs/heads/does-not-exist')

def test_ensure_log(repo):
    assert not repo.backend.has_log('refs/heads/new-log')
    repo.backend.ensure_log('refs/heads/new-log')
    assert repo.backend.has_log('refs/heads/new-log')
