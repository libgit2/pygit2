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

import pygit2
import pytest


ORIGIN_MASTER_COMMIT = '784855caf26449a1914d2cf62d12b9374d76ae78'


@pytest.fixture
def repo(emptyrepo):
    remote = emptyrepo.remotes[0]
    remote.fetch()
    yield emptyrepo


def test_branches_remote_get(repo):
    branch = repo.branches.remote.get('origin/master')
    assert branch.target.hex == ORIGIN_MASTER_COMMIT

    assert repo.branches.remote.get('origin/not-exists') is None

def test_branches_remote(repo):
    branches = sorted(repo.branches.remote)
    assert branches == ['origin/master']

def test_branches_remote_getitem(repo):
    branch = repo.branches.remote['origin/master']
    assert branch.remote_name == 'origin'

def test_branches_upstream(repo):
    remote_master = repo.branches.remote['origin/master']
    master = repo.branches.create('master', repo[remote_master.target.hex])

    assert master.upstream is None
    master.upstream = remote_master
    assert master.upstream.branch_name == 'origin/master'

    def set_bad_upstream():
        master.upstream = 2.5

    with pytest.raises(TypeError): set_bad_upstream()

    master.upstream = None
    assert master.upstream is None


def test_branches_upstream_name(repo):
    remote_master = repo.branches.remote['origin/master']
    master = repo.branches.create('master',
                                       repo[remote_master.target.hex])

    master.upstream = remote_master
    assert master.upstream_name == 'refs/remotes/origin/master'


#
# Low level API written in C, repo.remotes call these.
#

def test_lookup_branch_remote(repo):
    branch = repo.lookup_branch('origin/master', pygit2.GIT_BRANCH_REMOTE)
    assert branch.target.hex == ORIGIN_MASTER_COMMIT

    assert repo.lookup_branch('origin/not-exists', pygit2.GIT_BRANCH_REMOTE) is None

def test_listall_branches(repo):
    branches = sorted(repo.listall_branches(pygit2.GIT_BRANCH_REMOTE))
    assert branches == ['origin/master']

    branches = sorted(repo.raw_listall_branches(pygit2.GIT_BRANCH_REMOTE))
    assert branches == [b'origin/master']

def test_branch_remote_name(repo):
    branch = repo.lookup_branch('origin/master', pygit2.GIT_BRANCH_REMOTE)
    assert branch.remote_name == 'origin'

def test_branch_upstream(repo):
    remote_master = repo.lookup_branch('origin/master', pygit2.GIT_BRANCH_REMOTE)
    master = repo.create_branch('master', repo[remote_master.target.hex])

    assert master.upstream is None
    master.upstream = remote_master
    assert master.upstream.branch_name == 'origin/master'

    def set_bad_upstream():
        master.upstream = 2.5

    with pytest.raises(TypeError): set_bad_upstream()

    master.upstream = None
    assert master.upstream is None

def test_branch_upstream_name(repo):
    remote_master = repo.lookup_branch('origin/master', pygit2.GIT_BRANCH_REMOTE)
    master = repo.create_branch('master', repo[remote_master.target.hex])

    master.upstream = remote_master
    assert master.upstream_name == 'refs/remotes/origin/master'
