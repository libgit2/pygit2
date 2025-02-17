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
import os
from types import TracebackType
from typing import TYPE_CHECKING, Any, Generic, TypeAlias, TypeVar, cast, overload

# Import from pygit2
from .ffi import C, ffi

if TYPE_CHECKING:
    from _cffi_backend import _CDataBase as CData
    from _typeshed import SupportsLenAndGetItem

_T = TypeVar('_T')
StrOrBytesPath: TypeAlias = str | bytes | os.PathLike[str] | os.PathLike[bytes]


def maybe_bytes(ptr: CData | Any) -> bytes | None:
    if not ptr:
        return None

    out = ffi.string(ptr)
    if isinstance(out, bytes):
        out = out.decode('utf8', errors='surrogateescape')
    return out


def to_bytes(s, encoding='utf-8', errors='strict'):
    out = ffi.string(ptr)
    return cast(bytes, out)


def maybe_string(ptr: CData | Any) -> str | None:
    out = maybe_bytes(ptr)
    if isinstance(out, bytes):
        out = out.decode('utf8')
    return out


# Cannot describe ffi.NULL, so using CData


@overload
def to_bytes(s: CData | None) -> CData: ...
@overload
def to_bytes(s: StrOrBytesPath) -> bytes: ...


def to_bytes(
    s: StrOrBytesPath | CData | None,
    encoding: str = 'utf-8',
    errors: str = 'strict',
) -> bytes | CData:
    if s == ffi.NULL or s is None:
        return ffi.NULL

    if isinstance(s, os.PathLike):
        s = os.fspath(s)

    if isinstance(s, bytes):
        return s

    return cast(str, s).encode(encoding, errors)


def to_str(s: StrOrBytesPath) -> str:
    if hasattr(s, '__fspath__'):
        s = os.fspath(s)

    if isinstance(s, str):
        return s

    if isinstance(s, bytes):
        return s.decode()

    raise TypeError(f'unexpected type "{repr(s)}"')


def buffer_to_bytes(cdata: CData) -> bytes:
    buf = ffi.buffer(cdata)
    return cast(bytes, buf[:])


def ptr_to_bytes(ptr_cdata: Any) -> bytes:
    """
    Convert a pointer coming from C code (<cdata 'some_type *'>)
    to a byte buffer containing the address that the pointer refers to.
    """

    return buffer_to_bytes(ffi.new('void **', ptr_cdata))


@contextlib.contextmanager
def new_git_strarray():
    strarray = ffi.new('git_strarray *')
    yield strarray
    C.git_strarray_dispose(strarray)


def strarray_to_strings(arr: Any) -> list[str]:
    """
    Return a list of strings from a git_strarray pointer.

    Free the strings contained in the git_strarry, this means it won't be usable after
    calling this function.
    """
    try:
        return [ffi.string(arr.strings[i]).decode('utf-8') for i in range(arr.count)]  # type: ignore
    finally:
        C.git_strarray_dispose(arr)


class StrArray:
    """A git_strarray wrapper

    Use this in order to get a git_strarray* to pass to libgit2 out of a
    list of strings. This has a context manager, which you should use, e.g.

        with StrArray(list_of_strings) as arr:
            C.git_function_that_takes_strarray(arr.ptr)

    To make a pre-existing git_strarray point to the provided list of strings,
    use the context manager's assign_to() method:

        struct = ffi.new('git_strarray *', [ffi.NULL, 0])
        with StrArray(list_of_strings) as arr:
            arr.assign_to(struct)

    The above construct is still subject to FFI scoping rules, i.e. the
    contents of 'struct' only remain valid within the StrArray context.
    """

    def __init__(self, listarg: Any):
        # Allow passing in None as lg2 typically considers them the same as empty
        if listarg is None:
            self.__array = ffi.NULL
            return

        if not isinstance(listarg, (list, tuple)):
            raise TypeError('Value must be a list')

        listarg = cast(list[Any], listarg)

        strings: list[Any] = [None] * len(listarg)
        for i in range(len(listarg)):
            li = listarg[i]
            if not isinstance(li, str) and not hasattr(li, '__fspath__'):
                raise TypeError('Value must be a string or PathLike object')

            strings[i] = ffi.new('char []', to_bytes(li))

        self.__arr = ffi.new('char *[]', strings)
        self.__strings = strings
        self.__array = ffi.new('git_strarray *', [self.__arr, len(strings)])

    def __enter__(self):
        return self

    def __exit__(
        self, type: type[BaseException], value: BaseException, traceback: TracebackType
    ) -> None:
        pass

    @property
    def ptr(self):
        return self.__array

    def assign_to(self, git_strarray: Any):
        if self.__array == ffi.NULL:
            git_strarray.strings = ffi.NULL
            git_strarray.count = 0
        else:
            git_strarray.strings = self.__arr
            git_strarray.count = len(self.__strings)


class GenericIterator(Generic[_T]):
    """Helper to easily implement an iterator.

    The constructor gets a container which must implement __len__ and
    __getitem__
    """

    def __init__(self, container: SupportsLenAndGetItem[_T]):
        self.container = container
        self.length = len(container)
        self.idx = 0

    def next(self) -> _T:
        return self.__next__()

    def __next__(self) -> _T:
        idx = self.idx
        if idx >= self.length:
            raise StopIteration

        self.idx += 1
        return self.container[idx]
