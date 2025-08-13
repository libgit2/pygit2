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

import sys

import pytest

import pygit2
from pygit2 import option
from pygit2.enums import ConfigLevel, ObjectType, Option


def __option(getter: Option, setter: Option, value: object) -> None:
    old_value = option(getter)
    option(setter, value)
    assert value == option(getter)
    # Reset to avoid side effects in later tests
    option(setter, old_value)


def __proxy(name: str, value: object) -> None:
    old_value = getattr(pygit2.settings, name)
    setattr(pygit2.settings, name, value)
    assert value == getattr(pygit2.settings, name)
    # Reset to avoid side effects in later tests
    setattr(pygit2.settings, name, old_value)


def test_mwindow_size() -> None:
    __option(Option.GET_MWINDOW_SIZE, Option.SET_MWINDOW_SIZE, 200 * 1024)


def test_mwindow_size_proxy() -> None:
    __proxy('mwindow_size', 300 * 1024)


def test_mwindow_mapped_limit_200() -> None:
    __option(
        Option.GET_MWINDOW_MAPPED_LIMIT, Option.SET_MWINDOW_MAPPED_LIMIT, 200 * 1024
    )


def test_mwindow_mapped_limit_300() -> None:
    __proxy('mwindow_mapped_limit', 300 * 1024)


def test_cache_object_limit() -> None:
    new_limit = 2 * 1024
    option(Option.SET_CACHE_OBJECT_LIMIT, ObjectType.BLOB, new_limit)


def test_cache_object_limit_proxy() -> None:
    new_limit = 4 * 1024
    pygit2.settings.cache_object_limit(ObjectType.BLOB, new_limit)


def test_cached_memory() -> None:
    value = option(Option.GET_CACHED_MEMORY)
    assert value[1] == 256 * 1024**2


def test_cached_memory_proxy() -> None:
    assert pygit2.settings.cached_memory[1] == 256 * 1024**2


def test_enable_caching() -> None:
    pygit2.settings.enable_caching(False)
    pygit2.settings.enable_caching(True)
    # Lower level API
    option(Option.ENABLE_CACHING, False)
    option(Option.ENABLE_CACHING, True)


def test_disable_pack_keep_file_checks() -> None:
    pygit2.settings.disable_pack_keep_file_checks(False)
    pygit2.settings.disable_pack_keep_file_checks(True)
    # Lower level API
    option(Option.DISABLE_PACK_KEEP_FILE_CHECKS, False)
    option(Option.DISABLE_PACK_KEEP_FILE_CHECKS, True)


def test_cache_max_size_proxy() -> None:
    pygit2.settings.cache_max_size(128 * 1024**2)
    assert pygit2.settings.cached_memory[1] == 128 * 1024**2
    pygit2.settings.cache_max_size(256 * 1024**2)
    assert pygit2.settings.cached_memory[1] == 256 * 1024**2


def test_search_path() -> None:
    paths = [
        (ConfigLevel.GLOBAL, '/tmp/global'),
        (ConfigLevel.XDG, '/tmp/xdg'),
        (ConfigLevel.SYSTEM, '/tmp/etc'),
    ]

    for level, path in paths:
        option(Option.SET_SEARCH_PATH, level, path)
        assert path == option(Option.GET_SEARCH_PATH, level)


def test_search_path_proxy() -> None:
    paths = [
        (ConfigLevel.GLOBAL, '/tmp2/global'),
        (ConfigLevel.XDG, '/tmp2/xdg'),
        (ConfigLevel.SYSTEM, '/tmp2/etc'),
    ]

    for level, path in paths:
        pygit2.settings.search_path[level] = path
        assert path == pygit2.settings.search_path[level]


def test_owner_validation() -> None:
    __option(Option.GET_OWNER_VALIDATION, Option.SET_OWNER_VALIDATION, 0)


def test_template_path() -> None:
    original_path = option(Option.GET_TEMPLATE_PATH)

    test_path = '/tmp/test_templates'
    option(Option.SET_TEMPLATE_PATH, test_path)
    assert option(Option.GET_TEMPLATE_PATH) == test_path

    if original_path:
        option(Option.SET_TEMPLATE_PATH, original_path)
    else:
        option(Option.SET_TEMPLATE_PATH, None)


def test_user_agent() -> None:
    original_agent = option(Option.GET_USER_AGENT)

    test_agent = 'test-agent/1.0'
    option(Option.SET_USER_AGENT, test_agent)
    assert option(Option.GET_USER_AGENT) == test_agent

    if original_agent:
        option(Option.SET_USER_AGENT, original_agent)


def test_pack_max_objects() -> None:
    __option(Option.GET_PACK_MAX_OBJECTS, Option.SET_PACK_MAX_OBJECTS, 100000)


@pytest.mark.skipif(sys.platform != 'win32', reason='Windows-specific feature')
def test_windows_sharemode() -> None:
    __option(Option.GET_WINDOWS_SHAREMODE, Option.SET_WINDOWS_SHAREMODE, 1)


def test_ssl_ciphers() -> None:
    # Setting SSL ciphers (no getter available)
    try:
        option(Option.SET_SSL_CIPHERS, 'DEFAULT')
    except pygit2.GitError as e:
        if "TLS backend doesn't support custom ciphers" in str(e):
            pytest.skip(str(e))
        raise


def test_enable_http_expect_continue() -> None:
    option(Option.ENABLE_HTTP_EXPECT_CONTINUE, True)
    option(Option.ENABLE_HTTP_EXPECT_CONTINUE, False)


def test_odb_priorities() -> None:
    option(Option.SET_ODB_PACKED_PRIORITY, 1)
    option(Option.SET_ODB_LOOSE_PRIORITY, 2)


def test_extensions() -> None:
    original_extensions = option(Option.GET_EXTENSIONS)
    assert isinstance(original_extensions, list)

    test_extensions = ['objectformat', 'worktreeconfig']
    option(Option.SET_EXTENSIONS, test_extensions, len(test_extensions))

    new_extensions = option(Option.GET_EXTENSIONS)
    assert isinstance(new_extensions, list)

    # Note: libgit2 may add its own built-in extensions and sort them
    for ext in test_extensions:
        assert ext in new_extensions, f"Extension '{ext}' not found in {new_extensions}"

    option(Option.SET_EXTENSIONS, [], 0)
    empty_extensions = option(Option.GET_EXTENSIONS)
    assert isinstance(empty_extensions, list)

    custom_extensions = ['myextension', 'objectformat']
    option(Option.SET_EXTENSIONS, custom_extensions, len(custom_extensions))
    custom_result = option(Option.GET_EXTENSIONS)
    assert 'myextension' in custom_result
    assert 'objectformat' in custom_result

    if original_extensions:
        option(Option.SET_EXTENSIONS, original_extensions, len(original_extensions))
    else:
        option(Option.SET_EXTENSIONS, [], 0)

    final_extensions = option(Option.GET_EXTENSIONS)
    assert set(final_extensions) == set(original_extensions)


def test_homedir() -> None:
    original_homedir = option(Option.GET_HOMEDIR)

    test_homedir = '/tmp/test_home'
    option(Option.SET_HOMEDIR, test_homedir)
    assert option(Option.GET_HOMEDIR) == test_homedir

    if original_homedir:
        option(Option.SET_HOMEDIR, original_homedir)
    else:
        option(Option.SET_HOMEDIR, None)


def test_server_timeouts() -> None:
    original_connect = option(Option.GET_SERVER_CONNECT_TIMEOUT)
    option(Option.SET_SERVER_CONNECT_TIMEOUT, 5000)
    assert option(Option.GET_SERVER_CONNECT_TIMEOUT) == 5000
    option(Option.SET_SERVER_CONNECT_TIMEOUT, original_connect)

    original_timeout = option(Option.GET_SERVER_TIMEOUT)
    option(Option.SET_SERVER_TIMEOUT, 10000)
    assert option(Option.GET_SERVER_TIMEOUT) == 10000
    option(Option.SET_SERVER_TIMEOUT, original_timeout)


def test_user_agent_product() -> None:
    original_product = option(Option.GET_USER_AGENT_PRODUCT)

    test_product = 'test-product'
    option(Option.SET_USER_AGENT_PRODUCT, test_product)
    assert option(Option.GET_USER_AGENT_PRODUCT) == test_product

    if original_product:
        option(Option.SET_USER_AGENT_PRODUCT, original_product)


def test_mwindow_file_limit() -> None:
    __option(Option.GET_MWINDOW_FILE_LIMIT, Option.SET_MWINDOW_FILE_LIMIT, 100)
