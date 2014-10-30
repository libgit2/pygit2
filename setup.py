# -*- coding: utf-8 -*-
# coding: UTF-8
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

"""Setup file for pygit2."""

# Import from the future
from __future__ import print_function

# Import from the Standard Library
import codecs
from distutils.command.build import build
from distutils.command.sdist import sdist
from distutils import log
import os
from setuptools import setup, Extension, Command
import shlex
from subprocess import Popen, PIPE
import sys
import unittest

# Import stuff from pygit2/_utils.py without loading the whole pygit2 package
sys.path.insert(0, 'pygit2')
from _utils import __version__, get_libgit2_paths, get_ffi
del sys.path[0]

# Python 2 support
# See https://github.com/libgit2/pygit2/pull/180 for a discussion about this.
if sys.version_info[0] == 2:
    u = lambda s: unicode(s, 'utf-8')
else:
    u = str


libgit2_bin, libgit2_include, libgit2_lib = get_libgit2_paths()

pygit2_exts = [os.path.join('src', name) for name in os.listdir('src')
               if name.endswith('.c')]


class TestCommand(Command):
    """Command for running unittests without install."""

    user_options = [("args=", None, '''The command args string passed to
                                    unittest framework, such as
                                     --args="-v -f"''')]

    def initialize_options(self):
        self.args = ''
        pass

    def finalize_options(self):
        pass

    def run(self):
        self.run_command('build')
        bld = self.distribution.get_command_obj('build')
        # Add build_lib in to sys.path so that unittest can found DLLs and libs
        sys.path = [os.path.abspath(bld.build_lib)] + sys.path

        test_argv0 = [sys.argv[0] + ' test --args=']
        # For transfering args to unittest, we have to split args by ourself,
        # so that command like:
        #
        #   python setup.py test --args="-v -f"
        #
        # can be executed, and the parameter '-v -f' can be transfering to
        # unittest properly.
        test_argv = test_argv0 + shlex.split(self.args)
        unittest.main(None, defaultTest='test.test_suite', argv=test_argv)

class CFFIBuild(build):
    """Hack to combat the chicken and egg problem that we need cffi
    to add cffi as an extension.
    """
    def finalize_options(self):
        ffi, C = get_ffi()
        self.distribution.ext_modules.append(ffi.verifier.get_extension())
        build.finalize_options(self)


class BuildWithDLLs(CFFIBuild):

    # On Windows, we install the git2.dll too.
    def _get_dlls(self):
        # return a list of (FQ-in-name, relative-out-name) tuples.
        ret = []
        bld_ext = self.distribution.get_command_obj('build_ext')
        compiler_type = bld_ext.compiler.compiler_type
        libgit2_dlls = []
        if compiler_type == 'msvc':
            libgit2_dlls.append('git2.dll')
        elif compiler_type == 'mingw32':
            libgit2_dlls.append('libgit2.dll')
        look_dirs = [libgit2_bin] + os.getenv("PATH", "").split(os.pathsep)
        target = os.path.abspath(self.build_lib)
        for bin in libgit2_dlls:
            for look in look_dirs:
                f = os.path.join(look, bin)
                if os.path.isfile(f):
                    ret.append((f, target))
                    break
            else:
                log.warn("Could not find required DLL %r to include", bin)
                log.debug("(looked in %s)", look_dirs)
        return ret

    def run(self):
        build.run(self)
        if os.name == 'nt':
            # On Windows we package up the dlls with the plugin.
            for s, d in self._get_dlls():
                self.copy_file(s, d)


class sdist_files_from_git(sdist):
    def get_file_list(self):
        popen = Popen(['git', 'ls-files'], stdout=PIPE, stderr=PIPE)
        stdoutdata, stderrdata = popen.communicate()
        if popen.returncode != 0:
            print(stderrdata)
            sys.exit()

        for line in stdoutdata.splitlines():
            # Skip hidden files at the root
            if line[0] == '.':
                continue
            self.filelist.append(line)

        # Ok
        self.filelist.sort()
        self.filelist.remove_duplicates()
        self.write_manifest()

classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Version Control"]


with codecs.open('README.rst', 'r', 'utf-8') as readme:
    long_description = readme.read()


cmdclass = {
    'test': TestCommand,
    'sdist': sdist_files_from_git}

if os.name == 'nt':
    # BuildWithDLLs can copy external DLLs into source directory.
    cmdclass['build'] = BuildWithDLLs
else:
    # Build cffi
    cmdclass['build'] = CFFIBuild


setup(name='pygit2',
      description='Python bindings for libgit2.',
      keywords='git',
      version=__version__,
      url='http://github.com/libgit2/pygit2',
      classifiers=classifiers,
      license='GPLv2',
      maintainer=u('J. David Ibáñez'),
      maintainer_email='jdavid.ibp@gmail.com',
      long_description=long_description,
      packages=['pygit2'],
      package_data={'pygit2': ['decl.h']},
      setup_requires=['cffi'],
      install_requires=['cffi'],
      zip_safe=False,
      ext_modules=[
          Extension('_pygit2', pygit2_exts, libraries=['git2'],
                    include_dirs=[libgit2_include],
                    library_dirs=[libgit2_lib]),
          # FFI is added in the build step
      ],
      cmdclass=cmdclass)
