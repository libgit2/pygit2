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

from enum import IntEnum, IntFlag

from . import _pygit2
from .ffi import C


class RepositoryInitFlag(IntFlag):
    """
    Option flags for pygit2.init_repository().
    """

    BARE = C.GIT_REPOSITORY_INIT_BARE
    "Create a bare repository with no working directory."

    NO_REINIT = C.GIT_REPOSITORY_INIT_NO_REINIT
    "Raise GitError if the path appears to already be a git repository."

    NO_DOTGIT_DIR = C.GIT_REPOSITORY_INIT_NO_DOTGIT_DIR
    """Normally a "/.git/" will be appended to the repo path for
    non-bare repos (if it is not already there), but passing this flag
    prevents that behavior."""

    MKDIR = C.GIT_REPOSITORY_INIT_MKDIR
    """Make the repo_path (and workdir_path) as needed. Init is always willing
    to create the ".git" directory even without this flag. This flag tells
    init to create the trailing component of the repo and workdir paths
    as needed."""

    MKPATH = C.GIT_REPOSITORY_INIT_MKPATH
    "Recursively make all components of the repo and workdir paths as necessary."

    EXTERNAL_TEMPLATE = C.GIT_REPOSITORY_INIT_EXTERNAL_TEMPLATE
    """libgit2 normally uses internal templates to initialize a new repo.
    This flags enables external templates, looking at the "template_path" from
    the options if set, or the `init.templatedir` global config if not,
    or falling back on "/usr/share/git-core/templates" if it exists."""

    RELATIVE_GITLINK = C.GIT_REPOSITORY_INIT_RELATIVE_GITLINK
    """If an alternate workdir is specified, use relative paths for the gitdir
    and core.worktree."""


class RepositoryInitMode(IntEnum):
    """
    Mode options for pygit2.init_repository().
    """

    SHARED_UMASK = C.GIT_REPOSITORY_INIT_SHARED_UMASK
    "Use permissions configured by umask - the default."

    SHARED_GROUP = C.GIT_REPOSITORY_INIT_SHARED_GROUP
    """
    Use '--shared=group' behavior, chmod'ing the new repo to be group
    writable and "g+sx" for sticky group assignment.
    """

    SHARED_ALL = C.GIT_REPOSITORY_INIT_SHARED_ALL
    "Use '--shared=all' behavior, adding world readability."


class RepositoryOpenFlag(IntFlag):
    """
    Option flags for Repository.__init__().
    """

    DEFAULT = 0
    "Default flags."

    NO_SEARCH = C.GIT_REPOSITORY_OPEN_NO_SEARCH
    """
    Only open the repository if it can be immediately found in the
    start_path. Do not walk up from the start_path looking at parent
    directories.
    """

    CROSS_FS = C.GIT_REPOSITORY_OPEN_CROSS_FS
    """
    Unless this flag is set, open will not continue searching across
    filesystem boundaries (i.e. when `st_dev` changes from the `stat`
    system call).  For example, searching in a user's home directory at
    "/home/user/source/" will not return "/.git/" as the found repo if
    "/" is a different filesystem than "/home".
    """

    BARE = C.GIT_REPOSITORY_OPEN_BARE
    """
    Open repository as a bare repo regardless of core.bare config, and
    defer loading config file for faster setup.
    Unlike `git_repository_open_bare`, this can follow gitlinks.
    """

    NO_DOTGIT = C.GIT_REPOSITORY_OPEN_NO_DOTGIT
    """
    Do not check for a repository by appending /.git to the start_path;
    only open the repository if start_path itself points to the git
    directory.
    """

    FROM_ENV = C.GIT_REPOSITORY_OPEN_FROM_ENV
    """
    Find and open a git repository, respecting the environment variables
    used by the git command-line tools.
    If set, `git_repository_open_ext` will ignore the other flags and
    the `ceiling_dirs` argument, and will allow a NULL `path` to use
    `GIT_DIR` or search from the current directory.
    The search for a repository will respect $GIT_CEILING_DIRECTORIES and
    $GIT_DISCOVERY_ACROSS_FILESYSTEM.  The opened repository will
    respect $GIT_INDEX_FILE, $GIT_NAMESPACE, $GIT_OBJECT_DIRECTORY, and
    $GIT_ALTERNATE_OBJECT_DIRECTORIES.
    In the future, this flag will also cause `git_repository_open_ext`
    to respect $GIT_WORK_TREE and $GIT_COMMON_DIR; currently,
    `git_repository_open_ext` with this flag will error out if either
    $GIT_WORK_TREE or $GIT_COMMON_DIR is set.
    """


class RepositoryState(IntEnum):
    """
    Repository state: These values represent possible states for the repository
    to be in, based on the current operation which is ongoing.
    """
    NONE = C.GIT_REPOSITORY_STATE_NONE
    MERGE = C.GIT_REPOSITORY_STATE_MERGE
    REVERT = C.GIT_REPOSITORY_STATE_REVERT
    REVERT_SEQUENCE = C.GIT_REPOSITORY_STATE_REVERT_SEQUENCE
    CHERRYPICK = C.GIT_REPOSITORY_STATE_CHERRYPICK
    CHERRYPICK_SEQUENCE = C.GIT_REPOSITORY_STATE_CHERRYPICK_SEQUENCE
    BISECT = C.GIT_REPOSITORY_STATE_BISECT
    REBASE = C.GIT_REPOSITORY_STATE_REBASE
    REBASE_INTERACTIVE = C.GIT_REPOSITORY_STATE_REBASE_INTERACTIVE
    REBASE_MERGE = C.GIT_REPOSITORY_STATE_REBASE_MERGE
    APPLY_MAILBOX = C.GIT_REPOSITORY_STATE_APPLY_MAILBOX
    APPLY_MAILBOX_OR_REBASE = C.GIT_REPOSITORY_STATE_APPLY_MAILBOX_OR_REBASE


class SubmoduleIgnore(IntEnum):
    UNSPECIFIED = _pygit2.GIT_SUBMODULE_IGNORE_UNSPECIFIED
    "use the submodule's configuration"

    NONE = _pygit2.GIT_SUBMODULE_IGNORE_NONE
    "any change or untracked == dirty"

    UNTRACKED = _pygit2.GIT_SUBMODULE_IGNORE_UNTRACKED
    "dirty if tracked files change"

    DIRTY = _pygit2.GIT_SUBMODULE_IGNORE_DIRTY
    "only dirty if HEAD moved"

    ALL = _pygit2.GIT_SUBMODULE_IGNORE_ALL
    "never dirty"


class SubmoduleStatus(IntFlag):
    IN_HEAD = _pygit2.GIT_SUBMODULE_STATUS_IN_HEAD
    "superproject head contains submodule"

    IN_INDEX = _pygit2.GIT_SUBMODULE_STATUS_IN_INDEX
    "superproject index contains submodule"

    IN_CONFIG = _pygit2.GIT_SUBMODULE_STATUS_IN_CONFIG
    "superproject gitmodules has submodule"

    IN_WD = _pygit2.GIT_SUBMODULE_STATUS_IN_WD
    "superproject workdir has submodule"

    INDEX_ADDED = _pygit2.GIT_SUBMODULE_STATUS_INDEX_ADDED
    "in index, not in head (flag available if ignore is not ALL)"

    INDEX_DELETED = _pygit2.GIT_SUBMODULE_STATUS_INDEX_DELETED
    "in head, not in index (flag available if ignore is not ALL)"

    INDEX_MODIFIED = _pygit2.GIT_SUBMODULE_STATUS_INDEX_MODIFIED
    "index and head don't match (flag available if ignore is not ALL)"

    WD_UNINITIALIZED = _pygit2.GIT_SUBMODULE_STATUS_WD_UNINITIALIZED
    "workdir contains empty repository (flag available if ignore is not ALL)"

    WD_ADDED = _pygit2.GIT_SUBMODULE_STATUS_WD_ADDED
    "in workdir, not index (flag available if ignore is not ALL)"

    WD_DELETED = _pygit2.GIT_SUBMODULE_STATUS_WD_DELETED
    "in index, not workdir (flag available if ignore is not ALL)"

    WD_MODIFIED = _pygit2.GIT_SUBMODULE_STATUS_WD_MODIFIED
    "index and workdir head don't match (flag available if ignore is not ALL)"

    WD_INDEX_MODIFIED = _pygit2.GIT_SUBMODULE_STATUS_WD_INDEX_MODIFIED
    "submodule workdir index is dirty (flag available if ignore is NONE or UNTRACKED)"

    WD_WD_MODIFIED = _pygit2.GIT_SUBMODULE_STATUS_WD_WD_MODIFIED
    "submodule workdir has modified files (flag available if ignore is NONE or UNTRACKED)"

    WD_UNTRACKED = _pygit2.GIT_SUBMODULE_STATUS_WD_UNTRACKED
    "submodule workdir contains untracked files (flag available if ignore is NONE)"
