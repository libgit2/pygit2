# Copyright 2010-2025 The pygit2 contributors
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

import pytest

from pygit2 import Repository
from pygit2.enums import FileStatus


def test_status(dirtyrepo: Repository) -> None:
    """
    For every file in the status, check that the flags are correct.
    """
    git_status = dirtyrepo.status()
    for filepath, status in git_status.items():
        assert filepath in git_status
        assert status == git_status[filepath]


def test_status_untracked_no(dirtyrepo: Repository) -> None:
    git_status = dirtyrepo.status(untracked_files='no')
    assert not any(status & FileStatus.WT_NEW for status in git_status.values())


@pytest.mark.parametrize(
    'untracked_files,expected',
    [
        ('no', set()),
        (
            'normal',
            {
                'untracked_dir/',
                'staged_delete_file_modified',
                'subdir/new_file',
                'new_file',
            },
        ),
        (
            'all',
            {
                'new_file',
                'subdir/new_file',
                'staged_delete_file_modified',
                'untracked_dir/untracked_file',
            },
        ),
    ],
)
def test_status_untracked_normal(
    dirtyrepo: Repository, untracked_files: str, expected: set[str]
) -> None:
    git_status = dirtyrepo.status(untracked_files=untracked_files)
    assert {
        file for file, status in git_status.items() if status & FileStatus.WT_NEW
    } == expected


@pytest.mark.parametrize('ignored,expected', [(True, {'ignored'}), (False, set())])
def test_status_ignored(
    dirtyrepo: Repository, ignored: bool, expected: set[str]
) -> None:
    git_status = dirtyrepo.status(ignored=ignored)
    assert {
        file for file, status in git_status.items() if status & FileStatus.IGNORED
    } == expected
