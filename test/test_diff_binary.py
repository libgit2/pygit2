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

from . import utils


@pytest.fixture
def repo(tmp_path):
    with utils.TemporaryRepository('binaryfilerepo.zip', tmp_path) as path:
        yield pygit2.Repository(path)


PATCH_BINARY = """diff --git a/binary_file b/binary_file
index 86e5c10..b835d73 100644
Binary files a/binary_file and b/binary_file differ
"""

PATCH_BINARY_SHOW = """diff --git a/binary_file b/binary_file
index 86e5c1008b5ce635d3e3fffa4434c5eccd8f00b6..b835d73543244b6694f36a8c5dfdffb71b153db7 100644
GIT binary patch
literal 8
Pc${NM%FIhFs^kIy3n&7R

literal 8
Pc${NM&PdElPvrst3ey5{

"""

def test_binary_diff(repo):
    diff = repo.diff('HEAD', 'HEAD^')
    assert PATCH_BINARY == diff.patch
    diff = repo.diff('HEAD', 'HEAD^', flags=pygit2.GIT_DIFF_SHOW_BINARY)
    assert PATCH_BINARY_SHOW == diff.patch
    diff = repo.diff(b'HEAD', b'HEAD^')
    assert PATCH_BINARY == diff.patch
    diff = repo.diff(b'HEAD', b'HEAD^', flags=pygit2.GIT_DIFF_SHOW_BINARY)
    assert PATCH_BINARY_SHOW == diff.patch
