# -*- coding: UTF-8 -*-
#
# Copyright 2010 Google, Inc.
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

"""Setup file for pygit2."""

try:
    from setuptools import setup, Extension, Command
    SETUPTOOLS = True
except ImportError:
    from distutils.core import setup, Extension, Command
    SETUPTOOLS = False


# Replace with your libgit2 configuration.
include_dirs = ['/usr/local/include']
library_dirs = ['/usr/local/lib']
libraries = ['git2', 'z', 'crypto']


class TestCommand(Command):
    """Command for running pygit2 tests."""

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        self.run_command('build')
        import test
        test.main()


kwargs = {}
if SETUPTOOLS:
    kwargs = {'test_suite': 'test.test_suite'}
else:
    kwargs = {'cmdclass': {'test': TestCommand}}


classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Version Control"]


setup(name='pygit2',
      description='Python bindings for libgit2.',
      keywords='git',
      version='0.16.0',
      url='http://github.com/libgit2/pygit2',
      classifiers=classifiers,
      license='GPLv2',
      maintainer='J. David Ibáñez',
      maintainer_email='jdavid.ibp@gmail.com',
      long_description="""
      Bindings for libgit2, a linkable C library for the Git version-control
      system.
      """,
      ext_modules = [
          Extension('pygit2', ['pygit2.c'],
                    include_dirs=include_dirs,
                    library_dirs=library_dirs,
                    libraries=libraries),
          ],
      **kwargs
      )
