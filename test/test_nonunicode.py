# Copyright 2010-2024 The pygit2 contributors
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

"""Tests for non unicode byte strings"""

import pygit2
import os
import shutil


bstring = b'\xc3master'


def test_nonunicode_branchname(testrepo):
    folderpath = 'temp_repo_nonutf'
    if os.path.exists(folderpath):
        shutil.rmtree(folderpath)
    newrepo = pygit2.clone_repository(
        path=folderpath, url='https://github.com/pygit2/test_branch_notutf.git'
    )
    assert bstring in [
        (ref.split('/')[-1]).encode('utf8', 'surrogateescape')
        for ref in newrepo.listall_references()
    ]  # Remote branch among references: 'refs/remotes/origin/\udcc3master'
