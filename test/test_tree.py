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

import operator

import pygit2
import pytest

from . import utils


TREE_SHA = '967fce8df97cc71722d3c2a5930ef3e6f1d27b12'
SUBTREE_SHA = '614fd9a3094bf618ea938fffc00e7d1a54f89ad0'

def assertTreeEntryEqual(entry, sha, name, filemode):
    assert entry.hex == sha
    assert entry.name == name
    assert entry.filemode == filemode
    assert entry.raw_name == name.encode('utf-8')


def test_read_tree(barerepo):
    tree = barerepo[TREE_SHA]
    with pytest.raises(TypeError): tree[()]
    with pytest.raises(TypeError):
        tree / 123
    utils.assertRaisesWithArg(KeyError, 'abcd', lambda: tree['abcd'])
    utils.assertRaisesWithArg(IndexError, -4, lambda: tree[-4])
    utils.assertRaisesWithArg(IndexError, 3, lambda: tree[3])
    utils.assertRaisesWithArg(KeyError, 'abcd', lambda: tree / 'abcd')

    assert 3 == len(tree)
    sha = '7f129fd57e31e935c6d60a0c794efe4e6927664b'
    assert 'a' in tree
    assertTreeEntryEqual(tree[0], sha, 'a', 0o0100644)
    assertTreeEntryEqual(tree[-3], sha, 'a', 0o0100644)
    assertTreeEntryEqual(tree['a'], sha, 'a', 0o0100644)
    assertTreeEntryEqual(tree / 'a', sha, 'a', 0o0100644)

    sha = '85f120ee4dac60d0719fd51731e4199aa5a37df6'
    assert 'b' in tree
    assertTreeEntryEqual(tree[1], sha, 'b', 0o0100644)
    assertTreeEntryEqual(tree[-2], sha, 'b', 0o0100644)
    assertTreeEntryEqual(tree['b'], sha, 'b', 0o0100644)
    assertTreeEntryEqual(tree / 'b', sha, 'b', 0o0100644)

    sha = '297efb891a47de80be0cfe9c639e4b8c9b450989'
    assertTreeEntryEqual(tree['c/d'], sha, 'd', 0o0100644)
    assertTreeEntryEqual(tree / 'c/d', sha, 'd', 0o0100644)
    assertTreeEntryEqual(tree / 'c' / 'd', sha, 'd', 0o0100644)
    assertTreeEntryEqual(tree['c']['d'], sha, 'd', 0o0100644)
    assertTreeEntryEqual((tree / 'c')['d'], sha, 'd', 0o0100644)
    utils.assertRaisesWithArg(KeyError, 'ab/cd', lambda: tree['ab/cd'])
    utils.assertRaisesWithArg(KeyError, 'ab/cd', lambda: tree / 'ab/cd')
    utils.assertRaisesWithArg(KeyError, 'ab', lambda: tree / 'c' / 'ab')
    with pytest.raises(TypeError):
        tree / 'a' / 'cd'

def test_equality(barerepo):
    tree_a = barerepo['18e2d2e9db075f9eb43bcb2daa65a2867d29a15e']
    tree_b = barerepo['2ad1d3456c5c4a1c9e40aeeddb9cd20b409623c8']

    assert tree_a['a'] != tree_b['a']
    assert tree_a['a'] != tree_b['b']
    assert tree_a['b'] == tree_b['b']

def test_sorting(barerepo):
    tree_a = barerepo['18e2d2e9db075f9eb43bcb2daa65a2867d29a15e']
    assert list(tree_a) == sorted(reversed(list(tree_a)), key=pygit2.tree_entry_key)
    assert list(tree_a) != reversed(list(tree_a))

def test_read_subtree(barerepo):
    tree = barerepo[TREE_SHA]

    subtree_entry = tree['c']
    assertTreeEntryEqual(subtree_entry, SUBTREE_SHA, 'c', 0o0040000)
    assert subtree_entry.type == pygit2.GIT_OBJ_TREE
    assert subtree_entry.type_str == 'tree'

    subtree_entry = tree / 'c'
    assertTreeEntryEqual(subtree_entry, SUBTREE_SHA, 'c', 0o0040000)
    assert subtree_entry.type == pygit2.GIT_OBJ_TREE
    assert subtree_entry.type_str == 'tree'

    subtree = barerepo[subtree_entry.id]
    assert 1 == len(subtree)
    sha = '297efb891a47de80be0cfe9c639e4b8c9b450989'
    assertTreeEntryEqual(subtree[0], sha, 'd', 0o0100644)

    subtree_entry = (tree / 'c')
    assert subtree_entry == barerepo[subtree_entry.id]

def test_new_tree(barerepo):
    repo = barerepo
    b0 = repo.create_blob('1')
    b1 = repo.create_blob('2')
    st = repo.TreeBuilder()
    st.insert('a', b0, 0o0100644)
    subtree = repo[st.write()]

    t = repo.TreeBuilder()
    t.insert('x', b0, 0o0100644)
    t.insert('y', b1, 0o0100755)
    t.insert('z', subtree.id, pygit2.GIT_FILEMODE_TREE)
    tree = repo[t.write()]

    for name, oid, cls, filemode, type, type_str in [
        ('x', b0, pygit2.Blob, pygit2.GIT_FILEMODE_BLOB, pygit2.GIT_OBJ_BLOB, 'blob'),
        ('y', b1, pygit2.Blob, pygit2.GIT_FILEMODE_BLOB_EXECUTABLE, pygit2.GIT_OBJ_BLOB, 'blob'),
        ('z', subtree.id, pygit2.Tree, pygit2.GIT_FILEMODE_TREE, pygit2.GIT_OBJ_TREE, 'tree')]:

        assert name in tree
        obj = tree[name]
        assert isinstance(obj, cls)
        assert obj.name == name
        assert obj.filemode == filemode
        assert obj.type == type
        assert obj.type_str == type_str
        assert repo[obj.id].id == oid
        assert obj == repo[obj.id]

        obj = tree / name
        assert isinstance(obj, cls)
        assert obj.name == name
        assert obj.filemode == filemode
        assert obj.type == type
        assert obj.type_str == type_str
        assert repo[obj.id].id == oid
        assert obj == repo[obj.id]

def test_modify_tree(barerepo):
    tree = barerepo[TREE_SHA]
    with pytest.raises(TypeError): operator.setitem('c', tree['a'])
    with pytest.raises(TypeError): operator.delitem('c')

def test_iterate_tree(barerepo):
    """
    Testing that we're able to iterate of a Tree object and that the
    resulting sha strings are consitent with the sha strings we could
    get with other Tree access methods.
    """
    tree = barerepo[TREE_SHA]
    for tree_entry in tree:
        assert tree_entry == tree[tree_entry.name]

def test_iterate_tree_nested(barerepo):
    """
    Testing that we're able to iterate of a Tree object and then iterate
    trees we receive as a result.
    """
    tree = barerepo[TREE_SHA]
    for tree_entry in tree:
        if isinstance(tree_entry, pygit2.Tree):
            for tree_entry2 in tree_entry:
                pass

def test_deep_contains(barerepo):
    tree = barerepo[TREE_SHA]
    assert 'a' in tree
    assert 'c' in tree
    assert 'c/d' in tree
    assert 'c/e' not in tree
    assert 'd' not in tree

    assert 'd' in tree['c']
    assert 'e' not in tree['c']
