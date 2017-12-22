# -*- coding: utf-8 -*-
#
# Copyright 2010-2017 The pygit2 contributors
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

# Import from the Standard Library
from string import hexdigits
import sys, tarfile
from time import time

if sys.version_info[0] < 3:
    from cStringIO import StringIO
else:
    from io import BytesIO as StringIO

import six

# Import from pygit2
from _pygit2 import Repository as _Repository, init_file_backend
from _pygit2 import Oid, GIT_OID_HEXSZ, GIT_OID_MINPREFIXLEN
from _pygit2 import GIT_CHECKOUT_SAFE, GIT_CHECKOUT_RECREATE_MISSING, GIT_DIFF_NORMAL
from _pygit2 import GIT_FILEMODE_LINK
from _pygit2 import GIT_BRANCH_LOCAL, GIT_BRANCH_REMOTE, GIT_BRANCH_ALL
from _pygit2 import Reference, Tree, Commit, Blob

from .config import Config
from .errors import check_error
from .ffi import ffi, C
from .index import Index
from .remote import RemoteCollection
from .blame import Blame
from .utils import to_bytes, is_string
from .submodule import Submodule


class BaseRepository(_Repository):
    def __init__(self, backend, *args, **kwargs):
        super(BaseRepository, self).__init__(backend, *args, **kwargs)
        self._common_init()

    def _common_init(self):
        self.remotes = RemoteCollection(self)

        # Get the pointer as the contents of a buffer and store it for
        # later access
        repo_cptr = ffi.new('git_repository **')
        ffi.buffer(repo_cptr)[:] = self._pointer[:]
        self._repo = repo_cptr[0]

    def lookup_submodule(self, path):
        csub = ffi.new('git_submodule **')
        cpath = ffi.new('char[]', to_bytes(path))

        err = C.git_submodule_lookup(csub, self._repo, cpath)
        check_error(err)
        return Submodule._from_c(self, csub[0])

    def update_submodule2(self, submodule=None, init=False, callbacks=None):
        opts = ffi.new('git_submodule_update_options *')
        if init:
            i = 1
        else:
            i = 0
        C.git_submodule_update_init_options(
            opts,
            C.GIT_SUBMODULE_UPDATE_OPTIONS_VERSION)
        if callbacks is not None:
            callbacks._fill_fetch_options(opts.fetch_opts)
        err = C.git_submodule_update(submodule._subm, i, opts)

        check_error(err)

        return

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

    def __repr__(self):
        return "pygit2.Repository(%r)" % self.path

    #
    # Remotes
    #
    def create_remote(self, name, url):
        """Create a new remote. Return a <Remote> object.

        This method is deprecated, please use Remote.remotes.create()
        """
        return self.remotes.create(name, url)

    #
    # Configuration
    #
    @property
    def config(self):
        """The configuration file for this repository.

        If a the configuration hasn't been set yet, the default config for
        repository will be returned, including global and system configurations
        (if they are available).
        """
        cconfig = ffi.new('git_config **')
        err = C.git_repository_config(cconfig, self._repo)
        check_error(err)

        return Config.from_c(self, cconfig[0])

    @property
    def config_snapshot(self):
        """A snapshot for this repositiory's configuration

        This allows reads over multiple values to use the same version
        of the configuration files.
        """
        cconfig = ffi.new('git_config **')
        err = C.git_repository_config_snapshot(cconfig, self._repo)
        check_error(err)

        return Config.from_c(self, cconfig[0])

    #
    # References
    #
    def create_reference(self, name, target, force=False):
        """Create a new reference "name" which points to an object or to
        another reference.

        Based on the type and value of the target parameter, this method tries
        to guess whether it is a direct or a symbolic reference.

        Keyword arguments:

        force
            If True references will be overridden, otherwise (the default) an
            exception is raised.

        Examples::

            repo.create_reference('refs/heads/foo', repo.head.target)
            repo.create_reference('refs/tags/foo', 'refs/heads/master')
            repo.create_reference('refs/tags/foo', 'bbb78a9cec580')
        """
        direct = (
            type(target) is Oid
            or (
                all(c in hexdigits for c in target)
                and GIT_OID_MINPREFIXLEN <= len(target) <= GIT_OID_HEXSZ))

        if direct:
            return self.create_reference_direct(name, target, force)

        return self.create_reference_symbolic(name, target, force)

    #
    # Checkout
    #
    @staticmethod
    def _checkout_args_to_options(strategy=None, directory=None):
        # Create the options struct to pass
        copts = ffi.new('git_checkout_options *')
        check_error(C.git_checkout_init_options(copts, 1))

        # References we need to keep to strings and so forth
        refs = []

        # pygit2's default is SAFE | RECREATE_MISSING
        copts.checkout_strategy = GIT_CHECKOUT_SAFE | GIT_CHECKOUT_RECREATE_MISSING
        # and go through the arguments to see what the user wanted
        if strategy:
            copts.checkout_strategy = strategy

        if directory:
            target_dir = ffi.new('char[]', to_bytes(directory))
            refs.append(target_dir)
            copts.target_directory = target_dir

        return copts, refs

    def checkout_head(self, **kwargs):
        """Checkout HEAD

        For arguments, see Repository.checkout().
        """
        copts, refs = Repository._checkout_args_to_options(**kwargs)
        check_error(C.git_checkout_head(self._repo, copts))

    def checkout_index(self, **kwargs):
        """Checkout the repository's index

        For arguments, see Repository.checkout().
        """
        copts, refs = Repository._checkout_args_to_options(**kwargs)
        check_error(C.git_checkout_index(self._repo, ffi.NULL, copts))

    def checkout_tree(self, treeish, **kwargs):
        """Checkout the given treeish

        For arguments, see Repository.checkout().
        """
        copts, refs = Repository._checkout_args_to_options(**kwargs)
        cptr = ffi.new('git_object **')
        ffi.buffer(cptr)[:] = treeish._pointer[:]

        check_error(C.git_checkout_tree(self._repo, cptr[0], copts))

    def checkout(self, refname=None, **kwargs):
        """
        Checkout the given reference using the given strategy, and update the
        HEAD.
        The reference may be a reference name or a Reference object.
        The default strategy is GIT_CHECKOUT_SAFE | GIT_CHECKOUT_RECREATE_MISSING.

        If no reference is given, checkout from the index.

        Parameters:

        refname : str or Reference
            The reference to checkout. After checkout, the current branch will
            be switched to this one.

        strategy : int
            A ``GIT_CHECKOUT_`` value. The default is ``GIT_CHECKOUT_SAFE``.

        directory : str
            Alternative checkout path to workdir.

        Examples:

        * To checkout from the HEAD, just pass 'HEAD'::

            >>> checkout('HEAD')

          This is identical to calling checkout_head().
        """

        # Case 1: Checkout index
        if refname is None:
            return self.checkout_index(**kwargs)

        # Case 2: Checkout head
        if refname == 'HEAD':
            return self.checkout_head(**kwargs)

        # Case 3: Reference
        if isinstance(refname, Reference):
            reference = refname
            refname = refname.name
        else:
            reference = self.lookup_reference(refname)

        oid = reference.resolve().target
        treeish = self[oid]
        self.checkout_tree(treeish, **kwargs)

        self.set_head(refname)

    #
    # Setting HEAD
    #
    def set_head(self, target):
        """
        Set HEAD to point to the given target.

        Parameters:

        target
            The new target for HEAD. Can be a string or Oid (to detach).
        """

        if isinstance(target, Oid):
            oid = ffi.new('git_oid *')
            ffi.buffer(oid)[:] = target.raw[:]
            err = C.git_repository_set_head_detached(self._repo, oid)
            check_error(err)
            return

        # if it's a string, then it's a reference name
        err = C.git_repository_set_head(self._repo, to_bytes(target))
        check_error(err)

    #
    # Diff
    #
    def diff(self, a=None, b=None, cached=False, flags=GIT_DIFF_NORMAL,
             context_lines=3, interhunk_lines=0):
        """
        Show changes between the working tree and the index or a tree,
        changes between the index and a tree, changes between two trees, or
        changes between two blobs.

        Keyword arguments:

        a
            None, a str (that refers to an Object, see revparse_single()) or a
            Reference object.
            If None, b must be None, too. In this case the working directory is
            compared with the index. Otherwise the referred object is compared to
            'b'.

        b
            None, a str (that refers to an Object, see revparse_single()) or a
            Reference object.
            If None, the working directory is compared to 'a'. (except
            'cached' is True, in which case the index is compared to 'a').
            Otherwise the referred object is compared to 'a'

        cached
            if 'b' is None, by default the working directory is compared to 'a'.
            If 'cached' is set to True, the index/staging area is used for comparing.

        flag
            a GIT_DIFF_* constant

        context_lines
            the number of unchanged lines that define the boundary
            of a hunk (and to display before and after)

        interhunk_lines
            the maximum number of unchanged lines between hunk
            boundaries before the hunks will be merged into a one

        Examples::

          # Changes in the working tree not yet staged for the next commit
          >>> diff()

          # Changes between the index and your last commit
          >>> diff(cached=True)

          # Changes in the working tree since your last commit
          >>> diff('HEAD')

          # Changes between commits
          >>> t0 = revparse_single('HEAD')
          >>> t1 = revparse_single('HEAD^')
          >>> diff(t0, t1)
          >>> diff('HEAD', 'HEAD^') # equivalent

        If you want to diff a tree against an empty tree, use the low level
        API (Tree.diff_to_tree()) directly.
        """

        def whatever_to_tree_or_blob(obj):
            if obj is None:
                return None

            # If it's a string, then it has to be valid revspec
            if is_string(obj):
                obj = self.revparse_single(obj)

            # First we try to get to a blob
            try:
                obj = obj.peel(Blob)
            except Exception:
                # And if that failed, try to get a tree, raising a type
                # error if that still doesn't work
                try:
                    obj = obj.peel(Tree)
                except Exception:
                    raise TypeError('unexpected "%s"' % type(obj))

            return obj

        a = whatever_to_tree_or_blob(a)
        b = whatever_to_tree_or_blob(b)

        opt_keys = ['flags', 'context_lines', 'interhunk_lines']
        opt_values = [flags, context_lines, interhunk_lines]

        # Case 1: Diff tree to tree
        if isinstance(a, Tree) and isinstance(b, Tree):
            return a.diff_to_tree(b, **dict(zip(opt_keys, opt_values)))

        # Case 2: Index to workdir
        elif a is None and b is None:
            return self.index.diff_to_workdir(*opt_values)

        # Case 3: Diff tree to index or workdir
        elif isinstance(a, Tree) and b is None:
            if cached:
                return a.diff_to_index(self.index, *opt_values)
            else:
                return a.diff_to_workdir(*opt_values)

        # Case 4: Diff blob to blob
        if isinstance(a, Blob) and isinstance(b, Blob):
            return a.diff(b)

        raise ValueError("Only blobs and treeish can be diffed")

    def state_cleanup(self):
        """Remove all the metadata associated with an ongoing command like
        merge, revert, cherry-pick, etc. For example: MERGE_HEAD, MERGE_MSG,
        etc.
        """
        C.git_repository_state_cleanup(self._repo)

    #
    # blame
    #
    def blame(self, path, flags=None, min_match_characters=None,
              newest_commit=None, oldest_commit=None, min_line=None,
              max_line=None):
        """
        Return a Blame object for a single file.

        Parameters:

        path
            Path to the file to blame.

        flags
            A GIT_BLAME_* constant.

        min_match_characters
            The number of alphanum chars that must be detected as moving/copying
            within a file for it to associate those lines with the parent commit.

        newest_commit
            The id of the newest commit to consider.

        oldest_commit
            The id of the oldest commit to consider.

        min_line
            The first line in the file to blame.

        max_line
            The last line in the file to blame.

        Examples::

            repo.blame('foo.c', flags=GIT_BLAME_TRACK_COPIES_SAME_FILE)
        """

        options = ffi.new('git_blame_options *')
        C.git_blame_init_options(options, C.GIT_BLAME_OPTIONS_VERSION)
        if min_match_characters:
            options.min_match_characters = min_match_characters
        if newest_commit:
            if not isinstance(newest_commit, Oid):
                newest_commit = Oid(hex=newest_commit)
            ffi.buffer(ffi.addressof(options, 'newest_commit'))[:] = newest_commit.raw
        if oldest_commit:
            if not isinstance(oldest_commit, Oid):
                oldest_commit = Oid(hex=oldest_commit)
            ffi.buffer(ffi.addressof(options, 'oldest_commit'))[:] = oldest_commit.raw
        if min_line:
            options.min_line = min_line
        if max_line:
            options.max_line = max_line

        cblame = ffi.new('git_blame **')
        err = C.git_blame_file(cblame, self._repo, to_bytes(path), options)
        check_error(err)

        return Blame._from_c(self, cblame[0])

    #
    # Index
    #
    @property
    def index(self):
        """Index representing the repository's index file."""
        cindex = ffi.new('git_index **')
        err = C.git_repository_index(cindex, self._repo)
        check_error(err, True)

        return Index.from_c(self, cindex)

    #
    # Merging
    #

    @staticmethod
    def _merge_options(favor):
        """Return a 'git_merge_opts *'"""

        def favor_to_enum(favor):
            if favor == 'normal':
                return C.GIT_MERGE_FILE_FAVOR_NORMAL
            elif favor == 'ours':
                return C.GIT_MERGE_FILE_FAVOR_OURS
            elif favor == 'theirs':
                return C.GIT_MERGE_FILE_FAVOR_THEIRS
            elif favor == 'union':
                return C.GIT_MERGE_FILE_FAVOR_UNION
            else:
                return None

        favor_val = favor_to_enum(favor)
        if favor_val is None:
            raise ValueError("unkown favor value %s" % favor)

        opts = ffi.new('git_merge_options *')
        err = C.git_merge_init_options(opts, C.GIT_MERGE_OPTIONS_VERSION)
        check_error(err)

        opts.file_favor = favor_val

        return opts

    def merge_file_from_index(self, ancestor, ours, theirs):
        """Merge files from index. Return a string with the merge result
        containing possible conflicts.

        ancestor
            The index entry which will be used as a common
            ancestor.
        ours
            The index entry to take as "ours" or base.
        theirs
            The index entry which will be merged into "ours"
        """
        cmergeresult = ffi.new('git_merge_file_result *')

        cancestor, ancestor_str_ref = (
            ancestor._to_c() if ancestor is not None else (ffi.NULL, ffi.NULL))
        cours, ours_str_ref = (
            ours._to_c() if ours is not None else (ffi.NULL, ffi.NULL))
        ctheirs, theirs_str_ref = (
            theirs._to_c() if theirs is not None else (ffi.NULL, ffi.NULL))

        err = C.git_merge_file_from_index(
            cmergeresult, self._repo,
            cancestor, cours, ctheirs,
            ffi.NULL);
        check_error(err)

        ret = ffi.string(cmergeresult.ptr,
                         cmergeresult.len).decode('utf-8')
        C.git_merge_file_result_free(cmergeresult)

        return ret

    def merge_commits(self, ours, theirs, favor='normal'):
        """
        Merge two arbitrary commits.

        Returns: an index with the result of the merge.

        Parameters:

        ours
            The commit to take as "ours" or base.

        theirs
            The commit which will be merged into "ours"

        favor
            How to deal with file-level conflicts. Can be one of

            * normal (default). Conflicts will be preserved.
            * ours. The "ours" side of the conflict region is used.
            * theirs. The "theirs" side of the conflict region is used.
            * union. Unique lines from each side will be used.

            For all but NORMAL, the index will not record a conflict.

        Both "ours" and "theirs" can be any object which peels to a commit or the id
        (string or Oid) of an object which peels to a commit.
        """

        ours_ptr = ffi.new('git_commit **')
        theirs_ptr = ffi.new('git_commit **')
        cindex = ffi.new('git_index **')

        if is_string(ours) or isinstance(ours, Oid):
            ours = self[ours]
        if is_string(theirs) or isinstance(theirs, Oid):
            theirs = self[theirs]

        ours = ours.peel(Commit)
        theirs = theirs.peel(Commit)

        opts = self._merge_options(favor)

        ffi.buffer(ours_ptr)[:] = ours._pointer[:]
        ffi.buffer(theirs_ptr)[:] = theirs._pointer[:]

        err = C.git_merge_commits(cindex, self._repo, ours_ptr[0], theirs_ptr[0], opts)
        check_error(err)

        return Index.from_c(self, cindex)

    def merge_trees(self, ancestor, ours, theirs, favor='normal'):
        """
        Merge two trees.

        Returns: an Index that reflects the result of the merge.

        Parameters:

        ancestor
            The tree which is the common ancestor between 'ours' and 'theirs'.

        ours
            The commit to take as "ours" or base.

        theirs
            The commit which will be merged into "ours".

        favor
            How to deal with file-level conflicts. Can be one of:

            * normal (default). Conflicts will be preserved.
            * ours. The "ours" side of the conflict region is used.
            * theirs. The "theirs" side of the conflict region is used.
            * union. Unique lines from each side will be used.

            For all but NORMAL, the index will not record a conflict.
        """

        ancestor_ptr = ffi.new('git_tree **')
        ours_ptr = ffi.new('git_tree **')
        theirs_ptr = ffi.new('git_tree **')
        cindex = ffi.new('git_index **')

        if is_string(ancestor) or isinstance(ancestor, Oid):
            ancestor = self[ancestor]
        if is_string(ours) or isinstance(ours, Oid):
            ours = self[ours]
        if is_string(theirs) or isinstance(theirs, Oid):
            theirs = self[theirs]

        ancestor = ancestor.peel(Tree)
        ours = ours.peel(Tree)
        theirs = theirs.peel(Tree)

        opts = self._merge_options(favor)

        ffi.buffer(ancestor_ptr)[:] = ancestor._pointer[:]
        ffi.buffer(ours_ptr)[:] = ours._pointer[:]
        ffi.buffer(theirs_ptr)[:] = theirs._pointer[:]

        err = C.git_merge_trees(cindex, self._repo, ancestor_ptr[0], ours_ptr[0], theirs_ptr[0], opts)
        check_error(err)

        return Index.from_c(self, cindex)

    #
    # Describe
    #
    def describe(self, committish=None, max_candidates_tags=None,
                 describe_strategy=None, pattern=None,
                 only_follow_first_parent=None,
                 show_commit_oid_as_fallback=None, abbreviated_size=None,
                 always_use_long_format=None, dirty_suffix=None):
        """
        Describe a commit-ish or the current working tree.

        Returns: The description (str).

        Parameters:

        committish : `str`, :class:`~.Reference`, or :class:`~.Commit`
            Commit-ish object or object name to describe, or `None` to describe
            the current working tree.

        max_candidates_tags : int
            The number of candidate tags to consider. Increasing above 10 will
            take slightly longer but may produce a more accurate result. A
            value of 0 will cause only exact matches to be output.

        describe_strategy : int
            Can be one of:

            * `GIT_DESCRIBE_DEFAULT` - Only match annotated tags. (This is
              equivalent to setting this parameter to `None`.)
            * `GIT_DESCRIBE_TAGS` - Match everything under refs/tags/
              (includes lightweight tags).
            * `GIT_DESCRIBE_ALL` - Match everything under refs/ (includes
              branches).

        pattern : str
            Only consider tags matching the given `glob(7)` pattern, excluding
            the "refs/tags/" prefix.

        only_follow_first_parent : bool
            Follow only the first parent commit upon seeing a merge commit.

        show_commit_oid_as_fallback : bool
            Show uniquely abbreviated commit object as fallback.

        abbreviated_size : int
            The minimum number of hexadecimal digits to show for abbreviated
            object names. A value of 0 will suppress long format, only showing
            the closest tag.

        always_use_long_format : bool
            Always output the long format (the nearest tag, the number of
            commits, and the abbrevated commit name) even when the committish
            matches a tag.

        dirty_suffix : str
            A string to append if the working tree is dirty.

        Example::

            repo.describe(pattern='public/*', dirty_suffix='-dirty')
        """

        options = ffi.new('git_describe_options *')
        C.git_describe_init_options(options, C.GIT_DESCRIBE_OPTIONS_VERSION)

        if max_candidates_tags is not None:
            options.max_candidates_tags = max_candidates_tags
        if describe_strategy is not None:
            options.describe_strategy = describe_strategy
        if pattern:
            # The returned pointer object has ownership on the allocated
            # memory. Make sure it is kept alive until git_describe_commit() or
            # git_describe_workdir() are called below.
            pattern_char = ffi.new('char[]', to_bytes(pattern))
            options.pattern = pattern_char
        if only_follow_first_parent is not None:
            options.only_follow_first_parent = only_follow_first_parent
        if show_commit_oid_as_fallback is not None:
            options.show_commit_oid_as_fallback = show_commit_oid_as_fallback

        result = ffi.new('git_describe_result **')
        if committish:
            if is_string(committish):
                committish = self.revparse_single(committish)

            commit = committish.peel(Commit)

            cptr = ffi.new('git_object **')
            ffi.buffer(cptr)[:] = commit._pointer[:]

            err = C.git_describe_commit(result, cptr[0], options)
        else:
            err = C.git_describe_workdir(result, self._repo, options)
        check_error(err)

        try:
            format_options = ffi.new('git_describe_format_options *')
            C.git_describe_init_format_options(format_options, C.GIT_DESCRIBE_FORMAT_OPTIONS_VERSION)

            if abbreviated_size is not None:
                format_options.abbreviated_size = abbreviated_size
            if always_use_long_format is not None:
                format_options.always_use_long_format = always_use_long_format
            dirty_ptr = None
            if dirty_suffix:
                dirty_ptr = ffi.new('char[]', to_bytes(dirty_suffix))
                format_options.dirty_suffix = dirty_ptr

            buf = ffi.new('git_buf *', (ffi.NULL, 0))

            err = C.git_describe_format(buf, result[0], format_options)
            check_error(err)

            try:
                return ffi.string(buf.ptr).decode('utf-8')
            finally:
                C.git_buf_free(buf)
        finally:
            C.git_describe_result_free(result[0])

    #
    # Stash
    #
    def stash(self, stasher, message=None, keep_index=False,
              include_untracked=False, include_ignored=False):
        """
        Save changes to the working directory to the stash.

        Returns: The Oid of the stash merge commit (Oid).

        Parameters:

        stasher : Signature
            The identity of the person doing the stashing.

        message : str
            An optional description of stashed state.

        keep_index : bool
            Leave changes already added to the index in the working directory.

        include_untracked : bool
            Also stash untracked files.

        include_ignored : bool
            Also stash ignored files.

        Example::

            >>> repo = pygit2.Repsitory('.')
            >>> repo.stash(repo.default_signature(), 'WIP: stashing')
        """

        if message:
            stash_msg = ffi.new('char[]', to_bytes(message))
        else:
            stash_msg = ffi.NULL

        flags = 0
        flags |= keep_index * C.GIT_STASH_KEEP_INDEX
        flags |= include_untracked * C.GIT_STASH_INCLUDE_UNTRACKED
        flags |= include_ignored * C.GIT_STASH_INCLUDE_IGNORED

        stasher_cptr = ffi.new('git_signature **')
        ffi.buffer(stasher_cptr)[:] = stasher._pointer[:]

        coid = ffi.new('git_oid *')
        err = C.git_stash_save(coid, self._repo, stasher_cptr[0], stash_msg, flags)
        check_error(err)

        return Oid(raw=bytes(ffi.buffer(coid)[:]))

    @staticmethod
    def _stash_args_to_options(reinstate_index=False, **kwargs):
        stash_opts = ffi.new('git_stash_apply_options *')
        check_error(C.git_stash_apply_init_options(stash_opts, 1))

        flags = reinstate_index * C.GIT_STASH_APPLY_REINSTATE_INDEX
        stash_opts.flags = flags

        copts, refs = Repository._checkout_args_to_options(**kwargs)
        stash_opts.checkout_options = copts[0]

        return stash_opts

    def stash_apply(self, index=0, **kwargs):
        """
        Apply a stashed state in the stash list to the working directory.

        Parameters:

        index : int
            The position within the stash list of the stash to apply. 0 is the
            most recent stash.

        reinstate_index : bool
            Try to reinstate stashed changes to the index.

        The checkout options may be customized using the same arguments taken by
        Repository.checkout().

        Example::

            >>> repo = pygit2.Repsitory('.')
            >>> repo.stash(repo.default_signature(), 'WIP: stashing')
            >>> repo.stash_apply(strategy=GIT_CHECKOUT_ALLOW_CONFLICTS)
        """
        stash_opts = Repository._stash_args_to_options(**kwargs)
        check_error(C.git_stash_apply(self._repo, index, stash_opts))

    def stash_drop(self, index=0):
        """
        Remove a stashed state from the stash list.

        Parameters:

        index : int
            The position within the stash list of the stash to remove. 0 is
            the most recent stash.
        """
        check_error(C.git_stash_drop(self._repo, index))

    def stash_pop(self, index=0, **kwargs):
        """Apply a stashed state and remove it from the stash list.

        For arguments, see Repository.stash_apply().
        """
        stash_opts = Repository._stash_args_to_options(**kwargs)
        check_error(C.git_stash_pop(self._repo, index, stash_opts))

    #
    # Utility for writing a tree into an archive
    #
    def write_archive(self, treeish, archive, timestamp=None, prefix=''):
        """
        Write treeish into an archive.

        If no timestamp is provided and 'treeish' is a commit, its committer
        timestamp will be used. Otherwise the current time will be used.

        All path names in the archive are added to 'prefix', which defaults to
        an empty string.

        Parameters:

        treeish
            The treeish to write.

        archive
            An archive from the 'tarfile' module.

        timestamp
            Timestamp to use for the files in the archive.

        prefix
            Extra prefix to add to the path names in the archive.

        Example::

            >>> import tarfile, pygit2
            >>>> with tarfile.open('foo.tar', 'w') as archive:
            >>>>     repo = pygit2.Repsitory('.')
            >>>>     repo.write_archive(repo.head.target, archive)
        """

        # Try to get a tree form whatever we got
        if isinstance(treeish, Tree):
            tree = treeish

        if isinstance(treeish, Oid) or is_string(treeish):
            treeish = self[treeish]

        # if we don't have a timestamp, try to get it from a commit
        if not timestamp:
            try:
                commit = treeish.peel(Commit)
                timestamp = commit.committer.time
            except Exception:
                pass

        # as a last resort, use the current timestamp
        if not timestamp:
            timestamp = int(time())

        tree = treeish.peel(Tree)

        index = Index()
        index.read_tree(tree)

        for entry in index:
            content = self[entry.id].read_raw()
            info = tarfile.TarInfo(prefix + entry.path)
            info.size = len(content)
            info.mtime = timestamp
            info.uname = info.gname = 'root'  # just because git does this
            if entry.mode == GIT_FILEMODE_LINK:
                info.type = tarfile.SYMTYPE
                info.linkname = content.decode("utf-8")
                info.mode = 0o777  # symlinks get placeholder
                info.size = 0
                archive.addfile(info)
            else:
                archive.addfile(info, StringIO(content))

    #
    # Ahead-behind, which mostly lives on its own namespace
    #
    def ahead_behind(self, local, upstream):
        """
        Calculate how many different commits are in the non-common parts of the
        history between the two given ids.

        Ahead is how many commits are in the ancestry of the 'local' commit
        which are not in the 'upstream' commit. Behind is the opposite.

        Returns: a tuple of two integers with the number of commits ahead and
        behind respectively.

        Parameters:

        local
            The commit which is considered the local or current state.

        upstream
            The commit which is considered the upstream.
        """

        if not isinstance(local, Oid):
            local = self.expand_id(local)

        if not isinstance(upstream, Oid):
            upstream = self.expand_id(upstream)

        ahead, behind = ffi.new('size_t*'), ffi.new('size_t*')
        oid1, oid2 = ffi.new('git_oid *'), ffi.new('git_oid *')
        ffi.buffer(oid1)[:] = local.raw[:]
        ffi.buffer(oid2)[:] = upstream.raw[:]
        err = C.git_graph_ahead_behind(ahead, behind, self._repo, oid1, oid2)
        check_error(err)

        return int(ahead[0]), int(behind[0])

    #
    # Git attributes
    #
    def get_attr(self, path, name, flags=0):
        """
        Retrieve an attribute for a file by path.

        Returns: a boolean, None if the value is unspecified, or string with
        the value of the attribute.

        Parameters:

        path
            The path of the file to look up attributes for, relative to the
            workdir root.

        name
            The name of the attribute to look up.

        flags
            A combination of GIT_ATTR_CHECK_ flags which determine the
            lookup order.
        """

        cvalue = ffi.new('char **')
        err = C.git_attr_get(cvalue, self._repo, flags, to_bytes(path), to_bytes(name))
        check_error(err)

        # Now let's see if we can figure out what the value is
        attr_kind = C.git_attr_value(cvalue[0])
        if attr_kind == C.GIT_ATTR_UNSPECIFIED_T:
            return None
        elif attr_kind == C.GIT_ATTR_TRUE_T:
            return True
        elif attr_kind == C.GIT_ATTR_FALSE_T:
            return False
        elif attr_kind == C.GIT_ATTR_VALUE_T:
            return ffi.string(cvalue[0]).decode('utf-8')

        assert False, "the attribute value from libgit2 is invalid"

    #
    # Identity for reference operations
    #
    @property
    def ident(self):
        cname = ffi.new('char **')
        cemail = ffi.new('char **')

        err = C.git_repository_ident(cname, cemail, self._repo)
        check_error(err)

        return (ffi.string(cname).decode('utf-8'), ffi.string(cemail).decode('utf-8'))

    def set_ident(self, name, email):
        """Set the identity to be used for reference operations

        Updates to some references also append data to their
        reflog. You can use this method to set what identity will be
        used. If none is set, it will be read from the configuration.
        """

        err = C.git_repository_set_ident(self._repo, to_bytes(name), to_bytes(email))
        check_error(err)

    def revert_commit(self, revert_commit, our_commit, mainline=0):
        """
        Reverts the given Commit against the given "our" Commit, producing an
        Index that reflects the result of the revert.

        Returns: an Index with the result of the revert.

        Parameters:

        revert_commit
            The Commit to revert.

        our_commit
            The Commit to revert against (eg, HEAD).

        mainline
            The parent of the revert Commit, if it is a merge (i.e. 1, 2).
        """
        cindex = ffi.new('git_index **')
        revert_commit_ptr = ffi.new('git_commit **')
        our_commit_ptr = ffi.new('git_commit **')

        ffi.buffer(revert_commit_ptr)[:] = revert_commit._pointer[:]
        ffi.buffer(our_commit_ptr)[:] = our_commit._pointer[:]

        opts = ffi.new('git_merge_options *')
        err = C.git_merge_init_options(opts, C.GIT_MERGE_OPTIONS_VERSION)
        check_error(err)

        err = C.git_revert_commit(
            cindex, self._repo, revert_commit_ptr[0], our_commit_ptr[0], mainline, opts
        )
        check_error(err)

        return Index.from_c(self, cindex)


class Branches(object):
    def __init__(self, repository, flag=GIT_BRANCH_ALL):
        self._repository = repository
        self._flag = flag

        if flag == GIT_BRANCH_ALL:
            self.local = Branches(repository, flag=GIT_BRANCH_LOCAL)
            self.remote = Branches(repository, flag=GIT_BRANCH_REMOTE)

    def __getitem__(self, name):
        branch = None
        if self._flag & GIT_BRANCH_LOCAL:
            branch = self._repository.lookup_branch(name, GIT_BRANCH_LOCAL)

        if branch is None and self._flag & GIT_BRANCH_REMOTE:
            branch = self._repository.lookup_branch(name, GIT_BRANCH_REMOTE)

        if branch is None:
            raise KeyError('Branch not found: {}'.format(name))

        return branch

    def get(self, key):
        try:
            return self[key]
        except KeyError:
            return None

    def __iter__(self):
        for branch_name in self._repository.listall_branches(self._flag):
            yield branch_name

    def create(self, name, commit, force=False):
        return self._repository.create_branch(name, commit, force)

    def delete(self, name):
        self[name].delete()

    def __contains__(self, name):
        return self.get(name) is not None


class References(object):
    def __init__(self, repository):
        self._repository = repository

    def __getitem__(self, name):
        return self._repository.lookup_reference(name)

    def get(self, key):
        try:
            return self[key]
        except KeyError:
            return None

    def __iter__(self):
        for ref_name in self._repository.listall_references():
            yield ref_name

    def create(self, name, target, force=False):
        return self._repository.create_reference(name, target, force)

    def delete(self, name):
        self[name].delete()

    def __contains__(self, name):
        return self.get(name) is not None

    @property
    def objects(self):
        return self._repository.listall_reference_objects()


class Repository(BaseRepository):
    def __init__(self, path, *args, **kwargs):
        if not isinstance(path, six.string_types):
            path = path.decode('utf-8')

        path_backend = init_file_backend(path)
        super(Repository, self).__init__(backend=path_backend, *args, **kwargs)

        self.branches = Branches(self)
        self.references = References(self)

    @classmethod
    def _from_c(cls, ptr, owned):
        cptr = ffi.new('git_repository **')
        cptr[0] = ptr
        repo = cls.__new__(cls)
        super(cls, repo)._from_c(bytes(ffi.buffer(cptr)[:]), owned)
        repo._common_init()
        return repo
