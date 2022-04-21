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

import pytest

import pygit2
from pygit2 import Repository, Index, Oid
from . import utils


def test_bare(barerepo):
    assert len(barerepo.index) == 0


def test_index(testrepo):
    assert testrepo.index is not None

def test_read(testrepo):
    index = testrepo.index
    assert len(index) == 2

    with pytest.raises(TypeError): index[()]
    utils.assertRaisesWithArg(ValueError, -4, lambda: index[-4])
    utils.assertRaisesWithArg(KeyError, 'abc', lambda: index['abc'])

    sha = 'a520c24d85fbfc815d385957eed41406ca5a860b'
    assert 'hello.txt' in index
    assert index['hello.txt'].hex == sha
    assert index['hello.txt'].path == 'hello.txt'
    assert index[1].hex == sha

def test_add(testrepo):
    index = testrepo.index

    sha = '0907563af06c7464d62a70cdd135a6ba7d2b41d8'
    assert 'bye.txt' not in index
    index.add('bye.txt')
    assert 'bye.txt' in index
    assert len(index) == 3
    assert index['bye.txt'].hex == sha

def test_add_aspath(testrepo):
    index = testrepo.index

    assert 'bye.txt' not in index
    index.add(Path('bye.txt'))
    assert 'bye.txt' in index

def test_add_all(testrepo):
    clear(testrepo)

    sha_bye = '0907563af06c7464d62a70cdd135a6ba7d2b41d8'
    sha_hello = 'a520c24d85fbfc815d385957eed41406ca5a860b'

    index = testrepo.index
    index.add_all(['*.txt'])

    assert 'bye.txt' in index
    assert 'hello.txt' in index

    assert index['bye.txt'].hex == sha_bye
    assert index['hello.txt'].hex == sha_hello

    clear(testrepo)

    index.add_all(['bye.t??', 'hello.*'])
    assert 'bye.txt' in index
    assert 'hello.txt' in index

    assert index['bye.txt'].hex == sha_bye
    assert index['hello.txt'].hex == sha_hello

    clear(testrepo)

    index.add_all(['[byehlo]*.txt'])
    assert 'bye.txt' in index
    assert 'hello.txt' in index

    assert index['bye.txt'].hex == sha_bye
    assert index['hello.txt'].hex == sha_hello

def test_add_all_aspath(testrepo):
    clear(testrepo)

    index = testrepo.index
    index.add_all([Path('bye.txt'), Path('hello.txt')])
    assert 'bye.txt' in index
    assert 'hello.txt' in index

def clear(repo):
    index = repo.index
    assert len(index) == 2
    index.clear()
    assert len(index) == 0

def test_write(testrepo):
    index = testrepo.index
    index.add('bye.txt')
    index.write()

    index.clear()
    assert 'bye.txt' not in index
    index.read()
    assert 'bye.txt' in index


def test_read_tree(testrepo):
    tree_oid = '68aba62e560c0ebc3396e8ae9335232cd93a3f60'
    # Test reading first tree
    index = testrepo.index
    assert len(index) == 2
    index.read_tree(tree_oid)
    assert len(index) == 1
    # Test read-write returns the same oid
    oid = index.write_tree()
    assert oid.hex == tree_oid
    # Test the index is only modified in memory
    index.read()
    assert len(index) == 2


def test_write_tree(testrepo):
    oid = testrepo.index.write_tree()
    assert oid.hex == 'fd937514cb799514d4b81bb24c5fcfeb6472b245'

def test_iter(testrepo):
    index = testrepo.index
    n = len(index)
    assert len(list(index)) == n

    # Compare SHAs, not IndexEntry object identity
    entries = [index[x].hex for x in range(n)]
    assert list(x.hex for x in index) == entries

def test_mode(testrepo):
    """
        Testing that we can access an index entry mode.
    """
    index = testrepo.index

    hello_mode = index['hello.txt'].mode
    assert hello_mode == 33188

def test_bare_index(testrepo):
    index = pygit2.Index(Path(testrepo.path) / 'index')
    assert [x.hex for x in index] == [x.hex for x in testrepo.index]

    with pytest.raises(pygit2.GitError): index.add('bye.txt')

def test_remove(testrepo):
    index = testrepo.index
    assert 'hello.txt' in index
    index.remove('hello.txt')
    assert 'hello.txt' not in index

def test_remove_all(testrepo):
    index = testrepo.index
    assert 'hello.txt' in index
    index.remove_all(['*.txt'])
    assert 'hello.txt' not in index

    index.remove_all(['not-existing'])  # this doesn't error

def test_remove_aspath(testrepo):
    index = testrepo.index
    assert 'hello.txt' in index
    index.remove(Path('hello.txt'))
    assert 'hello.txt' not in index

def test_remove_all_aspath(testrepo):
    index = testrepo.index
    assert 'hello.txt' in index
    index.remove_all([Path('hello.txt')])
    assert 'hello.txt' not in index

def test_change_attributes(testrepo):
    index = testrepo.index
    entry = index['hello.txt']
    ign_entry = index['.gitignore']
    assert ign_entry.id != entry.id
    assert entry.mode != pygit2.GIT_FILEMODE_BLOB_EXECUTABLE
    entry.path = 'foo.txt'
    entry.id = ign_entry.id
    entry.mode = pygit2.GIT_FILEMODE_BLOB_EXECUTABLE
    assert 'foo.txt' == entry.path
    assert ign_entry.id == entry.id
    assert pygit2.GIT_FILEMODE_BLOB_EXECUTABLE == entry.mode

def test_write_tree_to(testrepo, tmp_path):
    pygit2.option(pygit2.GIT_OPT_ENABLE_STRICT_OBJECT_CREATION, False)
    with utils.TemporaryRepository('emptyrepo.zip', tmp_path) as path:
        nrepo = Repository(path)
        id = testrepo.index.write_tree(nrepo)
        assert nrepo[id] is not None


def test_create_entry(testrepo):
    index = testrepo.index
    hello_entry = index['hello.txt']
    entry = pygit2.IndexEntry('README.md', hello_entry.id, hello_entry.mode)
    index.add(entry)
    tree_id = index.write_tree()
    assert '60e769e57ae1d6a2ab75d8d253139e6260e1f912' == str(tree_id)

def test_create_entry_aspath(testrepo):
    index = testrepo.index
    hello_entry = index[Path('hello.txt')]
    entry = pygit2.IndexEntry(Path('README.md'), hello_entry.id, hello_entry.mode)
    index.add(entry)
    index.write_tree()

def test_entry_eq(testrepo):
    index = testrepo.index
    hello_entry = index['hello.txt']
    entry = pygit2.IndexEntry(hello_entry.path, hello_entry.id, hello_entry.mode)
    assert hello_entry == entry

    entry = pygit2.IndexEntry("README.md", hello_entry.id, hello_entry.mode)
    assert hello_entry != entry
    oid = Oid(hex='0907563af06c7464d62a70cdd135a6ba7d2b41d8')
    entry = pygit2.IndexEntry(hello_entry.path, oid, hello_entry.mode)
    assert hello_entry != entry
    entry = pygit2.IndexEntry(hello_entry.path, hello_entry.id, pygit2.GIT_FILEMODE_BLOB_EXECUTABLE)
    assert hello_entry != entry

def test_entry_repr(testrepo):
    index = testrepo.index
    hello_entry = index['hello.txt']
    assert (repr(hello_entry) ==
            "<pygit2.index.IndexEntry path=hello.txt id=a520c24d85fbfc815d385957eed41406ca5a860b mode=33188>")
    assert (str(hello_entry) ==
            "<path=hello.txt id=a520c24d85fbfc815d385957eed41406ca5a860b mode=33188>")


def test_create_empty():
    Index()

def test_create_empty_read_tree_as_string():
    index = Index()
    # no repo associated, so we don't know where to read from
    with pytest.raises(TypeError):
        index('read_tree', 'fd937514cb799514d4b81bb24c5fcfeb6472b245')

def test_create_empty_read_tree(testrepo):
    index = Index()
    index.read_tree(testrepo['fd937514cb799514d4b81bb24c5fcfeb6472b245'])
