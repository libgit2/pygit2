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

"""Tests for Blame objects."""

from __future__ import absolute_import
from __future__ import unicode_literals
import unittest
import pygit2
from pygit2 import GIT_OPT_GET_MWINDOW_SIZE, GIT_OPT_SET_MWINDOW_SIZE
from pygit2 import GIT_OPT_GET_SEARCH_PATH, GIT_OPT_SET_SEARCH_PATH
from pygit2 import GIT_CONFIG_LEVEL_SYSTEM, GIT_CONFIG_LEVEL_XDG, GIT_CONFIG_LEVEL_GLOBAL
from pygit2 import option
from . import utils

class OptionsTest(utils.NoRepoTestCase):

    def test_mwindow_size(self):
        new_size = 200 * 1024
        option(GIT_OPT_SET_MWINDOW_SIZE, new_size)
        self.assertEqual(new_size, option(GIT_OPT_GET_MWINDOW_SIZE))

    def test_mwindow_size_proxy(self):
        new_size = 300 * 1024
        pygit2.settings.mwindow_size = new_size

        self.assertEqual(new_size, pygit2.settings.mwindow_size)

    def test_search_path(self):
        paths = [(GIT_CONFIG_LEVEL_GLOBAL, '/tmp/global'),
                 (GIT_CONFIG_LEVEL_XDG,    '/tmp/xdg'),
                 (GIT_CONFIG_LEVEL_SYSTEM, '/tmp/etc')]

        for level, path in paths:
            option(GIT_OPT_SET_SEARCH_PATH, level, path)
            self.assertEqual(path, option(GIT_OPT_GET_SEARCH_PATH, level))

    def test_search_path_proxy(self):
        paths = [(GIT_CONFIG_LEVEL_GLOBAL, '/tmp2/global'),
                 (GIT_CONFIG_LEVEL_XDG,    '/tmp2/xdg'),
                 (GIT_CONFIG_LEVEL_SYSTEM, '/tmp2/etc')]

        for level, path in paths:
            pygit2.settings.search_path[level] = path
            self.assertEqual(path, pygit2.settings.search_path[level])

if __name__ == '__main__':
    unittest.main()
