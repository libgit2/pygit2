# -*- coding: UTF-8 -*-
#
# Copyright 2012 Nico von Geyso
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
from . import utils

__author__ = 'Nico.Geyso@FU-Berlin.de (Nico von Geyso)'


COMMIT_SHA1_1 = '5fe808e8953c12735680c257f56600cb0de44b10'
COMMIT_SHA1_2 = 'c2792cfa289ae6321ecf2cd5806c2194b0fd070c'
PATCH = b"""diff --git a/a b/a
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


class DiffTest(utils.BareRepoTestCase):

    def test_diff_invalid(self):
        commit_a = self.repo[COMMIT_SHA1_1]
        commit_b = self.repo[COMMIT_SHA1_2]
        self.assertRaises(TypeError, commit_a.tree.diff, commit_b)

    def test_diff_tree(self):
        commit_a = self.repo[COMMIT_SHA1_1]
        commit_b = self.repo[COMMIT_SHA1_2]

        diff = commit_a.tree.diff(commit_b.tree)

        self.assertIsNotNone(diff)
        self.assertIn(('a','a', 3), diff.changes['files'])
        self.assertEqual(2, len(diff.changes['hunks']))

        hunk = diff.changes['hunks'][0]
        self.assertEqual(hunk.old_start, 1)
        self.assertEqual(hunk.old_lines, 0)
        self.assertEqual(hunk.new_start, 1)
        self.assertEqual(hunk.new_lines, 0)

        self.assertEqual(hunk.old_file, 'a')
        self.assertEqual(hunk.new_file, 'a')

        self.assertEqual(hunk.old_data, b'a contents 2\n')
        self.assertEqual(hunk.new_data, b'a contents\n')

    def test_diff_patch(self):
        commit_a = self.repo[COMMIT_SHA1_1]
        commit_b = self.repo[COMMIT_SHA1_2]

        diff = commit_a.tree.diff(commit_b.tree)
        self.assertEqual(diff.patch, PATCH)


if __name__ == '__main__':
    unittest.main()
