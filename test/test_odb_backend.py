# Copyright 2010-2019 The pygit2 contributors
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

"""Tests for Odb backends."""

# Import from the Standard Library
import binascii
import gc
import os
import unittest

import pytest

# Import from pygit2
from pygit2 import Odb, OdbBackend, OdbBackendPack, OdbBackendLoose, Oid
from pygit2 import GIT_OBJ_ANY, GIT_OBJ_BLOB

from . import utils

BLOB_HEX = 'af431f20fc541ed6d5afede3e2dc7160f6f01f16'
BLOB_RAW = binascii.unhexlify(BLOB_HEX.encode('ascii'))
BLOB_OID = Oid(raw=BLOB_RAW)

class OdbBackendTest(utils.BareRepoTestCase):

    def setUp(self):
        super().setUp()
        self.ref_odb = self.repo.odb
        self.obj_path = os.path.join(os.path.dirname(__file__),
                'data', 'testrepo.git', 'objects')

    def tearDown(self):
        del self.ref_odb
        gc.collect()
        super().tearDown()

    def test_pack(self):
        pack = OdbBackendPack(self.obj_path)
        assert len(list(pack)) > 0
        for obj in pack:
            assert obj in self.ref_odb

    def test_loose(self):
        pack = OdbBackendLoose(self.obj_path, 5, False)
        assert len(list(pack)) > 0
        for obj in pack:
            assert obj in self.ref_odb

class ProxyBackend(OdbBackend):
    def __init__(self, source):
        super().__init__()
        self.source = source

    def read(self, oid):
        return self.source.read(oid)

    def read_prefix(self, oid):
        return self.source.read_prefix(oid)

    def read_header(self, oid):
        typ, data = self.source.read(oid)
        return typ, len(data)

    def exists(self, oid):
        return self.source.exists(oid)

    def exists_prefix(self, oid):
        return self.source.exists_prefix(oid)

    def __iter__(self):
        return iter(self.source)

class CustomBackendTest(utils.BareRepoTestCase):
    def setUp(self):
        super().setUp()
        self.obj_path = os.path.join(os.path.dirname(__file__),
                'data', 'testrepo.git', 'objects')
        self.odb = ProxyBackend(OdbBackendPack(self.obj_path))

    def test_iterable(self):
        assert BLOB_HEX in [str(o) for o in self.odb]

    def test_read(self):
        with pytest.raises(TypeError): self.odb.read(123)
        self.assertRaisesWithArg(KeyError, '1' * 40, self.odb.read, '1' * 40)

        ab = self.odb.read(BLOB_OID)
        a = self.odb.read(BLOB_HEX)
        assert ab == a
        assert (GIT_OBJ_BLOB, b'a contents\n') == a

    def test_read_prefix(self):
        a_hex_prefix = BLOB_HEX[:4]
        a3 = self.odb.read_prefix(a_hex_prefix)
        assert (GIT_OBJ_BLOB, b'a contents\n', BLOB_OID) == a3

    def test_exists(self):
        with pytest.raises(TypeError): self.odb.exists(123)

        assert self.odb.exists('1' * 40) == False
        assert self.odb.exists(BLOB_HEX) == True

    def test_exists_prefix(self):
        a_hex_prefix = BLOB_HEX[:4]
        a3 = self.odb.exists_prefix(a_hex_prefix)
        assert BLOB_HEX == a3.hex
