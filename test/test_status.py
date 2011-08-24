# -*- coding: UTF-8 -*-
#
# Copyright 2011 Julien Miotte
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

"""Tests for revision walk."""

from __future__ import absolute_import
from __future__ import unicode_literals
import unittest

import pygit2
from . import utils


__author__ = 'mike.perdide@gmail.com (Julien Miotte)'

EXPECTED = {
 "current_file":                    pygit2.GIT_STATUS_CURRENT,
 "file_deleted":                    pygit2.GIT_STATUS_WT_DELETED,
 "modified_file":                   pygit2.GIT_STATUS_WT_MODIFIED,
 "new_file":                        pygit2.GIT_STATUS_WT_NEW,

 "staged_changes":                  pygit2.GIT_STATUS_INDEX_MODIFIED,
 "staged_changes_file_deleted":     pygit2.GIT_STATUS_INDEX_MODIFIED |
                                    pygit2.GIT_STATUS_WT_DELETED,
 "staged_changes_file_modified":    pygit2.GIT_STATUS_INDEX_MODIFIED |
                                    pygit2.GIT_STATUS_WT_MODIFIED,

 "staged_delete":                   pygit2.GIT_STATUS_INDEX_DELETED,
 "staged_delete_file_modified":     pygit2.GIT_STATUS_INDEX_DELETED |
                                    pygit2.GIT_STATUS_WT_NEW,
 "staged_new":                      pygit2.GIT_STATUS_INDEX_NEW,

 "staged_new_file_deleted":         pygit2.GIT_STATUS_INDEX_NEW |
                                    pygit2.GIT_STATUS_WT_DELETED,
 "staged_new_file_modified":        pygit2.GIT_STATUS_INDEX_NEW |
                                    pygit2.GIT_STATUS_WT_MODIFIED,

 "subdir/current_file":             pygit2.GIT_STATUS_CURRENT,
 "subdir/deleted_file":             pygit2.GIT_STATUS_WT_DELETED,
 "subdir/modified_file":            pygit2.GIT_STATUS_WT_MODIFIED,
 "subdir/new_file":                 pygit2.GIT_STATUS_WT_NEW,
}

class StatusTest(utils.DirtyRepoTestCase):

    def test_status(self):
        """
            For every file in the status, check that the flags are correct.
        """
        git_status = self.repo.status()
        for filepath, status in git_status.items():
            self.assertTrue(filepath in git_status)
            self.assertEqual(status, git_status[filepath])


if __name__ == '__main__':
    unittest.main()
