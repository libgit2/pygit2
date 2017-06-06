# -*- coding: utf-8 -*-
# coding: UTF-8
#
# Copyright 2010-2017 The pygit2 contributors
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
from distutils.command.build_ext import build_ext
from distutils.command.sdist import sdist
from distutils import sysconfig
from distutils import dir_util
from distutils import log
from distutils import spawn
import os
from os import getenv, listdir, pathsep
from os.path import abspath, isfile
from setuptools import setup, Extension, Command
import hashlib
import platform
import shlex
import urllib
import zipfile
from subprocess import Popen, PIPE
import sys
import unittest

# Get cffi major version
try:
    import cffi
except ImportError:
    cffi_major_version = None
else:
    cffi_major_version = cffi.__version_info__[0]

# Import stuff from pygit2/_utils.py without loading the whole pygit2 package
sys.path.insert(0, 'pygit2')
from _build import __version__, get_libgit2_paths, __sha__
if cffi_major_version == 0:
    from _run import ffi, preamble, C_KEYWORDS
    ffi.verify(preamble, **C_KEYWORDS)
del sys.path[0]


libgit2_bin, libgit2_include, libgit2_lib = get_libgit2_paths()

platform_name = platform.system()
shared_ext = '.so'
if 'Windows' in platform_name:
    shared_ext = '.dll'
elif 'Darwin' in platform_name:
    shared_ext = '.dylib'

pygit2_exts = [os.path.join('src', name) for name in sorted(listdir('src'))
               if name.endswith('.c')]


class TestCommand(Command):
    """Command for running unittests without install."""

    user_options = [("args=", None, '''The command args string passed to
                                    unittest framework, such as
                                     --args="-v -f"''')]

    def initialize_options(self):
        self.args = ''

    def finalize_options(self):
        pass

    def run(self):
        self.run_command('build')
        bld = self.distribution.get_command_obj('build')
        # Add build_lib in to sys.path so that unittest can found DLLs and libs
        sys.path = [abspath(bld.build_lib)] + sys.path

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


class sdist_files_from_git(sdist):
    def get_file_list(self):
        popen = Popen(['git', 'ls-files'], stdout=PIPE, stderr=PIPE,
                      universal_newlines=True)
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
    'sdist': sdist_files_from_git,
}


#################
# CMake function
#################
def run_cmd(cmd="cmake", cmd_args=[]):
    """
    Runs CMake to determine configuration for this build
    """
    if spawn.find_executable(cmd) is None:
        log.error("%s is required to build libgit2" % cmd)
        log.error("Please install %s and re-run setup" % cmd)
        sys.exit(-1)

    # construct argument string
    try:
        spawn.spawn([cmd] + cmd_args)
    except spawn.DistutilsExecError:
        log.error("Error while running %s" % cmd)
        log.error("run 'setup.py build --help' for build options"
                  "You may also try editing the settings in "
                  "CMakeLists.txt file and re-running setup")
        sys.exit(-1)


class build_ext_subclass(build_ext):
    def build_extensions(self):
        # download and build libgit2
        fn = 'v%s.zip' % __version__
        url = 'https://github.com/libgit2/libgit2/archive/%s' % fn
        cwd = os.getcwd()
        install_path = os.path.abspath(os.path.join('build', 'libgit2'))
        prefix = os.path.abspath(sysconfig.PREFIX)
        libpath = os.path.join(prefix, 'lib')

        # only build libgit2 once
        if not (os.path.isdir(os.path.join(install_path, 'lib')) and
                os.path.isdir(os.path.join(install_path, 'include'))):

            dir_util.mkpath(self.build_temp)
            os.chdir(self.build_temp)

            # download and save zip file, only if checksum doesn't match
            sha = None
            try:
                sha = hashlib.sha256(open(fn, 'rb').read()).hexdigest()
            except IOError:
                pass
            if sha != __sha__:
                log.warn("Downloading libgit2...")
                urllib.urlretrieve(url, fn)

            with zipfile.ZipFile(fn, "r") as zf:
                log.warn("Extracting libgit2...")
                zf.extractall()

            if shared_ext == ".dll":
                # weird bug with visual studio compiler for python (later
                # versions do not have this problem; pre-2013 compilers on
                # windows do not include stdint.h ... but libgit2 includes the
                # file ...but win32-compat.h doesn't inlucde it correctly?
                win32path = os.path.join('libgit2-' + __version__, 'src',
                                         'win32', 'win32-compat.h')
                newpath = '"../../include/git2/stdint.h"'
                lines = []
                with open(win32path) as f:
                    for line in f:
                        lines.append(line.replace('#include <stdint.h>',
                                                  '#include ' + newpath))
                with open(win32path, 'w') as f:
                    for line in lines:
                        f.write(line)

            dir_util.mkpath('build')
            os.chdir('build')

            cmake_args = [
                '-DCMAKE_INSTALL_PREFIX:PATH=%s' % install_path,
                '-DCMAKE_INSTALL_RPATH:PATH=%s' % libpath,
                '-DCMAKE_INSTALL_NAME_DIR:PATH=%s' % libpath,
                '-DCMAKE_INSTALL_RPATH_USE_LINK_PATH:BOOL=TRUE',
                '-DBUILD_CLAR:BOOL=OFF',
                '../libgit2-%s' % __version__,
            ]

            run_cmd('cmake', cmake_args)
            opts = ''
            if shared_ext != ".dll":
                opts = " -- -j8"
            opts = '--build . --target install' + opts
            run_cmd('cmake', opts.split())

            os.chdir(cwd)
            # post-install: move to same location as _pygit2.so
            dir_util.mkpath(libpath)
            self.copy_tree(libgit2_lib, os.path.abspath(libpath))

        if shared_ext != ".dll":
            # make sure we search our header path first
            self.compiler.compiler_so.insert(1, '-I' + libgit2_include)
        build_ext.build_extensions(self)

# On Windows, we install the git2.dll too.
class BuildWithDLLs(build):
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
        look_dirs = [libgit2_bin] + getenv("PATH", "").split(pathsep)
        target = abspath(self.build_lib)
        for bin in libgit2_dlls:
            for look in look_dirs:
                f = os.path.join(look, bin)
                if isfile(f):
                    ret.append((f, target))
                    break
            else:
                log.warn("Could not find required DLL %r to include", bin)
                log.debug("(looked in %s)", look_dirs)
        return ret

    def run(self):
        build.run(self)
        for s, d in self._get_dlls():
            self.copy_file(s, d)

# On Windows we package up the dlls with the plugin.
if os.name == 'nt':
    cmdclass['build'] = BuildWithDLLs

# always bundle libgit2 shared libraries with pygit2
if os.path.abspath(os.path.join('build', 'libgit2', 'bin')) == libgit2_bin:
    cmdclass['build_ext'] = build_ext_subclass

extra_args = {
    'ext_modules': [
        Extension('_pygit2', pygit2_exts, libraries=['git2'],
                  include_dirs=[libgit2_include],
                  library_dirs=[libgit2_lib]),
        # FFI is added in the build step
    ],
}

if cffi_major_version == 0:
    extra_args['ext_modules'].append(ffi.verifier.get_extension())
else:
    extra_args['cffi_modules'] = ['pygit2/_run.py:ffi']


setup(name='pygit2',
      description='Python bindings for libgit2.',
      keywords='git',
      version=__version__,
      url='http://github.com/libgit2/pygit2',
      classifiers=classifiers,
      license='GPLv2 with linking exception',
      maintainer=u'J. David Ibáñez',
      maintainer_email='jdavid.ibp@gmail.com',
      long_description=long_description,
      packages=['pygit2'],
      package_data={'pygit2': ['decl.h']},
      setup_requires=['cffi'],
      install_requires=['cffi', 'six'],
      zip_safe=False,
      cmdclass=cmdclass,
      **extra_args)
