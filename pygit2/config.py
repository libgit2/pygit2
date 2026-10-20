# Copyright 2010-2026 The pygit2 contributors
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

from collections.abc import Callable, Iterator
from functools import cached_property
from os import PathLike
from typing import TYPE_CHECKING, Any, Optional, Self

# Import from pygit2
from .enums import ConfigLevel
from .errors import GitError, InvalidError, check_error
from .ffi import C, ffi
from .utils import encode_fs_path, encode_string

if TYPE_CHECKING:
    from ._libgit2.ffi import GitConfigC, GitConfigEntryC, GitConfigIteratorC
    from .repository import BaseRepository


def str_to_bytes(value: str | bytes, name: str) -> bytes:
    if isinstance(value, bytes):
        return value
    if isinstance(value, str):
        return encode_string(value)

    raise TypeError(f'{name} must be a string or bytes')


class _BaseIterator:
    def __init__(self, config: 'Config', c_iter: 'GitConfigIteratorC') -> None:
        self._config = config
        self._c_iter = c_iter

        self._freed = False
        self._c_entry_ptr = ffi.new('git_config_entry **')

    def _free(self):
        if not self._freed:
            self._freed = True
            self._c_entry_ptr = None  # do not free; see comment in _next_entry
            C.git_config_iterator_free(self._c_iter)

    def __del__(self) -> None:
        self._free()  # fallback in case we never hit StopIteration below

    def __iter__(self) -> Self:
        return self

    def _next_entry(self) -> 'ConfigEntry':
        try:
            # git_config_next (or, rather, the file backend specifically) reuses a
            # git_config_entry buffer from one call to the next. And more so than just
            # this, it reuses a buffer even from one iterator to the next. It's a
            # matter of discussion whether this is correct behavior, but what it means
            # is that we should never call git_config_entry_free on an entry allocated
            # by git_config_next. And, in fact, we must completely copy the data out of
            # one entry before the next git_config_next invocation, or else it might
            # get corrupted. See:
            # - https://github.com/libgit2/libgit2/issues/7307
            # - https://github.com/libgit2/pygit2/issues/970
            # - https://libgit2.org/docs/reference/v1.9.4/config/git_config_next.html
            self._config._stored_exception = None
            err = C.git_config_next(self._c_entry_ptr, self._c_iter)
            check_error(err, user_exception=self._config._stored_exception)
            return ConfigEntry(self._c_entry_ptr[0])
        except StopIteration:
            self._free()  # release the memory as soon as we can
            raise


class ConfigIterator(_BaseIterator):
    def __next__(self) -> 'ConfigEntry':
        return self._next_entry()


class ConfigMultivarIterator(_BaseIterator):
    def __next__(self) -> str | None:
        entry = self._next_entry()
        return entry.value


class Config:
    """Git configuration management.

    This class is for the reading and writing of Git configuration files.
    Configuration files are read individually, either by passing a path into
    the constructor or by using one of the static methods
    :meth:`Config.get_system_config`, :meth:`Config.get_global_config`, or
    :meth:`Config.get_xdg_config`. Additional files can be loaded into the
    `Config` object using :meth:`Config.add_file`.

    Changes made to the configuration with :meth:`Config.set_multivar` are
    immediately persisted to disk. Reads performed with accessor methods like
    :meth:`Config.get_multivar` or :meth:`Config.__getitem__` may result in
    reading from different versions of the configuration file if this or
    another process has modified the file. To avoid this and have all read
    operations occur against the same version of the configuration file, use
    :meth:`Config.snapshot()` to create a snapshot of the current config. This
    is especially important when iterating, as the contents of the config
    might change mid-iteration if you don't use a snapshot.

    This class can technically be used to manually read and write a repository's
    configuration file by pointing the constructor to the repository's
    ``.git/config`` file, but this is not recommended. The resulting ``Config``
    object represents only the configuration directly within ``.git/config``.
    It does not represent the total effective configuration for that repository
    that includes the combined system, global (user), and global (user) XDG.
    Instead, use :meth:`BaseRepository.config` for loading a repository's
    configuration.
    """

    _repo: Optional['BaseRepository']
    _config: 'GitConfigC'

    def __init__(self, path: PathLike | str | None = None) -> None:
        self._stored_exception: BaseException | None = None

        cconfig = ffi.new('git_config **')

        if not path:
            err = C.git_config_new(cconfig)
        else:
            path_bytes = encode_fs_path(path)
            err = C.git_config_open_ondisk(cconfig, path_bytes)

        check_error(err, io=True)
        self._repo = None
        self._config = cconfig[0]

    @classmethod
    def from_c(cls, repo: Optional['BaseRepository'], ptr: 'GitConfigC') -> 'Config':
        config = cls.__new__(cls)
        config._repo = repo
        config._config = ptr

        return config

    def __del__(self) -> None:
        try:
            C.git_config_free(self._config)
        except AttributeError:
            pass

    def _get(self, name: str | bytes) -> tuple[int, 'ConfigEntry | None']:
        name = str_to_bytes(name, 'name')

        c_entry_ptr = ffi.new('git_config_entry **')
        err = C.git_config_get_entry(c_entry_ptr, self._config, name)

        if err >= 0:
            try:
                return err, ConfigEntry(c_entry_ptr[0])
            finally:
                C.git_config_entry_free(c_entry_ptr[0])

        return err, None

    def _get_entry(self, key: str | bytes) -> 'ConfigEntry':
        err, entry = self._get(key)

        if err == C.GIT_ENOTFOUND:
            raise KeyError(key)

        check_error(err)
        assert entry is not None
        return entry

    def __contains__(self, key: str | bytes) -> bool:
        err, cstr = self._get(key)

        if err == C.GIT_ENOTFOUND:
            return False

        check_error(err)

        return True

    def __getitem__(self, key: str | bytes) -> str | None:
        """
        When using the mapping interface, the value is returned as a string. In
        order to apply the git-config parsing rules, you can use
        :meth:`Config.get_bool` or :meth:`Config.get_int`.
        """
        entry = self._get_entry(key)

        return entry.value

    def __setitem__(self, key: str | bytes, value: bool | int | str | bytes) -> None:
        key = str_to_bytes(key, 'key')

        err = 0
        if isinstance(value, bool):
            err = C.git_config_set_bool(self._config, key, value)
        elif isinstance(value, int):
            err = C.git_config_set_int64(self._config, key, value)
        else:
            err = C.git_config_set_string(self._config, key, encode_string(value))

        check_error(err)

    def __delitem__(self, key: str | bytes) -> None:
        key = str_to_bytes(key, 'key')

        err = C.git_config_delete_entry(self._config, key)
        check_error(err)

    def __iter__(self) -> Iterator['ConfigEntry']:
        """
        Iterate over configuration entries, returning a ``ConfigEntry``
        objects. These contain the name, level, and value of each configuration
        variable. Be aware that this may return multiple versions of each entry
        if they are set multiple times in the configuration files.
        """
        citer = ffi.new('git_config_iterator **')
        err = C.git_config_iterator_new(citer, self._config)
        check_error(err)

        return ConfigIterator(self, citer[0])

    def get_multivar(
        self, name: str | bytes, regex: str | None = None
    ) -> Iterator[str | None]:
        """Get each value of a multivar ''name'' as a list of strings.

        The optional ''regex'' parameter is expected to be a regular expression
        to filter the variables we're interested in.
        """
        name = str_to_bytes(name, 'name')
        regex_bytes = encode_string(regex or None)

        citer = ffi.new('git_config_iterator **')
        err = C.git_config_multivar_iterator_new(citer, self._config, name, regex_bytes)
        check_error(err)

        return ConfigMultivarIterator(self, citer[0])

    def set_multivar(
        self, name: str | bytes, regex: str | bytes, value: str | bytes
    ) -> None:
        """Set a multivar ''name'' to ''value''. ''regexp'' is a regular
        expression to indicate which values to replace. Changes are persisted
        to the configuration file(s) backing this ``Config``.
        """
        name = str_to_bytes(name, 'name')
        regex = str_to_bytes(regex, 'regex')
        value = str_to_bytes(value, 'value')

        err = C.git_config_set_multivar(self._config, name, regex, value)
        check_error(err)

    def delete_multivar(self, name: str | bytes, regex: str | bytes) -> None:
        """Delete a multivar ''name''. ''regexp'' is a regular expression to
        indicate which values to delete. Changes are persisted to the
        configuration file(s) backing this ``Config``.
        """
        name = str_to_bytes(name, 'name')
        regex = str_to_bytes(regex, 'regex')

        err = C.git_config_delete_multivar(self._config, name, regex)
        check_error(err)

    def get_bool(self, name: str | bytes) -> bool:
        """Obtain the last value found for a config var with name ``name`` as a boolean.

        Looks for a config var with name ``name`` and returns its value as a ``bool``.
        If the config var found is a multivar, only the last value is returned. If you
        need all the values of a multivar, use :meth:`Config.parse_bool` on each
        value returned by :meth:`Config.get_multivar`, instead.

        If this ``Config`` is backed by multiple files/backends, the one with the highest
        :class:`pygit2.enums.ConfigLevel` is searched first, and then the next-highest
        level, and so on.

        Truthy values are: 'true', '1', 'on', 'yes', or ``NULL``.
        Falsy values are: 'false', '0', 'off', 'no', or an empty value.

        :param name: The name of the config var to look for.

        :returns: The boolean value found for the config var with name ``name`` as
                  parsed by ``git_config_parse_bool`` rules.

        :raises KeyError: If no config var with name ``name`` is found in any
                          of this ``Config``'s files/backends.
        :raises ValueError: If the value does not match one of the expected truthy
                            or falsy values.
        """
        entry = self._get_entry(name)
        return self.parse_bool(entry.value)

    def get_int(self, name: bytes | str) -> int:
        """Obtain the last value found for a config var with name ``name`` as an integer.

        Looks for a config var with name ``name`` and returns its value as an ``int``.
        If the config var found is a multivar, only the last value is returned. If you
        need all the values of a multivar, use :meth:`Config.parse_int` on each
        value returned by :meth:`Config.get_multivar`, instead.

        If this ``Config`` is backed by multiple files/backends, the one with the highest
        :class:`pygit2.enums.ConfigLevel` is searched first, and then the next-highest
        level, and so on.

        A value can have a suffix 'k', 'm', or 'g' (lower or upper case) which stand for
        'kilo', 'mega', and 'giga', respectively. The values are calculated with powers
        of 2, not powers of 10.

        :param name: The name of the config var to look for.

        :returns: The integer value found for the config var with name ``name`` as
                  parsed by ``git_config_parse_int64`` rules.

        :raises KeyError: If no config var with name ``name`` is found in any
                          of this ``Config``'s files/backends.
        :raises ValueError: If the value is ``None`` or empty or otherwise does not
                            match the ``git_config_parse_int64`` parsing rules.
        """
        entry = self._get_entry(name)
        return self.parse_int(entry.value)

    def add_file(self, path: str | PathLike, level: int = 0, force: int = 0) -> None:
        """Add a config file instance to an existing config."""

        err = C.git_config_add_file_ondisk(
            self._config, encode_fs_path(path), level, ffi.NULL, force
        )
        check_error(err)

    def snapshot(self) -> 'Config':
        """Create a snapshot from this ``Config`` object.

        This means that looking up multiple values will use the same version
        of the configuration files.
        """
        ccfg = ffi.new('git_config **')
        err = C.git_config_snapshot(ccfg, self._config)
        check_error(err)

        return Config.from_c(self._repo, ccfg[0])

    #
    # Methods to parse a string according to the git-config rules
    #

    @staticmethod
    def parse_bool(text: str | None) -> bool:
        """Parses the provided string ``text`` as a boolean value according to
        Git config parsing rules.

        Truthy values are: 'true', '1', 'on', 'yes', or ``NULL``.
        Falsy values are: 'false', '0', 'off', 'no', or an empty value.

        :param text: The string to convert.

        :returns: The boolean value of the ``text`` as parsed by
                  ``git_config_parse_bool`` rules.

        :raises ValueError: If the value does not match one of the expected truthy
                            or falsy values.
        """
        res = ffi.new('int *')
        err = C.git_config_parse_bool(res, encode_string(text))

        try:
            check_error(err)
        except GitError as e:
            if err == -1 and getattr(e, 'error_class', None) == C.GIT_ERROR_CONFIG:
                # git_config_parse_bool returns a generic error code with class
                # GIT_ERROR_CONFIG if the value passed is not valid. Make that a
                # ValueError to be Pythonic.
                raise InvalidError(e.args[0])
            raise

        return res[0] != 0

    @staticmethod
    def parse_int(text: str | None) -> int:
        """Parses the provided string ``text`` as an integer value according to
        Git config parsing rules.

        A value can have a suffix 'k', 'm', or 'g' (lower or upper case) which stand for
        'kilo', 'mega', and 'giga', respectively. The values are calculated with powers
        of 2, not powers of 10.

        :param text: The string to convert.

        :returns: The integer value of the ``text`` as parsed by
                  ``git_config_parse_int64`` rules.

        :raises ValueError: If the value is ``None`` or empty or otherwise does not
                            match the ``git_config_parse_int64`` parsing rules.
        """
        if not text:
            raise ValueError(f'Text value {text!r} is not parseable as an integer.')

        res = ffi.new('int64_t *')
        err = C.git_config_parse_int64(res, encode_string(text))

        try:
            check_error(err)
        except GitError as e:
            if err == -1 and getattr(e, 'error_class', None) == C.GIT_ERROR_CONFIG:
                # git_config_parse_int64 returns a generic error code with class
                # GIT_ERROR_CONFIG if the value passed is not valid. Make that a
                # ValueError to be Pythonic.
                raise InvalidError(e.args[0])
            raise

        return res[0]

    #
    # Static methods to get specialized version of the config
    #

    @staticmethod
    def _from_found_config(fn: Callable) -> 'Config':
        buf = ffi.new('git_buf *', (ffi.NULL, 0))
        err = fn(buf)
        check_error(err, io=True)
        cpath = ffi.string(buf.ptr).decode('utf-8')
        C.git_buf_dispose(buf)

        return Config(cpath)

    @staticmethod
    def get_system_config() -> 'Config':
        """Return a ``Config`` object representing the system configuration file.

        The system configuration file is the one found at ``/etc/gitconfig`` or
        ``%PROGRAMFILES%\\Git\\etc\\gitconfig``, depending on the operating system.
        """
        return Config._from_found_config(C.git_config_find_system)

    @staticmethod
    def get_global_config() -> 'Config':
        """Return a ``Config`` object representing the global configuration file.

        The global configuration file is the one found at the standard user config
        location for Git, which is ``$HOME/.gitconfig``. This will not find the file
        at the XDG-compatible user config file location (for that, see
        :meth:`Config.get_xdg_config`).
        """
        return Config._from_found_config(C.git_config_find_global)

    @staticmethod
    def get_xdg_config() -> 'Config':
        """Return a ``Config`` object representing the XDG-compatible global configuration file.

        The XDG-compatible user config file follows the XDG Base Directory Specification.
        This file is located at ``$HOME/.config/git/config``. This will not find the file
        at the standard user config location (for that, see :meth:`Config.get_global_config`).
        """
        return Config._from_found_config(C.git_config_find_xdg)


class ConfigEntry:
    """An entry in a configuration object."""

    def __init__(self, c_entry: 'GitConfigEntryC') -> None:
        """For internal use only."""
        # The c_entry will not be valid for the entire life of this ConfigEntry, so we
        # must copy *all* of the data out of it at construction and *not* store the
        # c_entry.
        self._raw_name = ffi.string(c_entry.name)
        self._name = self._raw_name.decode('utf-8')

        self._raw_value: bytes | None = None
        if c_entry.value is not None and c_entry.value != ffi.NULL:
            self._raw_value = ffi.string(c_entry.value)

        self._raw_level = c_entry.level
        self._level = ConfigLevel(self._raw_level)

    @property
    def raw_name(self) -> bytes:
        """The entry's name as encoded bytes.

        :returns: The raw name obtained from the entry without decoding it.
        """
        return self._raw_name

    @property
    def raw_value(self) -> bytes | None:
        """The entry's value as encoded bytes.

        The value may be ``None`` if the config entry this represents was a
        valueless flag.

        :returns: The raw value obtained from the entry without decoding it.
        """
        return self._raw_value

    @property
    def raw_level(self) -> int:
        """The entry's level as an integer.

        :returns: The raw ``git_config_level_t`` value from the entry.
        """
        return self._raw_level

    @property
    def level(self) -> ConfigLevel:
        """The entry's level as a :class:`pygit2.enums.ConfigLevel`.

        :returns: The ``ConfigLevel`` equivalent of the entry's ``git_config_level_t``.
        """
        return self._level

    @property
    def name(self) -> str:
        """The entry's name.

        :returns: The name.
        """
        return self._name

    @cached_property
    def value(self) -> str | None:
        """The entry's value as a string.

        The value may be ``None`` if the config entry this represents was a
        valueless flag.

        The value is UTF-8 decoded from the :meth:`ConfigEntry.raw_value` the first time
        this property is accessed. If you know or suspect that the value cannot be UTF-8
        decoded, access :meth:`ConfigEntry.raw_value`, instead, and decode it by other
        means.

        :returns: The UTF-8 decoded string value from this entry.
        :raises UnicodeDecodeError: If the value cannot be UTF-8 decoded.
        """
        return self._raw_value.decode('utf-8') if self._raw_value is not None else None

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ConfigEntry):
            return NotImplemented
        return (
            self._raw_level == other._raw_level
            and self._raw_name == other._raw_name
            and self._raw_value == other._raw_value
        )

    def __hash__(self) -> int:
        return hash((self._raw_level, self._raw_name, self._raw_value))
