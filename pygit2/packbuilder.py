# Copyright 2010-2020 The pygit2 contributors
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


# Import from pygit2
from ._pygit2 import PackBuilder as _PackBuilder
from .errors import check_error
from .ffi import ffi, C
from .utils import to_bytes


class PackBuilder(_PackBuilder):

    def __init__(self, *args, **kwargs):
        self.repo = args[0]
        super().__init__(args[0])
        packbuilder_cptr = ffi.new('git_packbuilder **')
        ffi.buffer(packbuilder_cptr)[:] = self._pointer[:]
        self._packbuilder = packbuilder_cptr[0]

    @staticmethod
    def convert_object_to_oid(git_object):
        oid = ffi.new('git_oid *')
        ffi.buffer(oid)[:] = git_object.raw[:]
        return oid

    def add(self, git_object):
        oid = self.convert_object_to_oid(git_object)
        err = C.git_packbuilder_insert(self._packbuilder, oid, ffi.NULL)
        check_error(err)

    def add_recursive(self, git_object):
        oid = self.convert_object_to_oid(git_object)
        err = C.git_packbuilder_insert_recur(self._packbuilder, oid, ffi.NULL)
        check_error(err)

    def object_count(self):
        return C.git_packbuilder_object_count(self._packbuilder)

    def set_max_threads(self, n_threads):
        return C.git_packbuilder_set_threads(self._packbuilder, n_threads)

    def write(self, path):
        err = C.git_packbuilder_write(self._packbuilder, to_bytes(path), 0, ffi.NULL, ffi.NULL)
        check_error(err)

    @property
    def written_objects_count(self):
        return C.git_packbuilder_written(self._packbuilder)

    @classmethod
    def _from_c(cls, ptr, repo):
        cptr = ffi.new('git_packbuilder **')
        cptr[0] = ptr
        packbuilder = cls.__new__(cls)
        packbuilder.repo = repo
        super(cls, packbuilder)._from_c(bytes(ffi.buffer(cptr)[:]), repo)
        return packbuilder
