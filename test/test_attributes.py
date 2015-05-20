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

# Import from the future
from __future__ import absolute_import
from __future__ import unicode_literals, print_function

# Import from the Standard Library
import binascii
import unittest
import tempfile
import os
from os.path import join, realpath
import sys

# Import from pygit2
from pygit2 import GIT_OBJ_ANY, GIT_OBJ_BLOB, GIT_OBJ_COMMIT
from pygit2 import init_repository, clone_repository, discover_repository
from pygit2 import Oid, Reference, hashfile
import pygit2
from . import utils

try:
    import __pypy__
except ImportError:
    __pypy__ = None

class RepositorySignatureTest(utils.RepoTestCase):

    def test_no_attr(self):
        self.assertIsNone(self.repo.get_attr('file', 'foo'))

        with open(join(self.repo.workdir, '.gitattributes'), 'w+') as f:
            print('*.py  text\n', file=f)
            print('*.jpg -text\n', file=f)
            print('*.sh  eol=lf\n', file=f)

        self.assertIsNone(self.repo.get_attr('file.py', 'foo'))
        self.assertTrue(self.repo.get_attr('file.py', 'text'))
        self.assertFalse(self.repo.get_attr('file.jpg', 'text'))
        self.assertEqual("lf", self.repo.get_attr('file.sh', 'eol'))
