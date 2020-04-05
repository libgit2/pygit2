# Copyright 2010-2020 The pygit2 contributors
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

from cached_property import cached_property

# Import from pygit2
from .errors import GitException, GitIOError
from .ffi import ffi, C
from .utils import to_bytes


def assert_string(v, desc):
    if not isinstance(v, str):
        raise TypeError("%s must be a string" % desc)


class ConfigIterator(object):

    def __init__(self, config, ptr):
        self._iter = ptr
        self._config = config

    def __del__(self):
        C.git_config_iterator_free(self._iter)

    def __iter__(self):
        return self

    def _next_entry(self):
        centry = ffi.new('git_config_entry **')
        GitException.check_result(C.git_config_next)(centry, self._iter)
        return ConfigEntry._from_c(centry[0], self)

    def next(self):
        return self.__next__()

    def __next__(self):
        return self._next_entry()


class ConfigMultivarIterator(ConfigIterator):
    def __next__(self):
        entry = self._next_entry()
        return entry.value


class Config(object):
    """Git configuration management"""

    def __init__(self, path=None):
        cconfig = ffi.new('git_config **')

        if not path:
            GitIOError.check_result(C.git_config_new)(cconfig)
        else:
            assert_string(path, "path")
            GitIOError.check_result(C.git_config_open_ondisk)(cconfig, to_bytes(path))
        self._config = cconfig[0]

    @classmethod
    def from_c(cls, repo, ptr):
        config = cls.__new__(cls)
        config._repo = repo
        config._config = ptr

        return config

    def __del__(self):
        try:
            C.git_config_free(self._config)
        except AttributeError:
            pass

    def _get(self, key):
        assert_string(key, "key")

        entry = ffi.new('git_config_entry **')
        GitException.check_result(C.git_config_get_entry)(entry, self._config, to_bytes(key))

        return ConfigEntry._from_c(entry[0])

    def _get_entry(self, key):
        entry = self._get(key)
        return entry

    def __contains__(self, key):
        try:
            self._get(key)
        except KeyError:
            return False
        return True

    def __getitem__(self, key):
        entry = self._get_entry(key)

        return entry.value

    def __setitem__(self, key, value):
        assert_string(key, "key")
        if isinstance(value, bool):
            GitException.check_result(C.git_config_set_bool)(self._config, to_bytes(key), value)
        elif isinstance(value, int):
            GitException.check_result(C.git_config_set_int64)(self._config, to_bytes(key), value)
        else:
            GitException.check_result(C.git_config_set_string)(self._config, to_bytes(key),to_bytes(value))

    def __delitem__(self, key):
        assert_string(key, "key")
        GitException.check_result(C.git_config_delete_entry)(self._config, to_bytes(key))


    def __iter__(self):
        citer = ffi.new('git_config_iterator **')
        GitException.check_result(C.git_config_iterator_new)(citer, self._config)
        return ConfigIterator(self, citer[0])

    def get_multivar(self, name, regex=None):
        """Get each value of a multivar ''name'' as a list of strings.

        The optional ''regex'' parameter is expected to be a regular expression
        to filter the variables we're interested in.
        """
        assert_string(name, "name")

        citer = ffi.new('git_config_iterator **')
        GitException.check_result(C.git_config_multivar_iterator_new)(citer, self._config, to_bytes(name), to_bytes(regex))
        return ConfigMultivarIterator(self, citer[0])

    def set_multivar(self, name, regex, value):
        """Set a multivar ''name'' to ''value''. ''regexp'' is a regular
        expression to indicate which values to replace.
        """
        assert_string(name, "name")
        assert_string(regex, "regex")
        assert_string(value, "value")

        GitException.check_result(C.git_config_set_multivar)(self._config, to_bytes(name),to_bytes(regex), to_bytes(value))


    def get_bool(self, key):
        """Look up *key* and parse its value as a boolean as per the git-config
        rules. Return a boolean value (True or False).

        Truthy values are: 'true', 1, 'on' or 'yes'. Falsy values are: 'false',
        0, 'off' and 'no'
        """
        entry = self._get_entry(key)
        res = ffi.new('int *')
        GitException.check_result(C.git_config_parse_bool)(res, entry.c_value)
        return res[0] != 0

    def get_int(self, key):
        """Look up *key* and parse its value as an integer as per the git-config
        rules. Return an integer.

        A value can have a suffix 'k', 'm' or 'g' which stand for 'kilo',
        'mega' and 'giga' respectively.
        """

        entry = self._get_entry(key)
        res = ffi.new('int64_t *')
        GitException.check_result(C.git_config_parse_int64)(res, entry.c_value)

        return res[0]

    def add_file(self, path, level=0, force=0):
        """Add a config file instance to an existing config."""
        GitException.check_result(C.git_config_add_file_ondisk)(self._config, to_bytes(path), level, ffi.NULL, force)


    def snapshot(self):
        """Create a snapshot from this Config object.

        This means that looking up multiple values will use the same version
        of the configuration files.
        """
        ccfg = ffi.new('git_config **')
        GitException.check_result(C.git_config_snapshot)(ccfg, self._config)
        return Config.from_c(self._repo, ccfg[0])

    #
    # Methods to parse a string according to the git-config rules
    #

    @staticmethod
    def parse_bool(text):
        res = ffi.new('int *')
        GitException.check_result(C.git_config_parse_bool)(res, to_bytes(text))


        return res[0] != 0

    @staticmethod
    def parse_int(text):
        res = ffi.new('int64_t *')
        GitException.check_result(C.git_config_parse_int64)(res, to_bytes(text))
        return res[0]

    #
    # Static methods to get specialized version of the config
    #

    @staticmethod
    def _from_found_config(fn):
        buf = ffi.new('git_buf *', (ffi.NULL, 0))
        GitIOError.check_result(fn)(buf)
        cpath = ffi.string(buf.ptr).decode('utf-8')
        C.git_buf_dispose(buf)

        return Config(cpath)

    @staticmethod
    def get_system_config():
        """Return a <Config> object representing the system configuration file.
        """
        return Config._from_found_config(C.git_config_find_system)

    @staticmethod
    def get_global_config():
        """Return a <Config> object representing the global configuration file.
        """
        return Config._from_found_config(C.git_config_find_global)

    @staticmethod
    def get_xdg_config():
        """Return a <Config> object representing the global configuration file.
        """
        return Config._from_found_config(C.git_config_find_xdg)

class ConfigEntry(object):
    """An entry in a configuation object
    """

    @classmethod
    def _from_c(cls, ptr, iterator=None):
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
        return ffi.string(self._entry.name)

    @cached_property
    def raw_value(self):
        return ffi.string(self.c_value)

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
