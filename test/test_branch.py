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

"""Tests for branch methods."""

import pygit2
import pytest
import os


LAST_COMMIT = '2be5719152d4f82c7302b1c0932d8e5f0a4a0e98'
I18N_LAST_COMMIT = '5470a671a80ac3789f1a6a8cefbcf43ce7af0563'
ORIGIN_MASTER_COMMIT = '784855caf26449a1914d2cf62d12b9374d76ae78'
EXCLUSIVE_MASTER_COMMIT = '5ebeeebb320790caf276b9fc8b24546d63316533'
SHARED_COMMIT = '4ec4389a8068641da2d6578db0419484972284c8'


def test_branches_getitem(testrepo):
    branch = testrepo.branches['master']
    assert branch.target.hex == LAST_COMMIT

    branch = testrepo.branches.local['i18n']
    assert branch.target.hex == I18N_LAST_COMMIT
    assert testrepo.branches.get('not-exists') is None
    with pytest.raises(KeyError):
        testrepo.branches['not-exists']

def test_branches(testrepo):
    branches = sorted(testrepo.branches)
    assert branches == ['i18n', 'master']

def test_branches_create(testrepo):
    commit = testrepo[LAST_COMMIT]
    reference = testrepo.branches.create('version1', commit)
    assert 'version1' in testrepo.branches
    reference = testrepo.branches['version1']
    assert reference.target.hex == LAST_COMMIT

    # try to create existing reference
    with pytest.raises(ValueError):
        testrepo.branches.create('version1', commit)

    # try to create existing reference with force
    reference = testrepo.branches.create('version1', commit, True)
    assert reference.target.hex == LAST_COMMIT

def test_branches_delete(testrepo):
    testrepo.branches.delete('i18n')
    assert testrepo.branches.get('i18n') is None

def test_branches_delete_error(testrepo):
    with pytest.raises(pygit2.GitError):
        testrepo.branches.delete('master')

def test_branches_is_head(testrepo):
    branch = testrepo.branches.get('master')
    assert branch.is_head()

def test_branches_is_not_head(testrepo):
    branch = testrepo.branches.get('i18n')
    assert not branch.is_head()

def test_branches_rename(testrepo):
    new_branch = testrepo.branches['i18n'].rename('new-branch')
    assert new_branch.target.hex == I18N_LAST_COMMIT

    new_branch_2 = testrepo.branches.get('new-branch')
    assert new_branch_2.target.hex == I18N_LAST_COMMIT

def test_branches_rename_error(testrepo):
    original_branch = testrepo.branches.get('i18n')
    with pytest.raises(ValueError): original_branch.rename('master')

def test_branches_rename_force(testrepo):
    original_branch = testrepo.branches.get('master')
    new_branch = original_branch.rename('i18n', True)
    assert new_branch.target.hex == LAST_COMMIT

def test_branches_rename_invalid(testrepo):
    original_branch = testrepo.branches.get('i18n')
    with pytest.raises(ValueError):
        original_branch.rename('abc@{123')

def test_branches_name(testrepo):
    branch = testrepo.branches.get('master')
    assert branch.branch_name == 'master'
    assert branch.name == 'refs/heads/master'
    assert branch.raw_branch_name == branch.branch_name.encode('utf-8')

    branch = testrepo.branches.get('i18n')
    assert branch.branch_name == 'i18n'
    assert branch.name == 'refs/heads/i18n'
    assert branch.raw_branch_name == branch.branch_name.encode('utf-8')

def test_branches_with_commit(testrepo):
    branches = testrepo.branches.with_commit(EXCLUSIVE_MASTER_COMMIT)
    assert sorted(branches) == ['master']
    assert branches.get('i18n') is None
    assert branches['master'].branch_name == 'master'

    branches = testrepo.branches.with_commit(SHARED_COMMIT)
    assert sorted(branches) == ['i18n', 'master']

    branches = testrepo.branches.with_commit(LAST_COMMIT)
    assert sorted(branches) == ['master']

    branches = testrepo.branches.with_commit(testrepo[LAST_COMMIT])
    assert sorted(branches) == ['master']

    branches = testrepo.branches.remote.with_commit(LAST_COMMIT)
    assert sorted(branches) == []


#
# Low level API written in C, repo.branches call these.
#

def test_lookup_branch_local(testrepo):
    branch = testrepo.lookup_branch('master')
    assert branch.target.hex == LAST_COMMIT
    branch = testrepo.lookup_branch(b'master')
    assert branch.target.hex == LAST_COMMIT

    branch = testrepo.lookup_branch('i18n', pygit2.GIT_BRANCH_LOCAL)
    assert branch.target.hex == I18N_LAST_COMMIT
    branch = testrepo.lookup_branch(b'i18n', pygit2.GIT_BRANCH_LOCAL)
    assert branch.target.hex == I18N_LAST_COMMIT

    assert testrepo.lookup_branch('not-exists') is None
    assert testrepo.lookup_branch(b'not-exists') is None
    if os.name == 'posix':  # this call fails with an InvalidSpecError on NT
        assert testrepo.lookup_branch(b'\xb1') is None

def test_listall_branches(testrepo):
    branches = sorted(testrepo.listall_branches())
    assert branches == ['i18n', 'master']

    branches = sorted(testrepo.raw_listall_branches())
    assert branches == [b'i18n', b'master']

def test_create_branch(testrepo):
    commit = testrepo[LAST_COMMIT]
    reference = testrepo.create_branch('version1', commit)
    refs = testrepo.listall_branches()
    assert 'version1' in refs
    reference = testrepo.lookup_branch('version1')
    assert reference.target.hex == LAST_COMMIT
    reference = testrepo.lookup_branch(b'version1')
    assert reference.target.hex == LAST_COMMIT

    # try to create existing reference
    with pytest.raises(ValueError):
        testrepo.create_branch('version1', commit)

    # try to create existing reference with force
    reference = testrepo.create_branch('version1', commit, True)
    assert reference.target.hex == LAST_COMMIT

def test_delete(testrepo):
    branch = testrepo.lookup_branch('i18n')
    branch.delete()

    assert testrepo.lookup_branch('i18n') is None

def test_cant_delete_master(testrepo):
    branch = testrepo.lookup_branch('master')

    with pytest.raises(pygit2.GitError): branch.delete()

def test_branch_is_head_returns_true_if_branch_is_head(testrepo):
    branch = testrepo.lookup_branch('master')
    assert branch.is_head()

def test_branch_is_head_returns_false_if_branch_is_not_head(testrepo):
    branch = testrepo.lookup_branch('i18n')
    assert not branch.is_head()

def test_branch_is_checked_out_returns_true_if_branch_is_checked_out(testrepo):
    branch = testrepo.lookup_branch('master')
    assert branch.is_checked_out()

def test_branch_is_checked_out_returns_false_if_branch_is_not_checked_out(testrepo):
    branch = testrepo.lookup_branch('i18n')
    assert not branch.is_checked_out()

def test_branch_rename_succeeds(testrepo):
    original_branch = testrepo.lookup_branch('i18n')
    new_branch = original_branch.rename('new-branch')
    assert new_branch.target.hex == I18N_LAST_COMMIT

    new_branch_2 = testrepo.lookup_branch('new-branch')
    assert new_branch_2.target.hex == I18N_LAST_COMMIT

def test_branch_rename_fails_if_destination_already_exists(testrepo):
    original_branch = testrepo.lookup_branch('i18n')
    with pytest.raises(ValueError): original_branch.rename('master')

def test_branch_rename_not_fails_if_force_is_true(testrepo):
    original_branch = testrepo.lookup_branch('master')
    new_branch = original_branch.rename('i18n', True)
    assert new_branch.target.hex == LAST_COMMIT

def test_branch_rename_fails_with_invalid_names(testrepo):
    original_branch = testrepo.lookup_branch('i18n')
    with pytest.raises(ValueError):
        original_branch.rename('abc@{123')

def test_branch_name(testrepo):
    branch = testrepo.lookup_branch('master')
    assert branch.branch_name == 'master'
    assert branch.name == 'refs/heads/master'

    branch = testrepo.lookup_branch('i18n')
    assert branch.branch_name == 'i18n'
    assert branch.name == 'refs/heads/i18n'
