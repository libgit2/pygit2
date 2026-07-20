# Copyright 2010-2025 The pygit2 contributors
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

from collections.abc import Generator
from pathlib import Path

import pytest

from pygit2 import (
    Config,
    DefaultConfig,
    GitError,
    Repository,
    RepositoryConfig,
    Settings,
)

from . import utils


@pytest.fixture
def config_path(tmp_path: Path) -> Path:
    return tmp_path / 'test_config'


@pytest.fixture
def config(testrepo: Repository) -> Generator[RepositoryConfig, None, None]:
    yield testrepo.config


def test_config(config: Config) -> None:
    assert config is not None


def test_global_config() -> None:
    try:
        assert Config.get_global_config() is not None
    except IOError as e:
        settings = Settings()
        pytest.skip(f'Unavailable for testing with home dir = {settings.homedir}: {e}')


def test_system_config() -> None:
    try:
        assert Config.get_system_config() is not None
    except IOError as e:
        pytest.skip(f'Unavailable for testing: {e}')


def test_default_config() -> None:
    # this shouldn't throw, even if get_global_config and git_system_config don't find configs
    config = DefaultConfig()
    assert 'pygit2.test.default.config' not in config


def test_new(config_path: Path) -> None:
    # Touch file
    config_path.touch()

    config_write = Config(str(config_path))
    assert config_write is not None

    config_write['core.bare'] = False
    config_write['core.editor'] = 'ed'

    config_read = Config(str(config_path))
    assert 'core.bare' in config_read
    assert not config_read.get_bool('core.bare')
    assert 'core.editor' in config_read
    assert config_read['core.editor'] == 'ed'


def test_add(config_path: Path) -> None:
    with open(config_path, 'w') as new_file:
        new_file.write('[this]\n\tthat = true\n')
        new_file.write('[something "other"]\n\there = false')

    config = Config()
    config.add_file(config_path, 0)
    assert 'this.that' in config
    assert config.get_bool('this.that')
    assert 'something.other.here' in config
    assert not config.get_bool('something.other.here')


def test_add_aspath(config_path: Path) -> None:
    with open(config_path, 'w') as new_file:
        new_file.write('[this]\n\tthat = true\n')

    config = Config()
    config.add_file(config_path, 0)
    assert 'this.that' in config


def test_read(config: Config) -> None:
    with pytest.raises(TypeError):
        config[()]  # type: ignore
    with pytest.raises(TypeError):
        config[-4]  # type: ignore
    utils.assertRaisesWithArg(
        ValueError, "invalid config item name 'abc'", lambda: config['abc']
    )
    utils.assertRaisesWithArg(KeyError, 'abc.def', lambda: config['abc.def'])

    assert 'core.bare' in config
    assert not config.get_bool('core.bare')
    assert 'core.editor' in config
    assert config['core.editor'] == 'ed'
    assert 'core.repositoryformatversion' in config
    assert config.get_int('core.repositoryformatversion') == 0


def test_write(config: Config) -> None:
    with pytest.raises(TypeError):
        config.__setitem__((), 'This should not work')  # type: ignore

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


def test_multivar(config_path: Path) -> None:
    with open(config_path, 'w') as new_file:
        new_file.write('[this]\n\tthat = foobar\n\tthat = foobeer\n')

    config = Config()
    config.add_file(config_path, 6)
    assert 'this.that' in config

    assert ['foobar', 'foobeer'] == list(config.get_multivar('this.that'))
    assert ['foobar'] == list(config.get_multivar('this.that', 'bar'))
    assert ['foobar', 'foobeer'] == list(config.get_multivar('this.that', 'foo.*'))

    config.set_multivar('this.that', '^.*beer', 'fool')
    assert ['fool'] == list(config.get_multivar('this.that', 'fool'))

    config.set_multivar('this.that', 'foo.*', 'foo-123456')
    assert ['foo-123456', 'foo-123456'] == list(
        config.get_multivar('this.that', 'foo.*')
    )

    config.delete_multivar('this.that', 'bar')
    assert ['foo-123456', 'foo-123456'] == list(config.get_multivar('this.that', ''))

    config.delete_multivar('this.that', 'foo-[0-9]+')
    assert [] == list(config.get_multivar('this.that', ''))


def test_iterator(config: Config) -> None:
    lst = {}
    for entry in config:
        assert entry.level > -1
        lst[entry.name] = entry.value

    assert 'core.bare' in lst
    assert lst['core.bare']


def test_valueless_key_iteration(config_path: Path) -> None:
    # A valueless key (no `= value`) has a NULL value pointer in libgit2.
    # Iterating over such entries must not raise a RuntimeError.
    with open(config_path, 'w') as new_file:
        new_file.write('[section]\n\tvaluelesskey\n\tnormalkey = somevalue\n')

    config = Config()
    config.add_file(config_path, 6)

    entries = {entry.name: entry for entry in config}
    assert 'section.valuelesskey' in entries
    assert 'section.normalkey' in entries


def test_valueless_key_value(config_path: Path) -> None:
    # A valueless key must expose value=None and raw_value=None.
    with open(config_path, 'w') as new_file:
        new_file.write('[section]\n\tvaluelesskey\n\tnormalkey = somevalue\n')

    config = Config()
    config.add_file(config_path, 6)

    entries = {entry.name: entry for entry in config}
    assert entries['section.valuelesskey'].raw_value is None
    assert entries['section.valuelesskey'].value is None
    assert entries['section.normalkey'].raw_value == b'somevalue'
    assert entries['section.normalkey'].value == 'somevalue'


def test_parsing() -> None:
    assert Config.parse_bool('on')
    assert Config.parse_bool('1')

    assert 5 == Config.parse_int('5')
    assert 1024 == Config.parse_int('1k')


def test_repository_config_snapshot(config: RepositoryConfig) -> None:
    assert not config.is_snapshot
    assert 'core.bare' in config
    assert not config.get_bool('core.bare')
    assert 'core.editor' in config
    assert config['core.editor'] == 'ed'
    assert 'core.repositoryformatversion' in config
    assert config.get_int('core.repositoryformatversion') == 0

    snapshot = config.snapshot()
    assert not config.is_snapshot
    assert snapshot.is_snapshot
    assert 'core.bare' in snapshot
    assert not snapshot.get_bool('core.bare')
    assert 'core.editor' in snapshot
    assert snapshot['core.editor'] == 'ed'
    assert 'core.repositoryformatversion' in snapshot
    assert snapshot.get_int('core.repositoryformatversion') == 0
    utils.assertRaisesWithArg(
        GitError,
        "cannot set 'something.other.changed': the configuration is read-only",
        lambda: snapshot.set_multivar('something.other.changed', '^$', 'foo'),
    )
    utils.assertRaisesWithArg(
        TypeError,
        'A read-only config snapshot cannot be used as a context manager, '
        'because its backend data cannot be changed.',
        snapshot.__enter__,
    )

    assert 'core.snapshot1' not in config
    assert 'core.snapshot1' not in snapshot
    config['core.snapshot1'] = 42
    assert 'core.snapshot1' in config
    assert 'core.snapshot1' not in snapshot
    assert config.get_int('core.snapshot1') == 42
    utils.assertRaisesWithArg(
        KeyError,
        'core.snapshot1',
        lambda: snapshot.get_int('core.snapshot1'),
    )


def test_non_repository_config_snapshot(config_path: Path) -> None:
    with config_path.open('w') as new_file:
        new_file.write('[this]\n\tthat = true\n')
        new_file.write('[something "other"]\n\there = false')

    config = Config(config_path)
    assert not config.is_snapshot
    assert 'this.that' in config
    assert config.get_bool('this.that')
    assert 'something.other.here' in config
    assert not config.get_bool('something.other.here')

    snapshot = config.snapshot()
    assert not config.is_snapshot
    assert snapshot.is_snapshot
    assert 'this.that' in snapshot
    assert snapshot.get_bool('this.that')
    assert 'something.other.here' in snapshot
    assert not snapshot.get_bool('something.other.here')
    utils.assertRaisesWithArg(
        GitError,
        "cannot set 'something.other.changed': the configuration is read-only",
        lambda: snapshot.set_multivar('something.other.changed', '^$', 'foo'),
    )

    assert 'this.snapshot1' not in config
    assert 'this.snapshot1' not in snapshot
    config['this.snapshot1'] = 42
    assert 'this.snapshot1' in config
    assert 'this.snapshot1' not in snapshot
    assert config.get_int('this.snapshot1') == 42
    utils.assertRaisesWithArg(
        KeyError,
        'this.snapshot1',
        lambda: snapshot.get_int('this.snapshot1'),
    )


def test_default_config_snapshot() -> None:
    config = DefaultConfig()
    assert not config.is_snapshot
    snapshot = config.snapshot()
    assert not config.is_snapshot
    assert snapshot.is_snapshot
    utils.assertRaisesWithArg(
        GitError,
        "cannot set 'something.other.changed': the configuration is read-only",
        lambda: snapshot.set_multivar('something.other.changed', '^$', 'foo'),
    )
    utils.assertRaisesWithArg(
        TypeError,
        'A read-only config snapshot cannot be used as a context manager, '
        'because its backend data cannot be changed.',
        snapshot.__enter__,
    )


def test_repository_config_in_memory_overrides(config: RepositoryConfig) -> None:
    assert not config.is_snapshot
    assert 'core.bare' in config
    assert not config.get_bool('core.bare')
    assert 'core.editor' in config
    assert config['core.editor'] == 'ed'
    assert 'core.repositoryformatversion' in config
    assert config.get_int('core.repositoryformatversion') == 0

    assert 'core.override1' not in config
    assert 'core.override2' not in config
    assert 'core.override3' not in config
    assert 'core.override4' not in config
    assert 'core.override5' not in config
    assert 'core.local1' not in config
    assert 'core.local2' not in config
    assert 'core.local3' not in config

    with config:
        # these should be unaffected
        assert 'core.bare' in config
        assert not config.get_bool('core.bare')
        assert 'core.editor' in config
        assert config['core.editor'] == 'ed'
        assert 'core.repositoryformatversion' in config
        assert config.get_int('core.repositoryformatversion') == 0

        # now we should be able to add these to the local in-memory config
        assert 'core.override1' not in config
        config['core.override1'] = True
        assert 'core.override1' in config
        assert config.get_bool('core.override1')

        assert 'core.override2' not in config
        config['core.override2'] = 42
        assert 'core.override2' in config
        assert config.get_int('core.override2') == 42

        assert 'core.override3' not in config
        config['core.override3'] = 'foo'
        assert 'core.override3' in config
        assert config['core.override3'] == 'foo'

        assert 'core.override4' not in config
        config.set_multivar('core.override4', '^$', 'bar')
        assert 'core.override4' in config
        assert list(config.get_multivar('core.override4')) == ['bar']
        config.set_multivar('core.override4', '^$', 'baz')
        assert list(config.get_multivar('core.override4')) == ['bar', 'baz']
        config.set_multivar('core.override4', '^ba', 'qux')
        assert list(config.get_multivar('core.override4')) == ['qux']

        # try deleting some stuff
        assert 'core.override5' not in config
        config['core.override5'] = 'to be deleted'
        assert 'core.override5' in config
        assert config['core.override5'] == 'to be deleted'
        del config['core.override5']
        assert 'core.override5' not in config

        config.set_multivar('core.override5', '^$', 'lorem')
        config.set_multivar('core.override5', '^$', 'ipsum')
        config.set_multivar('core.override5', '^$', 'dolor')
        config.set_multivar('core.override5', '^$', 'simet')
        assert 'core.override5' in config
        assert list(config.get_multivar('core.override5')) == [
            'lorem',
            'ipsum',
            'dolor',
            'simet',
        ]
        config.delete_multivar('core.override5', r'.*or.*')
        assert 'core.override5' in config
        assert list(config.get_multivar('core.override5')) == ['ipsum', 'simet']
        config.delete_multivar('core.override5', r'.*')
        assert 'core.override5' not in config

        # these should not have been added yet
        assert 'core.local1' not in config
        assert 'core.local2' not in config
        assert 'core.local3' not in config

    # it all should have been erased
    assert 'core.override1' not in config
    assert 'core.override2' not in config
    assert 'core.override3' not in config
    assert 'core.override4' not in config
    assert 'core.override5' not in config

    # now let's add our local configs to the actual file backend
    assert 'core.local1' not in config
    config['core.local1'] = False
    assert 'core.local1' in config
    assert not config.get_bool('core.local1')
    assert 'core.local2' not in config
    config['core.local2'] = 56
    assert 'core.local2' in config
    assert config.get_int('core.local2') == 56
    assert 'core.local3' not in config
    config['core.local3'] = 'lorem ipsum'
    assert 'core.local3' in config
    assert config['core.local3'] == 'lorem ipsum'

    with config:
        # these should be unaffected
        assert 'core.bare' in config
        assert not config.get_bool('core.bare')
        assert 'core.editor' in config
        assert config['core.editor'] == 'ed'
        assert 'core.repositoryformatversion' in config
        assert config.get_int('core.repositoryformatversion') == 0
        assert 'core.local1' in config
        assert not config.get_bool('core.local1')
        assert 'core.local2' in config
        assert config.get_int('core.local2') == 56
        assert 'core.local3' in config
        assert config['core.local3'] == 'lorem ipsum'

        # let's try some different values now (and case insensitivity)
        assert 'core.override1' not in config
        config['core.oVeRrIdE1'] = False
        assert 'core.override1' in config
        assert 'core.oVeRrIdE1' in config
        assert not config.get_bool('core.override1')
        assert not config.get_bool('core.oVeRrIdE1')

        assert 'core.override2' not in config
        config['core.override2'] = 81
        assert 'core.override2' in config
        assert config.get_int('core.override2') == 81

        assert 'core.override3' not in config
        config['core.override3'] = 'dolor simet'
        assert 'core.override3' in config
        assert config['core.override3'] == 'dolor simet'

        # let's make sure snapshots work, too
        snapshot = config.snapshot()
        utils.assertRaisesWithArg(
            TypeError,
            'A read-only config snapshot cannot be used as a context manager, '
            'because its backend data cannot be changed.',
            snapshot.__enter__,
        )
        utils.assertRaisesWithArg(
            GitError,
            "cannot set 'core.override4': the configuration is read-only",
            lambda: snapshot.set_multivar('core.override4', '^$', 'foo'),
        )
        assert 'core.editor' in snapshot
        assert snapshot['core.editor'] == 'ed'
        assert 'core.repositoryformatversion' in snapshot
        assert snapshot.get_int('core.repositoryformatversion') == 0
        assert 'core.local1' in snapshot
        assert not snapshot.get_bool('core.local1')
        assert 'core.local2' in snapshot
        assert snapshot.get_int('core.local2') == 56
        assert 'core.local3' in snapshot
        assert snapshot['core.local3'] == 'lorem ipsum'
        assert 'core.oVeRrIdE1' in snapshot
        assert not snapshot.get_bool('core.override1')
        assert not snapshot.get_bool('core.oVeRrIdE1')
        assert 'core.override2' in snapshot
        assert snapshot.get_int('core.override2') == 81
        assert 'core.override3' in snapshot
        assert snapshot['core.override3'] == 'dolor simet'

    # it all should have been erased again
    assert 'core.override1' not in config
    assert 'core.override2' not in config
    assert 'core.override3' not in config
    assert 'core.override4' not in config

    # but these should not have been erased
    assert 'core.bare' in config
    assert not config.get_bool('core.bare')
    assert 'core.editor' in config
    assert config['core.editor'] == 'ed'
    assert 'core.repositoryformatversion' in config
    assert config.get_int('core.repositoryformatversion') == 0
    assert 'core.local1' in config
    assert not config.get_bool('core.local1')
    assert 'core.local2' in config
    assert config.get_int('core.local2') == 56
    assert 'core.local3' in config
    assert config['core.local3'] == 'lorem ipsum'


def test_default_config_in_memory_overrides() -> None:
    config = DefaultConfig()
    assert not config.is_snapshot

    assert 'core.override1' not in config
    assert 'core.override2' not in config
    assert 'core.override3' not in config
    assert 'core.override4' not in config
    assert 'core.override5' not in config

    with config:
        # now we should be able to add these to the local in-memory config
        assert 'core.override1' not in config
        config['core.override1'] = True
        assert 'core.override1' in config
        assert config.get_bool('core.override1')

        assert 'core.override2' not in config
        config['core.override2'] = 42
        assert 'core.override2' in config
        assert config.get_int('core.override2') == 42

        assert 'core.override3' not in config
        config['core.override3'] = 'foo'
        assert 'core.override3' in config
        assert config['core.override3'] == 'foo'

        assert 'core.override4' not in config
        config.set_multivar('core.override4', '^$', 'bar')
        assert 'core.override4' in config
        assert list(config.get_multivar('core.override4')) == ['bar']
        config.set_multivar('core.override4', '^$', 'baz')
        assert list(config.get_multivar('core.override4')) == ['bar', 'baz']
        config.set_multivar('core.override4', '^ba', 'qux')
        assert list(config.get_multivar('core.override4')) == ['qux']

        # try deleting some stuff
        assert 'core.override5' not in config
        config['core.override5'] = 'to be deleted'
        assert 'core.override5' in config
        assert config['core.override5'] == 'to be deleted'
        del config['core.override5']
        assert 'core.override5' not in config

        config.set_multivar('core.override5', '^$', 'lorem')
        config.set_multivar('core.override5', '^$', 'ipsum')
        config.set_multivar('core.override5', '^$', 'dolor')
        config.set_multivar('core.override5', '^$', 'simet')
        assert 'core.override5' in config
        assert list(config.get_multivar('core.override5')) == [
            'lorem',
            'ipsum',
            'dolor',
            'simet',
        ]
        config.delete_multivar('core.override5', r'.*or.*')
        assert 'core.override5' in config
        assert list(config.get_multivar('core.override5')) == ['ipsum', 'simet']
        config.delete_multivar('core.override5', r'.*')
        assert 'core.override5' not in config

    # it all should have been erased
    assert 'core.override1' not in config
    assert 'core.override2' not in config
    assert 'core.override3' not in config
    assert 'core.override4' not in config
    assert 'core.override5' not in config

    with config:
        # let's try some different values now (and case insensitivity)
        assert 'core.override1' not in config
        config['core.oVeRrIdE1'] = False
        assert 'core.override1' in config
        assert 'core.oVeRrIdE1' in config
        assert not config.get_bool('core.override1')
        assert not config.get_bool('core.oVeRrIdE1')

        assert 'core.override2' not in config
        config['core.override2'] = 81
        assert 'core.override2' in config
        assert config.get_int('core.override2') == 81

        assert 'core.override3' not in config
        config['core.override3'] = 'dolor simet'
        assert 'core.override3' in config
        assert config['core.override3'] == 'dolor simet'

        # let's make sure snapshots work, too
        snapshot = config.snapshot()
        utils.assertRaisesWithArg(
            TypeError,
            'A read-only config snapshot cannot be used as a context manager, '
            'because its backend data cannot be changed.',
            snapshot.__enter__,
        )
        utils.assertRaisesWithArg(
            GitError,
            "cannot set 'core.override4': the configuration is read-only",
            lambda: snapshot.set_multivar('core.override4', '^$', 'foo'),
        )
        assert 'core.oVeRrIdE1' in snapshot
        assert not snapshot.get_bool('core.override1')
        assert not snapshot.get_bool('core.oVeRrIdE1')
        assert 'core.override2' in snapshot
        assert snapshot.get_int('core.override2') == 81
        assert 'core.override3' in snapshot
        assert snapshot['core.override3'] == 'dolor simet'

    # it all should have been erased again
    assert 'core.override1' not in config
    assert 'core.override2' not in config
    assert 'core.override3' not in config
    assert 'core.override4' not in config
    assert 'core.override5' not in config
