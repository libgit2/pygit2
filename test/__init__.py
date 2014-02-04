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

"""Pygit2 test definitions.

These tests are run automatically with 'setup.py test', but can also be run
manually.
"""

from os import listdir
from os.path import dirname
import sys
import unittest


def test_suite():
    # Sometimes importing pygit2 fails, we try this first to get an
    # informative traceback.
    import pygit2

    # Build the list of modules
    modules = []
    for name in listdir(dirname(__file__)):
        if name.startswith('test_') and name.endswith('.py'):
            module = 'test.%s' % name[:-3]
            # Check the module imports correctly, have a nice error otherwise
            __import__(module)
            modules.append(module)

    # Go
    return unittest.defaultTestLoader.loadTestsFromNames(modules)


def main():
    unittest.main(module=__name__, defaultTest='test_suite', argv=sys.argv[:1])


if __name__ == '__main__':
    main()
