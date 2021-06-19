# Copyright 2020-2021 The pygit2 contributors
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

"""Tests for revision parsing."""

from pygit2 import GIT_REVPARSE_SINGLE, GIT_REVPARSE_RANGE, GIT_REVPARSE_MERGE_BASE, InvalidSpecError
from pytest import raises

HEAD_SHA = '2be5719152d4f82c7302b1c0932d8e5f0a4a0e98'
PARENT_SHA = '5ebeeebb320790caf276b9fc8b24546d63316533'  # HEAD^


def test_revparse_single(testrepo):
    o = testrepo.revparse_single('HEAD')
    assert o.hex == HEAD_SHA

    o = testrepo.revparse_single('HEAD^')
    assert o.hex == PARENT_SHA

    o = testrepo.revparse_single('@{-1}')
    assert o.hex == '5470a671a80ac3789f1a6a8cefbcf43ce7af0563'


def test_revparse_ext(testrepo):
    o, r = testrepo.revparse_ext('master')
    assert o.hex == HEAD_SHA
    assert r == testrepo.references['refs/heads/master']

    o, r = testrepo.revparse_ext('HEAD^')
    assert o.hex == PARENT_SHA
    assert r is None

    o, r = testrepo.revparse_ext('i18n')
    assert o.hex.startswith('5470a67')
    assert r == testrepo.references['refs/heads/i18n']


def test_revparse_1(testrepo):
    s = testrepo.revparse('master')
    assert s.from_object.hex == HEAD_SHA
    assert s.to_object is None
    assert s.flags == GIT_REVPARSE_SINGLE


def test_revparse_range_1(testrepo):
    s = testrepo.revparse('HEAD^1..acecd5e')
    assert s.from_object.hex == PARENT_SHA
    assert s.to_object.hex.startswith('acecd5e')
    assert s.flags == GIT_REVPARSE_RANGE


def test_revparse_range_2(testrepo):
    s = testrepo.revparse('HEAD...i18n')
    assert s.from_object.hex.startswith('2be5719')
    assert s.to_object.hex.startswith('5470a67')
    assert s.flags == GIT_REVPARSE_RANGE | GIT_REVPARSE_MERGE_BASE
    assert testrepo.merge_base(s.from_object.id, s.to_object.id) is not None


def test_revparse_range_errors(testrepo):
    with raises(KeyError):
        testrepo.revparse('nope..2be571915')

    with raises(InvalidSpecError):
        testrepo.revparse('master............2be571915')


def test_revparse_repr(testrepo):
    s = testrepo.revparse('HEAD...i18n')
    assert repr(s) == "<pygit2.RevSpec{from=<pygit2.Object{commit:2be5719152d4f82c7302b1c0932d8e5f0a4a0e98}>,to=<pygit2.Object{commit:5470a671a80ac3789f1a6a8cefbcf43ce7af0563}>}>"
