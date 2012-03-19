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

import os
try:
    from setuptools import setup, Extension, Command
    SETUPTOOLS = True
except ImportError:
    from distutils.core import setup, Extension, Command
    SETUPTOOLS = False

# Use environment variable LIBGIT2 to set your own libgit2 configuration.
libraries = ['git2', 'z', 'crypto']
if os.name == 'nt':
    libraries = ['git2']

libgit2_path = os.getenv("LIBGIT2")
if libgit2_path is None:
    if os.name == 'nt':
        program_files = os.getenv("ProgramFiles")
        libgit2_path = '%s\libgit2' % program_files
    else:
        libgit2_path = '/usr/local'

libgit2_bin = os.path.join(libgit2_path, 'bin')
libgit2_include = os.path.join(libgit2_path, 'include')
libgit2_lib =  os.path.join(libgit2_path, 'lib')

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


with open('README.rst') as readme:
    long_description = readme.read()

setup(name='pygit2',
      description='Python bindings for libgit2.',
      keywords='git',
      version='0.16.1',
      url='http://github.com/libgit2/pygit2',
      classifiers=classifiers,
      license='GPLv2',
      maintainer='J. David Ibáñez',
      maintainer_email='jdavid.ibp@gmail.com',
      long_description=long_description,
      ext_modules = [
          Extension('pygit2', ['pygit2.c'],
                    include_dirs=[libgit2_include],
                    library_dirs=[libgit2_lib],
                    libraries=libraries),
          ],
      **kwargs)
