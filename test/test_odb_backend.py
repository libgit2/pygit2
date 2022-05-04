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

"""Tests for Odb backends."""

# Standard Library
import binascii
from pathlib import Path

import pytest

# pygit2
import pygit2
from . import utils


BLOB_HEX = 'af431f20fc541ed6d5afede3e2dc7160f6f01f16'
BLOB_RAW = binascii.unhexlify(BLOB_HEX.encode('ascii'))
BLOB_OID = pygit2.Oid(raw=BLOB_RAW)


@pytest.fixture
def odb(barerepo):
    yield barerepo.odb, Path(barerepo.path) / 'objects'


def test_pack(odb):
    odb, path = odb

    pack = pygit2.OdbBackendPack(path)
    assert len(list(pack)) > 0
    for obj in pack:
        assert obj in odb

def test_loose(odb):
    odb, path = odb

    pack = pygit2.OdbBackendLoose(path, 5, False)
    assert len(list(pack)) > 0
    for obj in pack:
        assert obj in odb


class ProxyBackend(pygit2.OdbBackend):
    def __init__(self, source):
        super().__init__()
        self.source = source

    def read_cb(self, oid):
        return self.source.read(oid)

    def read_prefix_cb(self, oid):
        return self.source.read_prefix(oid)

    def read_header_cb(self, oid):
        typ, data = self.source.read(oid)
        return typ, len(data)

    def exists_cb(self, oid):
        return self.source.exists(oid)

    def exists_prefix_cb(self, oid):
        return self.source.exists_prefix(oid)

    def refresh_cb(self):
        self.source.refresh()

    def __iter__(self):
        return iter(self.source)


#
# Test a custom object backend alone (without adding it to an ODB)
# This doesn't make much sense, but it's possible.
#

@pytest.fixture
def proxy(barerepo):
    path = Path(barerepo.path) / 'objects'
    yield ProxyBackend(pygit2.OdbBackendPack(path))


def test_iterable(proxy):
    assert BLOB_HEX in [str(o) for o in proxy]

def test_read(proxy):
    with pytest.raises(TypeError):
        proxy.read(123)
    utils.assertRaisesWithArg(KeyError, '1' * 40, proxy.read, '1' * 40)

    ab = proxy.read(BLOB_OID)
    a = proxy.read(BLOB_HEX)
    assert ab == a
    assert (pygit2.GIT_OBJ_BLOB, b'a contents\n') == a

def test_read_prefix(proxy):
    a_hex_prefix = BLOB_HEX[:4]
    a3 = proxy.read_prefix(a_hex_prefix)
    assert (pygit2.GIT_OBJ_BLOB, b'a contents\n', BLOB_OID) == a3

def test_exists(proxy):
    with pytest.raises(TypeError):
        proxy.exists(123)

    assert proxy.exists('1' * 40) == False
    assert proxy.exists(BLOB_HEX) == True

def test_exists_prefix(proxy):
    a_hex_prefix = BLOB_HEX[:4]
    a3 = proxy.exists_prefix(a_hex_prefix)
    assert BLOB_HEX == a3.hex


#
# Test a custom object backend, through a Repository.
#

@pytest.fixture
def repo(barerepo):
    odb = pygit2.Odb()

    path = Path(barerepo.path) / 'objects'
    backend = pygit2.OdbBackendPack(path)
    backend = ProxyBackend(backend)
    odb.add_backend(backend, 1)

    repo = pygit2.Repository()
    repo.set_odb(odb)
    yield repo


def test_repo_read(repo):
    with pytest.raises(TypeError):
        repo[123]

    utils.assertRaisesWithArg(KeyError, '1' * 40, repo.__getitem__, '1' * 40)

    ab = repo[BLOB_OID]
    a = repo[BLOB_HEX]
    assert ab == a
