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

"""Tests for describing commits."""

import pytest

from pygit2 import GIT_DESCRIBE_TAGS, GIT_DESCRIBE_ALL
import pygit2


def add_tag(repo, name, target):
    message = 'Example tag.\n'
    tagger = pygit2.Signature('John Doe', 'jdoe@example.com', 12347, 0)

    sha = repo.create_tag(name, target, pygit2.GIT_OBJ_COMMIT, tagger, message)
    return sha


def test_describe(testrepo):
    add_tag(testrepo, 'thetag', '4ec4389a8068641da2d6578db0419484972284c8')
    assert 'thetag-2-g2be5719' == testrepo.describe()

def test_describe_without_ref(testrepo):
    with pytest.raises(pygit2.GitError): testrepo.describe()

def test_describe_default_oid(testrepo):
    assert '2be5719' == testrepo.describe(show_commit_oid_as_fallback=True)

def test_describe_strategies(testrepo):
    assert 'heads/master' == testrepo.describe(describe_strategy=GIT_DESCRIBE_ALL)

    testrepo.create_reference('refs/tags/thetag', '4ec4389a8068641da2d6578db0419484972284c8')
    with pytest.raises(KeyError): testrepo.describe()
    assert 'thetag-2-g2be5719' == testrepo.describe(describe_strategy=GIT_DESCRIBE_TAGS)

def test_describe_pattern(testrepo):
    add_tag(testrepo, 'private/tag1', '5ebeeebb320790caf276b9fc8b24546d63316533')
    add_tag(testrepo, 'public/tag2', '4ec4389a8068641da2d6578db0419484972284c8')

    assert 'public/tag2-2-g2be5719' == testrepo.describe(pattern='public/*')

def test_describe_committish(testrepo):
    add_tag(testrepo, 'thetag', 'acecd5ea2924a4b900e7e149496e1f4b57976e51')
    assert 'thetag-4-g2be5719' == testrepo.describe(committish='HEAD')
    assert 'thetag-1-g5ebeeeb' == testrepo.describe(committish='HEAD^')

    assert 'thetag-4-g2be5719' == testrepo.describe(committish=testrepo.head)

    assert 'thetag-1-g6aaa262' == testrepo.describe(committish='6aaa262e655dd54252e5813c8e5acd7780ed097d')
    assert 'thetag-1-g6aaa262' == testrepo.describe(committish='6aaa262')

def test_describe_follows_first_branch_only(testrepo):
    add_tag(testrepo, 'thetag', '4ec4389a8068641da2d6578db0419484972284c8')
    with pytest.raises(KeyError):
        testrepo.describe(only_follow_first_parent=True)

def test_describe_abbreviated_size(testrepo):
    add_tag(testrepo, 'thetag', '4ec4389a8068641da2d6578db0419484972284c8')
    assert 'thetag-2-g2be5719152d4f82c' == testrepo.describe(abbreviated_size=16)
    assert 'thetag' == testrepo.describe(abbreviated_size=0)

def test_describe_long_format(testrepo):
    add_tag(testrepo, 'thetag', '2be5719152d4f82c7302b1c0932d8e5f0a4a0e98')
    assert 'thetag-0-g2be5719' == testrepo.describe(always_use_long_format=True)



def test_describe_dirty(dirtyrepo):
    add_tag(dirtyrepo, 'thetag', 'a763aa560953e7cfb87ccbc2f536d665aa4dff22')
    assert 'thetag' == dirtyrepo.describe()

def test_describe_dirty_with_suffix(dirtyrepo):
    add_tag(dirtyrepo, 'thetag', 'a763aa560953e7cfb87ccbc2f536d665aa4dff22')
    assert 'thetag-dirty' == dirtyrepo.describe(dirty_suffix='-dirty')
