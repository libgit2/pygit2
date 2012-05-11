# -*- coding: UTF-8 -*-
#
# Copyright 2012 elego
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

"""Tests for Index files."""

import unittest

import pygit2
from . import utils


__author__ = 'mlenders@elegosoft.com (M. Lenders)'


class IndexTest(utils.RepoTestCase):

    def test_config(self):
        self.assertNotEqual(None, self.repo.config)

    def test_global_config(self):
        try:
            self.assertNotEqual(None, pygit2.Config.get_global_config())
        except IOError:
            pass

    def test_system_config(self):
        try:
            self.assertNotEqual(None, pygit2.Config.get_system_config())
        except IOError:
            pass

if __name__ == '__main__':
    unittest.main()
