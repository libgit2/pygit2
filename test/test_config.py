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

"""Tests for Index files."""

import os
import unittest

from pygit2 import Config
from . import utils


CONFIG_FILENAME = "test_config"

class ConfigTest(utils.RepoTestCase):

    def tearDown(self):
        super(ConfigTest, self).tearDown()
        try:
            os.remove(CONFIG_FILENAME)
        except OSError:
            pass

    def test_config(self):
        self.assertNotEqual(None, self.repo.config)

    def test_global_config(self):
        try:
            self.assertNotEqual(None, Config.get_global_config())
        except IOError:
            # There is no user config
            pass

    def test_system_config(self):
        try:
            self.assertNotEqual(None, Config.get_system_config())
        except IOError:
            # There is no system config
            pass

    def test_new(self):
        # Touch file
        open(CONFIG_FILENAME, 'w').close()

        config_write = Config(CONFIG_FILENAME)
        self.assertNotEqual(config_write, None)

        config_write['core.bare'] = False
        config_write['core.editor'] = 'ed'

        config_read = Config(CONFIG_FILENAME)
        self.assertTrue('core.bare' in config_read)
        self.assertFalse(config_read.get_bool('core.bare'))
        self.assertTrue('core.editor' in config_read)
        self.assertEqual(config_read['core.editor'], 'ed')

    def test_add(self):
        config = Config()

        new_file = open(CONFIG_FILENAME, "w")
        new_file.write("[this]\n\tthat = true\n")
        new_file.write("[something \"other\"]\n\there = false")
        new_file.close()

        config.add_file(CONFIG_FILENAME, 0)
        self.assertTrue('this.that' in config)
        self.assertTrue(config.get_bool('this.that'))
        self.assertTrue('something.other.here' in config)
        self.assertFalse(config.get_bool('something.other.here'))

    def test_read(self):
        config = self.repo.config

        self.assertRaises(TypeError, lambda: config[()])
        self.assertRaises(TypeError, lambda: config[-4])
        self.assertRaisesWithArg(ValueError, "Invalid config item name 'abc'",
                                 lambda: config['abc'])
        self.assertRaisesWithArg(KeyError, 'abc.def',
                                 lambda: config['abc.def'])

        self.assertTrue('core.bare' in config)
        self.assertFalse(config.get_bool('core.bare'))
        self.assertTrue('core.editor' in config)
        self.assertEqual(config['core.editor'], 'ed')
        self.assertTrue('core.repositoryformatversion' in config)
        self.assertEqual(config.get_int('core.repositoryformatversion'), 0)

        new_file = open(CONFIG_FILENAME, "w")
        new_file.write("[this]\n\tthat = foobar\n\tthat = foobeer\n")
        new_file.close()

        config.add_file(CONFIG_FILENAME, 0)
        self.assertTrue('this.that' in config)

        self.assertEqual(2, len(list(config.get_multivar('this.that'))))
        l = list(config.get_multivar('this.that', 'bar'))
        self.assertEqual(1, len(l))
        self.assertEqual(l[0], 'foobar')

    def test_write(self):
        config = self.repo.config

        self.assertRaises(TypeError, config.__setitem__,
                          (), 'This should not work')

        self.assertFalse('core.dummy1' in config)
        config['core.dummy1'] = 42
        self.assertTrue('core.dummy1' in config)
        self.assertEqual(config.get_int('core.dummy1'), 42)

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

        new_file = open(CONFIG_FILENAME, "w")
        new_file.write("[this]\n\tthat = foobar\n\tthat = foobeer\n")
        new_file.close()

        config.add_file(CONFIG_FILENAME, 5)
        self.assertTrue('this.that' in config)
        l = config.get_multivar('this.that', 'foo.*')
        self.assertEqual(2, len(list(l)))

        config.set_multivar('this.that', '^.*beer', 'fool')
        l = list(config.get_multivar('this.that', 'fool'))
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0], 'fool')

        config.set_multivar('this.that', 'foo.*', 'foo-123456')
        l = config.get_multivar('this.that', 'foo.*')
        self.assertEqual(2, len(list(l)))
        for i in l:
            self.assertEqual(i, 'foo-123456')

    def test_iterator(self):
        config = self.repo.config
        lst = {}

        for name in config:
            lst[name] = config[name]

        self.assertTrue('core.bare' in lst)
        self.assertTrue(lst['core.bare'])

    def test_parsing(self):
        self.assertTrue(Config.parse_bool("on"))
        self.assertTrue(Config.parse_bool("1"))

        self.assertEqual(5, Config.parse_int("5"))
        self.assertEqual(1024, Config.parse_int("1k"))

if __name__ == '__main__':
    unittest.main()
