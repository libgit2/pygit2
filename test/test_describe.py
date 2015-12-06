# -*- coding: UTF-8 -*-
#
# Copyright 2010-2015 The pygit2 contributors
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

from __future__ import absolute_import
from __future__ import unicode_literals
import unittest

from pygit2 import GIT_DESCRIBE_DEFAULT, GIT_DESCRIBE_TAGS, GIT_DESCRIBE_ALL
import pygit2
from . import utils


def add_tag(repo, name, target):
    message = 'Example tag.\n'
    tagger = pygit2.Signature('John Doe', 'jdoe@example.com', 12347, 0)

    sha = repo.create_tag(name, target, pygit2.GIT_OBJ_COMMIT, tagger, message)
    return sha


class DescribeTest(utils.RepoTestCase):

    def test_describe(self):
        add_tag(self.repo, 'thetag', '4ec4389a8068641da2d6578db0419484972284c8')
        self.assertEqual('thetag-2-g2be5719', self.repo.describe())

    def test_describe_without_ref(self):
        self.assertRaises(pygit2.GitError, self.repo.describe)

    def test_describe_default_oid(self):
        self.assertEqual('2be5719', self.repo.describe(show_commit_oid_as_fallback=True))

    def test_describe_strategies(self):
        self.assertEqual('heads/master', self.repo.describe(describe_strategy=GIT_DESCRIBE_ALL))

        self.repo.create_reference('refs/tags/thetag', '4ec4389a8068641da2d6578db0419484972284c8')
        self.assertRaises(KeyError, self.repo.describe)
        self.assertEqual('thetag-2-g2be5719', self.repo.describe(describe_strategy=GIT_DESCRIBE_TAGS))

    def test_describe_pattern(self):
        add_tag(self.repo, 'private/tag1', '5ebeeebb320790caf276b9fc8b24546d63316533')
        add_tag(self.repo, 'public/tag2', '4ec4389a8068641da2d6578db0419484972284c8')

        self.assertEqual('public/tag2-2-g2be5719', self.repo.describe(pattern='public/*'))

    def test_describe_committish(self):
        add_tag(self.repo, 'thetag', 'acecd5ea2924a4b900e7e149496e1f4b57976e51')
        self.assertEqual('thetag-4-g2be5719', self.repo.describe(committish='HEAD'))
        self.assertEqual('thetag-1-g5ebeeeb', self.repo.describe(committish='HEAD^'))

        self.assertEqual('thetag-4-g2be5719', self.repo.describe(committish=self.repo.head))

        self.assertEqual('thetag-1-g6aaa262', self.repo.describe(committish='6aaa262e655dd54252e5813c8e5acd7780ed097d'))
        self.assertEqual('thetag-1-g6aaa262', self.repo.describe(committish='6aaa262'))

    def test_describe_follows_first_branch_only(self):
        add_tag(self.repo, 'thetag', '4ec4389a8068641da2d6578db0419484972284c8')
        self.assertRaises(KeyError, self.repo.describe, only_follow_first_parent=True)

    def test_describe_abbreviated_size(self):
        add_tag(self.repo, 'thetag', '4ec4389a8068641da2d6578db0419484972284c8')
        self.assertEqual('thetag-2-g2be5719152d4f82c', self.repo.describe(abbreviated_size=16))
        self.assertEqual('thetag', self.repo.describe(abbreviated_size=0))

    def test_describe_long_format(self):
        add_tag(self.repo, 'thetag', '2be5719152d4f82c7302b1c0932d8e5f0a4a0e98')
        self.assertEqual('thetag-0-g2be5719', self.repo.describe(always_use_long_format=True))


class DescribeDirtyWorkdirTest(utils.DirtyRepoTestCase):

    def setUp(self):
        super(utils.DirtyRepoTestCase, self).setUp()
        add_tag(self.repo, 'thetag', 'a763aa560953e7cfb87ccbc2f536d665aa4dff22')

    def test_describe(self):
        self.assertEqual('thetag', self.repo.describe())

    def test_describe_with_dirty_suffix(self):
        self.assertEqual('thetag-dirty', self.repo.describe(dirty_suffix='-dirty'))
