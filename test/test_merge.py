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

"""Tests for merging and information about it."""

from pathlib import Path

import pytest

from pygit2 import GIT_MERGE_ANALYSIS_UP_TO_DATE
from pygit2 import GIT_MERGE_ANALYSIS_FASTFORWARD
import pygit2


def test_merge_none(mergerepo):
    with pytest.raises(TypeError): mergerepo.merge(None)

def test_merge_analysis_uptodate(mergerepo):
    branch_head_hex = '5ebeeebb320790caf276b9fc8b24546d63316533'
    branch_id = mergerepo.get(branch_head_hex).id

    analysis, preference = mergerepo.merge_analysis(branch_id)
    assert analysis & GIT_MERGE_ANALYSIS_UP_TO_DATE
    assert not analysis & GIT_MERGE_ANALYSIS_FASTFORWARD
    assert {} == mergerepo.status()

    analysis, preference = mergerepo.merge_analysis(branch_id, 'refs/heads/ff-branch')
    assert analysis & GIT_MERGE_ANALYSIS_UP_TO_DATE
    assert not analysis & GIT_MERGE_ANALYSIS_FASTFORWARD
    assert {} == mergerepo.status()

def test_merge_analysis_fastforward(mergerepo):
    branch_head_hex = 'e97b4cfd5db0fb4ebabf4f203979ca4e5d1c7c87'
    branch_id = mergerepo.get(branch_head_hex).id

    analysis, preference = mergerepo.merge_analysis(branch_id)
    assert not analysis & GIT_MERGE_ANALYSIS_UP_TO_DATE
    assert analysis & GIT_MERGE_ANALYSIS_FASTFORWARD
    assert {} == mergerepo.status()

    analysis, preference = mergerepo.merge_analysis(branch_id, 'refs/heads/master')
    assert not analysis & GIT_MERGE_ANALYSIS_UP_TO_DATE
    assert analysis & GIT_MERGE_ANALYSIS_FASTFORWARD
    assert {} == mergerepo.status()

def test_merge_no_fastforward_no_conflicts(mergerepo):
    branch_head_hex = '03490f16b15a09913edb3a067a3dc67fbb8d41f1'
    branch_id = mergerepo.get(branch_head_hex).id
    analysis, preference = mergerepo.merge_analysis(branch_id)
    assert not analysis & GIT_MERGE_ANALYSIS_UP_TO_DATE
    assert not analysis & GIT_MERGE_ANALYSIS_FASTFORWARD
    # Asking twice to assure the reference counting is correct
    assert {} == mergerepo.status()
    assert {} == mergerepo.status()

def test_merge_invalid_hex(mergerepo):
    branch_head_hex = '12345678'
    with pytest.raises(KeyError): mergerepo.merge(branch_head_hex)

def test_merge_already_something_in_index(mergerepo):
    branch_head_hex = '03490f16b15a09913edb3a067a3dc67fbb8d41f1'
    branch_oid = mergerepo.get(branch_head_hex).id
    with (Path(mergerepo.workdir) / 'inindex.txt').open('w') as f:
        f.write('new content')
    mergerepo.index.add('inindex.txt')
    with pytest.raises(pygit2.GitError): mergerepo.merge(branch_oid)


def test_merge_no_fastforward_conflicts(mergerepo):
    branch_head_hex = '1b2bae55ac95a4be3f8983b86cd579226d0eb247'
    branch_id = mergerepo.get(branch_head_hex).id

    analysis, preference = mergerepo.merge_analysis(branch_id)
    assert not analysis & GIT_MERGE_ANALYSIS_UP_TO_DATE
    assert not analysis & GIT_MERGE_ANALYSIS_FASTFORWARD

    mergerepo.merge(branch_id)
    assert mergerepo.index.conflicts is not None
    with pytest.raises(KeyError):
        mergerepo.index.conflicts.__getitem__('some-file')

    status = pygit2.GIT_STATUS_CONFLICTED
    # Asking twice to assure the reference counting is correct
    assert {'.gitignore': status} == mergerepo.status()
    assert {'.gitignore': status} == mergerepo.status()

    ancestor, ours, theirs = mergerepo.index.conflicts['.gitignore']
    assert ancestor is None
    assert ours is not None
    assert theirs is not None
    assert '.gitignore' == ours.path
    assert '.gitignore' == theirs.path
    assert 1 == len(list(mergerepo.index.conflicts))

    # Checking the index works as expected
    mergerepo.index.add('.gitignore')
    mergerepo.index.write()
    assert mergerepo.index.conflicts is None
    assert {'.gitignore': pygit2.GIT_STATUS_INDEX_MODIFIED} == mergerepo.status()

def test_merge_remove_conflicts(mergerepo):
    other_branch_tip = '1b2bae55ac95a4be3f8983b86cd579226d0eb247'
    mergerepo.merge(other_branch_tip)
    idx = mergerepo.index
    conflicts = idx.conflicts
    assert conflicts is not None
    try:
        conflicts['.gitignore']
    except KeyError:
        mergerepo.fail("conflicts['.gitignore'] raised KeyError unexpectedly")
    del idx.conflicts['.gitignore']
    with pytest.raises(KeyError): conflicts.__getitem__('.gitignore')
    assert idx.conflicts is None


def test_merge_commits(mergerepo):
    branch_head_hex = '03490f16b15a09913edb3a067a3dc67fbb8d41f1'
    branch_id = mergerepo.get(branch_head_hex).id

    merge_index = mergerepo.merge_commits(mergerepo.head.target, branch_head_hex)
    assert merge_index.conflicts is None
    merge_commits_tree = merge_index.write_tree(mergerepo)

    mergerepo.merge(branch_id)
    index = mergerepo.index
    assert index.conflicts is None
    merge_tree = index.write_tree()

    assert merge_tree == merge_commits_tree

def test_merge_commits_favor(mergerepo):
    branch_head_hex = '1b2bae55ac95a4be3f8983b86cd579226d0eb247'
    merge_index = mergerepo.merge_commits(mergerepo.head.target, branch_head_hex, favor='ours')
    assert merge_index.conflicts is None

    with pytest.raises(ValueError):
        mergerepo.merge_commits(mergerepo.head.target, branch_head_hex, favor='foo')


def test_merge_trees(mergerepo):
    branch_head_hex = '03490f16b15a09913edb3a067a3dc67fbb8d41f1'
    branch_id = mergerepo.get(branch_head_hex).id
    ancestor_id = mergerepo.merge_base(mergerepo.head.target, branch_id)

    merge_index = mergerepo.merge_trees(ancestor_id, mergerepo.head.target, branch_head_hex)
    assert merge_index.conflicts is None
    merge_commits_tree = merge_index.write_tree(mergerepo)

    mergerepo.merge(branch_id)
    index = mergerepo.index
    assert index.conflicts is None
    merge_tree = index.write_tree()

    assert merge_tree == merge_commits_tree

def test_merge_trees_favor(mergerepo):
    branch_head_hex = '1b2bae55ac95a4be3f8983b86cd579226d0eb247'
    ancestor_id = mergerepo.merge_base(mergerepo.head.target, branch_head_hex)
    merge_index = mergerepo.merge_trees(ancestor_id, mergerepo.head.target, branch_head_hex, favor='ours')
    assert merge_index.conflicts is None

    with pytest.raises(ValueError):
        mergerepo.merge_trees(ancestor_id, mergerepo.head.target, branch_head_hex, favor='foo')


def test_merge_options():
    from pygit2.ffi import C

    # Default
    o = pygit2.Repository._merge_options()
    assert o.file_favor == C.GIT_MERGE_FILE_FAVOR_NORMAL
    assert o.flags == C.GIT_MERGE_FIND_RENAMES
    assert o.file_flags == 0

    o = pygit2.Repository._merge_options(
        favor='ours', flags={'fail_on_conflict': True}, file_flags={'ignore_whitespace': True}
    )
    assert o.file_favor == C.GIT_MERGE_FILE_FAVOR_OURS
    assert o.flags == C.GIT_MERGE_FIND_RENAMES | C.GIT_MERGE_FAIL_ON_CONFLICT
    assert o.file_flags == C.GIT_MERGE_FILE_IGNORE_WHITESPACE

    o = pygit2.Repository._merge_options(
        favor='theirs', flags={'find_renames': False}, file_flags={'ignore_whitespace': False}
    )
    assert o.file_favor == C.GIT_MERGE_FILE_FAVOR_THEIRS
    assert o.flags == 0
    assert o.file_flags == 0

    o = pygit2.Repository._merge_options(
        favor='union',
        flags={'find_renames': True, 'no_recursive': True},
        file_flags={'diff3_style': True, 'ignore_whitespace': True, 'patience': True}
    )
    assert o.file_favor == C.GIT_MERGE_FILE_FAVOR_UNION
    assert o.flags == C.GIT_MERGE_FIND_RENAMES | C.GIT_MERGE_NO_RECURSIVE
    assert o.file_flags == (
        C.GIT_MERGE_FILE_STYLE_DIFF3
        | C.GIT_MERGE_FILE_IGNORE_WHITESPACE
        | C.GIT_MERGE_FILE_DIFF_PATIENCE
    )


def test_merge_many(mergerepo):
    branch_head_hex = '03490f16b15a09913edb3a067a3dc67fbb8d41f1'
    branch_id = mergerepo.get(branch_head_hex).id
    ancestor_id = mergerepo.merge_base_many([mergerepo.head.target, branch_id])

    merge_index = mergerepo.merge_trees(ancestor_id, mergerepo.head.target, branch_head_hex)
    assert merge_index.conflicts is None
    merge_commits_tree = merge_index.write_tree(mergerepo)

    mergerepo.merge(branch_id)
    index = mergerepo.index
    assert index.conflicts is None
    merge_tree = index.write_tree()

    assert merge_tree == merge_commits_tree


def test_merge_octopus(mergerepo):
    branch_head_hex = '03490f16b15a09913edb3a067a3dc67fbb8d41f1'
    branch_id = mergerepo.get(branch_head_hex).id
    ancestor_id = mergerepo.merge_base_octopus([mergerepo.head.target, branch_id])

    merge_index = mergerepo.merge_trees(ancestor_id, mergerepo.head.target, branch_head_hex)
    assert merge_index.conflicts is None
    merge_commits_tree = merge_index.write_tree(mergerepo)

    mergerepo.merge(branch_id)
    index = mergerepo.index
    assert index.conflicts is None
    merge_tree = index.write_tree()

    assert merge_tree == merge_commits_tree
