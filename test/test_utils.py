# -*- coding: utf-8 -*-
#
# Copyright 2012 Nico von Geyso
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

"""Tests for utils files."""

from __future__ import absolute_import
from __future__ import unicode_literals
import os
import unittest

from pygit2.utils import tree_insert_node
from . import utils

BLOB_PATH = 'path/to/create'
BLOB_NAME = 'foo.txt'
BLOB_SHA = 'af431f20fc541ed6d5afede3e2dc7160f6f01f16'
BLOB_CONTENT = b'a contents\n'

__author__ = 'Nico.Geyso@FU-Berlin.de (Nico von Geyso)'

class UtilsTest(utils.BareRepoTestCase):
    def test_tree_insert_node_in_root(self):
        root_oid = self.repo.TreeBuilder().write()
        node_oid = self.repo[BLOB_SHA].hex
        oid = tree_insert_node(self.repo, root_oid, node_oid, BLOB_NAME)  
        tree = self.repo[oid]
        self.assertEqual(oid, tree.oid)
        self.assertTrue(BLOB_NAME in tree)

    def _check_path(self, path, tree):
        dirs = path.split('/')
        dirs.reverse()
        while len(dirs) > 0:
            current = dirs.pop()
            self.assertTrue(current in tree)
            tree = tree[current].to_object()

    def test_tree_insert_node_in_subdir(self):
        root_oid = self.repo.TreeBuilder().write()
        node_oid = self.repo[BLOB_SHA].hex

        # insert in root
        root_oid = tree_insert_node(self.repo, root_oid, node_oid, BLOB_NAME)
        tree = self.repo[root_oid]
        self.assertEqual(root_oid, tree.oid)
        self._check_path(BLOB_NAME, tree) 

        # insert in new directory
        path = "%s/%s" % (BLOB_PATH, BLOB_NAME)
        root_oid = tree_insert_node(self.repo, root_oid, node_oid, path)
        tree = self.repo[root_oid]
        self.assertEqual(root_oid, tree.oid)
        self._check_path(path, tree) 

        # insert in existing dirs
        path = "%s/new/subdir/%s" % (BLOB_PATH, BLOB_NAME)
        root_oid = tree_insert_node(self.repo, root_oid, node_oid, path)
        tree = self.repo[root_oid]
        self.assertEqual(root_oid, tree.oid)
        self._check_path(path, tree) 


if __name__ == '__main__':
    unittest.main()
