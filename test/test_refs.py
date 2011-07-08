#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2011 Itaapy
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

"""Tests for reference objects."""


__author__ = 'david.versmisse@itaapy.com (David Versmisse)'

import unittest
import utils
from pygit2 import GIT_REF_OID, GIT_REF_SYMBOLIC



LAST_COMMIT = '2be5719152d4f82c7302b1c0932d8e5f0a4a0e98'



class ReferencesTest(utils.RepoTestCase):

    def test_list_all_references(self):
        repo = self.repo

        # Without argument
        self.assertEqual(sorted(repo.listall_references()),
                         ['refs/heads/i18n', 'refs/heads/master'])

        # We add a symbolic reference
        reference = repo.create_symbolic_reference('refs/tags/version1',
                                                   'refs/heads/master')
        self.assertEqual(sorted(repo.listall_references()),
                         ['refs/heads/i18n', 'refs/heads/master',
                          'refs/tags/version1'])

        # Now we list only the symbolic references
        self.assertEqual(repo.listall_references(GIT_REF_SYMBOLIC),
                         ('refs/tags/version1', ))


    def test_lookup_reference(self):
        repo = self.repo

        # Raise KeyError ?
        self.assertRaises(KeyError, repo.lookup_reference, 'foo')

        # Test a lookup
        reference = repo.lookup_reference('refs/heads/master')
        self.assertEqual(reference.name, 'refs/heads/master')


    def test_reference_get_sha(self):
        reference = self.repo.lookup_reference('refs/heads/master')
        self.assertEqual(reference.sha, LAST_COMMIT)


    def test_reference_set_sha(self):
        NEW_COMMIT = '5ebeeebb320790caf276b9fc8b24546d63316533'
        reference = self.repo.lookup_reference('refs/heads/master')
        reference.sha = NEW_COMMIT
        self.assertEqual(reference.sha, NEW_COMMIT)


    def test_reference_get_type(self):
        reference = self.repo.lookup_reference('refs/heads/master')
        self.assertEqual(reference.type, GIT_REF_OID)


    def test_get_target(self):
        reference = self.repo.lookup_reference('HEAD')
        self.assertEqual(reference.target, 'refs/heads/master')


    def test_set_target(self):
        reference = self.repo.lookup_reference('HEAD')
        self.assertEqual(reference.target, 'refs/heads/master')
        reference.target = 'refs/heads/i18n'
        self.assertEqual(reference.target, 'refs/heads/i18n')


    def test_delete(self):
        repo = self.repo

        # We add a tag as a new reference that points to "origin/master"
        reference = repo.create_reference('refs/tags/version1', LAST_COMMIT)
        self.assertTrue('refs/tags/version1' in repo.listall_references())

        # And we delete it
        reference.delete()
        self.assertFalse('refs/tags/version1' in repo.listall_references())


    def test_rename(self):
        # We add a tag as a new reference that points to "origin/master"
        reference = self.repo.create_reference('refs/tags/version1',
                                               LAST_COMMIT)
        self.assertEqual(reference.name, 'refs/tags/version1')
        reference.rename('refs/tags/version2')
        self.assertEqual(reference.name, 'refs/tags/version2')


    def test_reference_resolve(self):
        reference = self.repo.lookup_reference('HEAD')
        self.assertEqual(reference.type, GIT_REF_SYMBOLIC)
        reference = reference.resolve()
        self.assertEqual(reference.type, GIT_REF_OID)
        self.assertEqual(reference.sha, LAST_COMMIT)


    def test_create_reference(self):
        # We add a tag as a new reference that points to "origin/master"
        reference = self.repo.create_reference('refs/tags/version1',
                                               LAST_COMMIT)
        refs = self.repo.listall_references()
        self.assertTrue('refs/tags/version1' in refs)
        reference = self.repo.lookup_reference('refs/tags/version1')
        self.assertEqual(reference.sha, LAST_COMMIT)


    def test_create_symbolic_reference(self):
        # We add a tag as a new symbolic reference that always points to
        # "refs/heads/master"
        reference = self.repo.create_symbolic_reference('refs/tags/beta',
                                                        'refs/heads/master')
        self.assertEqual(reference.type, GIT_REF_SYMBOLIC)
        self.assertEqual(reference.target, 'refs/heads/master')


    def test_packall_references(self):
        self.repo.packall_references()


if __name__ == '__main__':
    unittest.main()
