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

import shutil
import sys
from pathlib import Path

import pytest

import pygit2
from pygit2 import Repository
from pygit2.enums import FileStatus
from pygit2.utils import to_bytes

from . import utils

# FIXME Detect the filesystem rather than the operating system
works_in_linux = pytest.mark.xfail(
    sys.platform != 'linux',
    reason='fails in macOS/Windows, and also in Linux with the FAT filesystem',
)


@utils.requires_network
@works_in_linux
def test_nonunicode_branchname(testrepo: Repository, tmp_path: Path) -> None:
    folderpath = tmp_path / 'temp_repo_nonutf'
    if folderpath.exists():
        shutil.rmtree(folderpath)
    newrepo = pygit2.clone_repository(
        path=str(folderpath), url='https://github.com/pygit2/test_branch_notutf.git'
    )
    bstring = b'\xc3master'
    assert bstring in [
        (ref.split('/')[-1]).encode('utf8', 'surrogateescape')
        for ref in newrepo.listall_references()
    ]  # Remote branch among references: 'refs/remotes/origin/\udcc3master'


@works_in_linux
def test_nonunicode_status_path(tmp_path: Path) -> None:
    repo = pygit2.init_repository(str(tmp_path / 'repo'), bare=False)
    path_bytes = 'éléphant'.encode('latin1')
    filepath = Path(repo.workdir) / path_bytes.decode('utf-8', 'surrogateescape')
    filepath.write_bytes(b'dummy')
    git_status = repo.status()
    path_key = os.fsdecode(path_bytes)
    assert path_bytes in [to_bytes(path) for path in git_status]
    assert git_status[path_key] & FileStatus.WT_NEW
    assert to_bytes(path_key) == path_bytes
