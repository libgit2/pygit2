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

"""Tests for branch methods."""

import os

import pytest

import pygit2
from pygit2 import Commit, Repository
from pygit2.enums import BranchType

LAST_COMMIT = '2be5719152d4f82c7302b1c0932d8e5f0a4a0e98'
I18N_LAST_COMMIT = '5470a671a80ac3789f1a6a8cefbcf43ce7af0563'
ORIGIN_MASTER_COMMIT = '784855caf26449a1914d2cf62d12b9374d76ae78'
EXCLUSIVE_MASTER_COMMIT = '5ebeeebb320790caf276b9fc8b24546d63316533'
SHARED_COMMIT = '4ec4389a8068641da2d6578db0419484972284c8'


def test_branches_getitem(testrepo: Repository) -> None:
    branch = testrepo.branches['master']
    assert branch.target == LAST_COMMIT

    branch = testrepo.branches.local['i18n']
    assert branch.target == I18N_LAST_COMMIT
    assert testrepo.branches.get('not-exists') is None
    with pytest.raises(KeyError):
        testrepo.branches['not-exists']


def test_branches(testrepo: Repository) -> None:
    branches = sorted(testrepo.branches)
    assert branches == ['i18n', 'master']


def test_branches_create(testrepo: Repository) -> None:
    commit = testrepo[LAST_COMMIT]
    assert isinstance(commit, Commit)
    reference = testrepo.branches.create('version1', commit)
    assert 'version1' in testrepo.branches
    reference = testrepo.branches['version1']
    assert reference.target == LAST_COMMIT

    # try to create existing reference
    with pytest.raises(ValueError):
        testrepo.branches.create('version1', commit)

    # try to create existing reference with force
    reference = testrepo.branches.create('version1', commit, True)
    assert reference.target == LAST_COMMIT


def test_branches_delete(testrepo: Repository) -> None:
    testrepo.branches.delete('i18n')
    assert testrepo.branches.get('i18n') is None


def test_branches_delete_error(testrepo: Repository) -> None:
    with pytest.raises(pygit2.GitError):
        testrepo.branches.delete('master')


def test_branches_is_head(testrepo: Repository) -> None:
    branch = testrepo.branches.get('master')
    assert branch.is_head()


def test_branches_is_not_head(testrepo: Repository) -> None:
    branch = testrepo.branches.get('i18n')
    assert not branch.is_head()


def test_branches_rename(testrepo: Repository) -> None:
    new_branch = testrepo.branches['i18n'].rename('new-branch')
    assert new_branch.target == I18N_LAST_COMMIT

    new_branch_2 = testrepo.branches.get('new-branch')
    assert new_branch_2.target == I18N_LAST_COMMIT


def test_branches_rename_error(testrepo: Repository) -> None:
    original_branch = testrepo.branches.get('i18n')
    with pytest.raises(ValueError):
        original_branch.rename('master')


def test_branches_rename_force(testrepo: Repository) -> None:
    original_branch = testrepo.branches.get('master')
    new_branch = original_branch.rename('i18n', True)
    assert new_branch.target == LAST_COMMIT


def test_branches_rename_invalid(testrepo: Repository) -> None:
    original_branch = testrepo.branches.get('i18n')
    with pytest.raises(ValueError):
        original_branch.rename('abc@{123')


def test_branches_name(testrepo: Repository) -> None:
    branch = testrepo.branches.get('master')
    assert branch.branch_name == 'master'
    assert branch.name == 'refs/heads/master'
    assert branch.raw_branch_name == branch.branch_name.encode('utf-8')

    branch = testrepo.branches.get('i18n')
    assert branch.branch_name == 'i18n'
    assert branch.name == 'refs/heads/i18n'
    assert branch.raw_branch_name == branch.branch_name.encode('utf-8')


def test_branches_with_commit(testrepo: Repository) -> None:
    branches = testrepo.branches.with_commit(EXCLUSIVE_MASTER_COMMIT)
    assert sorted(branches) == ['master']
    assert branches.get('i18n') is None
    assert branches['master'].branch_name == 'master'

    branches = testrepo.branches.with_commit(SHARED_COMMIT)
    assert sorted(branches) == ['i18n', 'master']

    branches = testrepo.branches.with_commit(LAST_COMMIT)
    assert sorted(branches) == ['master']

    commit = testrepo[LAST_COMMIT]
    assert isinstance(commit, Commit)
    branches = testrepo.branches.with_commit(commit)
    assert sorted(branches) == ['master']

    branches = testrepo.branches.remote.with_commit(LAST_COMMIT)
    assert sorted(branches) == []


#
# Low level API written in C, repo.branches call these.
#


def test_lookup_branch_local(testrepo: Repository) -> None:
    assert testrepo.lookup_branch('master').target == LAST_COMMIT
    assert testrepo.lookup_branch(b'master').target == LAST_COMMIT

    assert testrepo.lookup_branch('i18n', BranchType.LOCAL).target == I18N_LAST_COMMIT
    assert testrepo.lookup_branch(b'i18n', BranchType.LOCAL).target == I18N_LAST_COMMIT

    assert testrepo.lookup_branch('not-exists') is None
    assert testrepo.lookup_branch(b'not-exists') is None
    if os.name == 'posix':  # this call fails with an InvalidSpecError on NT
        assert testrepo.lookup_branch(b'\xb1') is None


def test_listall_branches(testrepo: Repository) -> None:
    branches = sorted(testrepo.listall_branches())
    assert branches == ['i18n', 'master']

    branches_raw = sorted(testrepo.raw_listall_branches())
    assert branches_raw == [b'i18n', b'master']


def test_create_branch(testrepo: Repository) -> None:
    commit = testrepo[LAST_COMMIT]
    assert isinstance(commit, Commit)
    testrepo.create_branch('version1', commit)
    refs = testrepo.listall_branches()
    assert 'version1' in refs
    assert testrepo.lookup_branch('version1').target == LAST_COMMIT
    assert testrepo.lookup_branch(b'version1').target == LAST_COMMIT

    # try to create existing reference
    with pytest.raises(ValueError):
        testrepo.create_branch('version1', commit)

    # try to create existing reference with force
    assert testrepo.create_branch('version1', commit, True).target == LAST_COMMIT


def test_delete(testrepo: Repository) -> None:
    branch = testrepo.lookup_branch('i18n')
    branch.delete()

    assert testrepo.lookup_branch('i18n') is None


def test_cant_delete_master(testrepo: Repository) -> None:
    branch = testrepo.lookup_branch('master')

    with pytest.raises(pygit2.GitError):
        branch.delete()


def test_branch_is_head_returns_true_if_branch_is_head(testrepo: Repository) -> None:
    branch = testrepo.lookup_branch('master')
    assert branch.is_head()


def test_branch_is_head_returns_false_if_branch_is_not_head(
    testrepo: Repository,
) -> None:
    branch = testrepo.lookup_branch('i18n')
    assert not branch.is_head()


def test_branch_is_checked_out_returns_true_if_branch_is_checked_out(
    testrepo: Repository,
) -> None:
    branch = testrepo.lookup_branch('master')
    assert branch.is_checked_out()


def test_branch_is_checked_out_returns_false_if_branch_is_not_checked_out(
    testrepo: Repository,
) -> None:
    branch = testrepo.lookup_branch('i18n')
    assert not branch.is_checked_out()


def test_branch_rename_succeeds(testrepo: Repository) -> None:
    branch = testrepo.lookup_branch('i18n')
    assert branch.rename('new-branch').target == I18N_LAST_COMMIT
    assert testrepo.lookup_branch('new-branch').target == I18N_LAST_COMMIT


def test_branch_rename_fails_if_destination_already_exists(
    testrepo: Repository,
) -> None:
    original_branch = testrepo.lookup_branch('i18n')
    with pytest.raises(ValueError):
        original_branch.rename('master')


def test_branch_rename_not_fails_if_force_is_true(testrepo: Repository) -> None:
    branch = testrepo.lookup_branch('master')
    assert branch.rename('i18n', True).target == LAST_COMMIT


def test_branch_rename_fails_with_invalid_names(testrepo: Repository) -> None:
    original_branch = testrepo.lookup_branch('i18n')
    with pytest.raises(ValueError):
        original_branch.rename('abc@{123')


def test_branch_name(testrepo: Repository) -> None:
    branch = testrepo.lookup_branch('master')
    assert branch.branch_name == 'master'
    assert branch.name == 'refs/heads/master'

    branch = testrepo.lookup_branch('i18n')
    assert branch.branch_name == 'i18n'
    assert branch.name == 'refs/heads/i18n'
