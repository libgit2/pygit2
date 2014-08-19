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
from _pygit2 import Oid
from .errors import check_error
from .ffi import ffi, C
from .utils import to_bytes


def oid_to_git_oid(repo, oid):
    coid = ffi.new('git_oid *')
    if isinstance(oid, Oid):
        ffi.buffer(coid)[:] = oid.raw[:]
        return coid, GIT_OID_HEXSZ

    bytes = to_bytes(oid)
    cstr = ffi.new('char []', bytes)
    err = C.git_oid_fromstrn(coid, cstr, len(bytes))
    if err < 0:
        check_error(err)

    return coid, len(bytes)


def oid_to_git_oid_expand(repo, oid):
    coid, len = oid_to_git_oid(repo, oid)

    codb = ffi.new('git_odb **')
    err = C.git_repository_odb(codb, repo)
    if err < 0:
        C.git_odb_free(codb)
        check_error(err)

    cout = ffi.new('git_oid *')
    err = C.git_odb_exists_prefix(cout, codb[0], coid, len)
    if err < 0:
        C.git_odb_free(codb)
        check_error(err)

    C.git_odb_free(codb[0])
    
    return cout
