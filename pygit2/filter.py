# Copyright 2010-2023 The pygit2 contributors
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

from contextlib import ExitStack, contextmanager
from functools import partial, wraps
from threading import Lock
from typing import Callable, List, Optional, Type

from ._pygit2 import Oid
from .callbacks import Payload
from .errors import check_error, Passthrough
from .ffi import ffi, C
from .utils import maybe_string, to_bytes


class FilterSource:
    """
    A filter source represents the file/blob to be processed.

    Attributes:
        path: File path the source data is from.
        filemode: Mode of the source file. If this is unknown,
            `filemode` will be 0.
        oid: Oid of the source object. If the Oid is unknown
            (often the case with GIT_FILTER_CLEAN) then `oid` will
            be None.
        flags: GIT_FILTER_* flags to be applied for this blob.
    """
    path: str
    filemode: int
    oid: Optional[Oid]
    flags: int

    @classmethod
    def _from_c(cls, ptr):
        src = cls.__new__(cls)
        src.path = maybe_string(C.git_filter_source_path(ptr))
        src.filemode = C.git_filter_source_filemode(ptr)
        try:
            oid_ptr = C.git_filter_source_id(ptr)
            src.oid = Oid(raw=bytes(ffi.buffer(oid_ptr)[:]))
        except ValueError:
            src.oid = None
        src.mode = C.git_filter_source_mode(ptr)
        src.flags = C.git_filter_source_flags(ptr)
        return src


class Filter:
    """
    Base filter class to be used with libgit2 filters.

    A new Filter instance will be instantiated for each stream which needs to
    be filtered. For each stream, filter methods will be called in this order:

        - `check()`
        - `write()` (may be called multiple times)
        - `close()`

    Output data should be written to the next filter in the chain during
    `write()` and `close()` via the `write_next` method. All output data
    must be written to the next filter before returning from `close()`.

    If a filter is dependent on reading the complete input data stream, the
    filter should only write output data in `close()`.
    """

    #: Space-separated string list of attributes to be used in `check()`
    attributes: str = ""

    def check(self, src: FilterSource, attr_values: List[str]):
        """
        Check whether this filter should be applied to the given source.

        `check` will be called once per stream.

        If `Passthrough` is raised, the filter will not be applied.
        """

    def write(
        self,
        data: bytes,
        src: FilterSource,
        write_next: Callable[[bytes], None]
    ):
        """
        Write input `data` to this filter.

        `write()` may be called multiple times per stream.

        Output data should be written to `write_next` whenever it is available.
        """
        write_next(data)

    def close(
        self,
        write_next: Callable[[bytes], None]
    ):
        """
        Close this filter.

        `close()` will be called once per stream whenever all writes() to this
        stream have been completed.

        Any remaining output data should be written to `write_next` before
        returning.
        """


_refs_lock = Lock()
_filter_refs = {}


def libgit2_filter_callback(f=None, self_index=0):
    if f is None:
        return partial(libgit2_filter_callback, self_index=self_index)

    @wraps(f)
    def wrapper(*args):
        cdata = args[self_index]
        with _refs_lock:
            data = ffi.from_handle(_filter_refs[cdata])
        args = args[:self_index] + (data,) + args[self_index + 1:]
        try:
            return f(*args)
        except Passthrough:
            # A user defined callback can raise Passthrough to decline to act;
            # then libgit2 will behave as if there was no callback set in the
            # first place.
            return C.GIT_PASSTHROUGH
        except BaseException as e:
            # Keep the exception to be re-raised later, and inform libgit2 that
            # the user defined callback has failed.
            data._stored_exception = e
            return C.GIT_EUSER

    return ffi.def_extern()(wrapper)


def libgit2_filter_callback_void(f=None, self_index=0):
    if f is None:
        return partial(libgit2_filter_callback_void, self_index=self_index)

    @wraps(f)
    def wrapper(*args):
        cdata = args[self_index]
        with _refs_lock:
            data = ffi.from_handle(_filter_refs[cdata])
        args = args[:self_index] + (data,) + args[self_index + 1:]
        try:
            f(*args)
        except Passthrough:
            # A user defined callback can raise Passthrough to decline to act;
            # then libgit2 will behave as if there was no callback set in the
            # first place.
            pass  # Function returns void
        except BaseException as e:
            # Keep the exception to be re-raised later
            data._stored_exception = e
            pass  # Function returns void, so we can't do much here.

    return ffi.def_extern()(wrapper)


class _FilterCallbacks(Payload):
    """Base class for pygit2 filter callbacks.

    In most cases you should use the higher level `pygit2.Filter` class to
    implement filters.
    """

    def __init__(self, filter_cls: Optional[Filter] = None, exit_stack=None):
        self._filters = {}
        if filter_cls is not None:
            self.filter_cls = filter_cls
        if exit_stack is not None:
            self.exit_stack = exit_stack

    def filter_check(self, src, attr_values):
        filter_cls = getattr(self, 'filter_cls', None)
        if filter_cls is None:
            return None

        filter = filter_cls()
        handle = ffi.new_handle(filter)
        self._filters[handle] = filter

        src = FilterSource._from_c(src)
        attr_values = [
            maybe_string(attr_values[i])
            for i in range(len(filter.attributes.split()))
        ]
        filter.check(src, attr_values)

        return handle

    def filter_stream(self, payload, src, next):
        filter = ffi.from_handle(payload[0])
        if filter == ffi.NULL:
            filter_cls = getattr(self, 'filter_cls', None)
            if filter_cls is None:
                return None
            filter = filter_cls()
            handle = ffi.new_handle(filter)
            self._filters[handle] = filter
        stack = ExitStack()
        src = FilterSource._from_c(src)
        callbacks = _WritestreamCallbacks(
            filter=filter, src=src, next=next, exit_stack=stack
        )
        stream = stack.enter_context(_git_writestream(callbacks))
        return stream

    def filter_cleanup(self, payload):
        if ffi.from_handle(payload) != ffi.NULL:
            del self._filters[payload]


class _WritestreamCallbacks(Payload):
    """
    Buffered git_writestream callbacks for pygit2 filters.
    """

    def __init__(self, filter=None, src=None, next=None, exit_stack=None):
        super().__init__()
        if filter is not None:
            self.filter = filter
        if src is not None:
            self.src = src
        if next is not None:
            self.next = next
        if exit_stack is not None:
            self.exit_stack = exit_stack
        self._closed_next = False

    def writestream_write(self, buffer, size):
        filter = getattr(self, 'filter', None)
        data = bytes(ffi.buffer(buffer, size)[:])
        try:
            if filter is None:
                self._write_next(data)
                return
            src = getattr(self, 'src', None)
            filter.write(data, src, self._write_next)
        except BaseException:
            self._close_next(False)
            raise

    def writestream_close(self):
        filter = getattr(self, 'filter', None)
        try:
            if filter is not None:
                filter.close(self._write_next)
        finally:
            self._close_next()

    def writestream_free(self):
        """
        Free any resources associated with this stream.
        """
        exit_stack = getattr(self, 'exit_stack', None)
        if exit_stack:
            exit_stack.close()

    def _write_next(self, data: bytes):
        next_stream = getattr(self, 'next', None)
        if next_stream is not None:
            err = next_stream.write(next_stream, data, len(data))
            check_error(err)

    def _close_next(self, check: bool = True):
        if self._closed_next:
            return
        self._closed_next = True
        next_stream = getattr(self, 'next', None)
        if next_stream is not None:
            err = next_stream.close(next_stream)
            if check:
                check_error(err)


@contextmanager
def _git_writestream(payload):
    if payload is None:
        payload = _WritestreamCallbacks()

    cdata = ffi.new('git_writestream *')

    # Plug callbacks
    cdata.write = C._writestream_write_cb
    cdata.close = C._writestream_close_cb
    cdata.free = C._writestream_free_cb
    # Payload
    handle = ffi.new_handle(payload)
    with _refs_lock:
        _filter_refs[cdata] = handle

    # Give back control
    payload._stored_exception = None
    payload.writestream = cdata
    yield payload
    with _refs_lock:
        del _filter_refs[cdata]


@contextmanager
def _git_filter(payload):
    if payload is None:
        payload = _FilterCallbacks()

    cdata = ffi.new('git_filter *')
    C.git_filter_init(cdata, C.GIT_FILTER_VERSION)

    filter_cls = getattr(payload, 'filter_cls', None)
    # Plug callbacks
    if filter_cls is None:
        raise TypeError('filter class must be set')
    attributes = ffi.new('char[]', to_bytes(filter_cls.attributes))
    refs = [attributes]
    cdata.attributes = attributes
    cdata.shutdown = C._filter_shutdown_cb
    cdata.check = C._filter_check_cb
    cdata.stream = C._filter_stream_cb
    cdata.cleanup = C._filter_cleanup_cb
    # Payload
    handle = ffi.new_handle(payload)
    with _refs_lock:
        _filter_refs[cdata] = handle

    # Give back control
    payload._stored_exception = None
    payload.filter = cdata
    payload._refs = refs
    yield payload
    with _refs_lock:
        del _filter_refs[cdata]


def filter_register(
    name: str,
    filter_cls: Type[Filter],
    priority: int = C.GIT_FILTER_DRIVER_PRIORITY,
):
    """
    Register a filter under the given name.

    Filters will be run in order of `priority` on smudge (to workdir) and in
    reverse order of priority on clean (to odb).

    Two filters are preregistered with libgit2:
        - GIT_FILTER_CRLF with priority 0
        - GIT_FILTER_IDENT with priority 100

    `priority` defaults to GIT_FILTER_DRIVER_PRIORITY which imitates a core
    Git filter driver that will be run last on checkout (smudge) and first on
    checkin (clean).

    Note that the filter registry is not thread safe. Any registering or
    deregistering of filters should be done outside of any possible usage
    of the filters.
    """
    stack = ExitStack()
    callbacks = _FilterCallbacks(filter_cls=filter_cls, exit_stack=stack)
    cdata = stack.enter_context(_git_filter(callbacks))
    error_code = C.git_filter_register(to_bytes(name), cdata.filter, priority)
    check_error(error_code)


def filter_unregister(name: str):
    """Unregister the given filter.

    Note that the filter registry is not thread safe. Any registering or
    deregistering of filters should be done outside of any possible usage
    of the filters.
    """
    error_code = C.git_filter_unregister(to_bytes(name))
    check_error(error_code)


@libgit2_filter_callback_void
def _filter_shutdown_cb(data: _FilterCallbacks):
    exit_stack = getattr(data, 'exit_stack', None)
    if exit_stack is not None:
        exit_stack.close()


@libgit2_filter_callback
def _filter_check_cb(data: _FilterCallbacks, payload, src, attr_values):
    filter_check = getattr(data, 'filter_check', None)
    if not filter_check:
        return 0
    handle = filter_check(src, attr_values)
    if handle is not None:
        payload[0] = handle
    return 0


@libgit2_filter_callback(self_index=1)
def _filter_stream_cb(out, data: _FilterCallbacks, payload, src, next):
    filter_stream = getattr(data, 'filter_stream', None)
    if not filter_stream:
        out[0] = next
        return 0
    cdata = filter_stream(payload, src, next)
    if cdata is None:
        out[0] = next
    else:
        out[0] = cdata.writestream
    return 0


@libgit2_filter_callback_void
def _filter_cleanup_cb(data: _FilterCallbacks, payload):
    filter_cleanup = getattr(data, 'filter_cleanup', None)
    if not filter_cleanup:
        return
    filter_cleanup(payload)


@libgit2_filter_callback
def _writestream_write_cb(data: _WritestreamCallbacks, buffer, len):
    writestream_write = getattr(data, 'writestream_write', None)
    if not writestream_write:
        return 0
    writestream_write(buffer, len)
    return 0


@libgit2_filter_callback
def _writestream_close_cb(data: _WritestreamCallbacks):
    writestream_close = getattr(data, 'writestream_close', None)
    if not writestream_close:
        return 0
    writestream_close()
    return 0


@libgit2_filter_callback_void
def _writestream_free_cb(data: _WritestreamCallbacks):
    writestream_free = getattr(data, 'writestream_free', None)
    if writestream_free is not None:
        writestream_free()
