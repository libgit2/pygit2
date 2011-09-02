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

"""Tests for revision walk."""

from __future__ import absolute_import
from __future__ import unicode_literals
import unittest

from pygit2 import GIT_SORT_TIME, GIT_SORT_REVERSE
from . import utils


__author__ = 'jdavid@itaapy.com (J. David Ibáñez)'


# In the order given by git log
log = [
    '2be5719152d4f82c7302b1c0932d8e5f0a4a0e98',
    '5ebeeebb320790caf276b9fc8b24546d63316533',
    '4ec4389a8068641da2d6578db0419484972284c8',
    '6aaa262e655dd54252e5813c8e5acd7780ed097d',
    'acecd5ea2924a4b900e7e149496e1f4b57976e51']


class WalkerTest(utils.RepoTestCase):

    def test_walk(self):
        walker = self.repo.walk(log[0], GIT_SORT_TIME)
        out = [ x.hex for x in walker ]
        self.assertEqual(out, log)

    def test_reverse(self):
        walker = self.repo.walk(log[0], GIT_SORT_TIME | GIT_SORT_REVERSE)
        out = [ x.hex for x in walker ]
        self.assertEqual(out, list(reversed(log)))

    def test_hide(self):
        walker = self.repo.walk(log[0], GIT_SORT_TIME)
        walker.hide('4ec4389a8068641da2d6578db0419484972284c8')
        self.assertEqual(len(list(walker)), 2)

    def test_reset(self):
        walker = self.repo.walk(log[0], GIT_SORT_TIME)
        walker.reset()
        out = [ x.hex for x in walker ]
        self.assertEqual(out, [])

    def test_push(self):
        walker = self.repo.walk(log[-1], GIT_SORT_TIME)
        out = [ x.hex for x in walker ]
        self.assertEqual(out, log[-1:])
        walker.reset()
        walker.push(log[0])
        out = [ x.hex for x in walker ]
        self.assertEqual(out, log)

    def test_sort(self):
        walker = self.repo.walk(log[0], GIT_SORT_TIME)
        walker.sort(GIT_SORT_TIME | GIT_SORT_REVERSE)
        out = [ x.hex for x in walker ]
        self.assertEqual(out, list(reversed(log)))

if __name__ == '__main__':
    unittest.main()
