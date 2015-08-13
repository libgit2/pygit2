# -*- coding: UTF-8 -*-
#
# Copyright 2010-2014 The pygit2 contributors
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

from pygit2 import Signature, Oid
from pygit2.repository import Repository


# pypy (in python2 mode) raises TypeError on writing to read-only, so
# we need to check and change the test accordingly
try:
    import __pypy__, sys
    pypy2 =  sys.version_info[0] < 3
except ImportError:
    __pypy__ = None
    pypy2 = False

TAG_SHA = '3d2962987c695a29f1f80b6c3aa4ec046ef44369'


class TagTest(utils.BareRepoTestCase):

    def test_read_tag(self):
        repo = self.repo
        tag = repo[TAG_SHA]
        target = repo[tag.target]
        self.assertTrue(isinstance(tag, pygit2.Tag))
        self.assertEqual(pygit2.GIT_OBJ_TAG, tag.type)
        self.assertEqual(pygit2.GIT_OBJ_COMMIT, target.type)
        self.assertEqual('root', tag.name)
        self.assertEqual('Tagged root commit.\n', tag.message)
        self.assertEqual('Initial test data commit.\n', target.message)
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
        error_type = AttributeError if not pypy2 else TypeError
        self.assertRaises(error_type, setattr, tag, 'name', name)
        self.assertRaises(error_type, setattr, tag, 'target', target)
        self.assertRaises(error_type, setattr, tag, 'tagger', tagger)
        self.assertRaises(error_type, setattr, tag, 'message', message)

    def test_get_object(self):
        repo = self.repo
        tag = repo[TAG_SHA]
        self.assertEqual(repo[tag.target].id, tag.get_object().id)


class MariadbTagTest(utils.MariadbRepositoryTestCase):
    def test_write_read_tag(self):
        repo = Repository(None, 0,
                self.TEST_DB_USER, self.TEST_DB_PASSWD,
                None, self.TEST_DB_DB,
                self.TEST_DB_TABLE_PREFIX,
                self.TEST_DB_REPO_ID,
                odb_partitions=2, refdb_partitions=2)
        try:
            author = Signature('Alice Author', 'alice@authors.tld')
            committer = Signature('Cecil Committer', 'cecil@committers.tld')
            tree = repo.TreeBuilder().write()
            commit_oid = repo.create_commit(
                    'refs/heads/master',  # create the branch
                    author, committer, 'one line commit message\n\ndetails',
                    tree,  # binary string representing the tree object ID
                    []  # parents of the new commit
                )
            self.assertNotEqual(commit_oid, None)

            name = 'thetag'
            target = commit_oid.hex
            message = 'Tag a blob.\n'
            tagger = pygit2.Signature('John Doe', 'jdoe@example.com', 12347, 0)

            target_prefix = target[:10]
            too_short_prefix = target[:3]
            self.assertRaises(ValueError, repo.create_tag, name,
                          too_short_prefix, pygit2.GIT_OBJ_COMMIT, tagger,
                          message)
            tag_oid = repo.create_tag(name, target_prefix,
                    pygit2.GIT_OBJ_COMMIT, tagger, message)
        finally:
            repo.close()

        repo = Repository(None, 0,
                self.TEST_DB_USER, self.TEST_DB_PASSWD,
                None, self.TEST_DB_DB,
                self.TEST_DB_TABLE_PREFIX,
                self.TEST_DB_REPO_ID,
                odb_partitions=2, refdb_partitions=2)
        try:
            tag = repo[tag_oid]

            self.assertEqual(tag_oid.hex, tag.hex)
            self.assertEqual(name, tag.name)
            self.assertEqual(target, tag.target.hex)
            self.assertEqual(message, tag.message)
            self.assertEqual(name, repo[tag.hex].name)

        finally:
            repo.close()

if __name__ == '__main__':
    unittest.main()
