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
from __future__ import absolute_import, unicode_literals

# Import from pygit2
from _pygit2 import Commit, Oid
from .errors import check_error
from .ffi import ffi, C
from .oid import oid_to_git_oid_expand
from .utils import is_string, strings_to_strarray, to_bytes, to_str


class Walker(object):

    def __del__(self):
        C.git_revwalk_free(self._walk)

    def __iter__(self):
        coid = ffi.new('git_oid *')
        while C.git_revwalk_next(coid, self._walk) != C.GIT_ITEROVER:
            ccommit = ffi.new('git_commit **')
            err = C.git_commit_lookup(ccommit, self._repo._repo, coid)
            check_error(err)
            yield Commit.from_c(bytes(ffi.buffer(ccommit)[:]), self._repo)

    @classmethod
    def from_c(cls, repo, ptr):
        walk = cls.__new__(cls)
        walk._repo = repo
        walk._walk = ptr[0]
        walk._cwalk = ptr

        return walk

    def hide(self, oid):
        """hide(oid)
  
        Mark a commit (and its ancestors) uninteresting for the output.
        """
        coid = oid_to_git_oid_expand(self._repo._repo, oid)
        err = C.git_revwalk_hide(self._walk, coid)
        check_error(err)

    def push(self, oid):
        """push(oid)

        Mark a commit to start traversal from.
        """
        coid = oid_to_git_oid_expand(self._repo._repo, oid)
        err = C.git_revwalk_push(self._walk, coid)
        check_error(err)

    def sort(self, mode):
        """sort(mode)

        Change the sorting mode (this resets the walker).
        """
        sort_mode = int(mode)
        C.git_revwalk_sorting(self._walk, sort_mode)

    def reset(self):
        """reset()

        Reset the walking machinery for reuse.
        """
        C.git_revwalk_reset(self._walk)

    def simplify_first_parent(self):
        """simplify_first_parent()

        Simplify the history by first-parent.
        """
        C.git_revwalk_simplify_first_parent(self._walk)
