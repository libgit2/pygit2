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

import abc
import contextlib
import re
import threading
from collections.abc import Callable, Generator, Iterator
from os import PathLike
from types import TracebackType

# Suppressing UP035 because ruff complains about using `Type` instead of `type` but
# Sphinx complains about using `type`, and there's no workaround for the Sphinx issue.
from typing import (  # noqa: UP035
    TYPE_CHECKING,
    Literal,
    NoReturn,
    Self,
    Type,
    cast,
    overload,
    override,
)

try:
    from functools import cached_property
except ImportError:
    from cached_property import cached_property  # type: ignore

# Import from pygit2
from .enums import ConfigLevel
from .errors import check_error
from .ffi import C, ffi
from .utils import to_bytes

if TYPE_CHECKING:
    from ._libgit2.ffi import (
        GitConfigBackendC,
        GitConfigBackendEntryC,
        GitConfigC,
        GitConfigEntryC,
        GitConfigIteratorC,
        GitRepositoryC,
        PyGitConfigBackendEntryC,
        PyGitConfigBackendWrapperC,
        PyGitConfigIteratorEntryC,
        PyGitConfigIteratorWrapperC,
        _Pointer,
        char_pointer,
    )
    from .repository import BaseRepository


def str_to_bytes(value: str | bytes, name: str) -> bytes:
    if isinstance(value, bytes):
        return value
    if isinstance(value, str):
        return to_bytes(value)

    raise TypeError(f'{name} must be a string or bytes')


class _BaseIterator:
    def __init__(self, config, ptr) -> None:
        self._iter = ptr
        self._config = config

    def __del__(self) -> None:
        C.git_config_iterator_free(self._iter)

    def __iter__(self) -> Self:
        return self

    def _next_entry(self) -> 'ConfigEntry':
        self._config._stored_exception = None
        centry = ffi.new('git_config_entry **')
        err = C.git_config_next(centry, self._iter)
        check_error(err, user_exception=self._config._stored_exception)

        return ConfigEntry._from_c(centry[0], self)


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
    ``Config`` object using :meth:`Config.add_file`.

    Changes made to the configuration with one of the mutator methods are
    immediately persisted to disk. Reads performed with accessor methods like
    :meth:`Config.get_multivar` or :meth:`Config.__getitem__` may result in
    reading from different versions of the configuration file if this or
    another process has modified the file. To avoid this and have all read
    operations occur against the same version of the configuration file, use
    :meth:`Config.snapshot()` to create a snapshot of the current config. This
    is especially important when iterating, as the contents of the config
    might change mid-iteration if you don't use a snapshot.

    Some ``Config`` objects may be backed by multiple files/backends, such as
    if you call :meth:`Config.add_file` with different levels or construct
    one of :class:`DefaultConfig` or :class:`RepositoryConfig`. In this case,
    read operations begin at the backend with the highest
    :class:`pygit2.enums.ConfigLevel` and proceed down one level at a time,
    and write operations affect only the highest-level non-read-only backend.

    This class can technically be used to manually read and write a repository's
    local configuration by pointing the constructor to the repository's
    ``.git/config`` file, but this is not recommended. The resulting ``Config``
    object represents only the configuration directly within ``.git/config``.
    It does not represent the total effective configuration for that repository
    that includes the combined program, system, XDG, global (user), and local
    configurations. Instead, use :meth:`pygit2.repository.BaseRepository.config`
    or :meth:`pygit2.repository.BaseRepository.config_snapshot` for loading a
    local configuration and see :class:`RepositoryConfig` for special behaviors
    supported by the local configuration.

    For the non-repository global configuration used by Git during operations
    not involving an existing repository (such as cloning), see
    :class:`DefaultConfig`.
    """

    _config: 'GitConfigC'

    @overload
    def __init__(self, /):
        """Constructs a new, empty ``Config`` object pointing to no file.

        To make changes to this ``Config`` object, you must use :meth:`Config.add_file`.
        """
        ...

    @overload
    def __init__(self, path: PathLike | str, /) -> None:
        """Constructs a ``Config`` object backed by the specified file.

        The configuration from the specified file is loaded, and subsequent writes
        will persist to that file. The file backend is assigned
        :attr:`pygit2.enums.ConfigLevel.LOCAL`. Additional files can be added to the
        config, with different levels, using :meth:`Config.add_file`.

        :param path: The path to the configuration file to load as a string or path-like
                     value.
        :raises IOError: If the path specified does not exist or could not be opened.
        """
        ...

    @overload
    def __init__(self, *, c_config: 'GitConfigC', is_snapshot: bool) -> None:
        """For internal use only.

        Constructs a ``Config`` object from a config object pointer.
        """
        ...

    def __init__(
        self,
        path: PathLike | str | None = None,
        *,
        c_config: 'GitConfigC | None' = None,
        is_snapshot: bool = False,
    ) -> None:
        """Constructs a ``Config`` object.

        **Overload 1: __init__()**

        Constructs a new, empty ``Config`` object pointing to no file. To make changes
        to this ``Config`` object, you must use :meth:`Config.add_file`.

        **Overload 2: __init__(path)**

        The configuration from the specified file is loaded, and subsequent writes
        will persist to that file. The file backend is assigned
        :attr:`pygit2.enums.ConfigLevel.LOCAL`. Additional files can be added to the
        config, with different levels, using :meth:`Config.add_file`.

        :param path: The path to the configuration file to load as a string or path-like
                     value.
        :raises IOError: If the path specified does not exist or could not be opened.

        **Overload 3: __init__(c_config, is_snapshot)**

        For internal use only.
        """
        # ^^ see https://github.com/sphinx-doc/sphinx/issues/7787
        if path is not None and c_config is not None:
            raise ValueError('Cannot initialize Config from both path and c_config')

        self._is_snapshot = is_snapshot
        self._stored_exception: BaseException | None = None

        if c_config is not None:
            self._config = c_config
        else:
            c_config_ptr = ffi.new('git_config **')

            if not path:
                err = C.git_config_new(c_config_ptr)
            else:
                path_bytes = to_bytes(path)
                err = C.git_config_open_ondisk(c_config_ptr, path_bytes)

            check_error(err, io=True)
            self._config = c_config_ptr[0]

    def __del__(self) -> None:
        try:
            C.git_config_free(self._config)
        except AttributeError:
            pass

    def _check_error(self, err: int, io: bool = False):
        try:
            check_error(err, io=io, user_exception=self._stored_exception)
        finally:
            self._stored_exception = None

    def _get(self, name: str | bytes) -> tuple[int, 'ConfigEntry | None']:
        name = str_to_bytes(name, 'name')

        entry = ffi.new('git_config_entry **')
        err = C.git_config_get_entry(entry, self._config, name)

        if err >= 0:
            return err, ConfigEntry._from_c(entry[0])

        return err, None

    def _get_entry(self, name: str | bytes) -> 'ConfigEntry':
        self._stored_exception = None
        err, entry = self._get(name)

        if err == C.GIT_ENOTFOUND:
            raise KeyError(name)

        self._check_error(err)
        assert entry is not None
        return entry

    def __contains__(self, name: str | bytes) -> bool:
        """Indicates whether the configuration contains ``name``.

        :param name: The name of the config var to look for.
        :returns: ``True`` if any file/backend in this ``Config`` object contains any
                  config var with the name ``name``, ``False`` otherwise.
        """
        self._stored_exception = None
        err, _ = self._get(name)

        if err == C.GIT_ENOTFOUND:
            return False

        self._check_error(err)

        return True

    def __getitem__(self, name: str | bytes) -> str | None:
        """Obtain the first value found for a config var with name ``name``.

        Looks for a config var with name ``name`` and returns its value as a string
        or ``None`` if the config var exists but the value is empty. If you want to
        apply the Git config parsing rules, use :meth:`Config.get_bool` or
        :meth:`Config.get_int` instead of ``[name]``.

        If the config var found is a multivar, only the first value is returned. To
        obtain all values, use :meth:`Config.get_multivar` instead of ``[name]``.

        If this ``Config`` is backed by multiple files/backends, the one with the highest
        :class:`pygit2.enums.ConfigLevel` is searched first, and then the next-highest
        level, and so on.

        :param name: The name of the config var to look for.

        :returns: The string value found for the config var with name ``name`` or,
                  in the case of a valueless flag, ``None``.

        :raises KeyError: If no config var with name ``name`` is found in any
                          of this ``Config``'s files/backends.
        """
        entry = self._get_entry(name)

        return entry.value

    def __setitem__(self, name: str | bytes, value: bool | int | str | bytes) -> None:
        """Set the config var with name ``name`` to the specified ``value``.

        If this ``Config`` is backed by multiple files/backends, only the first
        non-read-only backend with the highest :class:`pygit2.enums.ConfigLevel` is
        changed. If that backend is a file, changes are persisted to disk immediately.

        If the config var exists already, it is replaced. If it is already a multivar,
        all values are removed in favor of this new value. If you want to add values
        to a multivar instead of replacing them, use :meth:`Config.set_multivar` instead
        of ``[name] = value``.

        :param name: The name of the config var to set.
        :param value: The new value to set.
        """
        self._stored_exception = None
        name = str_to_bytes(name, 'name')

        err: int
        if isinstance(value, bool):
            err = C.git_config_set_bool(self._config, name, value)
        elif isinstance(value, int):
            err = C.git_config_set_int64(self._config, name, value)
        else:
            err = C.git_config_set_string(self._config, name, to_bytes(value))

        self._check_error(err)

    def __delitem__(self, name: str | bytes) -> None:
        """Deletes the config var with name ``name``.

        If this ``Config`` is backed by multiple files/backends, only the first
        non-read-only backend with the highest :class:`pygit2.enums.ConfigLevel` is
        changed. If that backend is a file, changes are persisted to disk immediately.

        If the config var is a multivar, all values are removed. If you want to remove
        only some values, use :meth:`Config.delete_multivar` instead of ``del [name]``.

        :param name: Name of the config var to delete.
        :raises KeyError: If no config var with name ``name`` is found in the first
                          non-read-only backend with the highest ``ConfigLevel``.
        """
        self._stored_exception = None
        name = str_to_bytes(name, 'name')

        err = C.git_config_delete_entry(self._config, name)
        self._check_error(err)

    def __iter__(self) -> Iterator['ConfigEntry']:
        """Iterate over configuration entries in the form of
        :class:`pygit2.config.ConfigEntry` objects.

        Creates and returns an iterator over all of the entries in this ``Config``
        object. Entries contain the name, level, and value of each configuration
        variable. Be aware that this may return multiple versions of each entry
        if they are set multiple times in the configuration files.

        If this ``Config`` is backed by multiple files/backends, iteration begins with
        all config vars from the backend with the highest
        :class:`pygit2.enums.ConfigLevel` first, and then proceeds to the one with the
        next-highest level, and so on.

        :returns: An iterator over :class:`pygit2.config.ConfigEntry` objects.
        """
        self._stored_exception = None
        citer = ffi.new('git_config_iterator **')
        err = C.git_config_iterator_new(citer, self._config)
        self._check_error(err)

        return ConfigIterator(self, citer[0])

    def get_multivar(
        self,
        name: str | bytes,
        regex: str | None = None,
    ) -> Iterator[str | None]:
        """Get each value of a multivar ``name`` as an iterator of strings.

        If this ``Config`` is backed by multiple files/backends, iteration begins with
        all matching multivars from the backend with the highest
        :class:`pygit2.enums.ConfigLevel` first, and then proceeds to the one with the
        next-highest level, and so on.

        :param name: The name of the multivar to iterate.
        :param regex: If specified, only multivar values matching this regular expression
                      will be iterated. The regular expression is matched case-sensitively.
                      To iterate over all values, do not specify this argument, or use
                      the regular expression ``r'.*'``.

        :returns: An iterator of config var values, each of which will be either a
                  string or, in the case of a valueless flag, ``None``.

        :raises KeyError: If no config var with name ``name`` is found in any of the
                          files/backends for this config.
        """
        self._stored_exception = None
        name = str_to_bytes(name, 'name')
        regex_bytes = to_bytes(regex or None)

        citer = ffi.new('git_config_iterator **')
        err = C.git_config_multivar_iterator_new(citer, self._config, name, regex_bytes)
        self._check_error(err)

        return ConfigMultivarIterator(self, citer[0])

    def set_multivar(
        self,
        name: str | bytes,
        regex: str | bytes,
        value: str | bytes,
    ) -> None:
        """Add a ``value`` to multivar ``name``, optionally replacing other values
        matching ``regex``.

        If this ``Config`` is backed by multiple files/backends, only the first
        non-read-only backend with the highest :class:`pygit2.enums.ConfigLevel` is
        changed. If that backend is a file, changes are persisted to disk immediately.

        :param name: The name of the multivar to set.
        :param regex: A (required) regular expression to indicate which values to
                      replace. It is matched case-sensitively. Values that match are
                      removed, values that do not match are kept. To merely add
                      without removing any values, use the regular expression ``r'^$'``.
        :param value: The value to add to the multivar.
        """
        self._stored_exception = None
        name = str_to_bytes(name, 'name')
        regex = str_to_bytes(regex, 'regex')
        value = str_to_bytes(value, 'value')

        err = C.git_config_set_multivar(self._config, name, regex, value)
        self._check_error(err)

    def delete_multivar(self, name: str | bytes, regex: str | bytes) -> None:
        """Delete values from a multivar with name ``name``.

        If this ``Config`` is backed by multiple files/backends, only the first
        non-read-only backend with the highest :class:`pygit2.enums.ConfigLevel` is
        changed. If that backend is a file, changes are persisted to disk immediately.

        :param name: The name of the multivar to delete.
        :param regex: A (required) regular expression to indicate which values to
                      delete. It is matched case-sensitively. To delete all values of
                      the multivar, use the regular expression ``r'.*'`` or,
                      alternatively, ``del config[name]``.

        :raises KeyError: If no config var with name ``name`` is found in the first
                          non-read-only backend with the highest ``ConfigLevel``.
        """
        self._stored_exception = None
        name = str_to_bytes(name, 'name')
        regex = str_to_bytes(regex, 'regex')

        err = C.git_config_delete_multivar(self._config, name, regex)
        self._check_error(err)

    def get_bool(self, name: str | bytes) -> bool:
        """Obtain the first value found for a config var with name ``name`` as a boolean.

        Looks for a config var with name ``name`` and returns its value as a ``bool``.
        If the config var found is a multivar, only the first value is returned. If you
        need all the values of a multivar, use :meth:`Config.parse_bool` on each
        value returned by :meth:`Config.get_multivar`, instead.

        If this ``Config`` is backed by multiple files/backends, the one with the highest
        :class:`pygit2.enums.ConfigLevel` is searched first, and then the next-highest
        level, and so on.

        Truthy values are: 'true', '1', 'on', 'yes', or an empty value / ``NULL``.
        Falsy values are: 'false', '0', 'off', or 'no'.

        :param name: The name of the config var to look for.

        :returns: The boolean value found for the config var with name ``name`` as
                  parsed by ``git_config_parse_bool`` rules.

        :raises KeyError: If no config var with name ``name`` is found in any
                          of this ``Config``'s files/backends.
        :raises ValueError: If the value does not match one of the expected truthy
                            or falsy values.
        """
        self._stored_exception = None
        entry = self._get_entry(name)
        return self.parse_bool(entry.value)

    def get_int(self, name: bytes | str) -> int:
        """Obtain the first value found for a config var with name ``name`` as an integer.

        Looks for a config var with name ``name`` and returns its value as an ``int``.
        If the config var found is a multivar, only the first value is returned. If you
        need all the values of a multivar, use :meth:`Config.parse_int` on each
        value returned by :meth:`Config.get_multivar`, instead.

        If this ``Config`` is backed by multiple files/backends, the one with the highest
        :class:`pygit2.enums.ConfigLevel` is searched first, and then the next-highest
        level, and so on.

        A value can have a suffix 'k', 'm', or 'g' which stand for 'kilo',
        'mega', and 'giga', respectively.

        :param name: The name of the config var to look for.

        :returns: The integer value found for the config var with name ``name`` as
                  parsed by ``git_config_parse_int64`` rules.

        :raises KeyError: If no config var with name ``name`` is found in any
                          of this ``Config``'s files/backends.
        :raises ValueError: If the value is ``None`` or empty or otherwise does not
                            match the ``git_config_parse_int64`` parsing rules.
        """
        self._stored_exception = None
        entry = self._get_entry(name)
        return self.parse_int(entry.value)

    def add_file(
        self,
        path: str | PathLike,
        level: ConfigLevel | int | None = None,
        force: bool | int = False,
    ) -> None:
        """Add a config file backend to this ``Config`` object.

        In a multi-backend ``Config`` object, write operations occur only against
        the first non-read-only backend with the highest
        :class:`pygit2.enums.ConfigLevel`, and read operations start with the backend
        with the highest :class:`pygit2.enums.ConfigLevel` and continue down through
        lower backends. Keep this in mind when choosing the value for ``level``.

        :param path: The path of the config file to add.
        :param level: The config level for the new file backend. If not specified, the
                      special value "0" is used. This makes this new file the
                      lowest-priority backend of all, superseded by all other backends
                      in this config.
        :param force: If another backend (of any kind) with the same level already
                      exists, that backend will be replaced if ``force`` is ``True`` or
                      1, otherwise a ``ValueError`` will be raised.

        :raises ValueError: If another backend with the same level already exists and
                            ``force`` was not specified or was ``False`` or 0.
        """
        self._stored_exception = None
        if level is None:
            level = 0
        elif isinstance(level, ConfigLevel):
            level = level.value

        if force is True:
            force = 1
        elif force is False:
            force = 0

        err = C.git_config_add_file_ondisk(
            self._config,
            to_bytes(path),
            level,
            ffi.NULL,
            force,
        )
        self._check_error(err)

    @property
    def is_snapshot(self) -> bool:
        """Indicates whether this Config object is a read-only snapshot
        of the underlying configuration.

        :returns: ``True`` if it's a read-only snapshot, ``False`` otherwise.
        """
        return self._is_snapshot

    def snapshot(self) -> Config:
        """Create a read-only snapshot of this ``Config`` object.

        This means that looking up multiple values will use the same version
        of the configuration files.

        :raises TypeError: If this is already a snapshot.
        """
        if self._is_snapshot:
            raise TypeError('This config is already a snapshot.')
        return Config(c_config=self._c_snapshot(), is_snapshot=True)

    def _c_snapshot(self) -> 'GitConfigC':
        self._stored_exception = None
        c_config = ffi.new('git_config **')
        err = C.git_config_snapshot(c_config, self._config)
        self._check_error(err)
        return c_config[0]

    #
    # Methods to parse a string according to the git-config rules
    #

    @staticmethod
    def parse_bool(text: str | None) -> bool:
        """Parses the provided string ``text`` as a boolean value according to
        Git config parsing rules.

        Truthy values are: 'true', '1', 'on', 'yes', or an empty value / ``NULL``.
        Falsy values are: 'false', '0', 'off', or 'no'.

        :param text: The string to convert.

        :returns: The boolean value of the ``text`` as parsed by
                  ``git_config_parse_bool`` rules.

        :raises ValueError: If the value does not match one of the expected truthy
                            or falsy values.
        """
        res = ffi.new('int *')
        err = C.git_config_parse_bool(res, to_bytes(text))
        check_error(err)

        return res[0] != 0

    @staticmethod
    def parse_int(text: str | None) -> int:
        """Parses the provided string ``text`` as an integer value according to
        Git config parsing rules.

        A value can have a suffix 'k', 'm', or 'g' which stand for 'kilo',
        'mega', and 'giga', respectively.

        :param text: The string to convert.

        :returns: The integer value of the ``text`` as parsed by
                  ``git_config_parse_int64`` rules.

        :raises ValueError: If the value is ``None`` or empty or otherwise does not
                            match the ``git_config_parse_int64`` parsing rules.
        """
        if not text:
            raise ValueError(f'Text value {text!r} is not parseable as an integer.')

        res = ffi.new('int64_t *')
        err = C.git_config_parse_int64(res, to_bytes(text))
        check_error(err)

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

        :raises IOError: If the configuration file is not found.
        """
        return Config._from_found_config(C.git_config_find_system)

    @staticmethod
    def get_global_config() -> 'Config':
        """Return a ``Config`` object representing the global configuration file.

        The global configuration file is the one found at the standard user config
        location for Git, which is ``$HOME/.gitconfig``. This will not find the file
        at the XDG-compatible user config file location (for that, see
        :meth:`Config.get_xdg_config`).

        :raises IOError: If the configuration file is not found.
        """
        return Config._from_found_config(C.git_config_find_global)

    @staticmethod
    def get_xdg_config() -> 'Config':
        """Return a ``Config`` object representing the XDG-compatible global configuration file.

        The XDG-compatible user config file follows the XDG Base Directory Specification.
        This file is located at ``$HOME/.config/git/config``. This will not find the file
        at the standard user config location (for that, see :meth:`Config.get_global_config`).

        :raises IOError: If the configuration file is not found.
        """
        return Config._from_found_config(C.git_config_find_xdg)


class _InMemoryAppBackendConfig(Config, abc.ABC):
    """For internal use only.

    This base class for :class:`DefaultConfig` and :class:`RepositoryConfig` implements
    the in-memory backend context manager semantics documented in those respective
    classes.
    """

    def __init__(self, *, c_config: 'GitConfigC', is_snapshot: bool) -> None:
        """For internal use only.

        Constructs a ``Config`` object from a config object pointer.
        """
        super().__init__(c_config=c_config, is_snapshot=is_snapshot)
        self._backend_added = False
        self._backend = _InMemoryBackend(self)

    @abc.abstractmethod
    def _add_backend_to_config(self, backend: _InMemoryBackend) -> None:
        """Adds the backend to the config object."""

    def __enter__(self) -> Self:
        """Enter a context where all writes occur against an in-memory configuration.

        When entered, all subsequent writes occur against an in-memory configuration
        backend and do not get persisted to the underlying config file. As long as
        the context endures, Git operations will use the sum total configuration that
        includes the in-memory configuration.

        :returns: ``self``

        :raises TypeError: If this is a read-only snapshot of the configuration.
        """
        if self._is_snapshot:
            raise TypeError(
                'A read-only config snapshot cannot be used as a context manager, '
                'because its backend data cannot be changed.'
            )
        if not self._backend_added:
            self._add_backend_to_config(self._backend)
            self._backend_added = True
        self._change_write_priority(ConfigLevel.APP)
        return self

    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> Literal[False]:
        """Exit the context so that writes occur against the config file again.

        When exited, any in-memory configuration is erased so that it is no longer
        effective for Git operations, and subsequent writes again occur against
        the underlying config file and persist to this file.

        :returns: ``False``
        """
        if self._backend_added:
            self._change_write_priority(ConfigLevel.LOCAL)
            self._backend.clear()
        return False

    def _change_write_priority(self, level: ConfigLevel) -> None:
        """For internal use only.

        By default, when libgit2 creates a ``git_config`` object for a repository, it sets
        the write order to ``{ GIT_CONFIG_LEVEL_LOCAL }``. This means that writes go
        only to the local config in ``.git/config`` and nowhere else. We need to change
        this to ``{ GIT_CONFIG_LEVEL_APP }` when entering the context and then back to
        ``{ GIT_CONFIG_LEVEL_LOCAL }`` when exiting the context.
        """
        c_levels = ffi.new(
            'git_config_level_t[]',
            [ffi.cast('git_config_level_t', level.value)],
        )
        err = C.git_config_set_writeorder(self._config, c_levels, 1)
        check_error(err)


class DefaultConfig(_InMemoryAppBackendConfig):
    """A special-case :class:`Config` extension representing the total default
    configuration.

    This extension to the base ``Config`` class represents the total default configuration
    outside the context of a repository (for that, see :class:`RepositoryConfig`). It also
    serves as a semantic indicator of the scope of the configuration.

    The ``DefaultConfig`` includes the program, system, XDG, and global (user)
    configurations. This is, in essence, the "effective" configuration that Git uses when
    performing operations that are not against a repository. When a read operation occurs,
    the configurations are searched in the following order: global (user), XDG, system,
    and then program data.

    The ``DefaultConfig`` can also be used as a context manager to effect a temporary
    in-memory override of the default configuration. When the context manager is entered,
    an empty in-memory configuration backend is assigned to the configuration and given
    the highest read priority. During this context, write operations change the in-memory
    backend and do not affect the configuration file(s). Read operations—including those
    performed by Git itself—consult the in-memory backend first before then consulting the
    usual order. When the context manager exits, the in-memory backend's contents are
    erased, undoing any changes made to it.

    The context manager can be re-entered and then re-exited repeatedly; it is not a
    one-use-only operation.

    Only writeable ``DefaultConfig`` objects can be used as a context manager.
    Read-only snapshot ``DefaultConfig`` objects cannot.
    """

    @overload
    def __init__(self, /) -> None:
        """Load the total default configuration and construct a ``DefaultConfig``
        from it.
        """
        ...

    @overload
    def __init__(self, *, c_snapshot: 'GitConfigC') -> None:
        """For internal use only.

        Constructs a ``DefaultConfig`` from a given snapshot config object pointer.
        The resulting configuration will be read-only.
        """
        ...

    def __init__(self, *, c_snapshot: 'GitConfigC | None' = None):
        """Constructs a ``DefaultConfig`` object.

        **Overload 1: __init__()**

        Loads the total default configuration.

        **Overload 2: __init__(c_snapshot)**

        For internal use only.
        """
        if c_snapshot is not None:
            super().__init__(c_config=c_snapshot, is_snapshot=True)
        else:
            c_config = ffi.new('git_config **')
            err = C.git_config_open_default(c_config)
            check_error(err)
            super().__init__(c_config=c_config[0], is_snapshot=False)

    @override
    def snapshot(self) -> DefaultConfig:
        """Create a read-only snapshot of this ``DefaultConfig`` object.

        This means that looking up multiple values will use the same version
        of the configuration files.

        :raises TypeError: If this is already a snapshot.
        """
        if self._is_snapshot:
            raise TypeError('This default config is already a snapshot.')
        return DefaultConfig(c_snapshot=self._c_snapshot())

    @override
    def _add_backend_to_config(self, backend: _InMemoryBackend) -> None:
        backend.add_to_config(self._config)

    @override
    def add_file(
        self,
        path: str | PathLike,
        level: ConfigLevel | int | None = None,
        force: bool | int = False,
    ) -> NoReturn:
        """
        :raises TypeError: The default configuration does not support adding files.
        """
        raise TypeError('The default configuration does not support adding files.')


class RepositoryConfig(_InMemoryAppBackendConfig):
    """A special-case :class:`Config` extension that handles local (repository)
    configuration.

    This extension to the base ``Config`` class handles some of the special behaviors
    associated with repository configs, as well as serving as a semantic indicator for
    the scope of the configuration. You should not construct it directly, but instead
    use one of :meth:`pygit2.repository.BaseRepository.config` or
    :meth:`pygit2.repository.BaseRepository.config_snapshot` to obtain the local
    configuration.

    The ``RepositoryConfig`` represents not just the configuration present in
    ``.git/config``, but the sum total of that plus the program, system, XDG, and global
    (user) configurations. This is, in essence, the "effective" configuration that Git
    uses when performing operations against this repository. When a read operation
    occurs, the local configuration is searched first, then the global (user), XDG,
    system, and finally program data configurations, in that order. When a write
    operation occurs, only the local configuration is changed.

    The ``RepositoryConfig`` can also be used as a context manager to effect a temporary
    in-memory override of the local configuration. When the context manager is entered,
    an empty in-memory configuration backend is assigned to the configuration and given
    the highest read priority. During this context, write operations change the
    in-memory backend and do not affect the local configuration file. Read
    operations—including those performed by Git itself—consult the in-memory backend
    first before then consulting the usual order. When the context manager exits, the
    in-memory backend's contents are erased, undoing any changes made to it and
    allowing write operations to resume affecting the local configuration.

    The context manager can be re-entered and then re-exited repeatedly; it is not a
    one-use-only operation.

    Only writeable ``RepositoryConfig`` objects can be used as a context manager.
    Read-only snapshot ``RepositoryConfig`` objects cannot.
    """

    @overload
    def __init__(
        self,
        repo: 'BaseRepository',
        c_repo: 'GitRepositoryC',
        *,
        do_snapshot: bool = False,
    ) -> None:
        """For internal use only.

        See :meth:`pygit2.repository.BaseRepository.config` for obtaining a repository
        configuration or :meth:`pygit2.repository.BaseRepository.config_snapshot` for
        obtaining a snapshot.

        Constructs a new ``RepositoryConfig`` from the given repository.

        If ``do_snapshot`` is ``True`` (defaults to ``False``), a read-only snapshot
        configuration will be created from the repository. Otherwise, a writeable
        configuration will be created.
        """
        ...

    @overload
    def __init__(
        self,
        repo: 'BaseRepository',
        c_repo: 'GitRepositoryC',
        *,
        c_snapshot: 'GitConfigC',
    ) -> None:
        """For internal use only.

        See :meth:`pygit2.repository.BaseRepository.config_snapshot` for obtaining a
        repository configuration snapshot.

        Constructs a ``RepositoryConfig`` from a given snapshot config object pointer.
        The resulting configuration will be read-only.
        """
        ...

    def __init__(
        self,
        repo: 'BaseRepository',
        c_repo: 'GitRepositoryC',
        *,
        do_snapshot: bool = False,
        c_snapshot: 'GitConfigC | None' = None,
    ) -> None:
        """Constructs a ``RepositoryConfig`` object. For internal use only."""
        self._repo = repo
        self._c_repo = c_repo

        if c_snapshot is not None:
            super().__init__(c_config=c_snapshot, is_snapshot=True)
        else:
            c_config = ffi.new('git_config **')
            if do_snapshot:
                err = C.git_repository_config_snapshot(c_config, self._c_repo)
            else:
                err = C.git_repository_config(c_config, self._c_repo)
            check_error(err)
            super().__init__(c_config=c_config[0], is_snapshot=do_snapshot)

    @override
    def snapshot(self) -> RepositoryConfig:
        """Create a read-only snapshot of this ``RepositoryConfig`` object.

        This means that looking up multiple values will use the same version
        of the configuration files. The resulting ``RepositoryConfig`` cannot be
        used as a context manager, because it is read-only.

        :raises TypeError: If this is already a snapshot.
        """
        if self._is_snapshot:
            raise TypeError('This repository config is already a snapshot.')
        return RepositoryConfig(self._repo, self._c_repo, c_snapshot=self._c_snapshot())

    @override
    def _add_backend_to_config(self, backend: _InMemoryBackend) -> None:
        backend.add_to_config(self._config, self._c_repo)

    @override
    def add_file(
        self,
        path: str | PathLike,
        level: ConfigLevel | int | None = None,
        force: bool | int = False,
    ) -> NoReturn:
        """
        :raises TypeError: The local repository configuration does not support adding files.
        """
        raise TypeError(
            'The local repository configuration does not support adding files.',
        )


class _InMemoryBackend:
    """For internal use only.

    An in-memory ``git_config_backend`` implementing the details of
    ``_pygit_in_memory_backend``. libgit2 has a built-in in-memory backend that can
    be constructed with (as of 1.9.5) ``git_config_backend_from_string`` or
    ``git_config_backend_from_values``, but that backend is read-only and cannot
    be mutated. To implement the semantics of temporary app-level configuration
    in :class:`DefaultConfig` and :class:`RepositoryConfig`, we need to implement
    our own backend.

    We could do so completely in C, but that has some serious downsides, notably
    all the memory management and how easy it is to get wrong and either leak or
    segfault. It's easier, and safer, to implement the backend primarily in Python,
    using C structs and CFFI to bridge the implementation so that libgit2 C code
    can call its member functions.

    Because of the way CFFI works, the `member` functions must be standalone
    functions and cannot be member functions of this class. See all of the
    ``_config_memory_*`` functions below.
    """

    type_string = cast('char_pointer', ffi.new('char[]', b'pygit2-in-memory'))
    origin_path_string = cast('char_pointer', ffi.new('char[]', b''))

    def __init__(self, config: _InMemoryAppBackendConfig) -> None:
        self._config = config

        self._read_data: dict[str, list[_InMemoryBackend.Entry]] = {}
        self._write_data: dict[str, list[_InMemoryBackend.Entry]] = self._read_data

        self._locked = False
        self._readers_lock = threading.Lock()
        self._write_lock = threading.Lock()
        self._locked_write_lock = threading.Lock()
        self._readers = 0

        self._c_backend: 'PyGitConfigBackendWrapperC | None' = None
        self._c_handle = ffi.new_handle(self)

        self._iterators: dict[int, _InMemoryBackend.Iterator] = {}
        self._c_entries: dict[int, 'PyGitConfigBackendEntryC'] = {}

    @contextlib.contextmanager
    def read_lock(self) -> Generator[None, None, None]:
        """For internal use only.

        Yield a lock to protect ``_read_data``. The lock will not block other readers
        from simultaneously reading ``_read_data`` but will prevent writers from
        mutating ``_write_data`` unless this backend is "locked" (in the midst of a
        transaction).
        """
        with self._readers_lock:
            self._readers += 1
            if self._readers == 1:
                self._write_lock.acquire()  # first reader blocks all writers

        try:
            yield
        finally:
            with self._readers_lock:
                self._readers -= 1
                if self._readers == 0:
                    self._write_lock.release()  # last reader unblocks all writers

    @contextlib.contextmanager
    def write_lock(self) -> Generator[None, None, None]:
        """For internal use only.

        If this backend is "locked" (in the midst of a transaction), yield a lock
        to protect ``_write_data``, which is a separate object from ``_read_data``
        (so it won't block readers). If this backend is not "locked," yield a lock
        to protect ``_write_data``/``_read_data``, which are the same object (so it
        will block readers).
        """
        if self._locked:
            with self._locked_write_lock:
                yield
        else:
            with self._write_lock:
                yield

    def add_to_config(
        self,
        c_config: 'GitConfigC',
        c_repo: 'GitRepositoryC | None' = None,
    ) -> None:
        """For internal use only.

        Adds the backend to the ``git_config``. Called by
        :meth:`_InMemoryAppBackendConfig.__enter__` the first time it enters, but not
        any subsequent times. This is because it's not possible to remove a backend
        from a config with libgit2's public API, and so we rely on clearing
        the backend's contents on ``__exit__``.

        The ``c_repo`` is optional and applies only to repository configurations.
        """
        if self._c_backend is not None:
            raise ValueError('add_to_config called twice')

        self._c_backend = ffi.new('_pygit_in_memory_backend *')
        assert self._c_backend is not None
        self._c_backend.self = self._c_handle
        self._c_backend.parent.version = 1
        self._c_backend.parent.readonly = 0
        self._c_backend.parent.open = C._config_memory_backend_open
        self._c_backend.parent.get = C._config_memory_backend_get
        self._c_backend.parent.set = C._config_memory_backend_set
        self._c_backend.parent.set_multivar = C._config_memory_backend_set_multivar
        # this unfortunate name conflicts with a Python keyword, so we must use setattr
        setattr(self._c_backend.parent, 'del', C._config_memory_backend_del)
        self._c_backend.parent.del_multivar = C._config_memory_backend_del_multivar
        self._c_backend.parent.iterator = C._config_memory_backend_iterator
        self._c_backend.parent.snapshot = C._config_memory_backend_snapshot
        self._c_backend.parent.lock = C._config_memory_backend_lock
        self._c_backend.parent.unlock = C._config_memory_backend_unlock
        self._c_backend.parent.free = C._config_memory_backend_free

        err = C.git_config_add_backend(
            c_config,
            ffi.cast('git_config_backend *', self._c_backend),
            ConfigLevel.APP.value,
            ffi.NULL if c_repo is None else c_repo,
            1,  # force=true
        )
        check_error(err)

    def clear(self) -> None:
        """For internal use only.

        Erases all contents of the backend. Called by
        :meth:`_InMemoryAppBackendConfig.__exit__` each time it exits.
        """
        with self.write_lock():
            self._read_data.clear()
            self._write_data.clear()
            self._iterators.clear()
            self._c_entries.clear()

    def multivar_generator(
        self,
    ) -> Generator[tuple[str, '_InMemoryBackend.Entry'], None, None]:
        """For internal use only.

        Creates a generator yielding the contents of this backend for use by a
        :class:`_InMemoryBackend.Iterator`.
        """
        with self.read_lock():
            for key in self._read_data.keys():
                for value in self._read_data[key]:
                    yield key, value

    class Entry:
        """For internal use only.

        The value stored in ``_read_data`` and ``_write_data`` to prolong the life of
        C strings until their corresponding values are removed or the backend is
        cleared or freed.
        """

        def __init__(self, name: str, value: str) -> None:
            self.name = name
            self.c_name = cast(
                'char_pointer',
                ffi.new('char[]', name.encode('utf-8')),
            )
            self.value = value
            self.c_value = cast(
                'char_pointer',
                ffi.new('char[]', value.encode('utf-8')),
            )

        def __repr__(self):
            return (
                f'Entry("{ffi.string(self.c_name).decode("utf-8")}", '
                f'"{ffi.string(self.c_value).decode("utf-8")}")'
            )

    class Iterator:
        """For internal use only.

        Backs the ``_pygit_in_memory_backend_iterator`` object.
        """

        def __init__(
            self,
            backend: _InMemoryBackend,
            c_iterator: 'PyGitConfigIteratorWrapperC',
        ) -> None:
            self._backend = backend
            self._generator = backend.multivar_generator()
            self._c_handle = ffi.new_handle(self)
            self._c_iterator = c_iterator
            self._c_entries: dict[int, 'PyGitConfigIteratorEntryC'] = {}

        def __next__(self) -> tuple[str, _InMemoryBackend.Entry]:
            return next(self._generator)

        def __enter__(self) -> Self:
            self._backend._iterators[id(self)] = self
            return self

        def __exit__(
            self,
            exc_type: Type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: TracebackType | None,
        ) -> Literal[False]:
            self._backend._iterators.pop(id(self), None)
            return False


def _populate_memory_backend_entry(
    entry: 'GitConfigBackendEntryC',
    source: _InMemoryBackend.Entry,
    free: Callable[[GitConfigBackendEntryC], None],
) -> None:
    """For internal use only.

    Helper function used by ``_config_memory_backend_get`` and
    ``_config_memory_iterator_next`` to populate an entry with the data from the
    backend.
    """
    entry.free = free
    entry.entry.name = source.c_name
    entry.entry.value = source.c_value
    entry.entry.backend_type = _InMemoryBackend.type_string
    entry.entry.origin_path = _InMemoryBackend.origin_path_string
    entry.entry.include_depth = 0
    entry.entry.level = ConfigLevel.APP.value


@ffi.def_extern()
def _config_memory_backend_open(
    _: 'GitConfigBackendC',
    __: int,
    ___: 'GitRepositoryC',
) -> int:
    """For internal use only.

    'Member' function of the ``_pygit_in_memory_backend`` struct, invoked by libgit2
    immediately after a backend is constructed. In our case, this doesn't need to do
    anything, because Python manages the backend instance and all of its data
    structures.

    The third argument, ``repo``, may be ``NULL`` if this backend was applied to
    other than a repository config.

    C signature:
        int open(
            git_config_backend *backend,
            git_config_level_t level,
            const git_repository *repo);
    """
    return 0


@ffi.def_extern()
def _config_memory_backend_get(
    backend: 'GitConfigBackendC',
    name: char_pointer,
    out: '_Pointer[GitConfigBackendEntryC]',
) -> int:
    """For internal use only.

    'Member' function of the ``_pygit_in_memory_backend`` struct, invoked by libgit2
    on each of a config's backends, in order of level, until a backend returns
    something other than ``GIT_ENOTFOUND``. If a match is found for ``name``, constructs
    a ``_pygit_in_memory_backend_entry``, stores it in the ``_Backend`` to prevent
    destruction, and returns 0.

    Obtains a read lock to prevent writers from mutating the backend while it is
    being read.

    C signature:
        int get(
            git_config_backend *backend,
            const char *name,
            git_config_backend_entry **entry);
    """
    backend_wrapper = ffi.cast('_pygit_in_memory_backend *', backend)
    self = cast(_InMemoryBackend, ffi.from_handle(backend_wrapper.self))
    try:
        key = ffi.string(name).decode('utf-8').lower()
        if key not in self._read_data or not self._read_data[key]:
            return C.GIT_ENOTFOUND

        value = self._read_data[key][0]
        entry = ffi.new('_pygit_in_memory_backend_entry *')
        ptr = int(ffi.cast('uintptr_t', entry))
        entry.owner = backend_wrapper
        _populate_memory_backend_entry(
            entry.parent,
            value,
            C._config_memory_backend_entry_free,
        )
        self._c_entries[ptr] = entry
        out[0] = ffi.cast('git_config_backend_entry *', entry)
    except BaseException as e:
        self._config._stored_exception = e
        return C.GIT_EUSER
    return 0


@ffi.def_extern()
def _config_memory_backend_set(
    backend: 'GitConfigBackendC',
    name: char_pointer,
    value: char_pointer,
) -> int:
    """For internal use only.

    'Member' function of the ``_pygit_in_memory_backend`` struct, invoked by libgit2
    on the config's first non-read-only backend (in the order defined by
    ``git_config_set_writeorder``) when other code calls ``git_config_set_*`` on that
    config. Replaces all values at the specified ``name`` with the new ``value``.

    Obtains a write lock to prevent readers from reading the backend while it is
    being mutated.

    C signature:
        int set(git_config_backend *backend, const char *name, const char *value);
    """
    backend_wrapper = ffi.cast('_pygit_in_memory_backend *', backend)
    self = cast(_InMemoryBackend, ffi.from_handle(backend_wrapper.self))
    try:
        key = ffi.string(name).decode('utf-8').lower()
        decoded_value = ffi.string(value).decode('utf-8')
        self._write_data[key] = [_InMemoryBackend.Entry(key, decoded_value)]
    except BaseException as e:
        self._config._stored_exception = e
        return C.GIT_EUSER
    return 0


@ffi.def_extern()
def _config_memory_backend_set_multivar(
    backend: 'GitConfigBackendC',
    name: char_pointer,
    regexp: char_pointer,
    value: char_pointer,
) -> int:
    """For internal use only.

    'Member' function of the ``_pygit_in_memory_backend`` struct, invoked by libgit2
    on the config's first non-read-only backend (in the order defined by
    ``git_config_set_writeorder``) when other code calls ``git_config_set_multivar`` on
    that config. If no current values with the given ``name`` exist, creates a new
    multivar. Appends the ``value`` to the multivar and, if ``regexp`` is not ``NULL``,
    removes all other values that match the regular expression case-sensitively.

    Obtains a write lock to prevent readers from reading the backend while it is
    being mutated.

    C signature:
        int set_multivar(
            git_config_backend *,
            const char *name,
            const char *regexp,
            const char *value);
    """
    backend_wrapper = ffi.cast('_pygit_in_memory_backend *', backend)
    self = cast(_InMemoryBackend, ffi.from_handle(backend_wrapper.self))
    try:
        key = ffi.string(name).decode('utf-8').lower()
        with self.write_lock():
            if key in self._write_data and regexp != ffi.NULL:
                expression = re.compile(ffi.string(regexp).decode('utf-8'))
                self._write_data[key] = [
                    v for v in self._write_data[key] if not expression.search(v.value)
                ]
            elif key not in self._write_data:
                self._write_data[key] = []
            self._write_data[key].append(
                _InMemoryBackend.Entry(key, ffi.string(value).decode('utf-8')),
            )
    except BaseException as e:
        self._config._stored_exception = e
        return C.GIT_EUSER
    return 0


@ffi.def_extern()
def _config_memory_backend_del(
    backend: 'GitConfigBackendC',
    name: char_pointer,
) -> int:
    """For internal use only.

    'Member' function of the ``_pygit_in_memory_backend`` struct, invoked by libgit2
    on the config's first non-read-only backend (in the order defined by
    ``git_config_set_writeorder``) when other code calls ``git_config_delete_entry`` on
    that config. Deletes all values with the specified name.

    Obtains a write lock to prevent readers from reading the backend while it is
    being mutated.

    C signature:
        int del(git_config_backend *backend, const char *name);
    """
    backend_wrapper = ffi.cast('_pygit_in_memory_backend *', backend)
    self = cast(_InMemoryBackend, ffi.from_handle(backend_wrapper.self))
    try:
        key = ffi.string(name).decode('utf-8').lower()
        with self.write_lock():
            if key not in self._write_data:
                return C.GIT_ENOTFOUND
            del self._write_data[key]
    except BaseException as e:
        self._config._stored_exception = e
        return C.GIT_EUSER
    return 0


@ffi.def_extern()
def _config_memory_backend_del_multivar(
    backend: 'GitConfigBackendC',
    name: char_pointer,
    regexp: char_pointer,
) -> int:
    """For internal use only.

    'Member' function of the ``_pygit_in_memory_backend`` struct, invoked by libgit2
    on all of a config's non-read-only backends when other code calls
    ``git_config_delete_multivar`` on that config. If the ``regexp`` is ``NULL``,
    deletes all values with the specified ``name``. Otherwise, deletes any values
    with the specified ``name`` that match the regular expression case-sensitively.

    Obtains a write lock to prevent readers from reading the backend while it is
    being mutated.

    C signature:
        int del_multivar(git_config_backend *backend, const char *name, const char *regexp);
    """
    backend_wrapper = ffi.cast('_pygit_in_memory_backend *', backend)
    self = cast(_InMemoryBackend, ffi.from_handle(backend_wrapper.self))
    try:
        key = ffi.string(name).decode('utf-8').lower()
        with self.write_lock():
            if key not in self._write_data:
                return C.GIT_ENOTFOUND
            if regexp == ffi.NULL:
                del self._write_data[key]
            else:
                expression = re.compile(ffi.string(regexp).decode('utf-8'))
                self._write_data[key] = [
                    v for v in self._write_data[key] if not expression.search(v.value)
                ]
    except BaseException as e:
        self._config._stored_exception = e
        return C.GIT_EUSER
    return 0


@ffi.def_extern()
def _config_memory_backend_iterator(
    out: '_Pointer[GitConfigIteratorC]',
    backend: 'GitConfigBackendC',
) -> int:
    """For internal use only.

    'Member' function of the ``_pygit_in_memory_backend`` struct, invoked by libgit2
    on all of a config's backends when other code calls ``git_config_iterator_new`` or
    ``git_config_multivar_iterator_new`` on that config followed by ``git_config_next``
    on the resulting iterator.

    Here's how it works:
    - User code (or, in this case, :meth:`Config.__iter__` or :meth:`Config.get_multivar`)
      calls ``git_config_iterator_new`` or ``git_config_multivar_iterator_new``.
    - libgit2 creates a special config iterator that wraps underlying backend iterators
      for all the backends backing the config.
    - User code (or, in this case, :meth:`ConfigIterator.__next__`) calls
      ``git_config_next`` on that config iterator.
    - libgit2 invokes this function on the highest-level backend to create the backend
      iterator, then immediately invokes ``next`` on that backend iterator to obtain the
      first entry.
    - libgit2 continues to invoke ``next`` on the backend iterator each time user code
      calls ``git_config_next`` on the config iterator, until the backend iterator returns
      ``GIT_ITEROVER``.
    - libgit2 then invokes this function on the next-higest-level backend to create the
      next backend iterator, and so on.
    - The config iterator returns ``GIT_ITEROVER`` to the user code only once all backends
      have been iterated.

    This constructs a :class:`_InMemoryBackend.Iterator` and a
    ``_pygit_in_memory_backend_iterator`` and stores references to each in the other,
    then enters the former's context manager to prepare for iteration.

    Obtains a read lock for the duration of iteration, automatically released when iteration
    either completes or breaks, without waiting for the iterator to be freed.

    C signature:
        int iterator(git_config_iterator **out, git_config_backend * backend);
    """
    backend_wrapper = ffi.cast('_pygit_in_memory_backend *', backend)
    self = cast(_InMemoryBackend, ffi.from_handle(backend_wrapper.self))
    try:
        iterator = ffi.new('_pygit_in_memory_backend_iterator *')
        py_iterator = _InMemoryBackend.Iterator(self, iterator)
        iterator.self = py_iterator._c_handle
        iterator.parent.backend = backend
        iterator.parent.flags = 0
        iterator.parent.next = C._config_memory_iterator_next
        iterator.parent.free = C._config_memory_iterator_free
        out[0] = ffi.cast('git_config_iterator *', iterator)
        py_iterator.__enter__()
    except BaseException as e:
        self._config._stored_exception = e
        return C.GIT_EUSER
    return 0


@ffi.def_extern()
def _config_memory_backend_snapshot(
    _: '_Pointer[GitConfigBackendC]',
    __: 'GitConfigBackendC',
) -> int:
    """For internal use only.

    'Member' function of the ``_pygit_in_memory_backend`` struct, invoked by libgit2
    on all of a config's backends when other code calls ``git_config_snapshot`` on
    that config.

    TODO: Implement this, the easiest way for which will be to use
    ``git_config_backend_from_string`` (an immutable in-memory backend) when it becomes
    available in 1.9.5.

    C signature:
        int snapshot(git_config_backend **out, git_config_backend *backend);
    """
    # backend_wrapper = ffi.cast('_pygit_in_memory_backend *', backend)
    # self = cast(_InMemoryBackend, ffi.from_handle(backend_wrapper.self))
    return C.GIT_PASSTHROUGH


@ffi.def_extern()
def _config_memory_backend_lock(backend: 'GitConfigBackendC') -> int:
    """For internal use only.

    'Member' function of the ``_pygit_in_memory_backend`` struct, invoked by libgit2
    on all of a config's non-read-only backends when other code calls
    ``git_config_lock`` on that config to begin a transaction. In practice, this is
    not currently used, as PyGit2 does not (yet?) support config transactions.

    This sets ``_write_data`` to a deep copy of the current value of ``_read_data``
    so that any changes made to ``_write_data`` during the transaction are not
    visible to readers unless and until ``unlock(true)`` is called.

    C signature:
        int lock(git_config_backend * backend);
    """
    backend_wrapper = ffi.cast('_pygit_in_memory_backend *', backend)
    self = cast(_InMemoryBackend, ffi.from_handle(backend_wrapper.self))
    try:
        with self.write_lock():
            if self._locked:
                return C.GIT_ELOCKED
            self._locked = True
            # this will return a different lock because _locked changed
            with self.write_lock():
                self._write_data = {k: v[:] for k, v in self._read_data.items()}
    except BaseException as e:
        self._config._stored_exception = e
        return C.GIT_EUSER
    return 0


@ffi.def_extern()
def _config_memory_backend_unlock(backend: 'GitConfigBackendC', success: int) -> int:
    """For internal use only.

    'Member' function of the ``_pygit_in_memory_backend`` struct, invoked by libgit2
    on all of a config's non-read-only backends when other code calls
    ``git_transaction_commit`` or ``git_transaction_free`` on a transaction obtained
    from ``git_config_lock``. If ``git_transaction_commit` was called, this function
    is invoked with a true ``success`` value. If ``git_transaction_free`` is called
    without ``git_transaction_commit`` having first been called, this function is
    invoked with a false ``success`` value. In practice, this is not currently used,
    as PyGit2 does not (yet?) support config transactions.

    If ``success`` is true (non-zero), this "commits" all changes made during the lock
    period by pointing ``_read_data`` to ``_write_data``, thus discarding the contents
    of ``_read_data``. If ``success`` is false (zero), this "rolls back" all changes
    made during the lock period by pointing ``_write_data`` to ``_read_data``, thus
    discarding the contents of ``_write_data``.

    C signature:
        int unlock(git_config_backend * backend, int success);
    """
    backend_wrapper = ffi.cast('_pygit_in_memory_backend *', backend)
    self = cast(_InMemoryBackend, ffi.from_handle(backend_wrapper.self))
    try:
        with self.write_lock():
            if not self._locked:
                return C.GIT_EINVALID
            self._locked = False
            # this will return a different lock because _locked changed
            with self.write_lock():
                if success == 0:
                    self._write_data = self._read_data
                else:
                    self._read_data = self._write_data
    except BaseException as e:
        self._config._stored_exception = e
        return C.GIT_EUSER
    return 0


@ffi.def_extern()
def _config_memory_backend_free(backend: 'GitConfigBackendC') -> None:
    """For internal use only.

    'Member' function of the ``_pygit_in_memory_backend`` struct, invoked by libgit2
    when it discards the in-memory backend. This occurs only when the
    config is freed. For a repository config, this is only when the repository itself
    is freed. For the default config, this is only when the application is unloaded.

    C signature:
        void free(git_config_backend *backend);
    """
    try:
        backend_wrapper = ffi.cast('_pygit_in_memory_backend *', backend)
        self = cast(_InMemoryBackend, ffi.from_handle(backend_wrapper.self))
        try:
            self.clear()
        except BaseException as e:
            self._config._stored_exception = e
            # nothing we can do here because of the void return type
    except (AttributeError, TypeError, RuntimeError, ReferenceError):
        # The Python interpreter is exiting when this is called. Nothing we can do.
        pass


@ffi.def_extern()
def _config_memory_backend_entry_free(entry: 'GitConfigBackendEntryC') -> None:
    """For internal use only.

    'Member' function of the ``_pygit_in_memory_backend_entry`` struct, invoked
    by libgit2 when it discards an entry obtained from ``_config_memory_backend_get``
    (and, in this specific case, by :meth:`ConfigEntry.__del__` when it calls
    ``git_config_entry_free``).

    Removes the entry previously stored in :class:`_InMemoryBackend`'s store of
    ``git_config_backend_entry`` instances.

    C signature:
        void free(git_config_backend_entry *entry);
    """
    sub_entry = ffi.cast('_pygit_in_memory_backend_entry *', entry)
    self = cast(_InMemoryBackend, ffi.from_handle(sub_entry.owner.self))
    try:
        ptr = int(ffi.cast('uintptr_t', entry))
        if ptr in self._c_entries:
            del self._c_entries[ptr]
    except BaseException as e:
        self._config._stored_exception = e
        # nothing we can do here because of the void return type


@ffi.def_extern()
def _config_memory_iterator_next(
    out: '_Pointer[GitConfigBackendEntryC]',
    iterator: 'GitConfigIteratorC',
) -> int:
    """For internal use only.

    'Member' function of the ``_pygit_in_memory_backend_iterator`` struct, invoked
    by libgit2 when it wants the next entry from the iterator (and, in this specific
    case, by :meth:`ConfigIterator.__next__` when it calls ``git_config_next``).

    C signature:
        int next(git_config_backend_entry **out, git_config_iterator *iterator);
    """
    iterator_wrapper = ffi.cast('_pygit_in_memory_backend_iterator *', iterator)
    self = cast(_InMemoryBackend.Iterator, ffi.from_handle(iterator_wrapper.self))
    try:
        key, value = next(self)
        entry = ffi.new('_pygit_in_memory_backend_iterator_entry *')
        ptr = int(ffi.cast('uintptr_t', entry))
        entry.owner = iterator_wrapper
        _populate_memory_backend_entry(
            entry.parent,
            value,
            C._config_memory_iterator_entry_free,
        )
        self._c_entries[ptr] = entry
        out[0] = ffi.cast('git_config_backend_entry *', entry)
        return 0
    except StopIteration:
        return C.GIT_ITEROVER
    except BaseException as e:
        self._backend._config._stored_exception = e
        return C.GIT_EUSER


@ffi.def_extern()
def _config_memory_iterator_free(iterator: 'GitConfigIteratorC') -> None:
    """For internal use only.

    'Member' function of the ``_pygit_in_memory_backend_iterator`` struct, invoked
    by libgit2 when it discards an iterator (and, in this specific case, by
    :meth:`ConfigIterator.__del__` when it calls ``git_config_iterator_free``).

    Exits the :class:`_InMemoryBackend.Iterator`'s context manager so that it
    releases its reference to the backend, the ``_pygit_in_memory_backend_iterator``
    instance, and the ``git_config_backend_entry`` instances it stored.

    C signature:
        void free(git_config_iterator *iterator);
    """
    iterator_wrapper = ffi.cast('_pygit_in_memory_backend_iterator *', iterator)
    self = cast(_InMemoryBackend.Iterator, ffi.from_handle(iterator_wrapper.self))
    try:
        self.__exit__(None, None, None)
    except BaseException as e:
        self._backend._config._stored_exception = e
        # nothing we can do here because of the void return type


@ffi.def_extern()
def _config_memory_iterator_entry_free(entry: 'GitConfigBackendEntryC') -> None:
    """For internal use only.

    'Member' function of the ``_pygit_in_memory_backend_iterator_entry`` struct, invoked
    by libgit2 when it discards an entry obtained from an iterator (and, in this
    specific case, by :meth:`ConfigEntry.__del__` when it calls
    ``git_config_entry_free``).

    Removes the entry previously stored in :class:`_InMemoryBackend.Iterator`'s store
    of ``git_config_backend_entry`` instances.

    C signature:
        void free(git_config_backend_entry *entry);
    """
    sub_entry = ffi.cast('_pygit_in_memory_backend_iterator_entry *', entry)
    self = cast(_InMemoryBackend.Iterator, ffi.from_handle(sub_entry.owner.self))
    try:
        ptr = int(ffi.cast('uintptr_t', entry))
        if ptr in self._c_entries:
            del self._c_entries[ptr]
    except BaseException as e:
        self._backend._config._stored_exception = e
        # nothing we can do here because of the void return type


class ConfigEntry:
    """An entry in a configuration object."""

    _entry: 'GitConfigEntryC'
    iterator: _BaseIterator | None

    @classmethod
    def _from_c(
        cls, ptr: 'GitConfigEntryC', iterator: _BaseIterator | None = None
    ) -> 'ConfigEntry':
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
        # So instead we load the Python object immediately. Ideally we should
        # investigate libgit2 source code.
        if iterator is not None:
            entry.raw_name = entry.raw_name
            entry.raw_value = entry.raw_value
            entry.level = entry.level

        return entry

    def __del__(self) -> None:
        if self.iterator is None and self._entry != ffi.NULL:
            C.git_config_entry_free(self._entry)

    @property
    def c_value(self) -> 'ffi.char_pointer':
        """The raw ``cData`` entry value."""
        return self._entry.value

    @cached_property
    def raw_name(self) -> bytes:
        return ffi.string(self._entry.name)

    @cached_property
    def raw_value(self) -> bytes | None:
        return ffi.string(self.c_value) if self.c_value != ffi.NULL else None

    @cached_property
    def level(self) -> int:
        """The entry's ``git_config_level_t`` value."""
        return self._entry.level

    @property
    def name(self) -> str:
        """The entry's name."""
        return self.raw_name.decode('utf-8')

    @property
    def value(self) -> str | None:
        """The entry's value as a string."""
        return self.raw_value.decode('utf-8') if self.raw_value is not None else None
