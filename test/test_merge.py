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

"""Tests for merging and information about it."""

from pathlib import Path

import pytest

import pygit2
from pygit2 import Repository
from pygit2.enums import FileStatus, MergeAnalysis, MergeFavor, MergeFileFlag, MergeFlag


@pytest.mark.parametrize('id', [None, 42])
def test_merge_invalid_type(mergerepo: Repository, id: None | int) -> None:
    with pytest.raises(TypeError):
        mergerepo.merge(id)  # type:ignore


# TODO: Once Repository.merge drops support for str arguments,
#       add an extra parameter to test_merge_invalid_type above
#       to make sure we cover legacy code.
def test_merge_string_argument_deprecated(mergerepo: Repository) -> None:
    branch_head_hex = '5ebeeebb320790caf276b9fc8b24546d63316533'

    with pytest.warns(DeprecationWarning, match=r'Pass Commit.+instead'):
        mergerepo.merge(branch_head_hex)


def test_merge_analysis_uptodate(mergerepo: Repository) -> None:
    branch_head_hex = '5ebeeebb320790caf276b9fc8b24546d63316533'
    branch_id = mergerepo[branch_head_hex].id

    analysis, preference = mergerepo.merge_analysis(branch_id)
    assert analysis & MergeAnalysis.UP_TO_DATE
    assert not analysis & MergeAnalysis.FASTFORWARD
    assert {} == mergerepo.status()

    analysis, preference = mergerepo.merge_analysis(branch_id, 'refs/heads/ff-branch')
    assert analysis & MergeAnalysis.UP_TO_DATE
    assert not analysis & MergeAnalysis.FASTFORWARD
    assert {} == mergerepo.status()


def test_merge_analysis_fastforward(mergerepo: Repository) -> None:
    branch_head_hex = 'e97b4cfd5db0fb4ebabf4f203979ca4e5d1c7c87'
    branch_id = mergerepo[branch_head_hex].id

    analysis, preference = mergerepo.merge_analysis(branch_id)
    assert not analysis & MergeAnalysis.UP_TO_DATE
    assert analysis & MergeAnalysis.FASTFORWARD
    assert {} == mergerepo.status()

    analysis, preference = mergerepo.merge_analysis(branch_id, 'refs/heads/master')
    assert not analysis & MergeAnalysis.UP_TO_DATE
    assert analysis & MergeAnalysis.FASTFORWARD
    assert {} == mergerepo.status()


def test_merge_no_fastforward_no_conflicts(mergerepo: Repository) -> None:
    branch_head_hex = '03490f16b15a09913edb3a067a3dc67fbb8d41f1'
    branch_id = mergerepo[branch_head_hex].id
    analysis, preference = mergerepo.merge_analysis(branch_id)
    assert not analysis & MergeAnalysis.UP_TO_DATE
    assert not analysis & MergeAnalysis.FASTFORWARD
    # Asking twice to assure the reference counting is correct
    assert {} == mergerepo.status()
    assert {} == mergerepo.status()


def test_merge_invalid_hex(mergerepo: Repository) -> None:
    branch_head_hex = '12345678'
    with (
        pytest.raises(KeyError),
        pytest.warns(DeprecationWarning, match=r'Pass Commit.+instead'),
    ):
        mergerepo.merge(branch_head_hex)


def test_merge_already_something_in_index(mergerepo: Repository) -> None:
    branch_head_hex = '03490f16b15a09913edb3a067a3dc67fbb8d41f1'
    branch_oid = mergerepo[branch_head_hex].id
    with (Path(mergerepo.workdir) / 'inindex.txt').open('w') as f:
        f.write('new content')
    mergerepo.index.add('inindex.txt')
    with pytest.raises(pygit2.GitError):
        mergerepo.merge(branch_oid)


def test_merge_no_fastforward_conflicts(mergerepo: Repository) -> None:
    branch_head_hex = '1b2bae55ac95a4be3f8983b86cd579226d0eb247'
    branch_id = mergerepo[branch_head_hex].id

    analysis, preference = mergerepo.merge_analysis(branch_id)
    assert not analysis & MergeAnalysis.UP_TO_DATE
    assert not analysis & MergeAnalysis.FASTFORWARD

    mergerepo.merge(branch_id)
    assert mergerepo.index.conflicts is not None
    with pytest.raises(KeyError):
        mergerepo.index.conflicts.__getitem__('some-file')
    assert 'some-file' not in mergerepo.index.conflicts
    assert '.gitignore' in mergerepo.index.conflicts

    status = FileStatus.CONFLICTED
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
    assert {'.gitignore': FileStatus.INDEX_MODIFIED} == mergerepo.status()


def test_merge_remove_conflicts(mergerepo: Repository) -> None:
    other_branch_tip = pygit2.Oid(hex='1b2bae55ac95a4be3f8983b86cd579226d0eb247')
    mergerepo.merge(other_branch_tip)
    idx = mergerepo.index
    conflicts = idx.conflicts
    assert conflicts is not None
    assert '.gitignore' in conflicts
    try:
        conflicts['.gitignore']
    except KeyError:
        mergerepo.fail("conflicts['.gitignore'] raised KeyError unexpectedly")  # type: ignore
    del idx.conflicts['.gitignore']
    with pytest.raises(KeyError):
        conflicts.__getitem__('.gitignore')
    assert '.gitignore' not in conflicts
    assert idx.conflicts is None


@pytest.mark.parametrize(
    'favor',
    [
        MergeFavor.OURS,
        MergeFavor.THEIRS,
        MergeFavor.UNION,
    ],
)
def test_merge_favor(mergerepo: Repository, favor: MergeFavor) -> None:
    branch_head = pygit2.Oid(hex='1b2bae55ac95a4be3f8983b86cd579226d0eb247')
    mergerepo.merge(branch_head, favor=favor)

    assert mergerepo.index.conflicts is None


def test_merge_fail_on_conflict(mergerepo: Repository) -> None:
    branch_head = pygit2.Oid(hex='1b2bae55ac95a4be3f8983b86cd579226d0eb247')

    with pytest.raises(pygit2.GitError, match=r'merge conflicts exist'):
        mergerepo.merge(
            branch_head, flags=MergeFlag.FIND_RENAMES | MergeFlag.FAIL_ON_CONFLICT
        )


def test_merge_commits(mergerepo: Repository) -> None:
    branch_head = pygit2.Oid(hex='03490f16b15a09913edb3a067a3dc67fbb8d41f1')

    merge_index = mergerepo.merge_commits(mergerepo.head.target, branch_head)
    assert merge_index.conflicts is None
    merge_commits_tree = merge_index.write_tree(mergerepo)

    mergerepo.merge(branch_head)
    index = mergerepo.index
    assert index.conflicts is None
    merge_tree = index.write_tree()

    assert merge_tree == merge_commits_tree


def test_merge_commits_favor(mergerepo: Repository) -> None:
    branch_head = pygit2.Oid(hex='1b2bae55ac95a4be3f8983b86cd579226d0eb247')

    merge_index = mergerepo.merge_commits(
        mergerepo.head.target, branch_head, favor=MergeFavor.OURS
    )
    assert merge_index.conflicts is None

    # Incorrect favor value
    with pytest.raises(TypeError, match=r'favor argument must be MergeFavor'):
        mergerepo.merge_commits(mergerepo.head.target, branch_head, favor='foo')  # type: ignore


def test_merge_trees(mergerepo: Repository) -> None:
    branch_id = pygit2.Oid(hex='03490f16b15a09913edb3a067a3dc67fbb8d41f1')
    ancestor_id = mergerepo.merge_base(mergerepo.head.target, branch_id)

    merge_index = mergerepo.merge_trees(ancestor_id, mergerepo.head.target, branch_id)
    assert merge_index.conflicts is None
    merge_commits_tree = merge_index.write_tree(mergerepo)

    mergerepo.merge(branch_id)
    index = mergerepo.index
    assert index.conflicts is None
    merge_tree = index.write_tree()

    assert merge_tree == merge_commits_tree


def test_merge_trees_favor(mergerepo: Repository) -> None:
    branch_head_hex = '1b2bae55ac95a4be3f8983b86cd579226d0eb247'
    ancestor_id = mergerepo.merge_base(mergerepo.head.target, branch_head_hex)
    merge_index = mergerepo.merge_trees(
        ancestor_id, mergerepo.head.target, branch_head_hex, favor=MergeFavor.OURS
    )
    assert merge_index.conflicts is None

    with pytest.raises(TypeError):
        mergerepo.merge_trees(
            ancestor_id,
            mergerepo.head.target,
            branch_head_hex,
            favor='foo',  # type: ignore
        )


def test_merge_options() -> None:
    favor = MergeFavor.OURS
    flags: int | MergeFlag = MergeFlag.FIND_RENAMES | MergeFlag.FAIL_ON_CONFLICT
    file_flags: int | MergeFileFlag = (
        MergeFileFlag.IGNORE_WHITESPACE | MergeFileFlag.DIFF_PATIENCE
    )
    o1 = pygit2.Repository._merge_options(
        favor=favor, flags=flags, file_flags=file_flags
    )
    assert favor == o1.file_favor
    assert flags == o1.flags
    assert file_flags == o1.file_flags

    favor = MergeFavor.THEIRS
    flags = 0
    file_flags = 0
    o1 = pygit2.Repository._merge_options(
        favor=favor, flags=flags, file_flags=file_flags
    )
    assert favor == o1.file_favor
    assert flags == o1.flags
    assert file_flags == o1.file_flags

    favor = MergeFavor.UNION
    flags = MergeFlag.FIND_RENAMES | MergeFlag.NO_RECURSIVE
    file_flags = (
        MergeFileFlag.STYLE_DIFF3
        | MergeFileFlag.IGNORE_WHITESPACE
        | MergeFileFlag.DIFF_PATIENCE
    )
    o1 = pygit2.Repository._merge_options(
        favor=favor, flags=flags, file_flags=file_flags
    )
    assert favor == o1.file_favor
    assert flags == o1.flags
    assert file_flags == o1.file_flags


def test_merge_many(mergerepo: Repository) -> None:
    branch_head_hex = '03490f16b15a09913edb3a067a3dc67fbb8d41f1'
    branch_id = mergerepo[branch_head_hex].id
    ancestor_id = mergerepo.merge_base_many([mergerepo.head.target, branch_id])

    merge_index = mergerepo.merge_trees(
        ancestor_id, mergerepo.head.target, branch_head_hex
    )
    assert merge_index.conflicts is None
    merge_commits_tree = merge_index.write_tree(mergerepo)

    mergerepo.merge(branch_id)
    index = mergerepo.index
    assert index.conflicts is None
    merge_tree = index.write_tree()

    assert merge_tree == merge_commits_tree


def test_merge_octopus(mergerepo: Repository) -> None:
    branch_head_hex = '03490f16b15a09913edb3a067a3dc67fbb8d41f1'
    branch_id = mergerepo[branch_head_hex].id
    ancestor_id = mergerepo.merge_base_octopus([mergerepo.head.target, branch_id])

    merge_index = mergerepo.merge_trees(
        ancestor_id, mergerepo.head.target, branch_head_hex
    )
    assert merge_index.conflicts is None
    merge_commits_tree = merge_index.write_tree(mergerepo)

    mergerepo.merge(branch_id)
    index = mergerepo.index
    assert index.conflicts is None
    merge_tree = index.write_tree()

    assert merge_tree == merge_commits_tree


def test_merge_mergeheads(mergerepo: Repository) -> None:
    assert mergerepo.listall_mergeheads() == []

    branch_head = pygit2.Oid(hex='1b2bae55ac95a4be3f8983b86cd579226d0eb247')
    mergerepo.merge(branch_head)

    assert mergerepo.listall_mergeheads() == [branch_head]

    mergerepo.state_cleanup()
    assert mergerepo.listall_mergeheads() == [], (
        'state_cleanup() should wipe the mergeheads'
    )


def test_merge_message(mergerepo: Repository) -> None:
    assert not mergerepo.message
    assert not mergerepo.raw_message

    branch_head = pygit2.Oid(hex='1b2bae55ac95a4be3f8983b86cd579226d0eb247')
    mergerepo.merge(branch_head)

    assert mergerepo.message.startswith(f"Merge commit '{branch_head}'")
    assert mergerepo.message.encode('utf-8') == mergerepo.raw_message

    mergerepo.state_cleanup()
    assert not mergerepo.message


def test_merge_remove_message(mergerepo: Repository) -> None:
    branch_head = pygit2.Oid(hex='1b2bae55ac95a4be3f8983b86cd579226d0eb247')
    mergerepo.merge(branch_head)

    assert mergerepo.message.startswith(f"Merge commit '{branch_head}'")
    mergerepo.remove_message()
    assert not mergerepo.message


def test_merge_commit(mergerepo: Repository) -> None:
    commit = mergerepo['1b2bae55ac95a4be3f8983b86cd579226d0eb247']
    assert isinstance(commit, pygit2.Commit)
    mergerepo.merge(commit)

    assert mergerepo.message.startswith(f"Merge commit '{str(commit.id)}'")
    assert mergerepo.listall_mergeheads() == [commit.id]


def test_merge_reference(mergerepo: Repository) -> None:
    branch = mergerepo.branches.local['branch-conflicts']
    branch_head_hex = '1b2bae55ac95a4be3f8983b86cd579226d0eb247'
    mergerepo.merge(branch)

    assert mergerepo.message.startswith("Merge branch 'branch-conflicts'")
    assert mergerepo.listall_mergeheads() == [pygit2.Oid(hex=branch_head_hex)]
