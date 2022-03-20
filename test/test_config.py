# Copyright 2010-2021 The pygit2 contributors
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

from pathlib import Path

import pytest

from pygit2 import Config
from . import utils


CONFIG_FILENAME = "test_config"


@pytest.fixture
def config(testrepo):
    yield testrepo.config
    try:
        Path(CONFIG_FILENAME).unlink()
    except OSError:
        pass


def test_config(config):
    assert config is not None

def test_global_config():
    try:
        assert Config.get_global_config() is not None
    except IOError:
        # There is no user config
        pass

def test_system_config():
    try:
        assert Config.get_system_config() is not None
    except IOError:
        # There is no system config
        pass

def test_new():
    # Touch file
    open(CONFIG_FILENAME, 'w').close()

    config_write = Config(CONFIG_FILENAME)
    assert config_write is not None

    config_write['core.bare'] = False
    config_write['core.editor'] = 'ed'

    config_read = Config(CONFIG_FILENAME)
    assert 'core.bare' in config_read
    assert not config_read.get_bool('core.bare')
    assert 'core.editor' in config_read
    assert config_read['core.editor'] == 'ed'

def test_add():
    with open(CONFIG_FILENAME, "w") as new_file:
        new_file.write("[this]\n\tthat = true\n")
        new_file.write("[something \"other\"]\n\there = false")

    config = Config()
    config.add_file(CONFIG_FILENAME, 0)
    assert 'this.that' in config
    assert config.get_bool('this.that')
    assert 'something.other.here' in config
    assert not config.get_bool('something.other.here')

def test_add_aspath():
    with open(CONFIG_FILENAME, "w") as new_file:
        new_file.write("[this]\n\tthat = true\n")

    config = Config()
    config.add_file(Path(CONFIG_FILENAME), 0)
    assert 'this.that' in config

def test_read(config):
    with pytest.raises(TypeError): config[()]
    with pytest.raises(TypeError): config[-4]
    utils.assertRaisesWithArg(ValueError, "invalid config item name 'abc'",
                              lambda: config['abc'])
    utils.assertRaisesWithArg(KeyError, 'abc.def',
                              lambda: config['abc.def'])

    assert 'core.bare' in config
    assert not config.get_bool('core.bare')
    assert 'core.editor' in config
    assert config['core.editor'] == 'ed'
    assert 'core.repositoryformatversion' in config
    assert config.get_int('core.repositoryformatversion') == 0


def test_write(config):
    with pytest.raises(TypeError):
        config.__setitem__((), 'This should not work')

    assert 'core.dummy1' not in config
    config['core.dummy1'] = 42
    assert 'core.dummy1' in config
    assert config.get_int('core.dummy1') == 42

    assert 'core.dummy2' not in config
    config['core.dummy2'] = 'foobar'
    assert 'core.dummy2' in config
    assert config['core.dummy2'] == 'foobar'

    assert 'core.dummy3' not in config
    config['core.dummy3'] = True
    assert 'core.dummy3' in config
    assert config['core.dummy3']

    del config['core.dummy1']
    assert 'core.dummy1' not in config
    del config['core.dummy2']
    assert 'core.dummy2' not in config
    del config['core.dummy3']
    assert 'core.dummy3' not in config

def test_multivar():
    with open(CONFIG_FILENAME, "w") as new_file:
        new_file.write("[this]\n\tthat = foobar\n\tthat = foobeer\n")

    config = Config()
    config.add_file(CONFIG_FILENAME, 6)
    assert 'this.that' in config

    l = list(config.get_multivar('this.that'))
    assert ['foobar', 'foobeer'] == l
    l = list(config.get_multivar('this.that', 'bar'))
    assert ['foobar'] == l

    l = list(config.get_multivar('this.that', 'foo.*'))
    assert ['foobar', 'foobeer'] == l

    config.set_multivar('this.that', '^.*beer', 'fool')
    l = list(config.get_multivar('this.that', 'fool'))
    assert ['fool'] == l

    config.set_multivar('this.that', 'foo.*', 'foo-123456')
    l = list(config.get_multivar('this.that', 'foo.*'))
    assert ['foo-123456', 'foo-123456'] == l

    config.delete_multivar('this.that', 'bar')
    l = list(config.get_multivar('this.that', ''))
    assert ['foo-123456', 'foo-123456'] == l

    config.delete_multivar('this.that', 'foo-[0-9]+')
    l = list(config.get_multivar('this.that', ''))
    assert [] == l

def test_iterator(config):
    lst = {}
    for entry in config:
        assert entry.level > -1
        lst[entry.name] = entry.value

    assert 'core.bare' in lst
    assert lst['core.bare']

def test_parsing():
    assert Config.parse_bool("on")
    assert Config.parse_bool("1")

    assert 5 == Config.parse_int("5")
    assert 1024 == Config.parse_int("1k")
