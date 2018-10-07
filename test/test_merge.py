# -*- coding: UTF-8 -*-
#
# Copyright 2010-2017 The pygit2 contributors
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

# Import from the future
from __future__ import absolute_import
from __future__ import unicode_literals

import os

import pytest

from pygit2 import GIT_MERGE_ANALYSIS_UP_TO_DATE
from pygit2 import GIT_MERGE_ANALYSIS_FASTFORWARD
import pygit2

from . import utils

class MergeTestBasic(utils.RepoTestCaseForMerging):

    def test_merge_none(self):
        with pytest.raises(TypeError): self.repo.merge(None)

    def test_merge_analysis_uptodate(self):
        branch_head_hex = '5ebeeebb320790caf276b9fc8b24546d63316533'
        branch_id = self.repo.get(branch_head_hex).id
        analysis, preference = self.repo.merge_analysis(branch_id)

        assert analysis & GIT_MERGE_ANALYSIS_UP_TO_DATE
        assert not analysis & GIT_MERGE_ANALYSIS_FASTFORWARD
        assert {} == self.repo.status()

    def test_merge_analysis_fastforward(self):
        branch_head_hex = 'e97b4cfd5db0fb4ebabf4f203979ca4e5d1c7c87'
        branch_id = self.repo.get(branch_head_hex).id
        analysis, preference = self.repo.merge_analysis(branch_id)
        assert not analysis & GIT_MERGE_ANALYSIS_UP_TO_DATE
        assert analysis & GIT_MERGE_ANALYSIS_FASTFORWARD
        assert {} == self.repo.status()

    def test_merge_no_fastforward_no_conflicts(self):
        branch_head_hex = '03490f16b15a09913edb3a067a3dc67fbb8d41f1'
        branch_id = self.repo.get(branch_head_hex).id
        analysis, preference = self.repo.merge_analysis(branch_id)
        assert not analysis & GIT_MERGE_ANALYSIS_UP_TO_DATE
        assert not analysis & GIT_MERGE_ANALYSIS_FASTFORWARD
        # Asking twice to assure the reference counting is correct
        assert {} == self.repo.status()
        assert {} == self.repo.status()

    def test_merge_no_fastforward_conflicts(self):
        branch_head_hex = '1b2bae55ac95a4be3f8983b86cd579226d0eb247'
        branch_id = self.repo.get(branch_head_hex).id

        analysis, preference = self.repo.merge_analysis(branch_id)
        assert not analysis & GIT_MERGE_ANALYSIS_UP_TO_DATE
        assert not analysis & GIT_MERGE_ANALYSIS_FASTFORWARD

        self.repo.merge(branch_id)
        assert self.repo.index.conflicts is not None
        status = pygit2.GIT_STATUS_CONFLICTED
        # Asking twice to assure the reference counting is correct
        assert {'.gitignore': status} == self.repo.status()
        assert {'.gitignore': status} == self.repo.status()
        # Checking the index works as expected
        self.repo.index.add('.gitignore')
        self.repo.index.write()
        assert {'.gitignore': pygit2.GIT_STATUS_INDEX_MODIFIED} == self.repo.status()

    def test_merge_invalid_hex(self):
        branch_head_hex = '12345678'
        with pytest.raises(KeyError): self.repo.merge(branch_head_hex)

    def test_merge_already_something_in_index(self):
        branch_head_hex = '03490f16b15a09913edb3a067a3dc67fbb8d41f1'
        branch_oid = self.repo.get(branch_head_hex).id
        with open(os.path.join(self.repo.workdir, 'inindex.txt'), 'w') as f:
            f.write('new content')
        self.repo.index.add('inindex.txt')
        with pytest.raises(pygit2.GitError): self.repo.merge(branch_oid)

class MergeTestWithConflicts(utils.RepoTestCaseForMerging):

    def test_merge_no_fastforward_conflicts(self):
        branch_head_hex = '1b2bae55ac95a4be3f8983b86cd579226d0eb247'
        branch_id = self.repo.get(branch_head_hex).id

        analysis, preference = self.repo.merge_analysis(branch_id)
        assert not analysis & GIT_MERGE_ANALYSIS_UP_TO_DATE
        assert not analysis & GIT_MERGE_ANALYSIS_FASTFORWARD

        self.repo.merge(branch_id)
        assert self.repo.index.conflicts is not None
        with pytest.raises(KeyError):
            self.repo.index.conflicts.__getitem__('some-file')

        ancestor, ours, theirs = self.repo.index.conflicts['.gitignore']
        assert ancestor is None
        assert ours is not None
        assert theirs is not None
        assert '.gitignore' == ours.path
        assert '.gitignore' == theirs.path
        assert 1 == len(list(self.repo.index.conflicts))
        # Checking the index works as expected
        self.repo.index.add('.gitignore')
        self.repo.index.write()
        assert self.repo.index.conflicts is None

    def test_merge_remove_conflicts(self):
        other_branch_tip = '1b2bae55ac95a4be3f8983b86cd579226d0eb247'
        self.repo.merge(other_branch_tip)
        idx = self.repo.index
        conflicts = idx.conflicts
        assert conflicts is not None
        try:
            conflicts['.gitignore']
        except KeyError:
            self.fail("conflicts['.gitignore'] raised KeyError unexpectedly")
        del idx.conflicts['.gitignore']
        with pytest.raises(KeyError): conflicts.__getitem__('.gitignore')
        assert idx.conflicts is None

class MergeCommitsTest(utils.RepoTestCaseForMerging):

    def test_merge_commits(self):
        branch_head_hex = '03490f16b15a09913edb3a067a3dc67fbb8d41f1'
        branch_id = self.repo.get(branch_head_hex).id

        merge_index = self.repo.merge_commits(self.repo.head.target, branch_head_hex)
        assert merge_index.conflicts is None
        merge_commits_tree = merge_index.write_tree(self.repo)

        self.repo.merge(branch_id)
        index = self.repo.index
        assert index.conflicts is None
        merge_tree = index.write_tree()

        assert merge_tree == merge_commits_tree

    def test_merge_commits_favor(self):
        branch_head_hex = '1b2bae55ac95a4be3f8983b86cd579226d0eb247'
        merge_index = self.repo.merge_commits(self.repo.head.target, branch_head_hex, favor='ours')
        assert merge_index.conflicts is None

        with pytest.raises(ValueError):
            self.repo.merge_commits(self.repo.head.target, branch_head_hex, favor='foo')

class MergeTreesTest(utils.RepoTestCaseForMerging):

    def test_merge_trees(self):
        branch_head_hex = '03490f16b15a09913edb3a067a3dc67fbb8d41f1'
        branch_id = self.repo.get(branch_head_hex).id
        ancestor_id = self.repo.merge_base(self.repo.head.target, branch_id)

        merge_index = self.repo.merge_trees(ancestor_id, self.repo.head.target, branch_head_hex)
        assert merge_index.conflicts is None
        merge_commits_tree = merge_index.write_tree(self.repo)

        self.repo.merge(branch_id)
        index = self.repo.index
        assert index.conflicts is None
        merge_tree = index.write_tree()

        assert merge_tree == merge_commits_tree

    def test_merge_commits_favor(self):
        branch_head_hex = '1b2bae55ac95a4be3f8983b86cd579226d0eb247'
        ancestor_id = self.repo.merge_base(self.repo.head.target, branch_head_hex)
        merge_index = self.repo.merge_trees(ancestor_id, self.repo.head.target, branch_head_hex, favor='ours')
        assert merge_index.conflicts is None

        with pytest.raises(ValueError):
            self.repo.merge_trees(ancestor_id, self.repo.head.target, branch_head_hex, favor='foo')
