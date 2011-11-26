# -*- coding: UTF-8 -*-
#
# Copyright 2011 J. David Ibáñez
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

from pygit2 import Signature
from .utils import NoRepoTestCase


__author__ = 'jdavid.ibp@gmail.com (J. David Ibáñez)'



class SignatureTest(NoRepoTestCase):

    def test_default(self):
        signature = Signature('Foo Ibáñez', 'foo@example.com', 1322174594, 60)
        encoding = signature._encoding
        self.assertEqual(encoding, 'utf-8')
        self.assertEqual(signature.name, signature._name.decode(encoding))
        self.assertEqual(signature.name.encode(encoding), signature._name)

    def test_latin1(self):
        encoding = 'iso-8859-1'
        signature = Signature('Foo Ibáñez', 'foo@example.com', 1322174594, 60,
                              encoding)
        self.assertEqual(encoding, signature._encoding)
        self.assertEqual(signature.name, signature._name.decode(encoding))
        self.assertEqual(signature.name.encode(encoding), signature._name)


if __name__ == '__main__':
    unittest.main()
