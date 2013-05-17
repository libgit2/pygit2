# -*- coding: UTF-8 -*-
#
# Copyright 2010-2013 The pygit2 contributors
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


class BranchesEmptyRepoTestCase(utils.EmptyRepoTestCase):
    def test_lookup_branch_remote(self):
        remote = self.repo.remotes[0]
        remote.fetch()

        branch = self.repo.lookup_branch('origin/master', pygit2.GIT_BRANCH_REMOTE)
        self.assertEqual(branch.target.hex, ORIGIN_MASTER_COMMIT)

        self.assertTrue(self.repo.lookup_branch('origin/not-exists', pygit2.GIT_BRANCH_REMOTE) is None)


if __name__ == '__main__':
    unittest.main()
