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

from collections.abc import Generator
from pathlib import Path

import pytest

import pygit2
from pygit2 import Commit, Repository

from . import utils


@pytest.fixture
def repo(tmp_path: Path) -> Generator[Repository, None, None]:
    with utils.TemporaryRepository('trailerrepo.zip', tmp_path) as path:
        yield pygit2.Repository(path)


def test_get_trailers_array(repo: Repository) -> None:
    commit_hash = '010231b2fdaee6b21da4f06058cf6c6a3392dd12'
    expected_trailers = {
        'Bug': '1234',
        'Signed-off-by': 'Tyler Cipriani <tyler@tylercipriani.com>',
    }
    commit = repo.get(commit_hash)
    assert isinstance(commit, Commit)
    trailers = commit.message_trailers

    assert trailers['Bug'] == expected_trailers['Bug']
    assert trailers['Signed-off-by'] == expected_trailers['Signed-off-by']
