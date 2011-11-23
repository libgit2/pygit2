# -*- coding: UTF-8 -*-
#
# Copyright 2010 Google, Inc.
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

from __future__ import absolute_import
from __future__ import unicode_literals
import unittest

import pygit2
from . import utils


__author__ = 'dborowitz@google.com (Dave Borowitz)'

TAG_SHA = '3d2962987c695a29f1f80b6c3aa4ec046ef44369'


class TagTest(utils.BareRepoTestCase):

    def test_read_tag(self):
        tag = self.repo[TAG_SHA]
        self.assertTrue(isinstance(tag, pygit2.Tag))
        self.assertEqual(pygit2.GIT_OBJ_TAG, tag.type)
        self.assertEqual(pygit2.GIT_OBJ_COMMIT, tag.target.type)
        self.assertEqual('root', tag.name)
        self.assertEqual('Tagged root commit.\n', tag.message)
        self.assertEqual('Initial test data commit.\n', tag.target.message)
        self.assertEqualSignature(
            tag.tagger,
            pygit2.Signature('Dave Borowitz', 'dborowitz@google.com',
                             1288724692, -420))

    def test_new_tag(self):
        name = 'thetag'
        target = 'af431f20fc541ed6d5afede3e2dc7160f6f01f16'
        message = 'Tag a blob.\n'
        tagger = pygit2.Signature('John Doe', 'jdoe@example.com', 12347, 0)

        target_prefix = target[:5]
        too_short_prefix = target[:3]
        self.assertRaises(ValueError, self.repo.create_tag, name, 
                          too_short_prefix, pygit2.GIT_OBJ_BLOB, tagger,
                          message)
        sha = self.repo.create_tag(name, target_prefix, pygit2.GIT_OBJ_BLOB,
                                   tagger, message)
        tag = self.repo[sha]

        self.assertEqual('3ee44658fd11660e828dfc96b9b5c5f38d5b49bb', tag.hex)
        self.assertEqual(name, tag.name)
        self.assertEqual(target, tag.target.hex)
        self.assertEqualSignature(tagger, tag.tagger)
        self.assertEqual(message, tag.message)
        self.assertEqual(name, self.repo[tag.hex].name)

    def test_modify_tag(self):
        name = 'thetag'
        target = 'af431f20fc541ed6d5afede3e2dc7160f6f01f16'
        message = 'Tag a blob.\n'
        tagger = ('John Doe', 'jdoe@example.com', 12347)

        tag = self.repo[TAG_SHA]
        self.assertRaises(AttributeError, setattr, tag, 'name', name)
        self.assertRaises(AttributeError, setattr, tag, 'target', target)
        self.assertRaises(AttributeError, setattr, tag, 'tagger', tagger)
        self.assertRaises(AttributeError, setattr, tag, 'message', message)


if __name__ == '__main__':
    unittest.main()
