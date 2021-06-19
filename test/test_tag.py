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

"""Tests for Tag objects."""

import pygit2
import pytest


TAG_SHA = '3d2962987c695a29f1f80b6c3aa4ec046ef44369'


def test_read_tag(barerepo):
    repo = barerepo
    tag = repo[TAG_SHA]
    target = repo[tag.target]
    assert isinstance(tag, pygit2.Tag)
    assert pygit2.GIT_OBJ_TAG == tag.type
    assert pygit2.GIT_OBJ_COMMIT == target.type
    assert 'root' == tag.name
    assert 'Tagged root commit.\n' == tag.message
    assert 'Initial test data commit.\n' == target.message
    assert tag.tagger == pygit2.Signature('Dave Borowitz', 'dborowitz@google.com', 1288724692, -420)

def test_new_tag(barerepo):
    name = 'thetag'
    target = 'af431f20fc541ed6d5afede3e2dc7160f6f01f16'
    message = 'Tag a blob.\n'
    tagger = pygit2.Signature('John Doe', 'jdoe@example.com', 12347, 0)

    target_prefix = target[:5]
    too_short_prefix = target[:3]
    with pytest.raises(ValueError):
        barerepo.create_tag(name, too_short_prefix, pygit2.GIT_OBJ_BLOB, tagger, message)

    sha = barerepo.create_tag(name, target_prefix, pygit2.GIT_OBJ_BLOB,
                               tagger, message)
    tag = barerepo[sha]

    assert '3ee44658fd11660e828dfc96b9b5c5f38d5b49bb' == tag.hex
    assert name == tag.name
    assert target == tag.target.hex
    assert tagger == tag.tagger
    assert message == tag.message
    assert name == barerepo[tag.hex].name

def test_modify_tag(barerepo):
    name = 'thetag'
    target = 'af431f20fc541ed6d5afede3e2dc7160f6f01f16'
    message = 'Tag a blob.\n'
    tagger = ('John Doe', 'jdoe@example.com', 12347)

    tag = barerepo[TAG_SHA]
    with pytest.raises(AttributeError): setattr(tag, 'name', name)
    with pytest.raises(AttributeError): setattr(tag, 'target', target)
    with pytest.raises(AttributeError): setattr(tag, 'tagger', tagger)
    with pytest.raises(AttributeError): setattr(tag, 'message', message)

def test_get_object(barerepo):
    repo = barerepo
    tag = repo[TAG_SHA]
    assert repo[tag.target].id == tag.get_object().id
