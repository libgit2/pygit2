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

"""Tests for Blob objects."""

import io
from pathlib import Path

import pytest

import pygit2
from . import utils


BLOB_SHA = 'a520c24d85fbfc815d385957eed41406ca5a860b'
BLOB_CONTENT = """hello world
hola mundo
bonjour le monde
""".encode()
BLOB_NEW_CONTENT = b'foo bar\n'
BLOB_FILE_CONTENT = b'bye world\n'

BLOB_PATCH = r"""diff --git a/file b/file
index a520c24..95d09f2 100644
--- a/file
+++ b/file
@@ -1,3 +1 @@
-hello world
-hola mundo
-bonjour le monde
+hello world
\ No newline at end of file
"""

BLOB_PATCH_2 = """diff --git a/file b/file
index a520c24..d675fa4 100644
--- a/file
+++ b/file
@@ -1,3 +1 @@
-hello world
-hola mundo
-bonjour le monde
+foo bar
"""

BLOB_PATCH_DELETED = """diff --git a/file b/file
deleted file mode 100644
index a520c24..0000000
--- a/file
+++ /dev/null
@@ -1,3 +0,0 @@
-hello world
-hola mundo
-bonjour le monde
"""


def test_read_blob(testrepo):
    blob = testrepo[BLOB_SHA]
    assert blob.hex == BLOB_SHA
    sha = blob.id.hex
    assert sha == BLOB_SHA
    assert isinstance(blob, pygit2.Blob)
    assert not blob.is_binary
    assert pygit2.GIT_OBJ_BLOB == blob.type
    assert BLOB_CONTENT == blob.data
    assert len(BLOB_CONTENT) == blob.size
    assert BLOB_CONTENT == blob.read_raw()

def test_create_blob(testrepo):
    blob_oid = testrepo.create_blob(BLOB_NEW_CONTENT)
    blob = testrepo[blob_oid]

    assert isinstance(blob, pygit2.Blob)
    assert pygit2.GIT_OBJ_BLOB == blob.type

    assert blob_oid == blob.id
    assert utils.gen_blob_sha1(BLOB_NEW_CONTENT) == blob_oid.hex

    assert BLOB_NEW_CONTENT == blob.data
    assert len(BLOB_NEW_CONTENT) == blob.size
    assert BLOB_NEW_CONTENT == blob.read_raw()
    blob_buffer = memoryview(blob)
    assert len(BLOB_NEW_CONTENT) == len(blob_buffer)
    assert BLOB_NEW_CONTENT == blob_buffer
    def set_content():
        blob_buffer[:2] = b'hi'

    with pytest.raises(TypeError): set_content()

def test_create_blob_fromworkdir(testrepo):
    blob_oid = testrepo.create_blob_fromworkdir("bye.txt")
    blob = testrepo[blob_oid]

    assert isinstance(blob, pygit2.Blob)
    assert pygit2.GIT_OBJ_BLOB == blob.type

    assert blob_oid == blob.id
    assert utils.gen_blob_sha1(BLOB_FILE_CONTENT) == blob_oid.hex

    assert BLOB_FILE_CONTENT == blob.data
    assert len(BLOB_FILE_CONTENT) == blob.size
    assert BLOB_FILE_CONTENT == blob.read_raw()

def test_create_blob_fromworkdir_aspath(testrepo):
    blob_oid = testrepo.create_blob_fromworkdir(Path("bye.txt"))
    blob = testrepo[blob_oid]

    assert isinstance(blob, pygit2.Blob)

def test_create_blob_outside_workdir(testrepo):
    with pytest.raises(KeyError):
        testrepo.create_blob_fromworkdir(__file__)


def test_create_blob_fromdisk(testrepo):
    blob_oid = testrepo.create_blob_fromdisk(__file__)
    blob = testrepo[blob_oid]

    assert isinstance(blob, pygit2.Blob)
    assert pygit2.GIT_OBJ_BLOB == blob.type

def test_create_blob_fromiobase(testrepo):
    with pytest.raises(TypeError):
        testrepo.create_blob_fromiobase('bad type')

    f = io.BytesIO(BLOB_CONTENT)
    blob_oid = testrepo.create_blob_fromiobase(f)
    blob = testrepo[blob_oid]

    assert isinstance(blob, pygit2.Blob)
    assert pygit2.GIT_OBJ_BLOB == blob.type

    assert blob_oid == blob.id
    assert BLOB_SHA == blob_oid.hex

def test_diff_blob(testrepo):
    blob = testrepo[BLOB_SHA]
    old_blob = testrepo['3b18e512dba79e4c8300dd08aeb37f8e728b8dad']
    patch = blob.diff(old_blob, old_as_path="hello.txt")
    assert len(patch.hunks) == 1

def test_diff_blob_to_buffer(testrepo):
    blob = testrepo[BLOB_SHA]
    patch = blob.diff_to_buffer("hello world")
    assert len(patch.hunks) == 1

def test_diff_blob_to_buffer_patch_patch(testrepo):
    blob = testrepo[BLOB_SHA]
    patch = blob.diff_to_buffer("hello world")
    assert patch.text == BLOB_PATCH

def test_diff_blob_to_buffer_delete(testrepo):
    blob = testrepo[BLOB_SHA]
    patch = blob.diff_to_buffer(None)
    assert patch.text == BLOB_PATCH_DELETED

def test_diff_blob_create(testrepo):
    old = testrepo[testrepo.create_blob(BLOB_CONTENT)]
    new = testrepo[testrepo.create_blob(BLOB_NEW_CONTENT)]

    patch = old.diff(new)
    assert patch.text == BLOB_PATCH_2

def test_blob_from_repo(testrepo):
    blob = testrepo[BLOB_SHA]
    patch_one = blob.diff_to_buffer(None)

    blob = testrepo[BLOB_SHA]
    patch_two = blob.diff_to_buffer(None)

    assert patch_one.text == patch_two.text
