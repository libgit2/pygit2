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

"""Tests for Diff objects."""

from __future__ import absolute_import
from __future__ import unicode_literals
import unittest
import pygit2
from pygit2 import GIT_DIFF_INCLUDE_UNMODIFIED
from . import utils


COMMIT_SHA1_1 = '5fe808e8953c12735680c257f56600cb0de44b10'
COMMIT_SHA1_2 = 'c2792cfa289ae6321ecf2cd5806c2194b0fd070c'
COMMIT_SHA1_3 = '2cdae28389c059815e951d0bb9eed6533f61a46b'
COMMIT_SHA1_4 = 'ccca47fbb26183e71a7a46d165299b84e2e6c0b3'
COMMIT_SHA1_5 = '056e626e51b1fc1ee2182800e399ed8d84c8f082'
COMMIT_SHA1_6 = 'f5e5aa4e36ab0fe62ee1ccc6eb8f79b866863b87'
COMMIT_SHA1_7 = '784855caf26449a1914d2cf62d12b9374d76ae78'


PATCH = """diff --git a/a b/a
index 7f129fd..af431f2 100644
--- a/a
+++ b/a
@@ -1 +1 @@
-a contents 2
+a contents
diff --git a/c/d b/c/d
deleted file mode 100644
index 297efb8..0000000
--- a/c/d
+++ /dev/null
@@ -1 +0,0 @@
-c/d contents
"""

DIFF_INDEX_EXPECTED = [
    'staged_changes',
    'staged_changes_file_deleted',
    'staged_changes_file_modified',
    'staged_delete',
    'staged_delete_file_modified',
    'staged_new',
    'staged_new_file_deleted',
    'staged_new_file_modified'
]

DIFF_WORKDIR_EXPECTED = [
    'file_deleted',
    'modified_file',
    'staged_changes',
    'staged_changes_file_deleted',
    'staged_changes_file_modified',
    'staged_delete',
    'staged_delete_file_modified',
    'subdir/deleted_file',
    'subdir/modified_file'
]

HUNK_EXPECTED = """@@ -1 +1 @@
a contents 2
a contents
"""

class DiffDirtyTest(utils.DirtyRepoTestCase):
    def test_diff_empty_index(self):
        repo = self.repo
        head = repo[repo.lookup_reference('HEAD').resolve().oid]
        diff = head.tree.diff(repo.index)

        files = [patch.new_file_path for patch in diff]
        self.assertEqual(DIFF_INDEX_EXPECTED, files)

    def test_workdir_to_tree(self):
        repo = self.repo
        head = repo[repo.lookup_reference('HEAD').resolve().oid]
        diff = head.tree.diff()

        files = [patch.new_file_path for patch in diff]
        self.assertEqual(DIFF_WORKDIR_EXPECTED, files)

class DiffTest(utils.BareRepoTestCase):

    def test_diff_invalid(self):
        commit_a = self.repo[COMMIT_SHA1_1]
        commit_b = self.repo[COMMIT_SHA1_2]
        self.assertRaises(TypeError, commit_a.tree.diff, commit_b)

    def test_diff_empty_index(self):
        repo = self.repo
        head = repo[repo.lookup_reference('HEAD').resolve().oid]
        diff = head.tree.diff(repo.index)

        files = [patch.new_file_path.split('/')[0] for patch in diff]
        self.assertEqual([x.name for x in head.tree], files)

    def test_diff_tree(self):
        commit_a = self.repo[COMMIT_SHA1_1]
        commit_b = self.repo[COMMIT_SHA1_2]

        diff = commit_a.tree.diff(commit_b.tree)

        # self.assertIsNotNone is 2.7 only
        self.assertTrue(diff is not None)
        # self.assertIn is 2.7 only
        self.assertEqual(2, sum(map(lambda x: len(x.hunks), diff)))

        patch = diff[0]
        hunk = patch.hunks[0]
        self.assertEqual(hunk.old_start, 1)
        self.assertEqual(hunk.old_lines, 1)
        self.assertEqual(hunk.new_start, 1)
        self.assertEqual(hunk.new_lines, 1)

        self.assertEqual(patch.old_file_path, 'a')
        self.assertEqual(patch.new_file_path, 'a')

    def test_diff_tree_opts(self):
        commit_c = self.repo[COMMIT_SHA1_3]
        commit_d = self.repo[COMMIT_SHA1_4]

        for opt in [pygit2.GIT_DIFF_IGNORE_WHITESPACE,
                    pygit2.GIT_DIFF_IGNORE_WHITESPACE_EOL]:
            diff = commit_c.tree.diff(commit_d.tree, opt)
            self.assertTrue(diff is not None)
            self.assertEqual(0, len(diff[0].hunks))

        diff = commit_c.tree.diff(commit_d.tree)
        self.assertTrue(diff is not None)
        self.assertEqual(1, len(diff[0].hunks))

    def test_diff_merge(self):
        commit_a = self.repo[COMMIT_SHA1_1]
        commit_b = self.repo[COMMIT_SHA1_2]
        commit_c = self.repo[COMMIT_SHA1_3]

        diff_b = commit_a.tree.diff(commit_b.tree)
        # self.assertIsNotNone is 2.7 only
        self.assertTrue(diff_b is not None)

        diff_c = commit_b.tree.diff(commit_c.tree)
        # self.assertIsNotNone is 2.7 only
        self.assertTrue(diff_c is not None)

        # assertIn / assertNotIn are 2.7 only
        self.assertFalse('b' in [patch.new_file_path for patch in diff_b])
        self.assertTrue('b' in [patch.new_file_path for patch in diff_c])

        diff_b.merge(diff_c)

        # assertIn is 2.7 only
        self.assertTrue('b' in [patch.new_file_path for patch in diff_b])

        patch = diff_b[0]
        hunk = patch.hunks[0]
        self.assertEqual(hunk.old_start, 1)
        self.assertEqual(hunk.old_lines, 1)
        self.assertEqual(hunk.new_start, 1)
        self.assertEqual(hunk.new_lines, 1)

        self.assertEqual(patch.old_file_path, 'a')
        self.assertEqual(patch.new_file_path, 'a')

    def test_diff_patch(self):
        commit_a = self.repo[COMMIT_SHA1_1]
        commit_b = self.repo[COMMIT_SHA1_2]

        diff = commit_a.tree.diff(commit_b.tree)
        self.assertEqual(diff.patch, PATCH)

    def test_diff_oids(self):
        commit_a = self.repo[COMMIT_SHA1_1]
        commit_b = self.repo[COMMIT_SHA1_2]
        patch = commit_a.tree.diff(commit_b.tree)[0]
        self.assertEqual(patch.old_oid,
                         '7f129fd57e31e935c6d60a0c794efe4e6927664b')
        self.assertEqual(patch.new_oid,
                         'af431f20fc541ed6d5afede3e2dc7160f6f01f16')

    def test_hunk_content(self):
        commit_a = self.repo[COMMIT_SHA1_1]
        commit_b = self.repo[COMMIT_SHA1_2]
        patch = commit_a.tree.diff(commit_b.tree)[0]
        hunk = patch.hunks[0]
        self.assertEqual(HUNK_EXPECTED, ''.join(hunk.lines))

    def test_find_similar(self):
        commit_a = self.repo[COMMIT_SHA1_6]
        commit_b = self.repo[COMMIT_SHA1_7]

        #~ Must pass GIT_DIFF_INCLUDE_UNMODIFIED if you expect to emulate
        #~ --find-copies-harder during rename transformion...
        diff = commit_a.tree.diff(commit_b.tree, GIT_DIFF_INCLUDE_UNMODIFIED)
        self.assertAll(lambda x: x.status is not pygit2.GIT_DELTA_RENAMED, diff)
        diff.find_similar()
        self.assertAny(lambda x: x.status is pygit2.GIT_DELTA_RENAMED, diff)

if __name__ == '__main__':
    unittest.main()
