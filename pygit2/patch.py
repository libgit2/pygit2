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
from .diff import DiffDelta, DiffHunkCollection
from .errors import check_error
from .ffi import ffi, C
from .utils import to_bytes, to_str


class Patch(object):

    @classmethod
    def _from_c(cls, ptr):
        patch = cls.__new__(cls)
        cpatch = ffi.new('git_patch **')
        ffi.buffer(cpatch)[:] = ptr[:]
        patch._patch = cpatch[0]

        return patch

    @classmethod
    def from_blob_and_buffer(cls, old_blob=None, old_as_path=None, buffer=None, buffer_as_path=None, flags=0):
        """from_blob_and_buffer([old_blob, old_as_path, buffer, buffer_as_path, flags] -> Patch

        Directly generate a :py:class:`~pygit2.Patch` from the difference between a blob and a buffer.
  
        :param Blob old_blob: the :py:class:`~pygit2.Blob` for old side of diff.
        :param str old_as_path: treat old blob as if it had this filename.
        :param Blob buffer: Raw data for new side of diff.
        :param str buffer_as_path: treat buffer as if it had this filename.
        :param flag: a GIT_DIFF_* constant.
        :rtype: Patch
        """
        copts = ffi.new('git_diff_options *')
        err = C.git_diff_init_options(copts, 1)
        check_error(err)

        copts.flags = flags

        old_blob_cptr = ffi.NULL
        if old_blob is not None:
            cblob = ffi.new('git_blob **')
            ffi.buffer(cblob)[:] = old_blob._pointer[:]
            old_blob_cptr = cblob[0]

        cpatch = ffi.new('git_patch **')
        err = C.git_patch_from_blob_and_buffer(cpatch,
                old_blob_cptr, to_bytes(old_as_path),
                to_bytes(buffer), len(buffer), to_bytes(buffer_as_path),
                copts)
        check_error(err)

        return Patch._from_c(bytes(ffi.buffer(cpatch)[:]))

    @classmethod
    def from_blobs(cls, old_blob=None, old_as_path=None, new_blob=None, new_as_path=None, flags=0):
        """from_blobs([old_blob, old_as_path, new_blob, new_as_path, flags] -> Patch
  
        Directly generate a :py:class:`pygit2.Patch` from the difference between two blobs.

        :param Blob old_blob: the :py:class:`~pygit2.Blob` for old side of diff.
        :param str old_as_path: treat old blob as if it had this filename.
        :param Blob new_blob: the :py:class:`~pygit2.Blob` for new side of diff.
        :param str new_as_path: treat new blob as if it had this filename.
        :param flag: a GIT_DIFF_* constant.
        :rtype: Patch
        """
        copts = ffi.new('git_diff_options *')
        err = C.git_diff_init_options(copts, 1)
        check_error(err)

        copts.flags = flags

        old_blob_cptr = ffi.NULL
        if old_blob is not None:
            cblob = ffi.new('git_blob **')
            ffi.buffer(cblob)[:] = old_blob._pointer[:]
            old_blob_cptr = cblob[0]

        new_blob_cptr = ffi.NULL
        if new_blob is not None:
            cblob = ffi.new('git_blob **')
            ffi.buffer(cblob)[:] = new_blob._pointer[:]
            new_blob_cptr = cblob[0]

        cpatch = ffi.new('git_patch **')
        err = C.git_patch_from_blobs(cpatch,
                old_blob_cptr, to_bytes(old_as_path),
                new_blob_cptr, to_bytes(new_as_path),
                copts)
        check_error(err)

        return Patch._from_c(bytes(ffi.buffer(cpatch)[:]))

    @classmethod
    def from_diff(cls, diff, idx):
        """from_diff(diff, idx) -> Patch
  
        Return the patch for an entry in the diff list.
  
        :param :py:class:`pygit2.Diff` diff: the list object.
        :param idx: index into diff list.
        :rtype: :py:class:`pygit2.Patch`
        """
        if not idx >= 0:
            raise ValueError(idx)

        cpatch = ffi.new('git_patch **')
        err = C.git_patch_from_diff(cpatch, diff._diff, idx)
        check_error(err)

        return Patch._from_c(bytes(ffi.buffer(cpatch)[:]))

    def __del__(self):
        C.git_patch_free(self._patch)

    def __str__(self):
        cbuf = ffi.new('git_buf *', (ffi.NULL, 0))
        err = C.git_patch_to_buf(cbuf, self._patch)
        check_error(err)
        str = to_str(ffi.string(cbuf.ptr))
        C.git_buf_free(cbuf)
        return str

    @property
    def delta(self):
        """Get the delta associated with a patch."""
        centry = ffi.NULL

        centry = C.git_patch_get_delta(self._patch)

        return DiffDelta._from_c(centry)

    @property
    def hunks(self):
        return DiffHunkCollection(self)

    @property
    def line_stats(self):
        """Get line counts of each type in a patch."""
        ccontext = ffi.new('size_t *')
        cadditions = ffi.new('size_t *')
        cdeletions = ffi.new('size_t *')

        err = C.git_patch_line_stats(ccontext, cadditions, cdeletions, self._patch)
        check_error(err)

        context = ccontext[0]
        additions = cadditions[0]
        deletions = cdeletions[0]
        
        return context, additions, deletions

    def size(self, include_context=False, include_hunk_headers=False, include_file_headers=False):
        """size([include_context, include_hunk_headers, include_file_headers]) -> size

        Look up size of patch diff data in bytes.
  
        :param bool include_context: include context lines in size if non-zero.
        :param bool include_hunk_headers: include hunk header lines if non-zero.
        :param bool include_file_headers: include file header lines if non-zero.
        :rtype: long
        """
        return C.git_patch_size(self._patch, include_context,
                include_hunk_headers, include_file_headers)


class PatchCollection(object):

    def __init__(self, diff):
        self._diff = diff

    def __len__(self):
        return C.git_diff_num_deltas(self._diff._diff)

    def __iter__(self):
        return PatchIterator(self)

    def __getitem__(self, idx):
        cpatch = ffi.new('git_patch **')
        if not idx >= 0:
            raise ValueError(idx)
        else:
            err = C.git_patch_from_diff(cpatch, self._diff._diff, idx)
            check_error(err)

        if cpatch == ffi.NULL:
            raise KeyError(idx)

        return Patch._from_c(bytes(ffi.buffer(cpatch)[:]))


class PatchIterator(object):

    def __init__(self, collection):
        self.collection = collection
        self.index = 0

    def next(self):
        return self.__next__()

    def __next__(self):
        if self.index >= len(self.collection):
            raise StopIteration

        patch = self.collection[self.index]
        self.index += 1

        return patch
