# Copyright 2010-2023 The pygit2 contributors
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

import time

import pytest

from pygit2 import Signature


def __assert(signature, encoding):
    encoding = encoding or 'utf-8'
    assert signature._encoding == encoding
    assert signature.name == signature.raw_name.decode(encoding)
    assert signature.name.encode(encoding) == signature.raw_name
    assert signature.email == signature.raw_email.decode(encoding)
    assert signature.email.encode(encoding) == signature.raw_email

@pytest.mark.parametrize('encoding', [None, 'utf-8', 'iso-8859-1'])
def test_encoding(encoding):
    signature = Signature('Foo Ibáñez', 'foo@example.com', encoding=encoding)
    __assert(signature, encoding)
    assert abs(signature.time - time.time()) < 5
    assert str(signature) == 'Foo Ibáñez <foo@example.com>'

def test_default_encoding():
    signature = Signature('Foo Ibáñez', 'foo@example.com', 1322174594, 60)
    __assert(signature, 'utf-8')

def test_ascii():
    with pytest.raises(UnicodeEncodeError):
        Signature('Foo Ibáñez', 'foo@example.com', encoding='ascii')

def test_repr():
    encoding = 'utf-8'
    signature = Signature('Foo Ibáñez', 'foo@bar.com', 1322174594, 60, encoding=encoding)
    expected = f"pygit2.Signature('Foo Ibáñez', 'foo@bar.com', 1322174594, 60, '{encoding}')"
    assert repr(signature) == expected

def test_repr_from_commit(barerepo):
    repo = barerepo
    signature = Signature('Foo Ibáñez', 'foo@example.com', encoding=None)
    tree = '967fce8df97cc71722d3c2a5930ef3e6f1d27b12'
    parents = ['5fe808e8953c12735680c257f56600cb0de44b10']
    sha = repo.create_commit(None, signature, signature, 'New commit.', tree, parents)
    commit = repo[sha]

    assert repr(signature) == repr(commit.author)
    assert repr(signature) == repr(commit.committer)
