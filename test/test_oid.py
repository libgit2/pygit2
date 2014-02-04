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

"""Tests for Object ids."""

# Import from the future
from __future__ import absolute_import
from __future__ import unicode_literals

# Import from the Standard Library
from binascii import unhexlify
from sys import version_info
import unittest

# Import from pygit2
from pygit2 import Oid
from . import utils


HEX = "15b648aec6ed045b5ca6f57f8b7831a8b4757298"
RAW = unhexlify(HEX.encode('ascii'))


class OidTest(utils.BareRepoTestCase):

    def test_raw(self):
        oid = Oid(raw=RAW)
        self.assertEqual(oid.raw, RAW)
        self.assertEqual(str(oid), HEX)

    def test_hex(self):
        oid = Oid(hex=HEX)
        self.assertEqual(oid.raw, RAW)
        self.assertEqual(str(oid), HEX)

    def test_hex_bytes(self):
        if version_info[0] == 2:
            hex = bytes(HEX)
            oid = Oid(hex=hex)
            self.assertEqual(oid.raw, RAW)
            self.assertEqual(str(oid), HEX)
        else:
            hex = bytes(HEX, "ascii")
            self.assertRaises(TypeError, Oid, hex=hex)

    def test_none(self):
        self.assertRaises(ValueError, Oid)

    def test_both(self):
        self.assertRaises(ValueError, Oid, raw=RAW, hex=HEX)

    def test_long(self):
        self.assertRaises(ValueError, Oid, raw=RAW + b'a')
        self.assertRaises(ValueError, Oid, hex=HEX + 'a')

    def test_cmp(self):
        oid1 = Oid(raw=RAW)

        # Equal
        oid2 = Oid(hex=HEX)
        self.assertEqual(oid1, oid2)

        # Not equal
        oid2 = Oid(hex="15b648aec6ed045b5ca6f57f8b7831a8b4757299")
        self.assertNotEqual(oid1, oid2)

        # Other
        self.assertTrue(oid1 < oid2)
        self.assertTrue(oid1 <= oid2)
        self.assertFalse(oid1 == oid2)
        self.assertFalse(oid1 > oid2)
        self.assertFalse(oid1 >= oid2)

    def test_hash(self):
        s = set()
        s.add(Oid(raw=RAW))
        s.add(Oid(hex=HEX))
        self.assertEqual(len(s), 1)

        s.add(Oid(hex="0000000000000000000000000000000000000000"))
        s.add(Oid(hex="0000000000000000000000000000000000000001"))
        self.assertEqual(len(s), 3)


if __name__ == '__main__':
    unittest.main()
