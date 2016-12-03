# -*- coding: utf-8 -*-
#
# Copyright 2010-2015 The pygit2 contributors
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

from _pygit2 import option
from _pygit2 import GIT_OPT_GET_SEARCH_PATH, GIT_OPT_SET_SEARCH_PATH
from _pygit2 import GIT_OPT_GET_MWINDOW_SIZE, GIT_OPT_SET_MWINDOW_SIZE
from _pygit2 import GIT_OPT_GET_MWINDOW_MAPPED_LIMIT, GIT_OPT_SET_MWINDOW_MAPPED_LIMIT
from _pygit2 import GIT_OPT_SET_CACHE_OBJECT_LIMIT
from _pygit2 import GIT_OPT_GET_CACHED_MEMORY
from _pygit2 import GIT_OPT_ENABLE_CACHING
from _pygit2 import GIT_OPT_SET_CACHE_MAX_SIZE


class SearchPathList(object):

    def __getitem__(self, key):
        return option(GIT_OPT_GET_SEARCH_PATH, key)

    def __setitem__(self, key, value):
        option(GIT_OPT_SET_SEARCH_PATH, key, value)


class Settings(object):
    """Library-wide settings"""

    __slots__ = []

    _search_path = SearchPathList()

    @property
    def search_path(self):
        """Configuration file search path.

        This behaves like an array whose indices correspond to the
        GIT_CONFIG_LEVEL_* values.  The local search path cannot be
        changed.
        """
        return self._search_path

    @property
    def mwindow_size(self):
        """Maximum mmap window size"""
        return option(GIT_OPT_GET_MWINDOW_SIZE)

    @mwindow_size.setter
    def mwindow_size(self, value):
        option(GIT_OPT_SET_MWINDOW_SIZE, value)

    @property
    def mwindow_mapped_limit(self):
        """Mwindow mapped limit"""
        return option(GIT_OPT_GET_MWINDOW_MAPPED_LIMIT)

    @mwindow_mapped_limit.setter
    def mwindow_mapped_limit(self, value):
        """Mwindow mapped limit"""
        return option(GIT_OPT_SET_MWINDOW_MAPPED_LIMIT, value)

    @property
    def cached_memory(self):
        """Maximum mmap window size"""
        return option(GIT_OPT_GET_CACHED_MEMORY)

    def enable_caching(self, value=True):
        return option(GIT_OPT_ENABLE_CACHING, value)

    def cache_max_size(self, value):
        return option(GIT_OPT_SET_CACHE_MAX_SIZE, value)

    def cache_object_limit(self, object_type, value):
        """Set the maximum data size for the given type of object to be
           considered eligible for caching in memory.

        Setting to value to zero means that that type of object will not
        be cached. Defaults to 0 for GIT_OBJ_BLOB (i.e. won't cache
        blobs) and 4k for GIT_OBJ_COMMIT, GIT_OBJ_TREE, and GIT_OBJ_TAG.
        """
        return option(GIT_OPT_SET_CACHE_OBJECT_LIMIT, object_type, value)


