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

"""Tests for Commit objects."""

import sys

import pytest

from pygit2 import GIT_OBJ_COMMIT, Signature, Oid, GitError
from . import utils


COMMIT_SHA = '5fe808e8953c12735680c257f56600cb0de44b10'
COMMIT_SHA_TO_AMEND = '784855caf26449a1914d2cf62d12b9374d76ae78'  # tip of the master branch


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

def test_amend_commit_metadata(barerepo):
    repo = barerepo
    commit = repo[COMMIT_SHA_TO_AMEND]
    assert commit.id == repo.head.target

    encoding = 'iso-8859-1'
    amended_message = "Amended commit message.\n\nMessage with non-ascii chars: ééé.\n"
    amended_author = Signature('Jane Author', 'jane@example.com', 12345, 0)
    amended_committer = Signature('John Committer', 'john@example.com', 12346, 0)

    amended_oid = repo.amend_commit(
        commit, 'HEAD', message=amended_message, author=amended_author,
        committer=amended_committer, encoding=encoding)
    amended_commit = repo[amended_oid]

    assert repo.head.target == amended_oid
    assert GIT_OBJ_COMMIT == amended_commit.type
    assert amended_committer == amended_commit.committer
    assert amended_author == amended_commit.author
    assert amended_message.encode(encoding) == amended_commit.raw_message
    assert commit.author != amended_commit.author
    assert commit.committer != amended_commit.committer
    assert commit.tree == amended_commit.tree  # we didn't touch the tree

def test_amend_commit_tree(barerepo):
    repo = barerepo
    commit = repo[COMMIT_SHA_TO_AMEND]
    assert commit.id == repo.head.target

    tree = '967fce8df97cc71722d3c2a5930ef3e6f1d27b12'
    tree_prefix = tree[:5]

    amended_oid = repo.amend_commit(commit, 'HEAD', tree=tree_prefix)
    amended_commit = repo[amended_oid]

    assert repo.head.target == amended_oid
    assert GIT_OBJ_COMMIT == amended_commit.type
    assert commit.message == amended_commit.message
    assert commit.author == amended_commit.author
    assert commit.committer == amended_commit.committer
    assert commit.tree_id != amended_commit.tree_id
    assert Oid(hex=tree) == amended_commit.tree_id

def test_amend_commit_not_tip_of_branch(barerepo):
    repo = barerepo

    # This commit isn't at the tip of the branch.
    commit = repo['5fe808e8953c12735680c257f56600cb0de44b10']
    assert commit.id != repo.head.target

    # Can't update HEAD to the rewritten commit because it's not the tip of the branch.
    with pytest.raises(GitError):
        repo.amend_commit(commit, 'HEAD', message="this won't work!")

    # We can still amend the commit if we don't try to update a ref.
    repo.amend_commit(commit, None, message="this will work")

def test_amend_commit_no_op(barerepo):
    repo = barerepo
    commit = repo[COMMIT_SHA_TO_AMEND]
    assert commit.id == repo.head.target

    amended_oid = repo.amend_commit(commit, None)
    assert amended_oid == commit.id

def test_amend_commit_argument_types(barerepo):
    repo = barerepo

    some_tree = repo['967fce8df97cc71722d3c2a5930ef3e6f1d27b12']
    commit = repo[COMMIT_SHA_TO_AMEND]
    alt_commit1 = Oid(hex=COMMIT_SHA_TO_AMEND)
    alt_commit2 = COMMIT_SHA_TO_AMEND
    alt_tree = some_tree
    alt_refname = repo.head  # try this one last, because it'll change the commit at the tip

    # Pass bad values/types for the commit
    with pytest.raises(ValueError): repo.amend_commit(None, None)
    with pytest.raises(TypeError): repo.amend_commit(some_tree, None)

    # Pass bad types for signatures
    with pytest.raises(TypeError): repo.amend_commit(commit, None, author="Toto")
    with pytest.raises(TypeError): repo.amend_commit(commit, None, committer="Toto")

    # Pass bad refnames
    with pytest.raises(ValueError): repo.amend_commit(commit, "this-ref-doesnt-exist")
    with pytest.raises(TypeError): repo.amend_commit(commit, repo)

    # Pass bad trees
    with pytest.raises(ValueError): repo.amend_commit(commit, None, tree="can't parse this")
    with pytest.raises(KeyError): repo.amend_commit(commit, None, tree="baaaaad")

    # Pass an Oid for the commit
    amended_oid = repo.amend_commit(alt_commit1, None, message="Hello")
    amended_commit = repo[amended_oid]
    assert GIT_OBJ_COMMIT == amended_commit.type
    assert str(amended_oid) != COMMIT_SHA_TO_AMEND

    # Pass a str for the commit
    amended_oid = repo.amend_commit(alt_commit2, None, message="Hello", tree=alt_tree)
    amended_commit = repo[amended_oid]
    assert GIT_OBJ_COMMIT == amended_commit.type
    assert str(amended_oid) != COMMIT_SHA_TO_AMEND
    assert repo[COMMIT_SHA_TO_AMEND].tree != amended_commit.tree
    assert alt_tree.id == amended_commit.tree_id

    # Pass an actual reference object for refname
    # (Warning: the tip of the branch will be altered after this test!)
    amended_oid = repo.amend_commit(alt_commit2, alt_refname, message="Hello")
    amended_commit = repo[amended_oid]
    assert GIT_OBJ_COMMIT == amended_commit.type
    assert str(amended_oid) != COMMIT_SHA_TO_AMEND
    assert repo.head.target == amended_oid
