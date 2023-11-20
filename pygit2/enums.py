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


class AttrCheck(IntFlag):
    FILE_THEN_INDEX = C.GIT_ATTR_CHECK_FILE_THEN_INDEX
    INDEX_THEN_FILE = C.GIT_ATTR_CHECK_INDEX_THEN_FILE
    INDEX_ONLY = C.GIT_ATTR_CHECK_INDEX_ONLY
    NO_SYSTEM = C.GIT_ATTR_CHECK_NO_SYSTEM
    INCLUDE_HEAD = C.GIT_ATTR_CHECK_INCLUDE_HEAD
    INCLUDE_COMMIT = C.GIT_ATTR_CHECK_INCLUDE_COMMIT


class CheckoutNotify(IntFlag):
    """
    Checkout notification flags

    Checkout will invoke an options notification callback
    (`CheckoutCallbacks.checkout_notify`) for certain cases - you pick which
    ones via `CheckoutCallbacks.checkout_notify_flags`.
    """

    NONE = C.GIT_CHECKOUT_NOTIFY_NONE

    CONFLICT = C.GIT_CHECKOUT_NOTIFY_CONFLICT
    "Invokes checkout on conflicting paths."

    DIRTY = C.GIT_CHECKOUT_NOTIFY_DIRTY
    """
    Notifies about "dirty" files, i.e. those that do not need an update
    but no longer match the baseline.  Core git displays these files when
    checkout runs, but won't stop the checkout.
    """

    UPDATED = C.GIT_CHECKOUT_NOTIFY_UPDATED
    "Sends notification for any file changed."

    UNTRACKED = C.GIT_CHECKOUT_NOTIFY_UNTRACKED
    "Notifies about untracked files."

    IGNORED = C.GIT_CHECKOUT_NOTIFY_UNTRACKED
    "Notifies about ignored files."

    ALL = C.GIT_CHECKOUT_NOTIFY_ALL


class CheckoutStrategy(IntFlag):
    NONE = _pygit2.GIT_CHECKOUT_NONE
    "Dry run, no actual updates"

    SAFE = _pygit2.GIT_CHECKOUT_SAFE
    """
    Allow safe updates that cannot overwrite uncommitted data.
    If the uncommitted changes don't conflict with the checked out files,
    the checkout will still proceed, leaving the changes intact.
    
    Mutually exclusive with FORCE.
    FORCE takes precedence over SAFE.
    """

    FORCE = _pygit2.GIT_CHECKOUT_FORCE
    """
    Allow all updates to force working directory to look like index.

    Mutually exclusive with SAFE.
    FORCE takes precedence over SAFE.
    """

    RECREATE_MISSING = _pygit2.GIT_CHECKOUT_RECREATE_MISSING
    """ Allow checkout to recreate missing files """

    ALLOW_CONFLICTS = _pygit2.GIT_CHECKOUT_ALLOW_CONFLICTS
    """ Allow checkout to make safe updates even if conflicts are found """

    REMOVE_UNTRACKED = _pygit2.GIT_CHECKOUT_REMOVE_UNTRACKED
    """ Remove untracked files not in index (that are not ignored) """

    REMOVE_IGNORED = _pygit2.GIT_CHECKOUT_REMOVE_IGNORED
    """ Remove ignored files not in index """

    UPDATE_ONLY = _pygit2.GIT_CHECKOUT_UPDATE_ONLY
    """ Only update existing files, don't create new ones """

    DONT_UPDATE_INDEX = _pygit2.GIT_CHECKOUT_DONT_UPDATE_INDEX
    """
    Normally checkout updates index entries as it goes; this stops that.
    Implies `DONT_WRITE_INDEX`.
    """

    NO_REFRESH = _pygit2.GIT_CHECKOUT_NO_REFRESH
    """ Don't refresh index/config/etc before doing checkout """

    SKIP_UNMERGED = _pygit2.GIT_CHECKOUT_SKIP_UNMERGED
    """ Allow checkout to skip unmerged files """

    USE_OURS = _pygit2.GIT_CHECKOUT_USE_OURS
    """ For unmerged files, checkout stage 2 from index """

    USE_THEIRS = _pygit2.GIT_CHECKOUT_USE_THEIRS
    """ For unmerged files, checkout stage 3 from index """

    DISABLE_PATHSPEC_MATCH = _pygit2.GIT_CHECKOUT_DISABLE_PATHSPEC_MATCH
    """ Treat pathspec as simple list of exact match file paths """

    SKIP_LOCKED_DIRECTORIES = _pygit2.GIT_CHECKOUT_SKIP_LOCKED_DIRECTORIES
    """ Ignore directories in use, they will be left empty """

    DONT_OVERWRITE_IGNORED = _pygit2.GIT_CHECKOUT_DONT_OVERWRITE_IGNORED
    """ Don't overwrite ignored files that exist in the checkout target """

    CONFLICT_STYLE_MERGE = _pygit2.GIT_CHECKOUT_CONFLICT_STYLE_MERGE
    """ Write normal merge files for conflicts """

    CONFLICT_STYLE_DIFF3 = _pygit2.GIT_CHECKOUT_CONFLICT_STYLE_DIFF3
    """ Include common ancestor data in diff3 format files for conflicts """

    DONT_REMOVE_EXISTING = _pygit2.GIT_CHECKOUT_DONT_REMOVE_EXISTING
    """ Don't overwrite existing files or folders """

    DONT_WRITE_INDEX = _pygit2.GIT_CHECKOUT_DONT_WRITE_INDEX
    """ Normally checkout writes the index upon completion; this prevents that. """

    DRY_RUN = _pygit2.GIT_CHECKOUT_DRY_RUN
    """
    Show what would be done by a checkout.  Stop after sending
    notifications; don't update the working directory or index.
    """

    CONFLICT_STYLE_ZDIFF3 = _pygit2.GIT_CHECKOUT_CONFLICT_STYLE_DIFF3
    """ Include common ancestor data in zdiff3 format for conflicts """


class DiffOption(IntFlag):
    """
    Flags for diff options.  A combination of these flags can be passed
    in via the `flags` value in `diff_*` functions.
    """

    NORMAL = _pygit2.GIT_DIFF_NORMAL
    "Normal diff, the default"

    REVERSE = _pygit2.GIT_DIFF_REVERSE
    "Reverse the sides of the diff"

    INCLUDE_IGNORED = _pygit2.GIT_DIFF_INCLUDE_IGNORED
    "Include ignored files in the diff"

    RECURSE_IGNORED_DIRS = _pygit2.GIT_DIFF_RECURSE_IGNORED_DIRS
    """
    Even with INCLUDE_IGNORED, an entire ignored directory
    will be marked with only a single entry in the diff; this flag
    adds all files under the directory as IGNORED entries, too.
    """

    INCLUDE_UNTRACKED = _pygit2.GIT_DIFF_INCLUDE_UNTRACKED
    "Include untracked files in the diff"

    RECURSE_UNTRACKED_DIRS = _pygit2.GIT_DIFF_RECURSE_UNTRACKED_DIRS
    """
    Even with INCLUDE_UNTRACKED, an entire untracked
    directory will be marked with only a single entry in the diff
    (a la what core Git does in `git status`); this flag adds *all*
    files under untracked directories as UNTRACKED entries, too.
    """

    INCLUDE_UNMODIFIED = _pygit2.GIT_DIFF_INCLUDE_UNMODIFIED
    "Include unmodified files in the diff"

    INCLUDE_TYPECHANGE = _pygit2.GIT_DIFF_INCLUDE_TYPECHANGE
    """
    Normally, a type change between files will be converted into a
    DELETED record for the old and an ADDED record for the new; this
    options enabled the generation of TYPECHANGE delta records.
    """

    INCLUDE_TYPECHANGE_TREES = _pygit2.GIT_DIFF_INCLUDE_TYPECHANGE_TREES
    """
    Even with INCLUDE_TYPECHANGE, blob->tree changes still generally
    show as a DELETED blob.  This flag tries to correctly label
    blob->tree transitions as TYPECHANGE records with new_file's
    mode set to tree.  Note: the tree SHA will not be available.
    """

    IGNORE_FILEMODE = _pygit2.GIT_DIFF_IGNORE_FILEMODE
    "Ignore file mode changes"

    IGNORE_SUBMODULES = _pygit2.GIT_DIFF_IGNORE_SUBMODULES
    "Treat all submodules as unmodified"

    IGNORE_CASE = _pygit2.GIT_DIFF_IGNORE_CASE
    "Use case insensitive filename comparisons"

    INCLUDE_CASECHANGE = _pygit2.GIT_DIFF_INCLUDE_CASECHANGE
    """
    May be combined with IGNORE_CASE to specify that a file
    that has changed case will be returned as an add/delete pair.
    """

    DISABLE_PATHSPEC_MATCH = _pygit2.GIT_DIFF_DISABLE_PATHSPEC_MATCH
    """
    If the pathspec is set in the diff options, this flags indicates
    that the paths will be treated as literal paths instead of
    fnmatch patterns.  Each path in the list must either be a full
    path to a file or a directory.  (A trailing slash indicates that
    the path will _only_ match a directory).  If a directory is
    specified, all children will be included.
    """

    SKIP_BINARY_CHECK = _pygit2.GIT_DIFF_SKIP_BINARY_CHECK
    """
    Disable updating of the `binary` flag in delta records.  This is
    useful when iterating over a diff if you don't need hunk and data
    callbacks and want to avoid having to load file completely.
    """

    ENABLE_FAST_UNTRACKED_DIRS = _pygit2.GIT_DIFF_ENABLE_FAST_UNTRACKED_DIRS
    """
    When diff finds an untracked directory, to match the behavior of
    core Git, it scans the contents for IGNORED and UNTRACKED files.
    If *all* contents are IGNORED, then the directory is IGNORED; if
    any contents are not IGNORED, then the directory is UNTRACKED.
    This is extra work that may not matter in many cases.  This flag
    turns off that scan and immediately labels an untracked directory
    as UNTRACKED (changing the behavior to not match core Git).
    """

    UPDATE_INDEX = _pygit2.GIT_DIFF_UPDATE_INDEX
    """
    When diff finds a file in the working directory with stat
    information different from the index, but the OID ends up being the
    same, write the correct stat information into the index.  Note:
    without this flag, diff will always leave the index untouched.
    """

    INCLUDE_UNREADABLE = _pygit2.GIT_DIFF_INCLUDE_UNREADABLE
    "Include unreadable files in the diff"

    INCLUDE_UNREADABLE_AS_UNTRACKED = _pygit2.GIT_DIFF_INCLUDE_UNREADABLE_AS_UNTRACKED
    "Include unreadable files in the diff"

    INDENT_HEURISTIC = _pygit2.GIT_DIFF_INDENT_HEURISTIC
    """
    Use a heuristic that takes indentation and whitespace into account
    which generally can produce better diffs when dealing with ambiguous
    diff hunks.
    """

    IGNORE_BLANK_LINES = _pygit2.GIT_DIFF_IGNORE_BLANK_LINES
    "Ignore blank lines"

    FORCE_TEXT = _pygit2.GIT_DIFF_FORCE_TEXT
    "Treat all files as text, disabling binary attributes & detection"

    FORCE_BINARY = _pygit2.GIT_DIFF_FORCE_BINARY
    "Treat all files as binary, disabling text diffs"

    IGNORE_WHITESPACE = _pygit2.GIT_DIFF_IGNORE_WHITESPACE
    "Ignore all whitespace"

    IGNORE_WHITESPACE_CHANGE = _pygit2.GIT_DIFF_IGNORE_WHITESPACE_CHANGE
    "Ignore changes in amount of whitespace"

    IGNORE_WHITESPACE_EOL = _pygit2.GIT_DIFF_IGNORE_WHITESPACE_EOL
    "Ignore whitespace at end of line"

    SHOW_UNTRACKED_CONTENT = _pygit2.GIT_DIFF_SHOW_UNTRACKED_CONTENT
    """
    When generating patch text, include the content of untracked files.
    This automatically turns on INCLUDE_UNTRACKED but it does not turn
    on RECURSE_UNTRACKED_DIRS.  Add that flag if you want the content
    of every single UNTRACKED file.
    """

    SHOW_UNMODIFIED = _pygit2.GIT_DIFF_SHOW_UNMODIFIED
    """
    When generating output, include the names of unmodified files if
    they are included in the git_diff.  Normally these are skipped in
    the formats that list files (e.g. name-only, name-status, raw).
    Even with this, these will not be included in patch format.
    """

    PATIENCE = _pygit2.GIT_DIFF_PATIENCE
    "Use the 'patience diff' algorithm"

    MINIMAL = _pygit2.GIT_DIFF_MINIMAL
    "Take extra time to find minimal diff"

    SHOW_BINARY = _pygit2.GIT_DIFF_SHOW_BINARY
    """
    Include the necessary deflate / delta information so that `git-apply`
    can apply given diff information to binary files.
    """


class Feature(IntFlag):
    """
    Combinations of these values describe the features with which libgit2
    was compiled.
    """

    THREADS = C.GIT_FEATURE_THREADS
    HTTPS = C.GIT_FEATURE_HTTPS
    SSH = C.GIT_FEATURE_SSH
    NSEC = C.GIT_FEATURE_NSEC


class ReferenceFilter(IntEnum):
    """ Filters for References.iterator(). """

    ALL = _pygit2.GIT_REFERENCES_ALL
    BRANCHES = _pygit2.GIT_REFERENCES_BRANCHES
    TAGS = _pygit2.GIT_REFERENCES_TAGS


class ReferenceType(IntFlag):
    """ Basic type of any Git reference. """

    INVALID = _pygit2.GIT_REF_INVALID
    OID = _pygit2.GIT_REF_OID
    SYMBOLIC = _pygit2.GIT_REF_SYMBOLIC
    LISTALL = _pygit2.GIT_REF_LISTALL


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


class StashApplyProgress(IntEnum):
    """
    Stash apply progression states
    """

    NONE = C.GIT_STASH_APPLY_PROGRESS_NONE

    LOADING_STASH = C.GIT_STASH_APPLY_PROGRESS_LOADING_STASH
    "Loading the stashed data from the object database."

    ANALYZE_INDEX = C.GIT_STASH_APPLY_PROGRESS_ANALYZE_INDEX
    "The stored index is being analyzed."

    ANALYZE_MODIFIED = C.GIT_STASH_APPLY_PROGRESS_ANALYZE_MODIFIED
    "The modified files are being analyzed."

    ANALYZE_UNTRACKED = C.GIT_STASH_APPLY_PROGRESS_ANALYZE_UNTRACKED
    "The untracked and ignored files are being analyzed."

    CHECKOUT_UNTRACKED = C.GIT_STASH_APPLY_PROGRESS_CHECKOUT_UNTRACKED
    "The untracked files are being written to disk."

    CHECKOUT_MODIFIED = C.GIT_STASH_APPLY_PROGRESS_CHECKOUT_MODIFIED
    "The modified files are being written to disk."

    DONE = C.GIT_STASH_APPLY_PROGRESS_DONE
    "The stash was applied successfully."


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
