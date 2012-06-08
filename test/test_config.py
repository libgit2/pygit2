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
        self.assertFalse(config_write['core.bare'])
        self.assertTrue('core.editor' in config_write)
        self.assertEqual(config_write['core.editor'], 'ed')

        os.remove(config_filename)
    
    def test_add(self):
        config = self.repo.config

        new_file = open(config_filename, "w")
        new_file.write("[this]\n\tthat = true\n")
        new_file.write("[something \"other\"]\n\there = false")
        new_file.close()

        config.add_file(config_filename, 0)
        self.assertTrue('this.that' in config)
        self.assertTrue(config['this.that'])
        self.assertTrue('something.other.here' in config)
        self.assertFalse(config['something.other.here'])
        
        os.remove(config_filename)

    def test_read(self):
        config = self.repo.config

        self.assertRaises(TypeError, lambda: config[()])
        self.assertRaises(TypeError, lambda: config[-4])
        self.assertRaisesWithArg(pygit2.GitError, 
                "Invalid variable name: 'abc'", lambda: config['abc'])
        self.assertRaisesWithArg(KeyError, 'abc.def', lambda: config['abc.def'])

        self.assertTrue('core.bare' in config)
        self.assertFalse(config['core.bare'])
        self.assertTrue('core.editor' in config)
        self.assertEqual(config['core.editor'], 'ed')
        self.assertTrue('core.repositoryformatversion' in config)
        self.assertEqual(config['core.repositoryformatversion'], 0)

        new_file = open(config_filename, "w")
        new_file.write("[this]\n\tthat = foobar\n\tthat = foobeer\n")
        new_file.close()

        config.add_file(config_filename, 0)
        self.assertTrue('this.that' in config)
        self.assertEqual(len(config.get_multivar('this.that')), 2)
        l = config.get_multivar('this.that', 'bar')
        self.assertEqual(len(l),1)
        self.assertEqual(l[0], 'foobar')
    
    def test_write(self):
        config = self.repo.config

        with self.assertRaises(TypeError):
            config[()] = 'This should not work'

        self.assertFalse('core.dummy1' in config)
        config['core.dummy1'] = 42
        self.assertTrue('core.dummy1' in config)
        self.assertEqual(config['core.dummy1'], 42)
        
        self.assertFalse('core.dummy2' in config)
        config['core.dummy2'] = 'foobar'
        self.assertTrue('core.dummy2' in config)
        self.assertEqual(config['core.dummy2'], 'foobar')
        
        self.assertFalse('core.dummy3' in config)
        config['core.dummy3'] = True
        self.assertTrue('core.dummy3' in config)
        self.assertTrue(config['core.dummy3'])

        del config['core.dummy1']
        self.assertFalse('core.dummy1' in config)
        del config['core.dummy2']
        self.assertFalse('core.dummy2' in config)
        del config['core.dummy3']
        self.assertFalse('core.dummy3' in config)

if __name__ == '__main__':
    unittest.main()
