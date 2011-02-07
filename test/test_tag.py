#!/usr/bin/env python
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

__author__ = 'dborowitz@google.com (Dave Borowitz)'

import unittest

import pygit2
import utils

TAG_SHA = '3d2962987c695a29f1f80b6c3aa4ec046ef44369'


class TagTest(utils.BareRepoTestCase):

    def test_read_tag(self):
        tag = self.repo[TAG_SHA]
        self.assertTrue(isinstance(tag, pygit2.Tag))
        self.assertEqual(pygit2.GIT_OBJ_TAG, tag.type)
        self.assertEqual(pygit2.GIT_OBJ_COMMIT, tag.target_type)
        self.assertEqual('root', tag.name)
        self.assertEqual(('Dave Borowitz', 'dborowitz@google.com', 1288724692),
                         tag.tagger)
        self.assertEqual('Tagged root commit.\n', tag.message)

        commit = tag.target
        del tag
        self.assertEqual('Initial test data commit.', commit.message_short)

    def test_new_tag(self):
        name = 'thetag'
        message = 'Tag a blob.\n'
        tagger = ('John Doe', 'jdoe@example.com', 12347)

        tag = pygit2.Tag(self.repo)
        self.assertEqual(None, tag.sha)
        self.assertEqual(None, tag.name)
        self.assertEqual(None, tag.tagger)
        self.assertEqual(None, tag.message)
        self.assertEqual(None, tag.target)

        tag.name = name
        tag.tagger = tagger
        tag.message = message
        target = self.repo['af431f20fc541ed6d5afede3e2dc7160f6f01f16']
        target_sha = target.sha
        tag.target = target
        del target
        self.assertEqual(name, tag.name)
        self.assertEqual(tagger, tag.tagger)
        self.assertEqual(target_sha, tag.target.sha)

        tag.write()
        self.assertEqual(name, self.repo[tag.sha].name)

    def test_modify_tag(self):
        message = 'Different message.\n'
        tag = self.repo[TAG_SHA]
        old_sha = tag.sha
        self.assertNotEqual(message, tag.message)
        tag.message = message
        self.assertEqual(message, tag.message)
        tag.write()
        self.assertNotEqual(old_sha, tag.sha)
        self.assertEqual(tag.sha, self.repo[tag.sha].sha)


if __name__ == '__main__':
  unittest.main()
