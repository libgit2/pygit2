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

import weakref
from collections.abc import Callable
from typing import TYPE_CHECKING

from ._pygit2 import Blob, FilterSource
from .errors import check_error
from .ffi import C, ffi
from .utils import to_bytes

if TYPE_CHECKING:
    from ._libgit2.ffi import GitFilterListC
    from .repository import BaseRepository


class Filter:
    """
    Base filter class to be used with libgit2 filters.

    Inherit from this class and override the `check()`, `write()` and `close()`
    methods to define a filter which can then be registered via
    `pygit2.filter_register()`.

    A new Filter instance will be instantiated for each stream which needs to
    be filtered. For each stream, filter methods will be called in this order:

        - `check()`
        - `write()` (may be called multiple times)
        - `close()`

    Filtered output data should be written to the next filter in the chain
    during `write()` and `close()` via the `write_next` method. All output data
    must be written to the next filter before returning from `close()`.

    If a filter is dependent on reading the complete input data stream, the
    filter should only write output data in `close()`.
    """

    #: Space-separated string list of attributes to be used in `check()`
    attributes: str = ''

    @classmethod
    def nattrs(cls) -> int:
        return len(cls.attributes.split())

    def check(self, src: FilterSource, attr_values: list[str | None]) -> None:
        """
        Check whether this filter should be applied to the given source.

        `check` will be called once per stream.

        If `Passthrough` is raised, the filter will not be applied.

        Parameters:

        src: The source of the filtered blob.

        attr_values: The values of each attribute for the blob being filtered.
            `attr_values` will be a sorted list containing attributes in the
            order they were defined in ``cls.attributes``.
        """

    def write(
        self, data: bytes, src: FilterSource, write_next: Callable[[bytes], None]
    ) -> None:
        """
        Write input `data` to this filter.

        `write()` may be called multiple times per stream.

        Parameters:

        data: Input data.

        src: The source of the filtered blob.

        write_next: The ``write()`` method of the next filter in the chain.
            Filtered output data should be written to `write_next` whenever it is
            available.
        """
        write_next(data)

    def close(self, write_next: Callable[[bytes], None]) -> None:
        """
        Close this filter.

        `close()` will be called once per stream whenever all writes() to this
        stream have been completed.

        Parameters:
            write_next: The ``write()`` method of the next filter in the chain.
                Any remaining filtered output data must be written to
                `write_next` before returning.
        """


class FilterList:
    _all_filter_lists: set[weakref.ReferenceType[FilterList]] = set()

    _pointer: GitFilterListC

    @classmethod
    def _from_c(cls, ptr: GitFilterListC):
        if ptr == ffi.NULL:
            return None

        fl = cls.__new__(cls)
        fl._pointer = ptr

        # Keep track of this FilterList until it's garbage collected. This lets
        # `filter_unregister` ensure the user isn't trying to delete a filter
        # that's still in use.
        ref = weakref.ref(fl, FilterList._all_filter_lists.remove)
        FilterList._all_filter_lists.add(ref)

        return fl

    @classmethod
    def _is_filter_in_use(cls, name: str) -> bool:
        for ref in cls._all_filter_lists:
            fl = ref()
            if fl is not None and name in fl:
                return True
        return False

    def __contains__(self, name: str) -> bool:
        if not isinstance(name, str):
            raise TypeError('argument must be str')
        c_name = to_bytes(name)
        result = C.git_filter_list_contains(self._pointer, c_name)
        return bool(result)

    def __len__(self) -> int:
        return C.git_filter_list_length(self._pointer)

    def apply_to_buffer(self, data: bytes) -> bytes:
        """
        Apply a filter list to a data buffer.
        Return the filtered contents.
        """
        buf = ffi.new('git_buf *')
        err = C.git_filter_list_apply_to_buffer(buf, self._pointer, data, len(data))
        check_error(err)
        try:
            return ffi.string(buf.ptr)
        finally:
            C.git_buf_dispose(buf)

    def apply_to_file(self, repo: BaseRepository, path: str) -> bytes:
        """
        Apply a filter list to the contents of a file on disk.
        Return the filtered contents.
        """
        buf = ffi.new('git_buf *')
        c_path = to_bytes(path)
        err = C.git_filter_list_apply_to_file(buf, self._pointer, repo._repo, c_path)
        check_error(err)
        try:
            return ffi.string(buf.ptr)
        finally:
            C.git_buf_dispose(buf)

    def apply_to_blob(self, blob: Blob) -> bytes:
        """
        Apply a filter list to a data buffer.
        Return the filtered contents.
        """
        buf = ffi.new('git_buf *')

        c_blob = ffi.new('git_blob **')
        ffi.buffer(c_blob)[:] = blob._pointer[:]

        err = C.git_filter_list_apply_to_blob(buf, self._pointer, c_blob[0])
        check_error(err)
        try:
            return ffi.string(buf.ptr)
        finally:
            C.git_buf_dispose(buf)

    def __del__(self):
        C.git_filter_list_free(self._pointer)
