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

"""Test the Settings class."""

import sys

import pytest

import pygit2
from pygit2.enums import ConfigLevel, ObjectType


def test_mwindow_size() -> None:
    original = pygit2.settings.mwindow_size
    try:
        test_size = 200 * 1024
        pygit2.settings.mwindow_size = test_size
        assert pygit2.settings.mwindow_size == test_size
    finally:
        pygit2.settings.mwindow_size = original


def test_mwindow_mapped_limit() -> None:
    original = pygit2.settings.mwindow_mapped_limit
    try:
        test_limit = 300 * 1024
        pygit2.settings.mwindow_mapped_limit = test_limit
        assert pygit2.settings.mwindow_mapped_limit == test_limit
    finally:
        pygit2.settings.mwindow_mapped_limit = original


def test_cached_memory() -> None:
    cached = pygit2.settings.cached_memory
    assert isinstance(cached, tuple)
    assert len(cached) == 2
    assert isinstance(cached[0], int)
    assert isinstance(cached[1], int)


def test_enable_caching() -> None:
    assert hasattr(pygit2.settings, 'enable_caching')
    assert callable(pygit2.settings.enable_caching)

    # Should not raise exceptions
    pygit2.settings.enable_caching(False)
    pygit2.settings.enable_caching(True)


def test_disable_pack_keep_file_checks() -> None:
    assert hasattr(pygit2.settings, 'disable_pack_keep_file_checks')
    assert callable(pygit2.settings.disable_pack_keep_file_checks)

    # Should not raise exceptions
    pygit2.settings.disable_pack_keep_file_checks(False)
    pygit2.settings.disable_pack_keep_file_checks(True)
    pygit2.settings.disable_pack_keep_file_checks(False)


def test_cache_max_size() -> None:
    original_max_size = pygit2.settings.cached_memory[1]
    try:
        pygit2.settings.cache_max_size(128 * 1024**2)
        assert pygit2.settings.cached_memory[1] == 128 * 1024**2
        pygit2.settings.cache_max_size(256 * 1024**2)
        assert pygit2.settings.cached_memory[1] == 256 * 1024**2
    finally:
        pygit2.settings.cache_max_size(original_max_size)


@pytest.mark.parametrize(
    'object_type,test_size,default_size',
    [
        (ObjectType.BLOB, 2 * 1024, 0),
        (ObjectType.COMMIT, 8 * 1024, 4096),
        (ObjectType.TREE, 8 * 1024, 4096),
        (ObjectType.TAG, 8 * 1024, 4096),
        (ObjectType.BLOB, 0, 0),
    ],
)
def test_cache_object_limit(
    object_type: ObjectType, test_size: int, default_size: int
) -> None:
    assert callable(pygit2.settings.cache_object_limit)

    pygit2.settings.cache_object_limit(object_type, test_size)
    pygit2.settings.cache_object_limit(object_type, default_size)


@pytest.mark.parametrize(
    'level,test_path',
    [
        (ConfigLevel.GLOBAL, '/tmp/test_global'),
        (ConfigLevel.XDG, '/tmp/test_xdg'),
        (ConfigLevel.SYSTEM, '/tmp/test_system'),
    ],
)
def test_search_path(level: ConfigLevel, test_path: str) -> None:
    original = pygit2.settings.search_path[level]
    try:
        pygit2.settings.search_path[level] = test_path
        assert pygit2.settings.search_path[level] == test_path
    finally:
        pygit2.settings.search_path[level] = original


def test_template_path() -> None:
    original = pygit2.settings.template_path
    try:
        pygit2.settings.template_path = '/tmp/test_templates'
        assert pygit2.settings.template_path == '/tmp/test_templates'
    finally:
        if original:
            pygit2.settings.template_path = original


def test_user_agent() -> None:
    original = pygit2.settings.user_agent
    try:
        pygit2.settings.user_agent = 'test-agent/1.0'
        assert pygit2.settings.user_agent == 'test-agent/1.0'
    finally:
        if original:
            pygit2.settings.user_agent = original


def test_user_agent_product() -> None:
    original = pygit2.settings.user_agent_product
    try:
        pygit2.settings.user_agent_product = 'test-product'
        assert pygit2.settings.user_agent_product == 'test-product'
    finally:
        if original:
            pygit2.settings.user_agent_product = original


def test_pack_max_objects() -> None:
    original = pygit2.settings.pack_max_objects
    try:
        pygit2.settings.pack_max_objects = 100000
        assert pygit2.settings.pack_max_objects == 100000
    finally:
        pygit2.settings.pack_max_objects = original


def test_owner_validation() -> None:
    original = pygit2.settings.owner_validation
    try:
        pygit2.settings.owner_validation = False
        assert pygit2.settings.owner_validation == False  # noqa: E712
        pygit2.settings.owner_validation = True
        assert pygit2.settings.owner_validation == True  # noqa: E712
    finally:
        pygit2.settings.owner_validation = original


def test_mwindow_file_limit() -> None:
    original = pygit2.settings.mwindow_file_limit
    try:
        pygit2.settings.mwindow_file_limit = 100
        assert pygit2.settings.mwindow_file_limit == 100
    finally:
        pygit2.settings.mwindow_file_limit = original


def test_homedir() -> None:
    original = pygit2.settings.homedir
    try:
        pygit2.settings.homedir = '/tmp/test_home'
        assert pygit2.settings.homedir == '/tmp/test_home'
    finally:
        if original:
            pygit2.settings.homedir = original


def test_server_timeouts() -> None:
    original_connect = pygit2.settings.server_connect_timeout
    original_timeout = pygit2.settings.server_timeout
    try:
        pygit2.settings.server_connect_timeout = 5000
        assert pygit2.settings.server_connect_timeout == 5000

        pygit2.settings.server_timeout = 10000
        assert pygit2.settings.server_timeout == 10000
    finally:
        pygit2.settings.server_connect_timeout = original_connect
        pygit2.settings.server_timeout = original_timeout


def test_extensions() -> None:
    original = pygit2.settings.extensions
    try:
        test_extensions = ['objectformat', 'worktreeconfig']
        pygit2.settings.set_extensions(test_extensions)

        new_extensions = pygit2.settings.extensions
        for ext in test_extensions:
            assert ext in new_extensions
    finally:
        if original:
            pygit2.settings.set_extensions(original)


@pytest.mark.parametrize(
    'method_name,default_value',
    [
        ('enable_strict_object_creation', True),
        ('enable_strict_symbolic_ref_creation', True),
        ('enable_ofs_delta', True),
        ('enable_fsync_gitdir', False),
        ('enable_strict_hash_verification', True),
        ('enable_unsaved_index_safety', False),
        ('enable_http_expect_continue', False),
    ],
)
def test_enable_methods(method_name: str, default_value: bool) -> None:
    assert hasattr(pygit2.settings, method_name)
    method = getattr(pygit2.settings, method_name)
    assert callable(method)

    method(True)
    method(False)
    method(default_value)


@pytest.mark.parametrize('priority', [1, 5, 10, 0, -1, -2])
def test_odb_priorities(priority: int) -> None:
    """Test setting ODB priorities"""
    assert hasattr(pygit2.settings, 'set_odb_packed_priority')
    assert hasattr(pygit2.settings, 'set_odb_loose_priority')
    assert callable(pygit2.settings.set_odb_packed_priority)
    assert callable(pygit2.settings.set_odb_loose_priority)

    pygit2.settings.set_odb_packed_priority(priority)
    pygit2.settings.set_odb_loose_priority(priority)

    pygit2.settings.set_odb_packed_priority(1)
    pygit2.settings.set_odb_loose_priority(2)


def test_ssl_ciphers() -> None:
    assert callable(pygit2.settings.set_ssl_ciphers)

    try:
        pygit2.settings.set_ssl_ciphers('DEFAULT')
    except pygit2.GitError as e:
        if "TLS backend doesn't support" in str(e):
            pytest.skip(str(e))
        raise


@pytest.mark.skipif(sys.platform != 'win32', reason='Windows-specific feature')
def test_windows_sharemode() -> None:
    original = pygit2.settings.windows_sharemode
    try:
        pygit2.settings.windows_sharemode = 1
        assert pygit2.settings.windows_sharemode == 1
        pygit2.settings.windows_sharemode = 2
        assert pygit2.settings.windows_sharemode == 2
    finally:
        pygit2.settings.windows_sharemode = original
