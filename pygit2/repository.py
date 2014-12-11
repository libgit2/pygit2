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

# Import from the Standard Library
from string import hexdigits
import sys, tarfile
from time import time
if sys.version_info[0] < 3:
    from cStringIO import StringIO
else:
    from io import BytesIO as StringIO

# Import from pygit2
from _pygit2 import Repository as _Repository
from _pygit2 import Oid, GIT_OID_HEXSZ, GIT_OID_MINPREFIXLEN
from _pygit2 import GIT_CHECKOUT_SAFE_CREATE, GIT_DIFF_NORMAL
from _pygit2 import GIT_FILEMODE_LINK
from _pygit2 import Reference, Tree, Commit, Blob

from .config import Config
from .errors import check_error
from .ffi import ffi, C
from .index import Index
from .remote import RemoteCollection
from .blame import Blame
from .utils import to_bytes, is_string


class Repository(_Repository):

    def __init__(self, *args, **kwargs):
        super(Repository, self).__init__(*args, **kwargs)
        self._common_init()

    @classmethod
    def _from_c(cls, ptr, owned):
        cptr = ffi.new('git_repository **')
        cptr[0] = ptr
        repo = cls.__new__(cls)
        super(cls, repo)._from_c(bytes(ffi.buffer(cptr)[:]), owned)
        repo._common_init()
        return repo

    def _common_init(self):
        self.remotes = RemoteCollection(self)

        # Get the pointer as the contents of a buffer and store it for
        # later access
        repo_cptr = ffi.new('git_repository **')
        ffi.buffer(repo_cptr)[:] = self._pointer[:]
        self._repo = repo_cptr[0]

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
        """create_remote(name, url) -> Remote

        Creates a new remote.

        This method is deprecated, please use Remote.remotes.create()
        """

        return self.remotes.create(name, url)

    #
    # Configuration
    #
    @property
    def config(self):
        """The configuration file for this repository

        If a the configuration hasn't been set yet, the default config for
        repository will be returned, including global and system configurations
        (if they are available)."""

        cconfig = ffi.new('git_config **')
        err = C.git_repository_config(cconfig, self._repo)
        check_error(err)

        return Config.from_c(self, cconfig[0])

    @property
    def config_snapshot(self):
        """A snapshot for this repositiory's configuration

        This allows reads over multiple values to use the same version
        of the configuration files"""

        cconfig = ffi.new('git_config **')
        err = C.git_repository_config_snapshot(cconfig, self._repo)
        check_error(err)

        return Config.from_c(self, cconfig[0])

    #
    # References
    #
    def create_reference(self, name, target, force=False):
        """
        Create a new reference "name" which points to an object or to another
        reference.

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

        # pygit2's default is SAFE_CREATE
        copts.checkout_strategy = GIT_CHECKOUT_SAFE_CREATE
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
        Checkout the given reference using the given strategy, and update
        the HEAD.
        The reference may be a reference name or a Reference object.
        The default strategy is GIT_CHECKOUT_SAFE_CREATE.

        To checkout from the HEAD, just pass 'HEAD'::

          >>> checkout('HEAD')

        This is identical to calling checkout_head().

        If no reference is given, checkout from the index.

        Arguments:

        :param str|Reference refname: The reference to checkout. After checkout,
          the current branch will be switched to this one.

        :param int strategy: A ``GIT_CHECKOUT_`` value. The default is
          ``GIT_CHECKOUT_SAFE_CREATE``.

        :param str directory: Alternative checkout path to workdir.

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
        head = self.lookup_reference('HEAD')
        if head.type == C.GIT_REF_SYMBOLIC:
            from_ = self.head.shorthand
        else:
            from_ = head.target.hex

        try:
            signature = self.default_signature
        except Exception:
            signature = None

        reflog_text = "checkout: moving from %s to %s" % (from_, reference)
        self.set_head(refname, signature, reflog_text)

    #
    # Setting HEAD
    #
    def set_head(self, target, signature=None, message=None):
        """Set HEAD to point to the given target

        Arguments:

        target
            The new target for HEAD. Can be a string or Oid (to detach)

        signature
            Signature to use for the reflog. If not provided, the repository's
            default will be used

        message
            Message to use for the reflog
        """

        sig_ptr = ffi.new('git_signature **')
        if signature:
            ffi.buffer(sig_ptr)[:] = signature._pointer[:]

        message_ptr = ffi.NULL
        if message_ptr:
            message_ptr = to_bytes(message)

        if isinstance(target, Oid):
            oid = ffi.new('git_oid *')
            ffi.buffer(oid)[:] = target.raw[:]
            err = C.git_repository_set_head_detached(self._repo, oid, sig_ptr[0], message_ptr)
            check_error(err)
            return

        # if it's a string, then it's a reference name
        err = C.git_repository_set_head(self._repo, to_bytes(target), sig_ptr[0], message_ptr)
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

        cached
            use staged changes instead of workdir

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
                pass

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
            raise NotImplementedError('git_diff_blob_to_blob()')

        raise ValueError("Only blobs and treeish can be diffed")

    def state_cleanup(self):
        """
        Remove all the metadata associated with an ongoing command like
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
        """Return a Blame object for a single file.

        Arguments:

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

            repo.blame('foo.c', flags=GIT_BLAME_TRACK_COPIES_SAME_FILE)");
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
        """Index representing the repository's index file
        """
        cindex = ffi.new('git_index **')
        err = C.git_repository_index(cindex, self._repo)
        check_error(err, True)

        return Index.from_c(self, cindex)

    #
    # Merging
    #
    def merge_commits(self, ours, theirs, favor='normal'):
        """Merge two arbitrary commits

        Arguments:

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

            for all but NORMAL, the index will not record a conflict.

        Both "ours" and "theirs" can be any object which peels to a commit or the id
        (string or Oid) of an object which peels to a commit.

        Returns an index with the result of the merge

        """
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

        ours_ptr = ffi.new('git_commit **')
        theirs_ptr = ffi.new('git_commit **')
        opts = ffi.new('git_merge_options *')
        cindex = ffi.new('git_index **')

        if is_string(ours) or isinstance(ours, Oid):
            ours = self[ours]
        if is_string(theirs) or isinstance(theirs, Oid):
            theirs = self[theirs]

        ours = ours.peel(Commit)
        theirs = theirs.peel(Commit)

        err = C.git_merge_init_options(opts, C.GIT_MERGE_OPTIONS_VERSION)
        check_error(err)

        favor_val = favor_to_enum(favor)
        if favor_val is None:
            raise ValueError("unkown favor value %s" % favor)

        opts.file_favor = favor_val

        ffi.buffer(ours_ptr)[:] = ours._pointer[:]
        ffi.buffer(theirs_ptr)[:] = theirs._pointer[:]

        err = C.git_merge_commits(cindex, self._repo, ours_ptr[0], theirs_ptr[0], opts)
        check_error(err)

        return Index.from_c(self, cindex)
    #
    # Utility for writing a tree into an archive
    #
    def write_archive(self, treeish, archive, timestamp=None):
        """Write treeish into an archive

        If no timestamp is provided and 'treeish' is a commit, its committer
        timestamp will be used. Otherwise the current time will be used.

        Arguments:

        treeish
            The treeish to write.
        archive
            An archive from the 'tarfile' module
        timestamp
            Timestamp to use for the files in the archive.

        Example::

            >>> import tarfile, pygit2
            >>>> with tarfile.open('foo.tar', 'w') as archive:
            >>>>     repo = pygit2.Repsitory('.')
            >>>>     repo.write_archive(archive, repo.head.target)
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
            info = tarfile.TarInfo(entry.path)
            info.size = len(content)
            info.mtime = timestamp
            info.uname = info.gname = 'root' # just because git does this
            if entry.mode == GIT_FILEMODE_LINK:
                info.type = archive.SYMTYPE
                info.linkname = content
                info.mode = 0o777 # symlinks get placeholder

            archive.addfile(info, StringIO(content))
