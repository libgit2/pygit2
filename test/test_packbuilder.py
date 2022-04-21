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

"""Tests for Index files."""

from pathlib import Path

import pygit2
from pygit2 import PackBuilder
from . import utils


def test_create_packbuilder(testrepo):
    # simple test of PackBuilder creation
    packbuilder = PackBuilder(testrepo)
    assert len(packbuilder) == 0


def test_add(testrepo):
    # Add a few objects and confirm that the count is correct
    packbuilder = PackBuilder(testrepo)
    objects_to_add = [obj for obj in testrepo]
    packbuilder.add(objects_to_add[0])
    assert len(packbuilder) == 1
    packbuilder.add(objects_to_add[1])
    assert len(packbuilder) == 2


def test_add_recursively(testrepo):
    # Add the head object and referenced objects recursively and confirm that the count is correct
    packbuilder = PackBuilder(testrepo)
    packbuilder.add_recur(testrepo.head.target)

    #expect a count of 4 made up of the following referenced objects:
    # Commit
    # Tree
    # Blob: hello.txt
    # Blob: .gitignore

    assert len(packbuilder) == 4


def test_repo_pack(testrepo, tmp_path):
    # pack the repo with the default strategy
    confirm_same_repo_after_packing(testrepo, tmp_path, None)


def test_pack_with_delegate(testrepo, tmp_path):
    # loop through all branches and add each commit to the packbuilder
    def pack_delegate(pb):
        for branch in pb._repo.branches:
            br = pb._repo.branches.get(branch)
            for commit in br.log():
                pb.add_recur(commit.oid_new)
    confirm_same_repo_after_packing(testrepo, tmp_path, pack_delegate)


def setup_second_repo(tmp_path):
    # helper method to set up a second repo for comparison
    tmp_path_2 = tmp_path / 'test_repo2'
    with utils.TemporaryRepository('testrepo.zip', tmp_path_2) as path:
        testrepo = pygit2.Repository(path)
    return testrepo

def confirm_same_repo_after_packing(testrepo, tmp_path, pack_delegate):
    # Helper method to confirm the contents of two repos before and after packing
    pack_repo = setup_second_repo(tmp_path)
    pack_repo_path = Path(pack_repo.path)

    objects_dir = pack_repo_path / 'objects'
    utils.rmtree(objects_dir)
    pack_path = objects_dir / 'pack'
    pack_path.mkdir(parents=True)

    # assert that the number of written objects is the same as the number of objects in the repo
    written_objects = testrepo.pack(pack_path, pack_delegate=pack_delegate)
    assert written_objects == len([obj for obj in testrepo])


    # assert that the number of objects in the pack repo is the same as the original repo
    orig_objects = [obj for obj in testrepo.odb]
    packed_objects = [obj for obj in pack_repo.odb]
    assert len(packed_objects) == len(orig_objects)

    # assert that the objects in the packed repo are the same objects as the original repo
    for i, obj in enumerate(orig_objects):
        assert pack_repo[obj].type == testrepo[obj].type
        assert pack_repo[obj].read_raw() == testrepo[obj].read_raw()
