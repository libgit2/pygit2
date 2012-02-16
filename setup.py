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
import sys
from distutils.core import setup, Extension, Command
from distutils.command.build import build

# Use environment variable LIBGIT2 to set your own libgit2 configuration.
libraries = ['git2', 'z', 'crypto']
libgit2_dlls = []
if os.name == 'nt':
    libgit2_dlls = ['git2.dll']
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

def we_are_frozen():
    # All of the modules are built-in to the interpreter, e.g., by py2exe
    return hasattr(sys, "frozen")

def module_path():
    if we_are_frozen():
        return os.path.dirname(sys.executable)
    return os.path.dirname(__file__)

pygit2_base = os.path.join(module_path(), 'pygit2')
try:
    os.makedirs(pygit2_base)
except OSError:
    pass

# On Windows, we install the git2.dll too.
def _get_dlls():
    # return a list of of (FQ-in-name, relative-out-name) tuples.
    ret = []
    look_dirs = [libgit2_bin] + os.environ.get("PATH","").split(os.pathsep)
    for bin in ['git2.dll']:
        for look in look_dirs:
            f = os.path.join(look, bin)
            if os.path.isfile(f):
                ret.append((f, bin))
                break
        else:
            log.warn("Could not find required DLL %r to include", bin)
            log.debug("(looked in %s)", look_dirs)
    return ret

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


class build_with_dlls(build):

    def run(self):
        build.run(self)
        # the apr binaries.
        if os.name == 'nt':
            # On Windows we package up the apr dlls with the plugin.
            for s, d in _get_dlls():
                self.copy_file(s, os.path.join(pygit2_base, d))

classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Version Control"]


with open('README.rst') as readme:
    long_description = readme.read()

setup(name='pygit2',
      description='Python bindings for libgit2.',
      keywords='git',
      version='0.16.0',
      url='http://github.com/libgit2/pygit2',
      classifiers=classifiers,
      license='GPLv2',
      maintainer='J. David Ibáñez',
      maintainer_email='jdavid.ibp@gmail.com',
      long_description=long_description,
      ext_modules=[
          Extension('pygit2', ['pygit2.c'],
                    include_dirs=[libgit2_include],
                    library_dirs=[libgit2_lib],
                    libraries=libraries),
          ],
      packages=[''],
      package_dir={'': 'pygit2'},
      package_data={'': libgit2_dlls},
      cmdclass={'test': TestCommand, 'build': build_with_dlls})
