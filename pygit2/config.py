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
from __future__ import annotations

from collections.abc import Callable, Iterator
from functools import cached_property
from os import PathLike
from typing import TYPE_CHECKING, Any, NoReturn, Self, overload

# Import from pygit2
from .enums import ConfigLevel
from .errors import GitError, InvalidError, check_error
from .ffi import C, ffi
from .utils import encode_fs_path, encode_string

if TYPE_CHECKING:
    from ._libgit2.ffi import (
        GitConfigC,
        GitConfigEntryC,
        GitConfigIteratorC,
        GitRepositoryC,
    )
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
    def __init__(self, /) -> None:
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
        :raises OSError: If the path specified does not exist or could not be opened.
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
        :raises OSError: If the path specified does not exist or could not be opened.

        **Overload 3: __init__(c_config, is_snapshot)**

        For internal use only.
        """
        # ^^ see https://github.com/sphinx-doc/sphinx/issues/7787
        if path is not None and c_config is not None:
            raise ValueError('Cannot initialize Config from both path and c_config')

        self._is_snapshot = is_snapshot
        self._stored_exception: BaseException | None = None

        if c_config is not None:
            self._c_config = c_config
        else:
            c_config_ptr = ffi.new('git_config **')

            if not path:
                err = C.git_config_new(c_config_ptr)
            else:
                path_bytes = encode_fs_path(path)
                err = C.git_config_open_ondisk(c_config_ptr, path_bytes)

            check_error(err, io=True)
            self._c_config = c_config_ptr[0]

    def __del__(self) -> None:
        try:
            C.git_config_free(self._c_config)
        except AttributeError:
            pass

    def _check_error(self, err: int, io: bool = False):
        try:
            check_error(err, io=io, user_exception=self._stored_exception)
        finally:
            self._stored_exception = None

    def _get(self, name: str | bytes) -> tuple[int, 'ConfigEntry | None']:
        name = str_to_bytes(name, 'name')

        c_entry_ptr = ffi.new('git_config_entry **')
        err = C.git_config_get_entry(c_entry_ptr, self._c_config, name)

        if err >= 0:
            try:
                return err, ConfigEntry(c_entry_ptr[0])
            finally:
                C.git_config_entry_free(c_entry_ptr[0])

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

        Looks for a config var with name ``name`` and returns its value as a string,
        or ``None`` if the config var is a valueless flag. If you want to apply the
        Git config parsing rules, use :meth:`Config.get_bool` or
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
            err = C.git_config_set_bool(self._c_config, name, value)
        elif isinstance(value, int):
            err = C.git_config_set_int64(self._c_config, name, value)
        else:
            err = C.git_config_set_string(self._c_config, name, encode_string(value))

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

        err = C.git_config_delete_entry(self._c_config, name)
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
        c_iter_ptr = ffi.new('git_config_iterator **')
        err = C.git_config_iterator_new(c_iter_ptr, self._c_config)
        self._check_error(err)

        return ConfigIterator(self, c_iter_ptr[0])

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
        regex_bytes = encode_string(regex or None)

        c_iter_ptr = ffi.new('git_config_iterator **')
        err = C.git_config_multivar_iterator_new(
            c_iter_ptr,
            self._c_config,
            name,
            regex_bytes,
        )
        self._check_error(err)

        return ConfigMultivarIterator(self, c_iter_ptr[0])

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

        err = C.git_config_set_multivar(self._c_config, name, regex, value)
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

        err = C.git_config_delete_multivar(self._c_config, name, regex)
        self._check_error(err)

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
        self._stored_exception = None
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
            self._c_config,
            encode_fs_path(path),
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
        c_config_ptr = ffi.new('git_config **')
        err = C.git_config_snapshot(c_config_ptr, self._c_config)
        self._check_error(err)
        return c_config_ptr[0]

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

        :raises OSError: If the configuration file is not found.
        """
        return Config._from_found_config(C.git_config_find_system)

    @staticmethod
    def get_global_config() -> 'Config':
        """Return a ``Config`` object representing the global configuration file.

        The global configuration file is the one found at the standard user config
        location for Git, which is ``$HOME/.gitconfig``. This will not find the file
        at the XDG-compatible user config file location (for that, see
        :meth:`Config.get_xdg_config`).

        :raises OSError: If the configuration file is not found.
        """
        return Config._from_found_config(C.git_config_find_global)

    @staticmethod
    def get_xdg_config() -> 'Config':
        """Return a ``Config`` object representing the XDG-compatible global configuration file.

        The XDG-compatible user config file follows the XDG Base Directory Specification.
        This file is located at ``$HOME/.config/git/config``. This will not find the file
        at the standard user config location (for that, see :meth:`Config.get_global_config`).

        :raises OSError: If the configuration file is not found.
        """
        return Config._from_found_config(C.git_config_find_xdg)


class DefaultConfig(Config):
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
    """

    @overload
    def __init__(self, /) -> None:
        """Load the total default configuration and construct a ``DefaultConfig``
        from it.
        """
        ...

    @overload
    def __init__(self, *, snapshot_of: DefaultConfig) -> None:
        """For internal use only.

        Constructs a ``DefaultConfig`` from a given snapshot config object pointer.
        The resulting configuration will be read-only.
        """
        ...

    def __init__(self, *, snapshot_of: DefaultConfig | None = None) -> None:
        """Constructs a ``DefaultConfig`` object.

        **Overload 1: __init__()**

        Loads the total default configuration.

        **Overload 2: __init__(c_snapshot)**

        For internal use only.
        """
        if snapshot_of is not None:
            super().__init__(
                c_config=snapshot_of._c_snapshot(),
                is_snapshot=True,
            )
        else:
            c_config_ptr = ffi.new('git_config **')
            err = C.git_config_open_default(c_config_ptr)
            check_error(err)
            super().__init__(c_config=c_config_ptr[0], is_snapshot=False)

    def snapshot(self) -> DefaultConfig:
        """Create a read-only snapshot of this ``DefaultConfig`` object.

        This means that looking up multiple values will use the same version
        of the configuration files.

        :raises TypeError: If this is already a snapshot.
        """
        if self._is_snapshot:
            raise TypeError('This default config is already a snapshot.')
        return DefaultConfig(snapshot_of=self)

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


class RepositoryConfig(Config):
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
        snapshot_of: RepositoryConfig,
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
        snapshot_of: RepositoryConfig | None = None,
    ) -> None:
        """Constructs a ``RepositoryConfig`` object. For internal use only."""
        self._repo = repo
        self._c_repo = c_repo
        if snapshot_of is not None:
            super().__init__(
                c_config=snapshot_of._c_snapshot(),
                is_snapshot=True,
            )
        else:
            c_config_ptr = ffi.new('git_config **')
            if do_snapshot:
                err = C.git_repository_config_snapshot(c_config_ptr, self._c_repo)
            else:
                err = C.git_repository_config(c_config_ptr, self._c_repo)
            check_error(err)
            super().__init__(c_config=c_config_ptr[0], is_snapshot=do_snapshot)

    def snapshot(self) -> RepositoryConfig:
        """Create a read-only snapshot of this ``RepositoryConfig`` object.

        This means that looking up multiple values will use the same version
        of the configuration files. The resulting ``RepositoryConfig`` cannot be
        used as a context manager, because it is read-only.

        :raises TypeError: If this is already a snapshot.
        """
        if self._is_snapshot:
            raise TypeError('This repository config is already a snapshot.')
        return RepositoryConfig(self._repo, self._c_repo, snapshot_of=self)

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
        """Tests whether this entry equals the other value.

        Two ``ConfigEntry`` objects are considered equal if they have the same values
        for ``raw_level``, ``raw_name``, and ``raw_value``.

        If the other value is not a ``ConfigEntry``, this returns ``NotImplemented``.

        :returns: Whether ``other`` equals this entry.
        """
        if not isinstance(other, ConfigEntry):
            return NotImplemented
        return (
            self._raw_level == other._raw_level
            and self._raw_name == other._raw_name
            and self._raw_value == other._raw_value
        )

    def __hash__(self) -> int:
        """Computes a hash for this entry.

        The hash is a combination of the hash of the ``raw_level``, ``raw_name``,
        and ``raw_value``.
        """
        return hash((self._raw_level, self._raw_name, self._raw_value))
