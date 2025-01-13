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

from __future__ import annotations

import contextlib
from functools import cached_property
from typing import TYPE_CHECKING, Callable, cast

# Import from pygit2
from .errors import check_error
from .ffi import C, ffi
from .utils import StrOrBytesPath, maybe_bytes, to_bytes

if TYPE_CHECKING:
    from _cffi_backend import _CDataBase as CData

    from ._ctyping import _CConfigEntry
    from .repository import BaseRepository


def str_to_bytes(value: StrOrBytesPath, name: str):
    if not isinstance(value, str):
        raise TypeError(f'{name} must be a string')

    return to_bytes(value)


class ConfigIterator:
    def __init__(self, config: Config, ptr: CData):
        self._iter = ptr
        self._config = config

    def __del__(self):
        C.git_config_iterator_free(self._iter)

    def __iter__(self):
        return self

    def __next__(self):
        return self._next_entry()

    def _next_entry(self):
        centry = ffi.new('git_config_entry **')
        err = C.git_config_next(centry, self._iter)
        check_error(err)

        return ConfigEntry._from_c(cast(_CConfigEntry, centry[0]), self)


class ConfigMultivarIterator(ConfigIterator):
    def __next__(self):  # type: ignore
        entry = self._next_entry()
        return entry.value


class Config:
    """Git configuration management."""

    if TYPE_CHECKING:
        _repo: BaseRepository
        _config: CData

    def __init__(self, path: StrOrBytesPath | None = None):
        cconfig = ffi.new('git_config **')

        if not path:
            err = C.git_config_new(cconfig)
        else:
            path = str_to_bytes(path, 'path')
            err = C.git_config_open_ondisk(cconfig, path)

        check_error(err, io=True)
        self._config = cconfig[0]

    @classmethod
    def from_c(cls, repo: BaseRepository, ptr: CData):
        config = cls.__new__(cls)
        config._repo = repo
        config._config = ptr

        return config

    def __del__(self):
        with contextlib.suppress(AttributeError):
            C.git_config_free(self._config)

    def _get(self, key: str | bytes):
        rkey = str_to_bytes(key, 'key')

        entry = ffi.new('git_config_entry **')
        err = C.git_config_get_entry(entry, self._config, rkey)

        return err, ConfigEntry._from_c(cast(_CConfigEntry, entry[0]))

    def _get_entry(self, key: str | bytes):
        err, entry = self._get(key)

        if err == C.GIT_ENOTFOUND:
            raise KeyError(key)

        check_error(err)
        return entry

    def __contains__(self, key: str):
        err, _ = self._get(key)

        if err == C.GIT_ENOTFOUND:
            return False

        check_error(err)

        return True

    def __getitem__(self, key: str):
        """
        When using the mapping interface, the value is returned as a string. In
        order to apply the git-config parsing rules, you can use
        :meth:`Config.get_bool` or :meth:`Config.get_int`.
        """
        entry = self._get_entry(key)

        return entry.value

    def __setitem__(self, key: str, value: int | bool | str):
        rkey = str_to_bytes(key, 'key')

        err = 0
        if isinstance(value, bool):
            err = C.git_config_set_bool(self._config, rkey, value)
        elif isinstance(value, int):
            err = C.git_config_set_int64(self._config, rkey, value)
        else:
            err = C.git_config_set_string(self._config, rkey, to_bytes(value))

        check_error(err)

    def __delitem__(self, key: str):
        rkey = str_to_bytes(key, 'key')

        err = C.git_config_delete_entry(self._config, rkey)
        check_error(err)

    def __iter__(self):
        """
        Iterate over configuration entries, returning a ``ConfigEntry``
        objects. These contain the name, level, and value of each configuration
        variable. Be aware that this may return multiple versions of each entry
        if they are set multiple times in the configuration files.
        """
        citer = ffi.new('git_config_iterator **')
        err = C.git_config_iterator_new(citer, self._config)
        check_error(err)

        ptr = cast(CData, citer[0])

        return ConfigIterator(self, ptr)

    def get_multivar(self, name: str | bytes, regex: CData | str | bytes | None = None):
        """Get each value of a multivar ''name'' as a list of strings.

        The optional ''regex'' parameter is expected to be a regular expression
        to filter the variables we're interested in.
        """
        name = str_to_bytes(name, 'name')
        regex = to_bytes(regex)

        citer = ffi.new('git_config_iterator **')
        err = C.git_config_multivar_iterator_new(citer, self._config, name, regex)
        check_error(err)
        cit = cast(CData, citer[0])

        return ConfigMultivarIterator(self, cit)

    def set_multivar(self, name: str | bytes, regex: str | bytes, value: str | bytes):
        """Set a multivar ''name'' to ''value''. ''regexp'' is a regular
        expression to indicate which values to replace.
        """
        name = str_to_bytes(name, 'name')
        regex = str_to_bytes(regex, 'regex')
        value = str_to_bytes(value, 'value')

        err = C.git_config_set_multivar(self._config, name, regex, value)
        check_error(err)

    def delete_multivar(self, name: str | bytes, regex: str | bytes):
        """Delete a multivar ''name''. ''regexp'' is a regular expression to
        indicate which values to delete.
        """
        name = str_to_bytes(name, 'name')
        regex = str_to_bytes(regex, 'regex')

        err = C.git_config_delete_multivar(self._config, name, regex)
        check_error(err)

    def get_bool(self, key: str | bytes):
        """Look up *key* and parse its value as a boolean as per the git-config
        rules. Return a boolean value (True or False).

        Truthy values are: 'true', 1, 'on' or 'yes'. Falsy values are: 'false',
        0, 'off' and 'no'
        """

        entry = self._get_entry(key)
        res = ffi.new('int *')
        err = C.git_config_parse_bool(res, entry.c_value)
        check_error(err)

        return cast(int, res[0]) != 0

    def get_int(self, key: str | bytes):
        """Look up *key* and parse its value as an integer as per the git-config
        rules. Return an integer.

        A value can have a suffix 'k', 'm' or 'g' which stand for 'kilo',
        'mega' and 'giga' respectively.
        """

        entry = self._get_entry(key)
        res = ffi.new('int64_t *')
        err = C.git_config_parse_int64(res, entry.c_value)
        check_error(err)

        return cast(int, res[0])

    def add_file(self, path: StrOrBytesPath, level: int = 0, force: int = 0):
        """Add a config file instance to an existing config."""

        err = C.git_config_add_file_ondisk(
            self._config, to_bytes(path), level, ffi.NULL, force
        )
        check_error(err)

    def snapshot(self):
        """Create a snapshot from this Config object.

        This means that looking up multiple values will use the same version
        of the configuration files.
        """
        ccfg = ffi.new('git_config **')
        err = C.git_config_snapshot(ccfg, self._config)
        check_error(err)

        return Config.from_c(self._repo, cast(CData, ccfg[0]))

    #
    # Methods to parse a string according to the git-config rules
    #

    @staticmethod
    def parse_bool(text: str):
        res = ffi.new('int *')
        err = C.git_config_parse_bool(res, to_bytes(text))
        check_error(err)

        return cast(int, res[0]) != 0

    @staticmethod
    def parse_int(text: str):
        res = ffi.new('int64_t *')
        err = C.git_config_parse_int64(res, to_bytes(text))
        check_error(err)

        return cast(int, res[0])

    #
    # Static methods to get specialized version of the config
    #

    @staticmethod
    def _from_found_config(fn: Callable[[CData], int]):
        buf = ffi.new('git_buf *', (ffi.NULL, 0))
        err = fn(buf)
        check_error(err, io=True)
        cpath = maybe_bytes(cast(CData, buf.ptr))
        assert cpath
        C.git_buf_dispose(buf)

        return Config(cpath.decode('utf-8'))

    @staticmethod
    def get_system_config():
        """Return a <Config> object representing the system configuration file."""
        return Config._from_found_config(C.git_config_find_system)

    @staticmethod
    def get_global_config():
        """Return a <Config> object representing the global configuration file."""
        return Config._from_found_config(C.git_config_find_global)

    @staticmethod
    def get_xdg_config():
        """Return a <Config> object representing the global configuration file."""
        return Config._from_found_config(C.git_config_find_xdg)


class ConfigEntry:
    """An entry in a configuation object."""

    if TYPE_CHECKING:
        _entry: _CConfigEntry

    @classmethod
    def _from_c(cls, ptr: _CConfigEntry, iterator: ConfigIterator | None = None):
        """Builds the entry from a ``git_config_entry`` pointer.

        ``iterator`` must be a ``ConfigIterator`` instance if the entry was
        created during ``git_config_iterator`` actions.
        """
        entry = cls.__new__(cls)
        entry._entry = ptr
        entry.iterator = iterator

        # It should be enough to keep a reference to iterator, so we only call
        # git_config_iterator_free when we've deleted all ConfigEntry objects.
        # But it's not, to reproduce the error comment the lines below and run
        # the script in https://github.com/libgit2/pygit2/issues/970
        # So instead we load the Python object immmediately. Ideally we should
        # investigate libgit2 source code.
        if iterator is not None:
            entry.raw_name = entry.raw_name
            entry.raw_value = entry.raw_value
            entry.level = entry.level

        return entry

    def __del__(self):
        if self.iterator is None:
            C.git_config_entry_free(self._entry)

    @property
    def c_value(self):
        """The raw ``cData`` entry value."""
        return self._entry.value

    @cached_property
    def raw_name(self):
        return cast(bytes, maybe_bytes(self._entry.name))

    @cached_property
    def raw_value(self):
        return cast(bytes, maybe_bytes(self.c_value))

    @cached_property
    def level(self):
        """The entry's ``git_config_level_t`` value."""
        return self._entry.level

    @property
    def name(self):
        """The entry's name."""
        return self.raw_name.decode('utf-8')

    @property
    def value(self):
        """The entry's value as a string."""
        return self.raw_value.decode('utf-8')
