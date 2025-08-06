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

"""Tests for Submodule objects."""

from collections.abc import Generator
from pathlib import Path

import pytest

import pygit2
from pygit2 import Repository, Submodule
from pygit2.enums import SubmoduleIgnore as SI
from pygit2.enums import SubmoduleStatus as SS

from . import utils

SUBM_NAME = 'TestGitRepository'
SUBM_PATH = 'TestGitRepository'
SUBM_URL = 'https://github.com/libgit2/TestGitRepository'
SUBM_HEAD_SHA = '49322bb17d3acc9146f98c97d078513228bbf3c0'
SUBM_BOTTOM_SHA = '6c8b137b1c652731597c89668f417b8695f28dd7'


@pytest.fixture
def repo(tmp_path: Path) -> Generator[Repository, None, None]:
    with utils.TemporaryRepository('submodulerepo.zip', tmp_path) as path:
        yield pygit2.Repository(path)


def test_lookup_submodule(repo: Repository) -> None:
    s: Submodule | None = repo.submodules[SUBM_PATH]
    assert s is not None
    s = repo.submodules.get(SUBM_PATH)
    assert s is not None


def test_lookup_submodule_aspath(repo: Repository) -> None:
    s = repo.submodules[Path(SUBM_PATH)]
    assert s is not None


def test_lookup_missing_submodule(repo: Repository) -> None:
    with pytest.raises(KeyError):
        repo.submodules['does-not-exist']
    assert repo.submodules.get('does-not-exist') is None


def test_listall_submodules(repo: Repository) -> None:
    submodules = repo.listall_submodules()
    assert len(submodules) == 1
    assert submodules[0] == SUBM_PATH


def test_contains_submodule(repo: Repository) -> None:
    assert SUBM_PATH in repo.submodules
    assert 'does-not-exist' not in repo.submodules


def test_submodule_iterator(repo: Repository) -> None:
    for s in repo.submodules:
        assert isinstance(s, pygit2.Submodule)
        assert s.path == repo.submodules[s.path].path


@utils.requires_network
def test_submodule_open(repo: Repository) -> None:
    s = repo.submodules[SUBM_PATH]
    repo.submodules.init()
    repo.submodules.update()
    r = s.open()
    assert r is not None
    assert r.head.target == SUBM_HEAD_SHA


@utils.requires_network
def test_submodule_open_from_repository_subclass(repo: Repository) -> None:
    class CustomRepoClass(pygit2.Repository):
        pass

    custom_repo = CustomRepoClass(repo.workdir)
    s = custom_repo.submodules[SUBM_PATH]
    custom_repo.submodules.init()
    custom_repo.submodules.update()
    r = s.open()
    assert isinstance(r, CustomRepoClass)
    assert r.head.target == SUBM_HEAD_SHA


def test_name(repo: Repository) -> None:
    s = repo.submodules[SUBM_PATH]
    assert SUBM_NAME == s.name


def test_path(repo: Repository) -> None:
    s = repo.submodules[SUBM_PATH]
    assert SUBM_PATH == s.path


def test_url(repo: Repository) -> None:
    s = repo.submodules[SUBM_PATH]
    assert SUBM_URL == s.url


def test_set_url(repo: Repository) -> None:
    new_url = 'ssh://git@127.0.0.1:2222/my_repo'
    s = repo.submodules[SUBM_PATH]
    s.url = new_url
    assert new_url == repo.submodules[SUBM_PATH].url
    # Ensure .gitmodules has been correctly altered
    with open(Path(repo.workdir, '.gitmodules'), 'r') as fd:
        modules = fd.read()
    assert new_url in modules


def test_missing_url(repo: Repository) -> None:
    # Remove "url" from .gitmodules
    with open(Path(repo.workdir, '.gitmodules'), 'wt') as f:
        f.write('[submodule "TestGitRepository"]\n')
        f.write('\tpath = TestGitRepository\n')
    s = repo.submodules[SUBM_PATH]
    assert not s.url


@utils.requires_network
def test_init_and_update(repo: Repository) -> None:
    subrepo_file_path = Path(repo.workdir) / SUBM_PATH / 'master.txt'
    assert not subrepo_file_path.exists()

    status = repo.submodules.status(SUBM_NAME)
    assert status == (SS.IN_HEAD | SS.IN_INDEX | SS.IN_CONFIG | SS.WD_UNINITIALIZED)

    repo.submodules.init()
    repo.submodules.update()

    assert subrepo_file_path.exists()

    status = repo.submodules.status(SUBM_NAME)
    assert status == (SS.IN_HEAD | SS.IN_INDEX | SS.IN_CONFIG | SS.IN_WD)


@utils.requires_network
def test_specified_update(repo: Repository) -> None:
    subrepo_file_path = Path(repo.workdir) / SUBM_PATH / 'master.txt'
    assert not subrepo_file_path.exists()
    repo.submodules.init(submodules=['TestGitRepository'])
    repo.submodules.update(submodules=['TestGitRepository'])
    assert subrepo_file_path.exists()


@utils.requires_network
def test_update_instance(repo: Repository) -> None:
    subrepo_file_path = Path(repo.workdir) / SUBM_PATH / 'master.txt'
    assert not subrepo_file_path.exists()
    sm = repo.submodules['TestGitRepository']
    sm.init()
    sm.update()
    assert subrepo_file_path.exists()


@utils.requires_network
@pytest.mark.parametrize('depth', [0, 1])
def test_oneshot_update(repo: Repository, depth: int) -> None:
    status = repo.submodules.status(SUBM_NAME)
    assert status == (SS.IN_HEAD | SS.IN_INDEX | SS.IN_CONFIG | SS.WD_UNINITIALIZED)

    subrepo_file_path = Path(repo.workdir) / SUBM_PATH / 'master.txt'
    assert not subrepo_file_path.exists()
    repo.submodules.update(init=True, depth=depth)
    assert subrepo_file_path.exists()

    status = repo.submodules.status(SUBM_NAME)
    assert status == (SS.IN_HEAD | SS.IN_INDEX | SS.IN_CONFIG | SS.IN_WD)

    sm_repo = repo.submodules[SUBM_NAME].open()
    if depth == 0:
        sm_repo[SUBM_BOTTOM_SHA]  # full history must be available
    else:
        with pytest.raises(KeyError):
            sm_repo[SUBM_BOTTOM_SHA]  # shallow clone


@utils.requires_network
@pytest.mark.parametrize('depth', [0, 1])
def test_oneshot_update_instance(repo: Repository, depth: int) -> None:
    subrepo_file_path = Path(repo.workdir) / SUBM_PATH / 'master.txt'
    assert not subrepo_file_path.exists()
    sm = repo.submodules[SUBM_NAME]
    sm.update(init=True, depth=depth)
    assert subrepo_file_path.exists()

    sm_repo = sm.open()
    if depth == 0:
        sm_repo[SUBM_BOTTOM_SHA]  # full history must be available
    else:
        with pytest.raises(KeyError):
            sm_repo[SUBM_BOTTOM_SHA]  # shallow clone


@utils.requires_network
def test_head_id(repo: Repository) -> None:
    assert repo.submodules[SUBM_PATH].head_id == SUBM_HEAD_SHA


@utils.requires_network
def test_head_id_null(repo: Repository) -> None:
    gitmodules_newlines = (
        '\n'
        '[submodule "uncommitted_submodule"]\n'
        '    path = pygit2\n'
        '    url = https://github.com/libgit2/pygit2\n'
        '\n'
    )
    with open(Path(repo.workdir, '.gitmodules'), 'a') as f:
        f.write(gitmodules_newlines)

    subm = repo.submodules['uncommitted_submodule']

    # The submodule isn't in the HEAD yet, so head_id should be None
    assert subm.head_id is None


@utils.requires_network
@pytest.mark.parametrize('depth', [0, 1])
def test_add_submodule(repo: Repository, depth: int) -> None:
    sm_repo_path = 'test/testrepo'
    sm = repo.submodules.add(SUBM_URL, sm_repo_path, depth=depth)

    status = repo.submodules.status(sm_repo_path)
    assert status == (SS.IN_INDEX | SS.IN_CONFIG | SS.IN_WD | SS.INDEX_ADDED)

    sm_repo = sm.open()
    assert sm_repo_path == sm.path
    assert SUBM_URL == sm.url
    assert not sm_repo.is_empty

    if depth == 0:
        sm_repo[SUBM_BOTTOM_SHA]  # full history must be available
    else:
        with pytest.raises(KeyError):
            sm_repo[SUBM_BOTTOM_SHA]  # shallow clone


@utils.requires_network
def test_submodule_status(repo: Repository) -> None:
    common_status = SS.IN_HEAD | SS.IN_INDEX | SS.IN_CONFIG

    # Submodule needs initializing
    assert repo.submodules.status(SUBM_PATH) == common_status | SS.WD_UNINITIALIZED

    # If ignoring ALL, don't look at WD
    assert repo.submodules.status(SUBM_PATH, ignore=SI.ALL) == common_status

    # Update the submodule
    repo.submodules.update(init=True)

    # It's in our WD now
    assert repo.submodules.status(SUBM_PATH) == common_status | SS.IN_WD

    # Open submodule repo
    sm_repo: pygit2.Repository = repo.submodules[SUBM_PATH].open()

    # Move HEAD in the submodule (WD_MODIFIED)
    sm_repo.checkout('refs/tags/annotated_tag')
    assert (
        repo.submodules.status(SUBM_PATH) == common_status | SS.IN_WD | SS.WD_MODIFIED
    )

    # Move HEAD back to master
    sm_repo.checkout('refs/heads/master')

    # Touch some file in the submodule's workdir (WD_WD_MODIFIED)
    with open(Path(repo.workdir, SUBM_PATH, 'master.txt'), 'wt') as f:
        f.write('modifying master.txt')
    assert (
        repo.submodules.status(SUBM_PATH)
        == common_status | SS.IN_WD | SS.WD_WD_MODIFIED
    )

    # Add an untracked file in the submodule's workdir (WD_UNTRACKED)
    with open(Path(repo.workdir, SUBM_PATH, 'some_untracked_file.txt'), 'wt') as f:
        f.write('hi')
    assert (
        repo.submodules.status(SUBM_PATH)
        == common_status | SS.IN_WD | SS.WD_WD_MODIFIED | SS.WD_UNTRACKED
    )

    # Add modified files to the submodule's index (WD_INDEX_MODIFIED)
    sm_repo.index.add_all()
    sm_repo.index.write()
    assert (
        repo.submodules.status(SUBM_PATH)
        == common_status | SS.IN_WD | SS.WD_INDEX_MODIFIED
    )


def test_submodule_cache(repo: Repository) -> None:
    # When the cache is turned on, looking up the same submodule twice must return the same git_submodule object
    repo.submodules.cache_all()
    sm1 = repo.submodules[SUBM_NAME]
    sm2 = repo.submodules[SUBM_NAME]
    assert sm1._subm == sm2._subm

    # After turning off the cache, each lookup must return a new git_submodule object
    repo.submodules.cache_clear()
    sm3 = repo.submodules[SUBM_NAME]
    sm4 = repo.submodules[SUBM_NAME]
    assert sm1._subm != sm3._subm
    assert sm3._subm != sm4._subm


def test_submodule_reload(repo: Repository) -> None:
    sm = repo.submodules[SUBM_NAME]
    assert sm.url == 'https://github.com/libgit2/TestGitRepository'

    # Doctor the config file outside of libgit2
    with open(Path(repo.workdir, '.gitmodules'), 'wt') as f:
        f.write('[submodule "TestGitRepository"]\n')
        f.write('\tpath = TestGitRepository\n')
        f.write('\turl = https://github.com/libgit2/pygit2\n')

    # Submodule object is oblivious to the change
    assert sm.url == 'https://github.com/libgit2/TestGitRepository'

    # Tell it to refresh its cache
    sm.reload()
    assert sm.url == 'https://github.com/libgit2/pygit2'
