# -*- coding: utf-8 -*-
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

# Import from the future
from __future__ import absolute_import

# Low level API
import _pygit2
from _pygit2 import *

# High level API
from .repository import Repository
from .version import __version__
from .settings import Settings
from .credentials import *

def init_repository(path, bare=False, **kw):
    """
    Creates a new Git repository in the given *path*.

    If *bare* is True the repository will be bare, i.e. it will not have a
    working copy.

    Keyword options:

    **shared** allows setting the permissions on the repository. Accepted
    values are 'false', 'uname', 'true', 'group', 'all', 'everybody', 'world',
    or an octal string, e.g. '0660'.

    **template_dir** A directory of templates to use instead of the default.
    It is not currently implemented in libgit, so this has no effect yet.

    **working_dir** The directory to use as the working tree. If this is
    specified, the git repository at **path** will have its working directory
    set to this value.

    **initial_head** if specified, points HEAD at this reference. If it begins
    with 'refs/', the value will be used verbatim. Otherwise 'refs/heads/' will
    be prefixed to the value.

    **origin_url** if specified, an 'origin' remote will be added that points
    at this URL.
    """

    if 'working_dir' in kw:  # Overrides the relative path behaviour in libgit
        from os.path import abspath
        kw['working_dir'] = str(abspath(kw['working_dir']))
    
    _pygit2.init_repository(path, bare, **kw)
    return Repository(path)


def clone_repository(
        url, path, bare=False, ignore_cert_errors=False,
        remote_name="origin", checkout_branch=None, credentials=None):
    """Clones a new Git repository from *url* in the given *path*.

    Returns a Repository class pointing to the newly cloned repository.

    :param str url: URL of the repository to clone

    :param str path: Local path to clone into

    :param bool bare: Whether the local repository should be bare

    :param str remote_name: Name to give the remote at *url*.

    :param str checkout_branch: Branch to checkout after the
     clone. The default is to use the remote's default branch.

    :param callable credentials: authentication to use if the remote
     requires it

    :rtype: Repository

    """

    _pygit2.clone_repository(
        url, path, bare, ignore_cert_errors, remote_name, checkout_branch, credentials)
    return Repository(path)

settings = Settings()
