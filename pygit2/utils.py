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
from sys import version_info

# Import from pygit2
from .ffi import ffi


if version_info[0] < 3:
    from .py2 import is_string, to_bytes, to_str
else:
    from .py3 import is_string, to_bytes, to_str



def strarray_to_strings(arr):
    l = [None] * arr.count
    for i in range(arr.count):
        l[i] = ffi.string(arr.strings[i]).decode()

    return l


def strings_to_strarray(l):
    """Convert a list of strings to a git_strarray

    We return first the git_strarray* you can pass to libgit2 and a
    list of references to the memory, which we must keep around for as
    long as the git_strarray must live.
    """

    if not isinstance(l, list):
        raise TypeError("Value must be a list")

    arr = ffi.new('git_strarray *')
    strings = ffi.new('char *[]', len(l))

    # We need refs in order to keep a reference to the value returned
    # by the ffi.new(). Otherwise, they will be freed and the memory
    # re-used, with less than great consequences.
    refs = [None] * len(l)

    for i in range(len(l)):
        if not is_string(l[i]):
            raise TypeError("Value must be a string")

        s = ffi.new('char []', to_bytes(l[i]))
        refs[i] = s
        strings[i] = s

    arr.strings = strings
    arr.count = len(l)

    return arr, refs
