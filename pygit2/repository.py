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

# Import from pygit2
from _pygit2 import Repository as _Repository
from _pygit2 import Oid, GIT_OID_HEXSZ, GIT_OID_MINPREFIXLEN
from _pygit2 import GIT_CHECKOUT_SAFE_CREATE, GIT_DIFF_NORMAL
from _pygit2 import Reference, Tree, Commit, Blob

from .config import Config
from .errors import check_error
from .ffi import ffi, C
from .index import Index
from .remote import Remote
from .utils import to_bytes


class Repository(_Repository):

    def __init__(self, *args, **kwargs):
        super(Repository, self).__init__(*args, **kwargs)

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
        """

        cremote = ffi.new('git_remote **')

        err = C.git_remote_create(cremote, self._repo, to_bytes(name),
                                  to_bytes(url))
        check_error(err)

        return Remote(self, cremote[0])

    @property
    def remotes(self):
        """Returns all configured remotes"""

        names = ffi.new('git_strarray *')

        try:
            err = C.git_remote_list(names, self._repo)
            check_error(err)

            l = [None] * names.count
            cremote = ffi.new('git_remote **')
            for i in range(names.count):
                err = C.git_remote_load(cremote, self._repo, names.strings[i])
                check_error(err)

                l[i] = Remote(self, cremote[0])
            return l
        finally:
            C.git_strarray_free(names)

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

        If no reference is given, checkout from the index.

        Arguments:

        :param str refname: The reference to checkout. After checkout,
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
        if type(refname) is Reference:
            reference = refname
            refname = refname.name
        else:
            reference = self.lookup_reference(refname)

        oid = reference.resolve().target
        treeish = self[oid]
        self.checkout_tree(treeish, **kwargs)
        self.head = refname

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

        def treeish_to_tree(obj):
            try:
                obj = self.revparse_single(obj)
            except:
                pass

            if isinstance(obj, Commit):
                return obj.tree
            elif isinstance(obj, Reference):
                oid = obj.resolve().target
                return self[oid]

        a = treeish_to_tree(a) or a
        b = treeish_to_tree(b) or b

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
