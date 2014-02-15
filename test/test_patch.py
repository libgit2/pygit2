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

"""Tests for Patch objects."""

from __future__ import absolute_import
from __future__ import unicode_literals
from os.path import dirname, join
import unittest

import pygit2
from . import utils


COMMIT_SHA1_1 = '5fe808e8953c12735680c257f56600cb0de44b10'
COMMIT_SHA1_2 = 'c2792cfa289ae6321ecf2cd5806c2194b0fd070c'


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

BLOB_SHA = 'a520c24d85fbfc815d385957eed41406ca5a860b'
BLOB_CONTENT = """hello world
hola mundo
bonjour le monde
""".encode()
BLOB_NEW_CONTENT = b'foo bar\n'
BLOB_FILE_CONTENT = b'bye world\n'


class DiffTest(utils.BareRepoTestCase):

    def test_diff_patch(self):
        commit_a = self.repo[COMMIT_SHA1_1]
        commit_b = self.repo[COMMIT_SHA1_2]

        diff = commit_a.tree.diff_to_tree(commit_b.tree)
        self.assertEqual(''.join([str(pygit2.Patch.from_diff(diff, i)) for i in range(len(diff))]), PATCH)
        self.assertEqual(len(diff), len([patch for patch in diff]))

class BlobTest(utils.RepoTestCase):

    def test_diff_blob(self):
        old_blob = self.repo[BLOB_SHA]
        new_blob = self.repo['3b18e512dba79e4c8300dd08aeb37f8e728b8dad']
        patch = pygit2.Patch.from_blobs(old_blob, "hello.txt", new_blob)
        self.assertEqual(len(patch), 1)
        self.assertEqual(patch.delta.old_file.path, "hello.txt")

    def test_diff_blob_to_buffer(self):
        old_blob = self.repo[BLOB_SHA]
        patch = pygit2.Patch.from_blob_and_buffer(old_blob, buffer="hello world")
        self.assertEqual(len(patch), 1)

if __name__ == '__main__':
    unittest.main()
