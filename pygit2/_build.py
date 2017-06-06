# -*- coding: utf-8 -*-
#
# Copyright 2010-2017 The pygit2 contributors
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
This is an special module, it provides stuff used by setup.py at build time.
But also used by pygit2 at run time.
"""

# Import from the Standard Library
import os

#
# The version number of pygit2
#
__version__ = '0.25.1'

#
# The checksum of libgit2
#
__sha__ = 'fe934dce35d83c298b9037aacef1cd430a6ed7a3be38b873203144a07bc360ff'

#
# Utility functions to get the paths required for bulding extensions
#
def _get_libgit2_path():
    # LIBGIT2 environment variable takes precedence
    libgit2_path = os.getenv("LIBGIT2")
    if libgit2_path is not None:
        return libgit2_path

    # Default
    return os.path.abspath(os.path.join('build', 'libgit2'))


def get_libgit2_paths():
    libgit2_path = _get_libgit2_path()
    return (
        os.path.join(libgit2_path, 'bin'),
        os.path.join(libgit2_path, 'include'),
        os.getenv('LIBGIT2_LIB', os.path.join(libgit2_path, 'lib')),
    )
