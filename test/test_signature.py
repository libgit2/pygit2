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

from __future__ import absolute_import
from __future__ import unicode_literals
import unittest
import time

from pygit2 import Signature
from .utils import NoRepoTestCase


class SignatureTest(NoRepoTestCase):

    def test_default(self):
        signature = Signature(
            'Foo', 'foo@example.com', 1322174594, 60)
        encoding = signature._encoding
        self.assertEqual(encoding, 'ascii')
        self.assertEqual(signature.name, signature.raw_name.decode(encoding))
        self.assertEqual(signature.name.encode(encoding), signature.raw_name)
        self.assertEqual(signature.email,
                         signature.raw_email.decode(encoding))
        self.assertEqual(signature.email.encode(encoding),
                         signature.raw_email)

    def test_ascii(self):
        self.assertRaises(UnicodeEncodeError,
                          Signature, 'Foo Ibáñez', 'foo@example.com')

    def test_latin1(self):
        encoding = 'iso-8859-1'
        signature = Signature(
            'Foo Ibáñez', 'foo@example.com', encoding=encoding)
        self.assertEqual(encoding, signature._encoding)
        self.assertEqual(signature.name, signature.raw_name.decode(encoding))
        self.assertEqual(signature.name.encode(encoding), signature.raw_name)
        self.assertEqual(signature.email,
                         signature.raw_email.decode(encoding))
        self.assertEqual(signature.email.encode(encoding),
                         signature.raw_email)

    def test_now(self):
        encoding = 'utf-8'
        signature = Signature(
            'Foo Ibáñez', 'foo@example.com', encoding=encoding)
        self.assertEqual(encoding, signature._encoding)
        self.assertEqual(signature.name, signature.raw_name.decode(encoding))
        self.assertEqual(signature.name.encode(encoding), signature.raw_name)
        self.assertEqual(signature.email,
                         signature.raw_email.decode(encoding))
        self.assertEqual(signature.email.encode(encoding),
                         signature.raw_email)
        self.assertTrue(abs(signature.time - time.time()) < 5)


if __name__ == '__main__':
    unittest.main()
