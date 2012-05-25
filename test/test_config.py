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

import os
import unittest

import pygit2
from . import utils


__author__ = 'mlenders@elegosoft.com (M. Lenders)'

config_filename = "test_config"

class ConfigTest(utils.RepoTestCase):

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

    def test_new(self):
        config_write = pygit2.Config(config_filename)
        
        config_write['core.bare'] = False
        config_write['core.editor'] = 'ed'
        
        config_read = pygit2.Config(config_filename)
        self.assertTrue('core.bare' in config_write)
        self.assertEqual(config_write['core.bare'], 'false')
        self.assertTrue('core.editor' in config_write)
        self.assertEqual(config_write['core.editor'], 'ed')

        os.remove(config_filename)

    def test_read(self):
        config = self.repo.config

        self.assertRaises(TypeError, lambda: config[()])
        self.assertRaises(TypeError, lambda: config[-4])
        self.assertRaisesWithArg(pygit2.GitError, 
                "Invalid variable name: 'abc'", lambda: config['abc'])
        self.assertRaisesWithArg(KeyError, 'abc.def', lambda: config['abc.def'])

        self.assertTrue('core.bare' in config)
        self.assertEqual(config['core.bare'], 'false')
        self.assertTrue('core.editor' in config)
        self.assertEqual(config['core.editor'], 'ed')
        self.assertTrue('core.repositoryformatversion' in config)
        self.assertEqual(config['core.repositoryformatversion'], '0')

if __name__ == '__main__':
    unittest.main()
