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
from pygit2 import GIT_REF_OID



LAST_COMMIT = '2be5719152d4f82c7302b1c0932d8e5f0a4a0e98'



class ReferencesTest(utils.RepoTestCase):

    def test_list_all_references(self):
        self.assertEqual(self.repo.listall_references(),
                         ('refs/heads/i18n', 'refs/heads/master'))


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


    def test_reference_get_type(self):
        reference = self.repo.lookup_reference('refs/heads/master')
        self.assertEqual(reference.type, GIT_REF_OID)


    def test_get_target(self):
        # XXX We must have a symbolic reference to make this test
        pass


    def test_reference_resolve(self):
        # XXX We must have a symbolic reference to make a better test
        reference = self.repo.lookup_reference('refs/heads/master')
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



if __name__ == '__main__':
    unittest.main()
