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

from __future__ import absolute_import
from __future__ import unicode_literals

import pygit2
from . import utils

BLOB_SHA = 'a520c24d85fbfc815d385957eed41406ca5a860b'
BLOB_OLD_CONTENT = """hello world
hola mundo
bonjour le monde
""".encode()
BLOB_NEW_CONTENT = b'foo bar\n'

BLOB_OLD_PATH = 'a/file'
BLOB_NEW_PATH = 'b/file'

BLOB_PATCH = """diff --git a/a/file b/b/file
index a520c24..d675fa4 100644
--- a/a/file
+++ b/b/file
@@ -1,3 +1 @@
-hello world
-hola mundo
-bonjour le monde
+foo bar
"""

BLOB_PATCH_ADDED = """diff --git a/a/file b/b/file
new file mode 100644
index 0000000..d675fa4
--- /dev/null
+++ b/b/file
@@ -0,0 +1 @@
+foo bar
"""

BLOB_PATCH_DELETED = """diff --git a/a/file b/b/file
deleted file mode 100644
index a520c24..0000000
--- a/a/file
+++ /dev/null
@@ -1,3 +0,0 @@
-hello world
-hola mundo
-bonjour le monde
"""


class PatchTest(utils.RepoTestCase):

    def test_patch_create_from_buffers(self):
        patch = pygit2.Patch.create_from(
            BLOB_OLD_CONTENT,
            BLOB_OLD_PATH,
            BLOB_NEW_CONTENT,
            BLOB_NEW_PATH,
        )

        self.assertEqual(patch.patch, BLOB_PATCH)

    def test_patch_create_from_blobs(self):
        old_blob = self.repo.create_blob(BLOB_OLD_CONTENT)
        new_blob = self.repo.create_blob(BLOB_NEW_CONTENT)

        patch = pygit2.Patch.create_from(
            self.repo[old_blob],
            BLOB_OLD_PATH,
            self.repo[new_blob],
            BLOB_NEW_PATH,
        )

        self.assertEqual(patch.patch, BLOB_PATCH)

    def test_patch_create_from_blob_buffer(self):
        old_blob = self.repo.create_blob(BLOB_OLD_CONTENT)
        patch = pygit2.Patch.create_from(
            self.repo[old_blob],
            BLOB_OLD_PATH,
            BLOB_NEW_CONTENT,
            BLOB_NEW_PATH,
        )

        self.assertEqual(patch.patch, BLOB_PATCH)

    def test_patch_create_from_blob_buffer_add(self):
        patch = pygit2.Patch.create_from(
            None,
            BLOB_OLD_PATH,
            BLOB_NEW_CONTENT,
            BLOB_NEW_PATH,
        )

        self.assertEqual(patch.patch, BLOB_PATCH_ADDED)

    def test_patch_create_from_blob_buffer_delete(self):
        old_blob = self.repo.create_blob(BLOB_OLD_CONTENT)

        patch = pygit2.Patch.create_from(
            self.repo[old_blob],
            BLOB_OLD_PATH,
            None,
            BLOB_NEW_PATH,
        )

        self.assertEqual(patch.patch, BLOB_PATCH_DELETED)

    def test_patch_create_from_bad_old_type_arg(self):
        with self.assertRaises(TypeError):
            pygit2.Patch.create_from(
                self.repo,
                BLOB_OLD_PATH,
                BLOB_NEW_CONTENT,
                BLOB_NEW_PATH,
            )

    def test_patch_create_from_bad_new_type_arg(self):
        with self.assertRaises(TypeError):
            pygit2.Patch.create_from(
                None,
                BLOB_OLD_PATH,
                self.repo,
                BLOB_NEW_PATH,
            )
