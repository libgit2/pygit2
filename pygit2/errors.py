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

# Import from the Standard Library
from string import hexdigits

# ffi
from .ffi import ffi, C

from _pygit2 import GitError

def check_error(err):
    if err >= 0:
        return

    message = "(no message provided)"
    giterr = C.giterr_last()
    if giterr != ffi.NULL:
        message = ffi.string(giterr.message).decode()

    if err in [C.GIT_EEXISTS, C.GIT_EINVALIDSPEC, C.GIT_EEXISTS, C.GIT_EAMBIGUOUS]:
        raise ValueError(message)
    elif err == C.GIT_ENOTFOUND:
        raise KeyError(message)
    elif err == C.GIT_EINVALIDSPEC:
        raise ValueError(message)
    elif err == C.GIT_ITEROVER:
        raise StopIteration()

    raise GitError(message)

