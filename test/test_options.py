# Copyright 2010-2024 The pygit2 contributors
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

import pygit2
from pygit2 import option
from pygit2.enums import ConfigLevel, ObjectType, Option


def __option(getter, setter, value):
    old_value = option(getter)
    option(setter, value)
    assert value == option(getter)
    # Reset to avoid side effects in later tests
    option(setter, old_value)


def __proxy(name, value):
    old_value = getattr(pygit2.settings, name)
    setattr(pygit2.settings, name, value)
    assert value == getattr(pygit2.settings, name)
    # Reset to avoid side effects in later tests
    setattr(pygit2.settings, name, old_value)


def test_mwindow_size():
    __option(Option.GET_MWINDOW_SIZE, Option.SET_MWINDOW_SIZE, 200 * 1024)


def test_mwindow_size_proxy():
    __proxy('mwindow_size', 300 * 1024)


def test_mwindow_mapped_limit_200():
    __option(
        Option.GET_MWINDOW_MAPPED_LIMIT, Option.SET_MWINDOW_MAPPED_LIMIT, 200 * 1024
    )


def test_mwindow_mapped_limit_300():
    __proxy('mwindow_mapped_limit', 300 * 1024)


def test_cache_object_limit():
    new_limit = 2 * 1024
    option(Option.SET_CACHE_OBJECT_LIMIT, ObjectType.BLOB, new_limit)


def test_cache_object_limit_proxy():
    new_limit = 4 * 1024
    pygit2.settings.cache_object_limit(ObjectType.BLOB, new_limit)


def test_cached_memory():
    value = option(Option.GET_CACHED_MEMORY)
    assert value[1] == 256 * 1024**2


def test_cached_memory_proxy():
    assert pygit2.settings.cached_memory[1] == 256 * 1024**2


def test_enable_caching():
    pygit2.settings.enable_caching(False)
    pygit2.settings.enable_caching(True)
    # Lower level API
    option(Option.ENABLE_CACHING, False)
    option(Option.ENABLE_CACHING, True)


def test_disable_pack_keep_file_checks():
    pygit2.settings.disable_pack_keep_file_checks(False)
    pygit2.settings.disable_pack_keep_file_checks(True)
    # Lower level API
    option(Option.DISABLE_PACK_KEEP_FILE_CHECKS, False)
    option(Option.DISABLE_PACK_KEEP_FILE_CHECKS, True)


def test_cache_max_size_proxy():
    pygit2.settings.cache_max_size(128 * 1024**2)
    assert pygit2.settings.cached_memory[1] == 128 * 1024**2
    pygit2.settings.cache_max_size(256 * 1024**2)
    assert pygit2.settings.cached_memory[1] == 256 * 1024**2


def test_search_path():
    paths = [
        (ConfigLevel.GLOBAL, '/tmp/global'),
        (ConfigLevel.XDG, '/tmp/xdg'),
        (ConfigLevel.SYSTEM, '/tmp/etc'),
    ]

    for level, path in paths:
        option(Option.SET_SEARCH_PATH, level, path)
        assert path == option(Option.GET_SEARCH_PATH, level)


def test_search_path_proxy():
    paths = [
        (ConfigLevel.GLOBAL, '/tmp2/global'),
        (ConfigLevel.XDG, '/tmp2/xdg'),
        (ConfigLevel.SYSTEM, '/tmp2/etc'),
    ]

    for level, path in paths:
        pygit2.settings.search_path[level] = path
        assert path == pygit2.settings.search_path[level]


def test_owner_validation():
    __option(Option.GET_OWNER_VALIDATION, Option.SET_OWNER_VALIDATION, 0)
