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

"""Tests for Blob objects."""

from __future__ import absolute_import
from __future__ import unicode_literals
from os.path import dirname, join
import unittest

import pygit2
from . import utils


BLOB_SHA = 'a520c24d85fbfc815d385957eed41406ca5a860b'
BLOB_CONTENT = """hello world
hola mundo
bonjour le monde
""".encode()
BLOB_NEW_CONTENT = b'foo bar\n'
BLOB_FILE_CONTENT = b'bye world\n'


class BlobTest(utils.RepoTestCase):

    def test_read_blob(self):
        blob = self.repo[BLOB_SHA]
        self.assertEqual(blob.hex, BLOB_SHA)
        sha = blob.oid.hex
        self.assertEqual(sha, BLOB_SHA)
        self.assertTrue(isinstance(blob, pygit2.Blob))
        self.assertFalse(blob.is_binary)
        self.assertEqual(pygit2.GIT_OBJ_BLOB, blob.type)
        self.assertEqual(BLOB_CONTENT, blob.data)
        self.assertEqual(len(BLOB_CONTENT), blob.size)
        self.assertEqual(BLOB_CONTENT, blob.read_raw())

    def test_create_blob(self):
        blob_oid = self.repo.create_blob(BLOB_NEW_CONTENT)
        blob = self.repo[blob_oid]

        self.assertTrue(isinstance(blob, pygit2.Blob))
        self.assertEqual(pygit2.GIT_OBJ_BLOB, blob.type)

        self.assertEqual(blob_oid, blob.oid)
        self.assertEqual(
            utils.gen_blob_sha1(BLOB_NEW_CONTENT),
            blob_oid.hex)

        self.assertEqual(BLOB_NEW_CONTENT, blob.data)
        self.assertEqual(len(BLOB_NEW_CONTENT), blob.size)
        self.assertEqual(BLOB_NEW_CONTENT, blob.read_raw())

    def test_create_blob_fromworkdir(self):

        blob_oid = self.repo.create_blob_fromworkdir("bye.txt")
        blob = self.repo[blob_oid]

        self.assertTrue(isinstance(blob, pygit2.Blob))
        self.assertEqual(pygit2.GIT_OBJ_BLOB, blob.type)

        self.assertEqual(blob_oid, blob.oid)
        self.assertEqual(
            utils.gen_blob_sha1(BLOB_FILE_CONTENT),
            blob_oid.hex)

        self.assertEqual(BLOB_FILE_CONTENT, blob.data)
        self.assertEqual(len(BLOB_FILE_CONTENT), blob.size)
        self.assertEqual(BLOB_FILE_CONTENT, blob.read_raw())


    def test_create_blob_outside_workdir(self):
        path = __file__
        self.assertRaises(KeyError, self.repo.create_blob_fromworkdir, path)


    def test_create_blob_fromdisk(self):
        blob_oid = self.repo.create_blob_fromdisk(__file__)
        blob = self.repo[blob_oid]

        self.assertTrue(isinstance(blob, pygit2.Blob))
        self.assertEqual(pygit2.GIT_OBJ_BLOB, blob.type)

if __name__ == '__main__':
    unittest.main()
