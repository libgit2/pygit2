# -*- coding: utf-8 -*-
#
# Copyright 2010-2014 The pygit2 contributors
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

# Import from the future
from __future__ import absolute_import

# Import from the Standard Library
from string import hexdigits

# Import from pygit2
from _pygit2 import Oid

from .errors import check_error
from .ffi import ffi, C
from .utils import is_string, strings_to_strarray, to_bytes, to_str


class Diff(object):

    @classmethod
    def _from_c(cls, ptr, repo):
        diff = cls.__new__(cls)
        cdiff = ffi.new('git_diff **')
        ffi.buffer(cdiff)[:] = ptr[:]
        diff._diff = cdiff[0]
        diff._repo = repo

        return diff

    def __del__(self):
        C.git_diff_free(self._diff)

    @property
    def deltas(self):
        return DiffDeltaCollection(self)

    @property
    def patches(self):
        from .patch import PatchCollection
        return PatchCollection(self)

    def find_similar(self, flags=0, rename_threshold=50,
                     rename_from_rewrite_threshold=50, copy_threshold=50,
                     break_rewrite_threshold=60, rename_limit=200):
        """find_similar([flags, rename_threshold, copy_threshold, rename_from_rewrite_threshold, break_rewrite_threshold, rename_limit])

        Find renamed files in diff and updates them in-place in the diff itself.
        """
        copts = ffi.new('git_diff_find_options *')
        err = C.git_diff_find_init_options(copts, 1)
        check_error(err)

        copts.flags = flags
        copts.rename_threshold = rename_threshold
        copts.rename_from_rewrite_threshold = rename_from_rewrite_threshold
        copts.copy_threshold = copy_threshold
        copts.break_rewrite_threshold = break_rewrite_threshold
        copts.rename_limit = rename_limit

        err = C.git_diff_find_similar(self._diff, copts)
        check_error(err)

    def merge(self, diff):
        """merge(diff)

        Merge one diff into another.
        """
        if not isinstance(diff, Diff):
            return None

        err = C.git_diff_merge(self._diff, diff._diff)
        check_error(err)


class DiffDelta(object):
    __slots__ = ['status', 'flags', 'similarity', 'nfiles', 'old_file', 'new_file']

    def __init__(self, status, flags, similarity, nfiles, old_file, new_file):
        self.status = status
        """A GIT_DELTA_* constant."""
        self.flags = flags
        """Combination of GIT_DIFF_FLAG_* flags."""
        self.similarity = similarity
        """For renamed and copied, value 0-100."""
        self.nfiles = nfiles
        """Number of files in this delta."""
        self.old_file = old_file
        """\"from\" side of the diff."""
        self.new_file = new_file
        """\"to\" side of the diff."""

    @classmethod
    def _from_c(cls, cdelta):
        if cdelta == ffi.NULL:
            return None

        delta = cls.__new__(cls)
        delta.status = to_str(C.git_diff_status_char(cdelta.status))
        delta.flags = cdelta.flags
        delta.similarity = cdelta.similarity
        delta.nfiles = cdelta.nfiles
        delta.old_file = DiffFile._from_c(cdelta.old_file)
        delta.new_file = DiffFile._from_c(cdelta.new_file)

        return delta

    @property
    def is_binary(self):
        """True if binary data, False if not."""
        return not (self.flags & C.GIT_DIFF_FLAG_NOT_BINARY) and (self.flags & C.GIT_DIFF_FLAG_BINARY)


class DiffDeltaCollection(object):

    def __init__(self, diff):
        self._diff = diff

    def __len__(self):
        return C.git_diff_num_deltas(self._diff._diff)

    def __iter__(self):
        return DiffDeltaIterator(self)

    def __getitem__(self, idx):
        cdelta = ffi.NULL
        if not idx >= 0:
            raise ValueError(idx)
        else:
            cdelta = C.git_diff_get_delta(self._diff._diff, idx)
        
        if cdelta == ffi.NULL:
            raise KeyError(idx)

        return DiffDelta._from_c(cdelta)


class DiffDeltaIterator(object):

    def __init__(self, collection):
        self.collection = collection
        self.index = 0

    def next(self):
        return self.__next__()

    def __next__(self):
        if self.index >= len(self.collection):
            raise StopIteration

        delta = self.collection[self.index]
        self.index += 1

        return delta


class DiffFile(object):
    __slots__ = ['id', 'path', 'size', 'flags', 'mode']

    def __init__(self, id, path, size, flags, mode):
        self.id = id
        """The id of the item."""
        self.path = path
        """Path to the entry relative to the working directory."""
        self.size = size
        """Size of the entry in bytes."""
        self.flags = flags
        """Combination of GIT_DIFF_FLAG_* flags."""
        self.mode = mode
        """Mode of the entry."""

    @property
    def oid(self):
        # For backwards compatibility
        return self.id

    @classmethod
    def _from_c(cls, cfile):
        if cfile == ffi.NULL:
            return None

        file = cls.__new__(cls)
        file.id = Oid(raw=bytes(ffi.buffer(ffi.addressof(cfile, 'id'))[:]))
        file.path = to_str(ffi.string(cfile.path))
        file.size = cfile.size
        file.flags = cfile.flags
        file.mode = cfile.mode

        return file


class DiffHunk(object):
    __slots__ = ['patch', 'index', 'old_start', 'old_lines', 'new_start', 'new_lines', 'header']

    def __init__(self, patch, index, old_start, old_lines, new_start, new_lines, header):
        self.patch = patch
        """Patch."""
        self.index = index
        """Hunk index within a patch."""
        self.old_start = old_start
        """Starting line number in old file."""
        self.old_lines = old_lines
        """Number of lines in old file."""
        self.new_start = new_start
        """Start line number in new file."""
        self.new_lines = new_lines
        """Number of lines in new file."""
        self.header = header
        """Header text."""

    @classmethod
    def _from_c(cls, chunk, patch, index):
        if chunk == ffi.NULL:
            return None

        hunk = cls.__new__(cls)
        hunk.patch = patch
        hunk.index = index
        hunk.old_start = chunk.old_start
        hunk.old_lines = chunk.old_lines
        hunk.new_start = chunk.new_start
        hunk.new_lines = chunk.new_lines
        hunk.header = to_str(ffi.string(chunk.header, chunk.header_len))

        return hunk

    @property
    def lines(self):
        return DiffLineCollection(self.patch, self.index)


class DiffHunkCollection(object):

    def __init__(self, patch):
        self._patch = patch

    def __len__(self):
        return C.git_patch_num_hunks(self._patch._patch)

    def __iter__(self):
        return DiffHunkIterator(self)

    def __getitem__(self, idx):
        hunk_cptr = ffi.new('git_diff_hunk **')
        if not idx >= 0:
            raise ValueError(idx)
        else:
            err = C.git_patch_get_hunk(hunk_cptr, ffi.NULL, self._patch._patch, idx)
            check_error(err)

        if hunk_cptr == ffi.NULL:
            raise KeyError(idx)

        return DiffHunk._from_c(hunk_cptr[0], self._patch, idx)


class DiffHunkIterator(object):

    def __init__(self, collection):
        self.collection = collection
        self.i = 0
        self.max = len(collection)

    def next(self):
        return self.__next__()

    def __next__(self):
        if self.i >= self.max:
            raise StopIteration

        hunk = self.collection[self.i]
        self.i += 1

        return hunk


class DiffLine(object):
    __slots__ = ['origin', 'old_lineno', 'new_lineno', 'num_lines', 'content', 'content_offset']

    def __init__(self, origin, old_lineno, new_lineno, num_lines, content, content_offset):
        self.origin = origin
        """A GIT_DIFF_LINE_* constant."""
        self.old_lineno = old_lineno
        """Line number in old file or -1 for added line."""
        self.new_lineno = new_lineno
        """Line number in new file or -1 for deleted line."""
        self.num_lines = num_lines
        """Number of newline characters in content."""
        self.content = content
        """Diff text."""
        self.content_offset = content_offset
        """Offset in the original file to the content."""

    @classmethod
    def _from_c(cls, cline):
        if cline == ffi.NULL:
            return None

        line = cls.__new__(cls)
        line.origin = to_str(cline.origin)
        line.old_lineno = cline.old_lineno
        line.new_lineno = cline.new_lineno
        line.num_lines = cline.num_lines
        line.content = to_str(ffi.string(cline.content, cline.content_len))
        line.content_offset = cline.content_offset

        return line


class DiffLineCollection(object):

    def __init__(self, patch, index):
        self._patch = patch
        self._index = index

    def __len__(self):
        return C.git_patch_num_lines_in_hunk(self._patch._patch, self._index)

    def __iter__(self):
        return DiffLineIterator(self)

    def __getitem__(self, idx):
        line_cptr = ffi.new('git_diff_line **')
        if not idx >= 0:
            raise ValueError(idx)
        else:
            err = C.git_patch_get_line_in_hunk(line_cptr, self._patch._patch, self._index, idx)
            check_error(err)
        
        if line_cptr == ffi.NULL:
            raise KeyError(idx)

        return DiffLine._from_c(line_cptr[0])


class DiffLineIterator(object):

    def __init__(self, collection):
        self.collection = collection
        self.index = 0

    def next(self):
        return self.__next__()

    def __next__(self):
        if self.index >= len(self.collection):
            raise StopIteration

        hunk = self.collection[self.index]
        self.index += 1

        return hunk
