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
from _pygit2 import *

# High level API
from .config import Config
from .credentials import *
from .errors import check_error
from .ffi import ffi, C
from .index import Index, IndexEntry
from .remote import Remote, get_credentials
from .repository import Repository
from .settings import Settings
from .utils import to_bytes
from .version import __version__


def init_repository(path, bare=False,
                    flags=C.GIT_REPOSITORY_INIT_MKPATH,
                    mode=0,
                    workdir_path=None,
                    description=None,
                    template_path=None,
                    initial_head=None,
                    origin_url=None):
    """
    Creates a new Git repository in the given *path*.

    If *bare* is True the repository will be bare, i.e. it will not have a
    working copy.

    The *flags* may be a combination of:

    - GIT_REPOSITORY_INIT_BARE (overriden by the *bare* parameter)
    - GIT_REPOSITORY_INIT_NO_REINIT
    - GIT_REPOSITORY_INIT_NO_DOTGIT_DIR
    - GIT_REPOSITORY_INIT_MKDIR
    - GIT_REPOSITORY_INIT_MKPATH (set by default)
    - GIT_REPOSITORY_INIT_EXTERNAL_TEMPLATE

    The *mode* parameter may be any of GIT_REPOSITORY_SHARED_UMASK (default),
    GIT_REPOSITORY_SHARED_GROUP or GIT_REPOSITORY_INIT_SHARED_ALL, or a custom
    value.

    The *workdir_path*, *description*, *template_path*, *initial_head* and
    *origin_url* are all strings.

    See libgit2's documentation on git_repository_init_ext for further details.
    """
    # Pre-process input parameters
    if bare:
        flags |= C.GIT_REPOSITORY_INIT_BARE

    # Options
    options = ffi.new('git_repository_init_options *')
    options.version = 1
    options.flags = flags
    options.mode = mode
    options.workdir_path = to_bytes(workdir_path)
    options.description = to_bytes(description)
    options.template_path = to_bytes(template_path)
    options.initial_head = to_bytes(initial_head)
    options.origin_url = to_bytes(origin_url)

    # Call
    crepository = ffi.new('git_repository **')
    err = C.git_repository_init_ext(crepository, to_bytes(path), options)
    check_error(err)

    # Ok
    return Repository(path)


@ffi.callback('int (*credentials)(git_cred **cred, const char *url,'
              'const char *username_from_url, unsigned int allowed_types,'
              'void *data)')
def _credentials_cb(cred_out, url, username_from_url, allowed, data):
    d = ffi.from_handle(data)

    try:
        ccred = get_credentials(d['callback'], url, username_from_url, allowed)
        cred_out[0] = ccred[0]
    except Exception as e:
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

    remote_name_ref = ffi.new('char []', to_bytes(remote_name))
    opts.remote_name = remote_name_ref

    opts.version = 1
    opts.ignore_cert_errors = ignore_cert_errors
    opts.bare = bare
    opts.remote_callbacks.version = 1
    opts.checkout_opts.version = 1
    if credentials:
        opts.remote_callbacks.credentials = _credentials_cb
        opts.remote_callbacks.payload = d_handle

    err = C.git_clone(crepo, to_bytes(url), to_bytes(path), opts)
    C.git_repository_free(crepo[0])

    if 'exception' in d:
        raise d['exception']

    check_error(err)

    return Repository(path)


def clone_into(repo, remote, branch=None):
    """Clone into an empty repository from the specified remote

    :param Repository repo: The empty repository into which to clone

    :param Remote remote: The remote from which to clone

    :param str branch: Branch to checkout after the clone. Pass None
     to use the remotes's default branch.

    This allows you specify arbitrary repository and remote configurations
    before performing the clone step itself. E.g. you can replicate git-clone's
    '--mirror' option by setting a refspec of '+refs/*:refs/*', 'core.mirror'
    to true and calling this function.
    """

    err = C.git_clone_into(repo._repo, remote._remote, ffi.NULL,
                           to_bytes(branch), ffi.NULL)

    if remote._stored_exception:
        raise remote._stored_exception

    check_error(err)

settings = Settings()
