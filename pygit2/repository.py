# -*- coding: utf-8 -*-
#
# Copyright 2010-2013 The pygit2 contributors
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
from _pygit2 import Repository as _Repository


class Repository(_Repository):

    #
    # Mapping interface
    #
    def get(self, key, default=None):
        value = self.git_object_lookup_prefix(key)
        return value if (value is not None) else default


    def __getitem__(self, key):
        value = self.git_object_lookup_prefix(key)
        if value is None:
            raise KeyError(key)
        return value


    def __contains__(self, key):
        return self.git_object_lookup_prefix(key) is not None


    #
    # References
    #
    def create_reference(self, name, target, force=False, symbolic=False):
        """
        Create a new reference "name" which points to a object or another
        reference.

        Keyword arguments:

        force
            If True references will be overridden, otherwise (the default) an
            exception is raised.

        symbolic
            If True a symbolic reference will be created, then source has to
            be a valid existing reference name; if False (the default) a
            normal reference will be created, then source must has to be a
            valid SHA hash.

        Examples::

            repo.create_reference('refs/heads/foo', repo.head.hex)
            repo.create_reference('refs/tags/foo', 'refs/heads/master',
                                  symbolic=True)
        """
        if symbolic:
            return self.git_reference_symbolic_create(name, target, force)

        return self.git_reference_create(name, target, force)
