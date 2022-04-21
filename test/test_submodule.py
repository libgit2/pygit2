# Copyright 2010-2021 The pygit2 contributors
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

"""Tests for Submodule objects."""

from pathlib import Path

import pygit2
import pytest

from . import utils


SUBM_NAME = 'TestGitRepository'
SUBM_PATH = 'TestGitRepository'
SUBM_URL = 'https://github.com/libgit2/TestGitRepository'
SUBM_HEAD_SHA = '49322bb17d3acc9146f98c97d078513228bbf3c0'


@pytest.fixture
def repo(tmp_path):
    with utils.TemporaryRepository('submodulerepo.zip', tmp_path) as path:
        yield pygit2.Repository(path)


def test_lookup_submodule(repo):
    s = repo.lookup_submodule(SUBM_PATH)
    assert s is not None

def test_lookup_submodule_aspath(repo):
    s = repo.lookup_submodule(Path(SUBM_PATH))
    assert s is not None

def test_listall_submodules(repo):
    submodules = repo.listall_submodules()
    assert len(submodules) == 1
    assert submodules[0] == SUBM_PATH

@utils.requires_network
def test_submodule_open(repo):
    s = repo.lookup_submodule(SUBM_PATH)
    repo.init_submodules()
    repo.update_submodules()
    r = s.open()
    assert r is not None
    assert str(r.head.target) == SUBM_HEAD_SHA

def test_name(repo):
    s = repo.lookup_submodule(SUBM_PATH)
    assert SUBM_NAME == s.name

def test_path(repo):
    s = repo.lookup_submodule(SUBM_PATH)
    assert SUBM_PATH == s.path

def test_url(repo):
    s = repo.lookup_submodule(SUBM_PATH)
    assert SUBM_URL == s.url

@utils.requires_network
def test_init_and_update(repo):
    subrepo_file_path = Path(repo.workdir) / 'TestGitRepository' / 'master.txt'
    assert not subrepo_file_path.exists()
    repo.init_submodules()
    repo.update_submodules()
    assert subrepo_file_path.exists()

@utils.requires_network
def test_specified_update(repo):
    subrepo_file_path = Path(repo.workdir) / 'TestGitRepository' / 'master.txt'
    assert not subrepo_file_path.exists()
    repo.init_submodules(submodules=['TestGitRepository'])
    repo.update_submodules(submodules=['TestGitRepository'])
    assert subrepo_file_path.exists()

@utils.requires_network
def test_oneshot_update(repo):
    subrepo_file_path = Path(repo.workdir) / 'TestGitRepository' / 'master.txt'
    assert not subrepo_file_path.exists()
    repo.update_submodules(init=True)
    assert subrepo_file_path.exists()

@utils.requires_network
def test_head_id(repo):
    s = repo.lookup_submodule(SUBM_PATH)
    assert str(s.head_id) == SUBM_HEAD_SHA

@utils.requires_network
def test_add_submodule(repo):
    sm_repo_path = "test/testrepo"
    sm = repo.add_submodule(SUBM_URL, sm_repo_path)
    sm_repo = sm.open()
    assert sm_repo_path == sm.path
    assert SUBM_URL == sm.url
    assert not sm_repo.is_empty
