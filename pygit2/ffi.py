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

import inspect
import codecs
from os import path, getenv
from cffi import FFI
import sys

(major_version, _, _, _, _) = sys.version_info

if major_version < 3:
    def to_str(s, encoding='utf-8', errors='strict'):
        if s == ffi.NULL or s is None:
            return ffi.NULL

        if isinstance(s, unicode):
            encoding = encoding or 'utf-8'
            return s.encode(encoding, errors)

        return s
else:
    def to_str(s, encoding='utf-8', errors='strict'):
        if s == ffi.NULL or s is None:
            return ffi.NULL

        if isinstance(s, bytes):
            return s

        return s.encode(encoding, errors)

if major_version < 3:
    def is_string(s):
        return isinstance(s, basestring)
else:
    def is_string(s):
        return isinstance(s, str)

ffi = FFI()

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

        s = ffi.new('char []', to_str(l[i]))
        refs[i] = s
        strings[i] = s

    arr.strings = strings
    arr.count = len(l)

    return arr, refs

dir_path = path.dirname(path.abspath(inspect.getfile(inspect.currentframe())))

decl_path = path.join(dir_path, 'decl.h')
with codecs.open(decl_path, 'r', 'utf-8') as header:
    ffi.cdef(header.read())

# if LIBGIT2 exists, set build and link against that version
libgit2_path = getenv('LIBGIT2')
include_dirs = []
library_dirs = []
if libgit2_path:
    include_dirs = [path.join(libgit2_path, 'include')]
    library_dirs = [path.join(libgit2_path, 'lib')]

C = ffi.verify("#include <git2.h>", libraries=["git2"],
               include_dirs=include_dirs, library_dirs=library_dirs)
