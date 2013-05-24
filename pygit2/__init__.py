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

# Import from the future
from __future__ import absolute_import

# Low level API
import _pygit2
from _pygit2 import *

# High level API
from .repository import Repository
from .version import __version__


def init_repository(path, bare=False):
    """
    Creates a new Git repository in the given *path*.

    If *bare* is True the repository will be bare, i.e. it will not have a
    working copy.
    """
    _pygit2.init_repository(path, bare)
    return Repository(path)


def clone_repository(
        url, path, bare=False, remote_name="origin",
        push_url=None, fetch_spec=None,
        push_spec=None, checkout_branch=None):
    """
    Clones a new Git repository from *url* in the given *path*.

    **bare** indicates whether a bare git repository should be created.

    **remote_name** is the name given to the "origin" remote.
    The default is "origin".

    **push_url** is a URL to be used for pushing.
    None means use the *url* parameter.

    **fetch_spec** defines the the default fetch spec.
    None results in the same behavior as *GIT_REMOTE_DEFAULT_FETCH*.

    **push_spec** is the fetch specification to be used for pushing.
    None means use the same spec as for *fetch_spec*.

    **checkout_branch** gives the name of the branch to checkout.
    None means use the remote's *HEAD*.

    Returns a Repository class pointing to the newly cloned repository.

    If you wish to use the repo, you need to do a checkout for one of
    the available branches, like this:

        >>> repo = repo.clone_repository("url", "path")
        >>> repo.checkout(branch)  # i.e.: refs/heads/master

    """

    _pygit2.clone_repository(
        url, path, bare, remote_name, push_url,
        fetch_spec, push_spec, checkout_branch)
    return Repository(path)
