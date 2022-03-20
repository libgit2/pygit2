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


@pytest.fixture
def clonerepo(testrepo, tmp_path):
    cloned_repo_path = tmp_path / 'test_remote_prune'

    pygit2.clone_repository(testrepo.workdir, cloned_repo_path)
    clonerepo = pygit2.Repository(cloned_repo_path)
    testrepo.branches.delete('i18n')
    yield clonerepo


def test_fetch_remote_default(clonerepo):
    clonerepo.remotes[0].fetch()
    assert 'origin/i18n' in clonerepo.branches

def test_fetch_remote_prune(clonerepo):
    clonerepo.remotes[0].fetch(prune=pygit2.GIT_FETCH_PRUNE)
    assert 'origin/i18n' not in clonerepo.branches

def test_fetch_no_prune(clonerepo):
    clonerepo.remotes[0].fetch(prune=pygit2.GIT_FETCH_NO_PRUNE)
    assert 'origin/i18n' in clonerepo.branches

def test_remote_prune(clonerepo):
    pruned = []
    class MyCallbacks(pygit2.RemoteCallbacks):
        def update_tips(self, name, old, new):
            pruned.append(name)

    callbacks = MyCallbacks()
    remote = clonerepo.remotes['origin']
    # We do a fetch in order to establish the connection to the remote.
    # Prune operation requires an active connection.
    remote.fetch(prune=pygit2.GIT_FETCH_NO_PRUNE)
    assert 'origin/i18n' in clonerepo.branches
    remote.prune(callbacks)
    assert pruned == ['refs/remotes/origin/i18n']
    assert 'origin/i18n' not in clonerepo.branches
