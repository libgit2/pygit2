# Copyright 2010-2020 The pygit2 contributors
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

# Standard Library
import binascii
import gc
import os

import pytest

# pygit2
from pygit2 import OdbBackend, OdbBackendPack, OdbBackendLoose, Oid
from pygit2 import GIT_OBJ_BLOB
from . import utils


BLOB_HEX = 'af431f20fc541ed6d5afede3e2dc7160f6f01f16'
BLOB_RAW = binascii.unhexlify(BLOB_HEX.encode('ascii'))
BLOB_OID = Oid(raw=BLOB_RAW)


@pytest.fixture
def odb(barerepo):
    odb = barerepo.odb
    path = os.path.join(os.path.dirname(__file__), 'data', 'testrepo.git', 'objects')
    yield odb, path
    del odb
    gc.collect()

def test_pack(odb):
    odb, path = odb

    pack = OdbBackendPack(path)
    assert len(list(pack)) > 0
    for obj in pack:
        assert obj in odb

def test_loose(odb):
    odb, path = odb

    pack = OdbBackendLoose(path, 5, False)
    assert len(list(pack)) > 0
    for obj in pack:
        assert obj in odb


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


@pytest.fixture
def proxy(barerepo):
    path = os.path.join(os.path.dirname(__file__), 'data', 'testrepo.git', 'objects')
    yield ProxyBackend(OdbBackendPack(path))


def test_iterable(proxy):
    assert BLOB_HEX in [str(o) for o in proxy]

def test_read(proxy):
    with pytest.raises(TypeError):
        proxy.read(123)
    utils.assertRaisesWithArg(KeyError, '1' * 40, proxy.read, '1' * 40)

    ab = proxy.read(BLOB_OID)
    a = proxy.read(BLOB_HEX)
    assert ab == a
    assert (GIT_OBJ_BLOB, b'a contents\n') == a

def test_read_prefix(proxy):
    a_hex_prefix = BLOB_HEX[:4]
    a3 = proxy.read_prefix(a_hex_prefix)
    assert (GIT_OBJ_BLOB, b'a contents\n', BLOB_OID) == a3

def test_exists(proxy):
    with pytest.raises(TypeError):
        proxy.exists(123)

    assert proxy.exists('1' * 40) == False
    assert proxy.exists(BLOB_HEX) == True

def test_exists_prefix(proxy):
    a_hex_prefix = BLOB_HEX[:4]
    a3 = proxy.exists_prefix(a_hex_prefix)
    assert BLOB_HEX == a3.hex
