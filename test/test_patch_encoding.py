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

import pygit2


expected_diff = b"""diff --git a/iso-8859-1.txt b/iso-8859-1.txt
index e84e339..201e0c9 100644
--- a/iso-8859-1.txt
+++ b/iso-8859-1.txt
@@ -1 +1,2 @@
 Kristian H\xf8gsberg
+foo
"""

def test_patch_from_non_utf8():
    # blobs encoded in ISO-8859-1
    old_content = b'Kristian H\xf8gsberg\n'
    new_content = old_content + b'foo\n'
    patch = pygit2.Patch.create_from(
        old_content,
        new_content,
        old_as_path='iso-8859-1.txt',
        new_as_path='iso-8859-1.txt',
    )

    assert patch.data == expected_diff
    assert patch.text == expected_diff.decode('utf-8', errors='replace')

    # `patch.text` corrupted the ISO-8859-1 content as it forced UTF-8
    # decoding, so assert that we cannot get the original content back:
    assert patch.text.encode('utf-8') != expected_diff

def test_patch_create_from_blobs(encodingrepo):
    patch = pygit2.Patch.create_from(
        encodingrepo['e84e339ac7fcc823106efa65a6972d7a20016c85'],
        encodingrepo['201e0c908e3d9f526659df3e556c3d06384ef0df'],
        old_as_path='iso-8859-1.txt',
        new_as_path='iso-8859-1.txt',
    )

    assert patch.data == expected_diff
    assert patch.text == expected_diff.decode('utf-8', errors='replace')

    # `patch.text` corrupted the ISO-8859-1 content as it forced UTF-8
    # decoding, so assert that we cannot get the original content back:
    assert patch.text.encode('utf-8') != expected_diff
