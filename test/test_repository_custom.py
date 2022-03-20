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

from pathlib import Path

import pygit2
import pytest


@pytest.fixture
def repo(testrepopacked):
    testrepo = testrepopacked

    odb = pygit2.Odb()
    object_path = Path(testrepo.path) / 'objects'
    odb.add_backend(pygit2.OdbBackendPack(object_path), 1)
    odb.add_backend(pygit2.OdbBackendLoose(object_path, 0, False), 1)

    refdb = pygit2.Refdb.new(testrepo)
    refdb.set_backend(pygit2.RefdbFsBackend(testrepo))

    repo = pygit2.Repository()
    repo.set_odb(odb)
    repo.set_refdb(refdb)
    yield repo

def test_references(repo):
    refs = [(ref.name, ref.target.hex) for ref in repo.references.objects]
    assert sorted(refs) == [
        ('refs/heads/i18n', '5470a671a80ac3789f1a6a8cefbcf43ce7af0563'),
        ('refs/heads/master', '2be5719152d4f82c7302b1c0932d8e5f0a4a0e98')]

def test_objects(repo):
    a = repo.read('323fae03f4606ea9991df8befbb2fca795e648fa')
    assert (pygit2.GIT_OBJ_BLOB, b'foobar\n') == a
