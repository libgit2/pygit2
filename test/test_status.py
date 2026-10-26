# Copyright 2010-2026 The pygit2 contributors
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

from pathlib import Path

import pytest

import pygit2
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


def test_status_file_non_ascii(tmp_path: Path) -> None:
    """status_file must round-trip non-ASCII path names."""
    repo = pygit2.init_repository(str(tmp_path / 'repo'))
    path = 'täst_é.txt'
    (Path(repo.workdir) / path).write_text('hello')
    repo.index.add(path)
    repo.index.write()
    assert repo.status_file(path) == FileStatus.INDEX_NEW


def test_status_file_non_breaking_space(tmp_path: Path) -> None:
    """status_file must handle U+00A0 in the path."""
    repo = pygit2.init_repository(str(tmp_path / 'repo'))
    path = 'file\u00a0name.txt'
    (Path(repo.workdir) / path).write_text('hello')
    repo.index.add(path)
    repo.index.write()
    assert repo.status_file(path) == FileStatus.INDEX_NEW


@pytest.mark.parametrize(
    'path',
    [
        'café.txt',  # NFC
        'cafe\u0301.txt',  # NFD
    ],
)
def test_status_file_unicode_normalization(tmp_path: Path, path: str) -> None:
    """status_file must work for both NFC and NFD forms of a path."""
    repo = pygit2.init_repository(str(tmp_path / 'repo'))
    (Path(repo.workdir) / path).write_text('hello')
    repo.index.add(path)
    repo.index.write()
    assert repo.status_file(path) == FileStatus.INDEX_NEW


def test_status_file_bytes_path(tmp_path: Path) -> None:
    """status_file must accept raw UTF-8 bytes for a path."""
    repo = pygit2.init_repository(str(tmp_path / 'repo'))
    path = 'täst_é.txt'
    (Path(repo.workdir) / path).write_text('hello')
    repo.index.add(path)
    repo.index.write()
    assert repo.status_file(path.encode('utf-8')) == FileStatus.INDEX_NEW
