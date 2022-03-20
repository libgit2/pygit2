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

# Standard Library
import binascii
import os
from pathlib import Path
import sys
import tempfile

import pygit2
import pytest

from . import utils


HEAD_SHA = '784855caf26449a1914d2cf62d12b9374d76ae78'
PARENT_SHA = 'f5e5aa4e36ab0fe62ee1ccc6eb8f79b866863b87'  # HEAD^
BLOB_HEX = 'af431f20fc541ed6d5afede3e2dc7160f6f01f16'
BLOB_RAW = binascii.unhexlify(BLOB_HEX.encode('ascii'))
BLOB_OID = pygit2.Oid(raw=BLOB_RAW)

def test_is_empty(barerepo):
    assert not barerepo.is_empty

def test_is_bare(barerepo):
    assert barerepo.is_bare

def test_head(barerepo):
    head = barerepo.head
    assert HEAD_SHA == head.target.hex
    assert type(head) == pygit2.Reference
    assert not barerepo.head_is_unborn
    assert not barerepo.head_is_detached

def test_set_head(barerepo):
    # Test setting a detatched HEAD.
    barerepo.set_head(pygit2.Oid(hex=PARENT_SHA))
    assert barerepo.head.target.hex == PARENT_SHA
    # And test setting a normal HEAD.
    barerepo.set_head("refs/heads/master")
    assert barerepo.head.name == "refs/heads/master"
    assert barerepo.head.target.hex == HEAD_SHA

def test_read(barerepo):
    with pytest.raises(TypeError):
        barerepo.read(123)
    utils.assertRaisesWithArg(KeyError, '1' * 40, barerepo.read, '1' * 40)

    ab = barerepo.read(BLOB_OID)
    a = barerepo.read(BLOB_HEX)
    assert ab == a
    assert (pygit2.GIT_OBJ_BLOB, b'a contents\n') == a

    a2 = barerepo.read('7f129fd57e31e935c6d60a0c794efe4e6927664b')
    assert (pygit2.GIT_OBJ_BLOB, b'a contents 2\n') == a2

    a_hex_prefix = BLOB_HEX[:4]
    a3 = barerepo.read(a_hex_prefix)
    assert (pygit2.GIT_OBJ_BLOB, b'a contents\n') == a3

def test_write(barerepo):
    data = b"hello world"
    # invalid object type
    with pytest.raises(ValueError):
        barerepo.write(pygit2.GIT_OBJ_ANY, data)

    oid = barerepo.write(pygit2.GIT_OBJ_BLOB, data)
    assert type(oid) == pygit2.Oid

def test_contains(barerepo):
    with pytest.raises(TypeError):
        123 in barerepo
    assert BLOB_OID in barerepo
    assert BLOB_HEX in barerepo
    assert BLOB_HEX[:10] in barerepo
    assert ('a' * 40) not in barerepo
    assert ('a' * 20) not in barerepo

def test_iterable(barerepo):
    l = [obj for obj in barerepo]
    oid = pygit2.Oid(hex=BLOB_HEX)
    assert oid in l

def test_lookup_blob(barerepo):
    with pytest.raises(TypeError):
        barerepo[123]
    assert barerepo[BLOB_OID].hex == BLOB_HEX
    a = barerepo[BLOB_HEX]
    assert b'a contents\n' == a.read_raw()
    assert BLOB_HEX == a.hex
    assert pygit2.GIT_OBJ_BLOB == a.type

def test_lookup_blob_prefix(barerepo):
    a = barerepo[BLOB_HEX[:5]]
    assert b'a contents\n' == a.read_raw()
    assert BLOB_HEX == a.hex
    assert pygit2.GIT_OBJ_BLOB == a.type

def test_lookup_commit(barerepo):
    commit_sha = '5fe808e8953c12735680c257f56600cb0de44b10'
    commit = barerepo[commit_sha]
    assert commit_sha == commit.hex
    assert pygit2.GIT_OBJ_COMMIT == commit.type
    assert commit.message == ('Second test data commit.\n\n'
                              'This commit has some additional text.\n')

def test_lookup_commit_prefix(barerepo):
    commit_sha = '5fe808e8953c12735680c257f56600cb0de44b10'
    commit_sha_prefix = commit_sha[:7]
    too_short_prefix = commit_sha[:3]
    commit = barerepo[commit_sha_prefix]
    assert commit_sha == commit.hex
    assert pygit2.GIT_OBJ_COMMIT == commit.type
    assert 'Second test data commit.\n\n' 'This commit has some additional text.\n' == commit.message
    with pytest.raises(ValueError):
        barerepo.__getitem__(too_short_prefix)

def test_expand_id(barerepo):
    commit_sha = '5fe808e8953c12735680c257f56600cb0de44b10'
    expanded = barerepo.expand_id(commit_sha[:7])
    assert commit_sha == expanded.hex

@utils.refcount
def test_lookup_commit_refcount(barerepo):
    start = sys.getrefcount(barerepo)
    commit_sha = '5fe808e8953c12735680c257f56600cb0de44b10'
    commit = barerepo[commit_sha]
    del commit
    end = sys.getrefcount(barerepo)
    assert start == end

def test_get_path(barerepo_path):
    barerepo, path = barerepo_path

    directory = Path(barerepo.path).resolve()
    assert directory == path.resolve()

def test_get_workdir(barerepo):
    assert barerepo.workdir is None

def test_revparse_single(barerepo):
    parent = barerepo.revparse_single('HEAD^')
    assert parent.hex == PARENT_SHA

def test_hash(barerepo):
    data = "foobarbaz"
    hashed_sha1 = pygit2.hash(data)
    written_sha1 = barerepo.create_blob(data)
    assert hashed_sha1 == written_sha1

def test_hashfile(barerepo):
    data = "bazbarfoo"
    handle, tempfile_path = tempfile.mkstemp()
    with os.fdopen(handle, 'w') as fh:
        fh.write(data)
    hashed_sha1 = pygit2.hashfile(tempfile_path)
    Path(tempfile_path).unlink()
    written_sha1 = barerepo.create_blob(data)
    assert hashed_sha1 == written_sha1

def test_conflicts_in_bare_repository(barerepo):
    def create_conflict_file(repo, branch, content):
        oid = repo.create_blob(content.encode('utf-8'))
        tb = repo.TreeBuilder()
        tb.insert('conflict', oid, pygit2.GIT_FILEMODE_BLOB)
        tree = tb.write()

        sig = pygit2.Signature('Author', 'author@example.com')
        commit = repo.create_commit(branch.name, sig, sig,
                'Conflict', tree, [branch.target])
        assert commit is not None
        return commit

    b1 = barerepo.create_branch('b1', barerepo.head.peel())
    c1 = create_conflict_file(barerepo, b1, 'ASCII - abc')
    b2 = barerepo.create_branch('b2', barerepo.head.peel())
    c2 = create_conflict_file(barerepo, b2, 'Unicode - äüö')

    index = barerepo.merge_commits(c1, c2)
    assert index.conflicts is not None

    # ConflictCollection does not allow calling len(...) on it directly so
    # we have to calculate length by iterating over its entries
    assert sum(1 for _ in index.conflicts) == 1

    (a, t, o) = index.conflicts['conflict']
    diff = barerepo.merge_file_from_index(a, t, o)
    assert diff == '''<<<<<<< conflict
ASCII - abc
=======
Unicode - äüö
>>>>>>> conflict
'''
