# -*- coding: UTF-8 -*-
#
# Copyright 2010-2014 The pygit2 contributors
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

from __future__ import absolute_import
from __future__ import unicode_literals
import unittest

import pygit2
from . import utils

LAST_COMMIT = '2be5719152d4f82c7302b1c0932d8e5f0a4a0e98'
I18N_LAST_COMMIT = '5470a671a80ac3789f1a6a8cefbcf43ce7af0563'
ORIGIN_MASTER_COMMIT = '784855caf26449a1914d2cf62d12b9374d76ae78'


class BranchesTestCase(utils.RepoTestCase):
    def test_lookup_branch_local(self):
        branch = self.repo.lookup_branch('master')
        self.assertEqual(branch.target.hex, LAST_COMMIT)

        branch = self.repo.lookup_branch('i18n', pygit2.GIT_BRANCH_LOCAL)
        self.assertEqual(branch.target.hex, I18N_LAST_COMMIT)

        self.assertTrue(self.repo.lookup_branch('not-exists') is None)

    def test_listall_branches(self):
        branches = sorted(self.repo.listall_branches())
        self.assertEqual(branches, ['i18n', 'master'])

    def test_create_branch(self):
        commit = self.repo[LAST_COMMIT]
        reference = self.repo.create_branch('version1', commit)
        refs = self.repo.listall_branches()
        self.assertTrue('version1' in refs)
        reference = self.repo.lookup_branch('version1')
        self.assertEqual(reference.target.hex, LAST_COMMIT)

        # try to create existing reference
        self.assertRaises(ValueError,
                          lambda: self.repo.create_branch('version1', commit))

        # try to create existing reference with force
        reference = self.repo.create_branch('version1', commit, True)
        self.assertEqual(reference.target.hex, LAST_COMMIT)

    def test_delete(self):
        branch = self.repo.lookup_branch('i18n')
        branch.delete()

        self.assertTrue(self.repo.lookup_branch('i18n') is None)

    def test_cant_delete_master(self):
        branch = self.repo.lookup_branch('master')

        self.assertRaises(pygit2.GitError, lambda: branch.delete())

    def test_branch_is_head_returns_true_if_branch_is_head(self):
        branch = self.repo.lookup_branch('master')
        self.assertTrue(branch.is_head())

    def test_branch_is_head_returns_false_if_branch_is_not_head(self):
        branch = self.repo.lookup_branch('i18n')
        self.assertFalse(branch.is_head())

    def test_branch_rename_succeeds(self):
        original_branch = self.repo.lookup_branch('i18n')
        new_branch = original_branch.rename('new-branch')
        self.assertEqual(new_branch.target.hex, I18N_LAST_COMMIT)

        new_branch_2 = self.repo.lookup_branch('new-branch')
        self.assertEqual(new_branch_2.target.hex, I18N_LAST_COMMIT)

    def test_branch_rename_fails_if_destination_already_exists(self):
        original_branch = self.repo.lookup_branch('i18n')
        self.assertRaises(ValueError, lambda: original_branch.rename('master'))

    def test_branch_rename_not_fails_if_force_is_true(self):
        original_branch = self.repo.lookup_branch('master')
        new_branch = original_branch.rename('i18n', True)
        self.assertEqual(new_branch.target.hex, LAST_COMMIT)

    def test_branch_rename_fails_with_invalid_names(self):
        original_branch = self.repo.lookup_branch('i18n')
        self.assertRaises(ValueError,
                          lambda: original_branch.rename('abc@{123'))

    def test_branch_name(self):
        branch = self.repo.lookup_branch('master')
        self.assertEqual(branch.branch_name, 'master')
        self.assertEqual(branch.name, 'refs/heads/master')

        branch = self.repo.lookup_branch('i18n')
        self.assertEqual(branch.branch_name, 'i18n')
        self.assertEqual(branch.name, 'refs/heads/i18n')


class BranchesEmptyRepoTestCase(utils.EmptyRepoTestCase):
    def setUp(self):
        super(utils.EmptyRepoTestCase, self).setUp()

        remote = self.repo.remotes[0]
        remote.fetch()

    def test_lookup_branch_remote(self):
        branch = self.repo.lookup_branch('origin/master',
                                         pygit2.GIT_BRANCH_REMOTE)
        self.assertEqual(branch.target.hex, ORIGIN_MASTER_COMMIT)

        self.assertTrue(
            self.repo.lookup_branch('origin/not-exists',
                                    pygit2.GIT_BRANCH_REMOTE) is None)

    def test_listall_branches(self):
        branches = sorted(self.repo.listall_branches(pygit2.GIT_BRANCH_REMOTE))
        self.assertEqual(branches, ['origin/master'])

    def test_branch_remote_name(self):
        self.repo.remotes[0].fetch()
        branch = self.repo.lookup_branch('origin/master',
                                         pygit2.GIT_BRANCH_REMOTE)
        self.assertEqual(branch.remote_name, 'origin')

    def test_branch_upstream(self):
        self.repo.remotes[0].fetch()
        remote_master = self.repo.lookup_branch('origin/master',
                                                pygit2.GIT_BRANCH_REMOTE)
        master = self.repo.create_branch('master',
                                         self.repo[remote_master.target.hex])

        self.assertTrue(master.upstream is None)
        master.upstream = remote_master
        self.assertEqual(master.upstream.branch_name, 'origin/master')

        def set_bad_upstream():
            master.upstream = 2.5
        self.assertRaises(TypeError, set_bad_upstream)

        master.upstream = None
        self.assertTrue(master.upstream is None)

    def test_branch_upstream_name(self):
        self.repo.remotes[0].fetch()
        remote_master = self.repo.lookup_branch('origin/master',
                                                pygit2.GIT_BRANCH_REMOTE)
        master = self.repo.create_branch('master',
                                         self.repo[remote_master.target.hex])

        master.upstream = remote_master
        self.assertEqual(master.upstream_name, 'refs/remotes/origin/master')


if __name__ == '__main__':
    unittest.main()
