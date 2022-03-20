# Copyright 2010-2021 The pygit2 contributors
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

# Import setuptools before distutils to avoid user warning
from setuptools import setup, Extension

# Import from the Standard Library
import codecs
from distutils.command.build import build
from distutils.command.sdist import sdist
from distutils import log
import os
from pathlib import Path
from subprocess import Popen, PIPE
import sys

# Import stuff from pygit2/_utils.py without loading the whole pygit2 package
sys.path.insert(0, 'pygit2')
from _build import __version__, get_libgit2_paths
del sys.path[0]


libgit2_bin, libgit2_kw = get_libgit2_paths()


class sdist_files_from_git(sdist):
    def get_file_list(self):
        popen = Popen(['git', 'ls-files'], stdout=PIPE, stderr=PIPE,
                      universal_newlines=True)
        stdoutdata, stderrdata = popen.communicate()
        if popen.returncode != 0:
            print(stderrdata)
            sys.exit()

        def exclude(line):
            for prefix in ['.', 'appveyor.yml', 'docs/', 'misc/']:
                if line.startswith(prefix):
                    return True
            return False

        for line in stdoutdata.splitlines():
            if not exclude(line):
                self.filelist.append(line)

        # Ok
        self.filelist.sort()
        self.filelist.remove_duplicates()
        self.write_manifest()


classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: Implementation :: PyPy",
    "Programming Language :: Python :: Implementation :: CPython",
    "Topic :: Software Development :: Version Control"]

with codecs.open('README.rst', 'r', 'utf-8') as readme:
    long_description = readme.read()

cmdclass = {
    'sdist': sdist_files_from_git,
}


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
        look_dirs = [libgit2_bin] + os.getenv("PATH", "").split(os.pathsep)

        target = Path(self.build_lib).absolute() / 'pygit2'
        for dll in libgit2_dlls:
            for look in look_dirs:
                f = Path(look) / dll
                if f.is_file():
                    ret.append((f, target))
                    break
            else:
                log.warn('"Could not find required DLL {dll} to include')
                log.debug(f'(looked in {look_dirs})')
        return ret

    def run(self):
        build.run(self)
        for s, d in self._get_dlls():
            self.copy_file(s, d)

# On Windows we package up the dlls with the plugin.
if os.name == 'nt':
    cmdclass['build'] = BuildWithDLLs

src = Path('src')
pygit2_exts = [str(path) for path in sorted(src.iterdir()) if path.suffix == '.c']
ext_modules = [
    Extension('pygit2._pygit2', pygit2_exts, **libgit2_kw)
]

with open('requirements.txt') as f:
    install_requires = f.read().splitlines()

setup(
    name='pygit2',
    description='Python bindings for libgit2.',
    keywords='git',
    version=__version__,
    classifiers=classifiers,
    license='GPLv2 with linking exception',
    maintainer='J. David Ibáñez',
    maintainer_email='jdavid.ibp@gmail.com',
    long_description=long_description,
    packages=['pygit2'],
    package_data={'pygit2': ['decl/*.h', '*.pyi']},
    zip_safe=False,
    cmdclass=cmdclass,
    cffi_modules=['pygit2/_run.py:ffi'],
    ext_modules=ext_modules,
    # Requirements
    python_requires='>=3.7',
    setup_requires=['cffi>=1.9.1'],
    install_requires=install_requires,
    # URLs
    url='https://github.com/libgit2/pygit2',
    project_urls={
        'Documentation': 'https://www.pygit2.org/',
        'Changelog': 'https://github.com/libgit2/pygit2/blob/master/CHANGELOG.rst',
        'Funding': 'https://github.com/sponsors/jdavid',
    },
)
