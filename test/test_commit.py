# Copyright 2010-2020 The pygit2 contributors
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

"""Tests for Commit objects."""

import sys

import pytest

from pygit2 import GIT_OBJ_COMMIT, Signature, Oid
from . import utils


COMMIT_SHA = '5fe808e8953c12735680c257f56600cb0de44b10'


@utils.refcount
def test_commit_refcount(barerepo):
    commit = barerepo[COMMIT_SHA]
    start = sys.getrefcount(commit)
    tree = commit.tree
    del tree
    end = sys.getrefcount(commit)
    assert start == end


def test_read_commit(barerepo):
    commit = barerepo[COMMIT_SHA]
    assert COMMIT_SHA == str(commit.id)
    parents = commit.parents
    assert 1 == len(parents)
    assert 'c2792cfa289ae6321ecf2cd5806c2194b0fd070c' == str(parents[0].id)
    assert commit.message_encoding is None
    assert commit.message == ('Second test data commit.\n\n'
                              'This commit has some additional text.\n')
    commit_time = 1288481576
    assert commit_time == commit.commit_time
    assert commit.committer == Signature('Dave Borowitz', 'dborowitz@google.com', commit_time, -420)
    assert commit.author == Signature('Dave Borowitz', 'dborowitz@google.com', 1288477363, -420)
    assert '967fce8df97cc71722d3c2a5930ef3e6f1d27b12' == str(commit.tree.id)

def test_new_commit(barerepo):
    repo = barerepo
    message = 'New commit.\n\nMessage with non-ascii chars: ééé.\n'
    committer = Signature('John Doe', 'jdoe@example.com', 12346, 0)
    author = Signature(
        'J. David Ibáñez', 'jdavid@example.com', 12345, 0,
        encoding='utf-8')
    tree = '967fce8df97cc71722d3c2a5930ef3e6f1d27b12'
    tree_prefix = tree[:5]
    too_short_prefix = tree[:3]

    parents = [COMMIT_SHA[:5]]
    with pytest.raises(ValueError):
        repo.create_commit(None, author, committer, message, too_short_prefix, parents)

    sha = repo.create_commit(None, author, committer, message,
                             tree_prefix, parents)
    commit = repo[sha]

    assert GIT_OBJ_COMMIT == commit.type
    assert '98286caaab3f1fde5bf52c8369b2b0423bad743b' == commit.hex
    assert commit.message_encoding is None
    assert message == commit.message
    assert 12346 == commit.commit_time
    assert committer == commit.committer
    assert author == commit.author
    assert tree == commit.tree.hex
    assert Oid(hex=tree) == commit.tree_id
    assert 1 == len(commit.parents)
    assert COMMIT_SHA == commit.parents[0].hex
    assert Oid(hex=COMMIT_SHA) == commit.parent_ids[0]

def test_new_commit_encoding(barerepo):
    repo = barerepo
    encoding = 'iso-8859-1'
    message = 'New commit.\n\nMessage with non-ascii chars: ééé.\n'
    committer = Signature('John Doe', 'jdoe@example.com', 12346, 0,
                          encoding)
    author = Signature('J. David Ibáñez', 'jdavid@example.com', 12345, 0,
                       encoding)
    tree = '967fce8df97cc71722d3c2a5930ef3e6f1d27b12'
    tree_prefix = tree[:5]

    parents = [COMMIT_SHA[:5]]
    sha = repo.create_commit(None, author, committer, message,
                             tree_prefix, parents, encoding)
    commit = repo[sha]

    assert GIT_OBJ_COMMIT == commit.type
    assert 'iso-8859-1' == commit.message_encoding
    assert message.encode(encoding) == commit.raw_message
    assert 12346 == commit.commit_time
    assert committer == commit.committer
    assert author == commit.author
    assert tree == commit.tree.hex
    assert Oid(hex=tree) == commit.tree_id
    assert 1 == len(commit.parents)
    assert COMMIT_SHA == commit.parents[0].hex
    assert Oid(hex=COMMIT_SHA) == commit.parent_ids[0]

def test_modify_commit(barerepo):
    message = 'New commit.\n\nMessage.\n'
    committer = ('John Doe', 'jdoe@example.com', 12346)
    author = ('Jane Doe', 'jdoe2@example.com', 12345)

    commit = barerepo[COMMIT_SHA]

    with pytest.raises(AttributeError): setattr(commit, 'message', message)
    with pytest.raises(AttributeError): setattr(commit, 'committer', committer)
    with pytest.raises(AttributeError): setattr(commit, 'author', author)
    with pytest.raises(AttributeError): setattr(commit, 'tree', None)
    with pytest.raises(AttributeError): setattr(commit, 'parents', None)
