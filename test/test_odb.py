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

"""Tests for Odb objects."""

# Standard Library
import binascii
from pathlib import Path

import pytest

# pygit2
from pygit2 import Odb, Oid
from pygit2 import GIT_OBJ_ANY, GIT_OBJ_BLOB
from . import utils


BLOB_HEX = 'af431f20fc541ed6d5afede3e2dc7160f6f01f16'
BLOB_RAW = binascii.unhexlify(BLOB_HEX.encode('ascii'))
BLOB_OID = Oid(raw=BLOB_RAW)


def test_emptyodb(barerepo):
    odb = Odb()

    assert len([str(o) for o in odb]) == 0
    assert BLOB_HEX not in odb
    path = Path(barerepo.path) / 'objects'
    odb.add_disk_alternate(path)
    assert BLOB_HEX in odb


@pytest.fixture
def odb(barerepo):
    odb = barerepo.odb
    yield odb

def test_iterable(odb):
    assert BLOB_HEX in [str(o) for o in odb]

def test_contains(odb):
    assert BLOB_HEX in odb

def test_read(odb):
    with pytest.raises(TypeError):
        odb.read(123)
    utils.assertRaisesWithArg(KeyError, '1' * 40, odb.read, '1' * 40)

    ab = odb.read(BLOB_OID)
    a = odb.read(BLOB_HEX)
    assert ab == a
    assert (GIT_OBJ_BLOB, b'a contents\n') == a

    a2 = odb.read('7f129fd57e31e935c6d60a0c794efe4e6927664b')
    assert (GIT_OBJ_BLOB, b'a contents 2\n') == a2

    a_hex_prefix = BLOB_HEX[:4]
    a3 = odb.read(a_hex_prefix)
    assert (GIT_OBJ_BLOB, b'a contents\n') == a3

def test_write(odb):
    data = b"hello world"
    # invalid object type
    with pytest.raises(ValueError):
        odb.write(GIT_OBJ_ANY, data)

    oid = odb.write(GIT_OBJ_BLOB, data)
    assert type(oid) == Oid
