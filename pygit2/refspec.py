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

from .ffi import ffi, C, to_str
from .errors import check_error

class Refspec(object):
    def __init__(self, owner, ptr):
        self._owner = owner
        self._refspec = ptr

    @property
    def src(self):
        """Source or lhs of the refspec"""
        return ffi.string(C.git_refspec_src(self._refspec)).decode()

    @property
    def dst(self):
        """Destinaton or rhs of the refspec"""
        return ffi.string(C.git_refspec_dst(self._refspec)).decode()

    @property
    def force(self):
        """Whether this refspeca llows non-fast-forward updates"""
        return bool(C.git_refspec_force(self._refspec))

    @property
    def string(self):
        """String which was used to create this refspec"""
        return ffi.string(C.git_refspec_string(self._refspec)).decode()

    @property
    def direction(self):
        """Direction of this refspec (fetch or push)"""
        return C.git_refspec_direction(self._refspec)

    def src_matches(self, ref):
        """src_matches(str) -> Bool

        Returns whether the given string matches the source of this refspec"""
        return bool(C.git_refspec_src_matches(self._refspec, to_str(ref)))

    def dst_matches(self, ref):
        """dst_matches(str) -> Bool

        Returns whether the given string matches the destination of this refspec"""
        return bool(C.git_refspec_dst_matches(self._refspec, to_str(ref)))

    def transform(self, ref):
        """transform(str) -> str

        Transform a reference name according to this refspec from the lhs to the rhs."""
        alen = len(ref)
        err = C.GIT_EBUFS
        ptr = None
        ref_str = to_str(ref)

        while err == C.GIT_EBUFS:
            alen *= 2
            ptr = ffi.new('char []', alen)

            err = C.git_refspec_transform(ptr, alen, self._refspec, ref_str)

        check_error(err)
        return ffi.string(ptr).decode()

    def rtransform(self, ref):
        """transform(str) -> str

        Transform a reference name according to this refspec from the lhs to the rhs"""
        alen = len(ref)
        err = C.GIT_EBUFS
        ptr = None
        ref_str = to_str(ref)

        while err == C.GIT_EBUFS:
            alen *= 2
            ptr = ffi.new('char []', alen)

            err = C.git_refspec_rtransform(ptr, alen, self._refspec, ref_str)

        check_error(err)
        return ffi.string(ptr).decode()
