# Copyright 2010-2023 The pygit2 contributors
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

# High level API
from ._build import __version__
from .blame import Blame, BlameHunk
from .blob import BlobIO
from .callbacks import Payload, RemoteCallbacks, CheckoutCallbacks, StashApplyCallbacks
from .callbacks import git_clone_options, git_fetch_options, get_credentials
from .config import Config
from .credentials import *
from .enums import (
    AttrCheck,
    ApplyLocation,
    BlameFlag,
    BlobFilter,
    BranchType,
    CheckoutNotify,
    CheckoutStrategy,
    ConfigLevel,
    CredentialType,
    DeltaStatus,
    DescribeStrategy,
    DiffFlag,
    DiffOption,
    DiffStatsFormat,
    Feature,
    FetchPrune,
    FileMode,
    FilterFlag,
    FilterMode,
    ObjectType,
    Option,
    MergeAnalysis,
    MergePreference,
    ReferenceFilter,
    ReferenceType,
    RepositoryInitFlag,
    RepositoryInitMode,
    RepositoryOpenFlag,
    RepositoryState,
    ResetMode,
    RevSpecFlag,
    StashApplyProgress,
    FileStatus,
    SubmoduleIgnore,
    SubmoduleStatus,
    SortMode,
)
from .errors import check_error, Passthrough
from .ffi import ffi, C
from .filter import Filter
from .index import Index, IndexEntry
from .packbuilder import PackBuilder
from .remotes import Remote
from .repository import Repository
from .settings import Settings
from .submodules import Submodule
from .utils import to_bytes, to_str


# Features
features = Feature(C.git_libgit2_features())

# GIT_FEATURE_* values for legacy code
GIT_FEATURE_THREADS = Feature.THREADS
GIT_FEATURE_HTTPS   = Feature.HTTPS
GIT_FEATURE_SSH     = Feature.SSH
GIT_FEATURE_NSEC    = Feature.NSEC

# GIT_REPOSITORY_INIT_* values for legacy code
GIT_REPOSITORY_INIT_BARE                = RepositoryInitFlag.BARE
GIT_REPOSITORY_INIT_NO_REINIT           = RepositoryInitFlag.NO_REINIT
GIT_REPOSITORY_INIT_NO_DOTGIT_DIR       = RepositoryInitFlag.NO_DOTGIT_DIR
GIT_REPOSITORY_INIT_MKDIR               = RepositoryInitFlag.MKDIR
GIT_REPOSITORY_INIT_MKPATH              = RepositoryInitFlag.MKPATH
GIT_REPOSITORY_INIT_EXTERNAL_TEMPLATE   = RepositoryInitFlag.EXTERNAL_TEMPLATE
GIT_REPOSITORY_INIT_RELATIVE_GITLINK    = RepositoryInitFlag.RELATIVE_GITLINK
GIT_REPOSITORY_INIT_SHARED_UMASK        = RepositoryInitMode.SHARED_UMASK
GIT_REPOSITORY_INIT_SHARED_GROUP        = RepositoryInitMode.SHARED_GROUP
GIT_REPOSITORY_INIT_SHARED_ALL          = RepositoryInitMode.SHARED_ALL

# GIT_REPOSITORY_OPEN_* values for legacy code
GIT_REPOSITORY_OPEN_NO_SEARCH   = RepositoryOpenFlag.NO_SEARCH
GIT_REPOSITORY_OPEN_CROSS_FS    = RepositoryOpenFlag.CROSS_FS
GIT_REPOSITORY_OPEN_BARE        = RepositoryOpenFlag.BARE
GIT_REPOSITORY_OPEN_NO_DOTGIT   = RepositoryOpenFlag.NO_DOTGIT
GIT_REPOSITORY_OPEN_FROM_ENV    = RepositoryOpenFlag.FROM_ENV

# GIT_REPOSITORY_STATE_* values for legacy code
GIT_REPOSITORY_STATE_NONE                    = RepositoryState.NONE
GIT_REPOSITORY_STATE_MERGE                   = RepositoryState.MERGE
GIT_REPOSITORY_STATE_REVERT                  = RepositoryState.REVERT
GIT_REPOSITORY_STATE_REVERT_SEQUENCE         = RepositoryState.REVERT_SEQUENCE
GIT_REPOSITORY_STATE_CHERRYPICK              = RepositoryState.CHERRYPICK
GIT_REPOSITORY_STATE_CHERRYPICK_SEQUENCE     = RepositoryState.CHERRYPICK_SEQUENCE
GIT_REPOSITORY_STATE_BISECT                  = RepositoryState.BISECT
GIT_REPOSITORY_STATE_REBASE                  = RepositoryState.REBASE
GIT_REPOSITORY_STATE_REBASE_INTERACTIVE      = RepositoryState.REBASE_INTERACTIVE
GIT_REPOSITORY_STATE_REBASE_MERGE            = RepositoryState.REBASE_MERGE
GIT_REPOSITORY_STATE_APPLY_MAILBOX           = RepositoryState.APPLY_MAILBOX
GIT_REPOSITORY_STATE_APPLY_MAILBOX_OR_REBASE = RepositoryState.APPLY_MAILBOX_OR_REBASE

# GIT_ATTR_CHECK_* values for legacy code
GIT_ATTR_CHECK_FILE_THEN_INDEX = AttrCheck.FILE_THEN_INDEX
GIT_ATTR_CHECK_INDEX_THEN_FILE = AttrCheck.INDEX_THEN_FILE
GIT_ATTR_CHECK_INDEX_ONLY      = AttrCheck.INDEX_ONLY
GIT_ATTR_CHECK_NO_SYSTEM       = AttrCheck.NO_SYSTEM
GIT_ATTR_CHECK_INCLUDE_HEAD    = AttrCheck.INCLUDE_HEAD
GIT_ATTR_CHECK_INCLUDE_COMMIT  = AttrCheck.INCLUDE_COMMIT

# GIT_FETCH_PRUNE_* values for legacy code
GIT_FETCH_PRUNE_UNSPECIFIED    = FetchPrune.UNSPECIFIED
GIT_FETCH_PRUNE                = FetchPrune.PRUNE
GIT_FETCH_NO_PRUNE             = FetchPrune.NO_PRUNE

# GIT_CHECKOUT_NOTIFY_* values for legacy code
GIT_CHECKOUT_NOTIFY_NONE       = CheckoutNotify.NONE
GIT_CHECKOUT_NOTIFY_CONFLICT   = CheckoutNotify.CONFLICT
GIT_CHECKOUT_NOTIFY_DIRTY      = CheckoutNotify.DIRTY
GIT_CHECKOUT_NOTIFY_UPDATED    = CheckoutNotify.UPDATED
GIT_CHECKOUT_NOTIFY_UNTRACKED  = CheckoutNotify.UNTRACKED
GIT_CHECKOUT_NOTIFY_IGNORED    = CheckoutNotify.IGNORED
GIT_CHECKOUT_NOTIFY_ALL        = CheckoutNotify.ALL

# GIT_STASH_APPLY_PROGRESS_* values for legacy code
GIT_STASH_APPLY_PROGRESS_NONE               = StashApplyProgress.NONE
GIT_STASH_APPLY_PROGRESS_LOADING_STASH      = StashApplyProgress.LOADING_STASH
GIT_STASH_APPLY_PROGRESS_ANALYZE_INDEX      = StashApplyProgress.ANALYZE_INDEX
GIT_STASH_APPLY_PROGRESS_ANALYZE_MODIFIED   = StashApplyProgress.ANALYZE_MODIFIED
GIT_STASH_APPLY_PROGRESS_ANALYZE_UNTRACKED  = StashApplyProgress.ANALYZE_UNTRACKED
GIT_STASH_APPLY_PROGRESS_CHECKOUT_UNTRACKED = StashApplyProgress.CHECKOUT_UNTRACKED
GIT_STASH_APPLY_PROGRESS_CHECKOUT_MODIFIED  = StashApplyProgress.CHECKOUT_MODIFIED
GIT_STASH_APPLY_PROGRESS_DONE               = StashApplyProgress.DONE

# GIT_CREDENTIAL_* values for legacy code
GIT_CREDENTIAL_USERPASS_PLAINTEXT           = CredentialType.USERPASS_PLAINTEXT
GIT_CREDENTIAL_SSH_KEY                      = CredentialType.SSH_KEY
GIT_CREDENTIAL_SSH_CUSTOM                   = CredentialType.SSH_CUSTOM
GIT_CREDENTIAL_DEFAULT                      = CredentialType.DEFAULT
GIT_CREDENTIAL_SSH_INTERACTIVE              = CredentialType.SSH_INTERACTIVE
GIT_CREDENTIAL_USERNAME                     = CredentialType.USERNAME
GIT_CREDENTIAL_SSH_MEMORY                   = CredentialType.SSH_MEMORY

# libgit version tuple
LIBGIT2_VER = (LIBGIT2_VER_MAJOR, LIBGIT2_VER_MINOR, LIBGIT2_VER_REVISION)


def init_repository(
        path: typing.Union[str, bytes, PathLike, None],
        bare: bool = False,
        flags: RepositoryInitFlag = RepositoryInitFlag.MKPATH,
        mode: typing.Union[int, RepositoryInitMode] = RepositoryInitMode.SHARED_UMASK,
        workdir_path: typing.Optional[str] = None,
        description: typing.Optional[str] = None,
        template_path: typing.Optional[str] = None,
        initial_head: typing.Optional[str] = None,
        origin_url: typing.Optional[str] = None
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
        flags |= RepositoryInitFlag.BARE

    # Options
    options = ffi.new('git_repository_init_options *')
    C.git_repository_init_options_init(options,
                                       C.GIT_REPOSITORY_INIT_OPTIONS_VERSION)
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
        url, path, bare=False, repository=None, remote=None,
        checkout_branch=None, callbacks=None, depth=0):
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
