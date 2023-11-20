# Copyright 2010-2023 The pygit2 contributors
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
from pygit2 import SubmoduleIgnore as SI, SubmoduleStatus as SS


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
    subrepo_file_path = Path(repo.workdir) / SUBM_PATH / 'master.txt'
    assert not subrepo_file_path.exists()

    status = repo.submodule_status(SUBM_NAME)
    assert status == (SS.IN_HEAD | SS.IN_INDEX | SS.IN_CONFIG | SS.WD_UNINITIALIZED)

    repo.init_submodules()
    repo.update_submodules()

    assert subrepo_file_path.exists()

    status = repo.submodule_status(SUBM_NAME)
    assert status == (SS.IN_HEAD | SS.IN_INDEX | SS.IN_CONFIG | SS.IN_WD)

@utils.requires_network
def test_specified_update(repo):
    subrepo_file_path = Path(repo.workdir) / SUBM_PATH / 'master.txt'
    assert not subrepo_file_path.exists()
    repo.init_submodules(submodules=['TestGitRepository'])
    repo.update_submodules(submodules=['TestGitRepository'])
    assert subrepo_file_path.exists()

@utils.requires_network
def test_update_instance(repo):
    subrepo_file_path = Path(repo.workdir) / SUBM_PATH / 'master.txt'
    assert not subrepo_file_path.exists()
    sm = repo.lookup_submodule('TestGitRepository')
    sm.init()
    sm.update()
    assert subrepo_file_path.exists()

@utils.requires_network
def test_oneshot_update(repo):
    status = repo.submodule_status(SUBM_NAME)
    assert status == (SS.IN_HEAD | SS.IN_INDEX | SS.IN_CONFIG | SS.WD_UNINITIALIZED)

    subrepo_file_path = Path(repo.workdir) / SUBM_PATH / 'master.txt'
    assert not subrepo_file_path.exists()
    repo.update_submodules(init=True)
    assert subrepo_file_path.exists()

    status = repo.submodule_status(SUBM_NAME)
    assert status == (SS.IN_HEAD | SS.IN_INDEX | SS.IN_CONFIG | SS.IN_WD)

@utils.requires_network
def test_oneshot_update_instance(repo):
    subrepo_file_path = Path(repo.workdir) / SUBM_PATH / 'master.txt'
    assert not subrepo_file_path.exists()
    sm = repo.lookup_submodule(SUBM_NAME)
    sm.update(init=True)
    assert subrepo_file_path.exists()

@utils.requires_network
def test_head_id(repo):
    s = repo.lookup_submodule(SUBM_PATH)
    assert str(s.head_id) == SUBM_HEAD_SHA

@utils.requires_network
def test_add_submodule(repo):
    sm_repo_path = "test/testrepo"
    sm = repo.add_submodule(SUBM_URL, sm_repo_path)

    status = repo.submodule_status(sm_repo_path)
    assert status == (SS.IN_INDEX | SS.IN_CONFIG | SS.IN_WD | SS.INDEX_ADDED)

    sm_repo = sm.open()
    assert sm_repo_path == sm.path
    assert SUBM_URL == sm.url
    assert not sm_repo.is_empty

@utils.requires_network
def test_submodule_status(repo):
    common_status = SS.IN_HEAD | SS.IN_INDEX | SS.IN_CONFIG

    # Submodule needs initializing
    assert repo.submodule_status(SUBM_PATH) == common_status | SS.WD_UNINITIALIZED

    # If ignoring ALL, don't look at WD
    assert repo.submodule_status(SUBM_PATH, ignore=SI.ALL) == common_status

    # Update the submodule
    repo.update_submodules(init=True)

    # It's in our WD now
    assert repo.submodule_status(SUBM_PATH) == common_status | SS.IN_WD

    # Open submodule repo
    sm_repo: pygit2.Repository = repo.lookup_submodule(SUBM_PATH).open()

    # Move HEAD in the submodule (WD_MODIFIED)
    sm_repo.checkout('refs/tags/annotated_tag')
    assert repo.submodule_status(SUBM_PATH) == common_status | SS.IN_WD | SS.WD_MODIFIED

    # Move HEAD back to master
    sm_repo.checkout('refs/heads/master')

    # Touch some file in the submodule's workdir (WD_WD_MODIFIED)
    with open(Path(repo.workdir, SUBM_PATH, 'master.txt'), 'wt') as f:
        f.write("modifying master.txt")
    assert repo.submodule_status(SUBM_PATH) == common_status | SS.IN_WD | SS.WD_WD_MODIFIED

    # Add an untracked file in the submodule's workdir (WD_UNTRACKED)
    with open(Path(repo.workdir, SUBM_PATH, 'some_untracked_file.txt'), 'wt') as f:
        f.write("hi")
    assert repo.submodule_status(SUBM_PATH) == common_status | SS.IN_WD | SS.WD_WD_MODIFIED | SS.WD_UNTRACKED

    # Add modified files to the submodule's index (WD_INDEX_MODIFIED)
    sm_repo.index.add_all()
    sm_repo.index.write()
    assert repo.submodule_status(SUBM_PATH) == common_status | SS.IN_WD | SS.WD_INDEX_MODIFIED

def test_submodule_cache(repo):
    # When the cache is turned on, looking up the same submodule twice must return the same git_submodule object
    repo.submodule_cache_all()
    sm1 = repo.lookup_submodule(SUBM_NAME)
    sm2 = repo.lookup_submodule(SUBM_NAME)
    assert sm1._subm == sm2._subm

    # After turning off the cache, each lookup must return a new git_submodule object
    repo.submodule_cache_clear()
    sm3 = repo.lookup_submodule(SUBM_NAME)
    sm4 = repo.lookup_submodule(SUBM_NAME)
    assert sm1._subm != sm3._subm
    assert sm3._subm != sm4._subm

def test_submodule_reload(repo):
    sm = repo.lookup_submodule(SUBM_NAME)
    assert sm.url == "https://github.com/libgit2/TestGitRepository"

    # Doctor the config file outside of libgit2
    with open(Path(repo.workdir, ".gitmodules"), "wt") as f:
        f.write('[submodule "TestGitRepository"]\n')
        f.write('\tpath = TestGitRepository\n')
        f.write('\turl = https://github.com/libgit2/pygit2\n')

    # Submodule object is oblivious to the change
    assert sm.url == "https://github.com/libgit2/TestGitRepository"

    # Tell it to refresh its cache
    sm.reload()
    assert sm.url == "https://github.com/libgit2/pygit2"
