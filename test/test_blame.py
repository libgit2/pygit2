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

"""Tests for Blame objects."""

import pytest

from pygit2 import Oid, Repository, Signature
from pygit2.enums import BlameFlag

PATH = 'hello.txt'

HUNKS = [
    (
        Oid(hex='acecd5ea2924a4b900e7e149496e1f4b57976e51'),
        1,
        Signature(
            'J. David Ibañez', 'jdavid@itaapy.com', 1297179898, 60, encoding='utf-8'
        ),
        True,
    ),
    (
        Oid(hex='6aaa262e655dd54252e5813c8e5acd7780ed097d'),
        2,
        Signature(
            'J. David Ibañez', 'jdavid@itaapy.com', 1297696877, 60, encoding='utf-8'
        ),
        False,
    ),
    (
        Oid(hex='4ec4389a8068641da2d6578db0419484972284c8'),
        3,
        Signature(
            'J. David Ibañez', 'jdavid@itaapy.com', 1297696908, 60, encoding='utf-8'
        ),
        False,
    ),
]


def test_blame_index(testrepo: Repository) -> None:
    blame = testrepo.blame(PATH)

    assert len(blame) == 3

    for i, hunk in enumerate(blame):
        assert hunk.lines_in_hunk == 1
        assert HUNKS[i][0] == hunk.final_commit_id
        assert HUNKS[i][1] == hunk.final_start_line_number
        assert HUNKS[i][2] == hunk.final_committer
        assert HUNKS[i][0] == hunk.orig_commit_id
        assert hunk.orig_path == PATH
        assert HUNKS[i][1] == hunk.orig_start_line_number
        assert HUNKS[i][2] == hunk.orig_committer
        assert HUNKS[i][3] == hunk.boundary


def test_blame_flags(blameflagsrepo: Repository) -> None:
    blame = blameflagsrepo.blame(PATH, flags=BlameFlag.IGNORE_WHITESPACE)

    assert len(blame) == 3

    for i, hunk in enumerate(blame):
        assert hunk.lines_in_hunk == 1
        assert HUNKS[i][0] == hunk.final_commit_id
        assert HUNKS[i][1] == hunk.final_start_line_number
        assert HUNKS[i][2] == hunk.final_committer
        assert HUNKS[i][0] == hunk.orig_commit_id
        assert hunk.orig_path == PATH
        assert HUNKS[i][1] == hunk.orig_start_line_number
        assert HUNKS[i][2] == hunk.orig_committer
        assert HUNKS[i][3] == hunk.boundary


def test_blame_with_invalid_index(testrepo: Repository) -> None:
    blame = testrepo.blame(PATH)

    with pytest.raises(IndexError):
        blame[100000]

    with pytest.raises(OverflowError):
        blame[-1]


def test_blame_for_line(testrepo: Repository) -> None:
    blame = testrepo.blame(PATH)

    for i, line in zip(range(0, 2), range(1, 3)):
        hunk = blame.for_line(line)

        assert hunk.lines_in_hunk == 1
        assert HUNKS[i][0] == hunk.final_commit_id
        assert HUNKS[i][1] == hunk.final_start_line_number
        assert HUNKS[i][2] == hunk.final_committer
        assert HUNKS[i][0] == hunk.orig_commit_id
        assert hunk.orig_path == PATH
        assert HUNKS[i][1] == hunk.orig_start_line_number
        assert HUNKS[i][2] == hunk.orig_committer
        assert HUNKS[i][3] == hunk.boundary


def test_blame_with_invalid_line(testrepo: Repository) -> None:
    blame = testrepo.blame(PATH)

    with pytest.raises(IndexError):
        blame.for_line(0)
    with pytest.raises(IndexError):
        blame.for_line(100000)
    with pytest.raises(IndexError):
        blame.for_line(-1)


def test_blame_newest(testrepo: Repository) -> None:
    revs = [
        ('master^2', 3),
        ('master^2^', 2),
        ('master^2^^', 1),
    ]

    for rev, num_commits in revs:
        commit = testrepo.revparse_single(rev)
        blame = testrepo.blame(PATH, newest_commit=commit.id)

        assert len(blame) == num_commits

        for i, hunk in enumerate(tuple(blame)[:num_commits]):
            assert hunk.lines_in_hunk == 1
            assert HUNKS[i][0] == hunk.final_commit_id
            assert HUNKS[i][1] == hunk.final_start_line_number
            assert HUNKS[i][2] == hunk.final_committer
            assert HUNKS[i][0] == hunk.orig_commit_id
            assert hunk.orig_path == PATH
            assert HUNKS[i][1] == hunk.orig_start_line_number
            assert HUNKS[i][2] == hunk.orig_committer
            assert HUNKS[i][3] == hunk.boundary
