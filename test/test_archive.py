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
import tarfile

from pygit2 import Index, Oid, Tree, Object


TREE_HASH = 'fd937514cb799514d4b81bb24c5fcfeb6472b245'
COMMIT_HASH = '2be5719152d4f82c7302b1c0932d8e5f0a4a0e98'

def check_writing(repo, treeish, timestamp=None):
    archive = tarfile.open('foo.tar', mode='w')
    repo.write_archive(treeish, archive)

    index = Index()
    if isinstance(treeish, Object):
        index.read_tree(treeish.peel(Tree))
    else:
        index.read_tree(repo[treeish].peel(Tree))

    assert len(index) == len(archive.getmembers())

    if timestamp:
        fileinfo = archive.getmembers()[0]
        assert timestamp == fileinfo.mtime

    archive.close()
    path = Path('foo.tar')
    assert path.is_file()
    path.unlink()

def test_write_tree(testrepo):
    check_writing(testrepo, TREE_HASH)
    check_writing(testrepo, Oid(hex=TREE_HASH))
    check_writing(testrepo, testrepo[TREE_HASH])

def test_write_commit(testrepo):
    commit_timestamp = testrepo[COMMIT_HASH].committer.time
    check_writing(testrepo, COMMIT_HASH, commit_timestamp)
    check_writing(testrepo, Oid(hex=COMMIT_HASH), commit_timestamp)
    check_writing(testrepo, testrepo[COMMIT_HASH], commit_timestamp)
