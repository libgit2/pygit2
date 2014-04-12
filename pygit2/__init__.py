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
from .remote import Remote, get_credentials
from .errors import check_error
from .ffi import ffi, C, to_str

def init_repository(path, bare=False):
    """
    Creates a new Git repository in the given *path*.

    If *bare* is True the repository will be bare, i.e. it will not have a
    working copy.
    """
    _pygit2.init_repository(path, bare)
    return Repository(path)


@ffi.callback('int (*credentials)(git_cred **cred, const char *url, const char *username_from_url, unsigned int allowed_types,	void *data)')
def _credentials_cb(cred_out, url, username_from_url, allowed, data):
    d = ffi.from_handle(data)

    try:
        ccred = get_credentials(d['callback'], url, username_from_url, allowed)
        cred_out[0] = ccred[0]
    except Exception, e:
        d['exception'] = e
        return C.GIT_EUSER

    return 0

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

    opts = ffi.new('git_clone_options *')
    crepo = ffi.new('git_repository **')

    branch = checkout_branch or None

    # Data, let's use a dict as we don't really want much more
    d = {}
    d['callback'] = credentials
    d_handle = ffi.new_handle(d)

    # We need to keep the ref alive ourselves
    checkout_branch_ref = None
    if branch:
        checkout_branch_ref = ffi.new('char []', branch)
        opts.checkout_branch = checkout_branch_ref

    remote_name_ref = ffi.new('char []', to_str(remote_name))
    opts.remote_name = remote_name_ref

    opts.version = 1
    opts.ignore_cert_errors = ignore_cert_errors
    opts.bare = bare
    opts.remote_callbacks.version = 1
    opts.checkout_opts.version = 1
    if credentials:
        opts.remote_callbacks.credentials = _credentials_cb
        opts.remote_callbacks.payload = d_handle

    err = C.git_clone(crepo, to_str(url), to_str(path), opts)
    C.git_repository_free(crepo[0])

    if 'exception' in d:
        raise d['exception']

    check_error(err)

    return Repository(path)

settings = Settings()
