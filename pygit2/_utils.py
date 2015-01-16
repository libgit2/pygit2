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

"""
This is an special module, it provides stuff used by setup.py and by
pygit2 at run-time.
"""

# Import from the Standard Library
from binascii import crc32
import inspect
import codecs
import os
from os import getenv
from os.path import abspath, dirname
import sys


#
# The version number of pygit2
#
__version__ = '0.22.0'


#
# Utility functions to get the paths required for bulding extensions
#
def _get_libgit2_path():
    # LIBGIT2 environment variable takes precedence
    libgit2_path = getenv("LIBGIT2")
    if libgit2_path is not None:
        return libgit2_path

    # Default
    if os.name == 'nt':
        return '%s\libgit2' % getenv("ProgramFiles")
    return '/usr/local'


def get_libgit2_paths():
    libgit2_path = _get_libgit2_path()
    return (
        os.path.join(libgit2_path, 'bin'),
        os.path.join(libgit2_path, 'include'),
        getenv('LIBGIT2_LIB', os.path.join(libgit2_path, 'lib')),
    )


#
# Loads the cffi extension
#
def get_ffi():
    import cffi

    ffi = cffi.FFI()

    # Load C definitions
    dir_path = dirname(abspath(inspect.getfile(inspect.currentframe())))
    decl_path = os.path.join(dir_path, 'decl.h')
    with codecs.open(decl_path, 'r', 'utf-8') as header:
        ffi.cdef(header.read())

    # The modulename
    # Simplified version of what cffi does: remove kwargs and vengine
    preamble = "#include <git2.h>"
    key = [sys.version[:3], cffi.__version__, preamble] + ffi._cdefsources
    key = '\x00'.join(key)
    if sys.version_info >= (3,):
        key = key.encode('utf-8')
    k1 = hex(crc32(key[0::2]) & 0xffffffff).lstrip('0x').rstrip('L')
    k2 = hex(crc32(key[1::2]) & 0xffffffff).lstrip('0').rstrip('L')
    modulename = 'pygit2_cffi_%s%s' % (k1, k2)

    # Load extension module
    libgit2_bin, libgit2_include, libgit2_lib = get_libgit2_paths()
    C = ffi.verify(preamble, modulename=modulename, libraries=["git2"],
                   include_dirs=[libgit2_include], library_dirs=[libgit2_lib])

    # Ok
    return ffi, C
