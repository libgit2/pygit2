# Copyright 2010-2024 The pygit2 contributors
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

# Standard Library
import functools
from os import PathLike
import typing

# Low level API
from ._pygit2 import *
from ._pygit2 import _cache_enums

# High level API
from . import enums
from ._build import __version__
from .blame import Blame, BlameHunk
from .blob import BlobIO
from .callbacks import Payload, RemoteCallbacks, CheckoutCallbacks, StashApplyCallbacks
from .callbacks import git_clone_options, git_fetch_options, get_credentials
from .config import Config
from .credentials import *
from .errors import check_error, Passthrough
from .ffi import ffi, C
from .filter import Filter
from .index import Index, IndexEntry
from .legacyenums import *
from .packbuilder import PackBuilder
from .remotes import Remote
from .repository import Repository
from .settings import Settings
from .submodules import Submodule
from .utils import to_bytes, to_str


# Features
features = enums.Feature(C.git_libgit2_features())

# libgit version tuple
LIBGIT2_VER = (LIBGIT2_VER_MAJOR, LIBGIT2_VER_MINOR, LIBGIT2_VER_REVISION)

# Let _pygit2 cache references to Python enum types.
# This is separate from PyInit__pygit2() to avoid a circular import.
_cache_enums()


def init_repository(
    path: typing.Union[str, bytes, PathLike, None],
    bare: bool = False,
    flags: enums.RepositoryInitFlag = enums.RepositoryInitFlag.MKPATH,
    mode: typing.Union[
        int, enums.RepositoryInitMode
    ] = enums.RepositoryInitMode.SHARED_UMASK,
    workdir_path: typing.Optional[str] = None,
    description: typing.Optional[str] = None,
    template_path: typing.Optional[str] = None,
    initial_head: typing.Optional[str] = None,
    origin_url: typing.Optional[str] = None,
) -> Repository:
    """
    Creates a new Git repository in the given *path*.

    If *bare* is True the repository will be bare, i.e. it will not have a
    working copy.

    The *flags* may be a combination of enums.RepositoryInitFlag constants:

    - BARE (overriden by the *bare* parameter)
    - NO_REINIT
    - NO_DOTGIT_DIR
    - MKDIR
    - MKPATH (set by default)
    - EXTERNAL_TEMPLATE

    The *mode* parameter may be any of the predefined modes in
    enums.RepositoryInitMode (SHARED_UMASK being the default), or a custom int.

    The *workdir_path*, *description*, *template_path*, *initial_head* and
    *origin_url* are all strings.

    See libgit2's documentation on git_repository_init_ext for further details.
    """
    # Pre-process input parameters
    if path is None:
        raise TypeError('Expected string type for path, found None.')

    if bare:
        flags |= enums.RepositoryInitFlag.BARE

    # Options
    options = ffi.new('git_repository_init_options *')
    C.git_repository_init_options_init(options, C.GIT_REPOSITORY_INIT_OPTIONS_VERSION)
    options.flags = int(flags)
    options.mode = mode

    if workdir_path:
        workdir_path_ref = ffi.new('char []', to_bytes(workdir_path))
        options.workdir_path = workdir_path_ref

    if description:
        description_ref = ffi.new('char []', to_bytes(description))
        options.description = description_ref

    if template_path:
        template_path_ref = ffi.new('char []', to_bytes(template_path))
        options.template_path = template_path_ref

    if initial_head:
        initial_head_ref = ffi.new('char []', to_bytes(initial_head))
        options.initial_head = initial_head_ref

    if origin_url:
        origin_url_ref = ffi.new('char []', to_bytes(origin_url))
        options.origin_url = origin_url_ref

    # Call
    crepository = ffi.new('git_repository **')
    err = C.git_repository_init_ext(crepository, to_bytes(path), options)
    check_error(err)

    # Ok
    return Repository(to_str(path))


def clone_repository(
    url,
    path,
    bare=False,
    repository=None,
    remote=None,
    checkout_branch=None,
    callbacks=None,
    depth=0,
):
    """
    Clones a new Git repository from *url* in the given *path*.

    Returns: a Repository class pointing to the newly cloned repository.

    Parameters:

    url : str
        URL of the repository to clone.
    path : str
        Local path to clone into.
    bare : bool
        Whether the local repository should be bare.
    remote : callable
        Callback for the remote to use.

        The remote callback has `(Repository, name, url) -> Remote` as a
        signature. The Remote it returns will be used instead of the default
        one.
    repository : callable
        Callback for the repository to use.

        The repository callback has `(path, bare) -> Repository` as a
        signature. The Repository it returns will be used instead of creating a
        new one.
    checkout_branch : str
        Branch to checkout after the clone. The default is to use the remote's
        default branch.
    callbacks : RemoteCallbacks
        Object which implements the callbacks as methods.

        The callbacks should be an object which inherits from
        `pyclass:RemoteCallbacks`.
    depth : int
        Number of commits to clone.

        If greater than 0, creates a shallow clone with a history truncated to
        the specified number of commits.
        The default is 0 (full commit history).
    """

    if callbacks is None:
        callbacks = RemoteCallbacks()

    # Add repository and remote to the payload
    payload = callbacks
    payload.repository = repository
    payload.remote = remote

    with git_clone_options(payload):
        opts = payload.clone_options
        opts.bare = bare
        opts.fetch_opts.depth = depth

        if checkout_branch:
            checkout_branch_ref = ffi.new('char []', to_bytes(checkout_branch))
            opts.checkout_branch = checkout_branch_ref

        with git_fetch_options(payload, opts=opts.fetch_opts):
            crepo = ffi.new('git_repository **')
            err = C.git_clone(crepo, to_bytes(url), to_bytes(path), opts)
            payload.check_error(err)

    # Ok
    return Repository._from_c(crepo[0], owned=True)


tree_entry_key = functools.cmp_to_key(tree_entry_cmp)

settings = Settings()
