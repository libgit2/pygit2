# -*- coding: UTF-8 -*-
#
# Copyright 2010 Google, Inc.
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
from binascii import b2a_hex
import unittest

import pygit2
from . import utils


__author__ = 'dborowitz@google.com (Dave Borowitz)'

BLOB_SHA = 'af431f20fc541ed6d5afede3e2dc7160f6f01f16'


class BlobTest(utils.BareRepoTestCase):

    def test_read_blob(self):
        blob = self.repo[BLOB_SHA]
        self.assertEqual(blob.hex, BLOB_SHA)
        sha = b2a_hex(blob.oid).decode('ascii')
        self.assertEqual(sha, BLOB_SHA)
        self.assertTrue(isinstance(blob, pygit2.Blob))
        self.assertEqual(pygit2.GIT_OBJ_BLOB, blob.type)
        self.assertEqual(b'a contents\n', blob.data)
        self.assertEqual(b'a contents\n', blob.read_raw())


if __name__ == '__main__':
    unittest.main()
