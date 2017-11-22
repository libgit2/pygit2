# -*- coding: UTF-8 -*-
#
# Copyright 2010-2017 The pygit2 contributors
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

"""Tests for Submodule objects."""

# Import from the future
from __future__ import absolute_import

import os
import unittest

from . import utils

SUBM_NAME = 'submodule'
SUBM_PATH = 'submodule'
SUBM_URL = 'https://github.com/libgit2/pygit2'
SUBM_HEAD_SHA = '819cbff552e46ac4b8d10925cc422a30aa04e78e'

class SubmoduleTest(utils.SubmoduleRepoTestCase):

    def test_lookup_submodule(self):
        s = self.repo.lookup_submodule(SUBM_PATH)
        self.assertIsNotNone(s)

    def test_listall_submodules(self):
        submodules = self.repo.listall_submodules()
        self.assertEqual(len(submodules), 1)
        self.assertEqual(submodules[0], SUBM_PATH)

    @unittest.skipIf(utils.no_network(), "Requires network")
    def test_submodule_open(self):
        s = self.repo.lookup_submodule(SUBM_PATH)
        self.repo.init_submodules()
        self.repo.update_submodules()
        r = s.open()
        self.assertIsNotNone(r)
        self.assertEqual(str(r.head.target), SUBM_HEAD_SHA)

    def test_name(self):
        s = self.repo.lookup_submodule(SUBM_PATH)
        self.assertEqual(SUBM_NAME, s.name)

    def test_path(self):
        s = self.repo.lookup_submodule(SUBM_PATH)
        self.assertEqual(SUBM_PATH, s.path)

    def test_url(self):
        s = self.repo.lookup_submodule(SUBM_PATH)
        self.assertEqual(SUBM_URL, s.url)

    @unittest.skipIf(utils.no_network(), "Requires network")
    def test_init_and_update(self):
        subrepo_file_path = os.path.join(self.repo_path, 'submodule', 'setup.py')
        self.assertFalse(os.path.exists(subrepo_file_path))
        self.repo.init_submodules()
        self.repo.update_submodules()
        self.assertTrue(os.path.exists(subrepo_file_path))

    @unittest.skipIf(utils.no_network(), "Requires network")
    def test_specified_update(self):
        subrepo_file_path = os.path.join(self.repo_path, 'submodule', 'setup.py')
        self.assertFalse(os.path.exists(subrepo_file_path))
        self.repo.init_submodules(submodules=['submodule'])
        self.repo.update_submodules(submodules=['submodule'])
        self.assertTrue(os.path.exists(subrepo_file_path))

    @unittest.skipIf(utils.no_network(), "Requires network")
    def test_oneshot_update(self):
        subrepo_file_path = os.path.join(self.repo_path, 'submodule', 'setup.py')
        self.assertFalse(os.path.exists(subrepo_file_path))
        self.repo.update_submodules(init=True)
        self.assertTrue(os.path.exists(subrepo_file_path))

if __name__ == '__main__':
    unittest.main()
