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

from ._pygit2 import Oid
from .callbacks import git_fetch_options
from .errors import check_error
from .ffi import ffi, C
from .utils import to_bytes


# GIT_SUBMODULE_UPDATE_*
GIT_SUBMODULE_UPDATE_CHECKOUT = C.GIT_SUBMODULE_UPDATE_CHECKOUT
GIT_SUBMODULE_UPDATE_REBASE   = C.GIT_SUBMODULE_UPDATE_REBASE
GIT_SUBMODULE_UPDATE_MERGE    = C.GIT_SUBMODULE_UPDATE_MERGE
GIT_SUBMODULE_UPDATE_NONE     = C.GIT_SUBMODULE_UPDATE_NONE
GIT_SUBMODULE_UPDATE_DEFAULT  = C.GIT_SUBMODULE_UPDATE_DEFAULT

# GIT_SUBMODULE_RECURSE_*
GIT_SUBMODULE_RECURSE_NO       = C.GIT_SUBMODULE_RECURSE_NO
GIT_SUBMODULE_RECURSE_YES      = C.GIT_SUBMODULE_RECURSE_YES
GIT_SUBMODULE_RECURSE_ONDEMAND = C.GIT_SUBMODULE_RECURSE_ONDEMAND

# GIT_SUBMODULE_IGNORE_*
GIT_SUBMODULE_IGNORE_UNSPECIFIED = C.GIT_SUBMODULE_IGNORE_UNSPECIFIED
GIT_SUBMODULE_IGNORE_NONE        = C.GIT_SUBMODULE_IGNORE_NONE
GIT_SUBMODULE_IGNORE_UNTRACKED   = C.GIT_SUBMODULE_IGNORE_UNTRACKED
GIT_SUBMODULE_IGNORE_DIRTY       = C.GIT_SUBMODULE_IGNORE_DIRTY
GIT_SUBMODULE_IGNORE_ALL         = C.GIT_SUBMODULE_IGNORE_ALL

# GIT_SUBMODULE_STATUS_*
GIT_SUBMODULE_STATUS_IN_HEAD           = C.GIT_SUBMODULE_STATUS_IN_HEAD
GIT_SUBMODULE_STATUS_IN_INDEX          = C.GIT_SUBMODULE_STATUS_IN_INDEX
GIT_SUBMODULE_STATUS_IN_CONFIG         = C.GIT_SUBMODULE_STATUS_IN_CONFIG
GIT_SUBMODULE_STATUS_IN_WD             = C.GIT_SUBMODULE_STATUS_IN_WD
GIT_SUBMODULE_STATUS_INDEX_ADDED       = C.GIT_SUBMODULE_STATUS_INDEX_ADDED
GIT_SUBMODULE_STATUS_INDEX_DELETED     = C.GIT_SUBMODULE_STATUS_INDEX_DELETED
GIT_SUBMODULE_STATUS_INDEX_MODIFIED    = C.GIT_SUBMODULE_STATUS_INDEX_MODIFIED
GIT_SUBMODULE_STATUS_WD_UNINITIALIZED  = C.GIT_SUBMODULE_STATUS_WD_UNINITIALIZED
GIT_SUBMODULE_STATUS_WD_ADDED          = C.GIT_SUBMODULE_STATUS_WD_ADDED
GIT_SUBMODULE_STATUS_WD_DELETED        = C.GIT_SUBMODULE_STATUS_WD_DELETED
GIT_SUBMODULE_STATUS_WD_MODIFIED       = C.GIT_SUBMODULE_STATUS_WD_MODIFIED
GIT_SUBMODULE_STATUS_WD_INDEX_MODIFIED = C.GIT_SUBMODULE_STATUS_WD_INDEX_MODIFIED
GIT_SUBMODULE_STATUS_WD_WD_MODIFIED    = C.GIT_SUBMODULE_STATUS_WD_WD_MODIFIED
GIT_SUBMODULE_STATUS_WD_UNTRACKED      = C.GIT_SUBMODULE_STATUS_WD_UNTRACKED


class Submodule:

    @classmethod
    def _from_c(cls, repo, cptr):
        subm = cls.__new__(cls)

        subm._repo = repo
        subm._subm = cptr

        return subm

    def __del__(self):
        C.git_submodule_free(self._subm)

    def open(self):
        """Open the repository for a submodule."""
        crepo = ffi.new('git_repository **')
        err = C.git_submodule_open(crepo, self._subm)
        check_error(err)

        return self._repo._from_c(crepo[0], True)

    def init(self, force=False):
        """Copy submodule info into ".git/config" file.

        Parameters:

        force
            Force entry to be updated.
        """
        cforce = 1 if force else 0
        err = C.git_submodule_init(self._subm, cforce)
        check_error(err)

    def update(self, init=False, callbacks=None):
        """Update a submodule.

        This will clone a missing submodule and checkout the subrepository to the commit
        specified in the index of the containing repository. If the submodule repository
        doesn't contain the target commit (e.g. because fetchRecurseSubmodules isn't set),
        then the submodule is fetched using the fetch options supplied in options.

        Parameters:

        init
            If the submodule is not initialized, setting this flag to true will initialize
            the submodule before updating. Otherwise, this will return an error if attempting
            to update an uninitialzed repository. but setting this to true forces them to be
            updated.

        callbacks
            Configuration options for the update."""
        opts = ffi.new('git_submodule_update_options *')
        C.git_submodule_update_init_options(opts, C.GIT_SUBMODULE_UPDATE_OPTIONS_VERSION)

        with git_fetch_options(callbacks, opts=opts.fetch_opts) as payload:
            i = 1 if init else 0
            err = C.git_submodule_update(self._subm, i, opts)
            payload.check_error(err)

    def sync(self):
        """Copy submodule remote info into submodule repo."""
        err = C.git_submodule_sync(self._subm)
        check_error(err)

    def reload(self, force=False):
        """Reread submodule info from config, index, and HEAD.

        Parameters:

        force
            Force reload even if the data doesn't seem out of date.
        """
        cforce = 1 if force else 0
        err = C.git_submodule_reload(self._subm, cforce)
        check_error(err)

    def add_to_index(self, write_index=False):
        """Add current submodule HEAD commit to index of superproject.

        Parameters:

        write_index
            Immediately write the index file.
        """
        cwrite_index = 1 if write_index else 0
        err = C.git_submodule_add_to_index(self._subm, cwrite_index)
        check_error(err)

    def status(self, ignore=GIT_SUBMODULE_IGNORE_UNSPECIFIED):
        """Get the status for a submodule."""
        crepo = self._repo._repo
        cname = ffi.new('char[]', to_bytes(self.name))
        cstatus = ffi.new('uint *')

        err = C.git_submodule_status(cstatus, crepo, cname, ignore)
        check_error(err)

        return cstatus[0]

    @property
    def name(self):
        """Name of the submodule."""
        name = C.git_submodule_name(self._subm)
        return ffi.string(name).decode('utf-8')

    @property
    def owner(self):
        """The parent repository"""
        return self._repo

    @property
    def path(self):
        """Path of the submodule."""
        path = C.git_submodule_path(self._subm)
        return ffi.string(path).decode('utf-8')

    @property
    def url(self):
        """URL of the submodule."""
        url = C.git_submodule_url(self._subm)
        return ffi.string(url).decode('utf-8')

    @url.setter
    def url(self, u):
        """Set the URL for the submodule in the configuration."""
        crepo = self._repo._repo
        cname = ffi.new('char[]', to_bytes(self.name))
        curl = ffi.new('char[]', to_bytes(u))

        err = C.git_submodule_set_url(crepo, cname, curl)
        check_error(err)

    @property
    def branch(self):
        """Branch that is to be tracked by the submodule."""
        branch = C.git_submodule_branch(self._subm)
        return ffi.string(branch).decode('utf-8')

    @branch.setter
    def branch(self, b):
        """Set the branch for the submodule in the configuration."""
        crepo = self._repo._repo
        cname = ffi.new('char[]', to_bytes(self.name))
        cbranch = ffi.new('char[]', to_bytes(b))

        err = C.git_submodule_set_branch(crepo, cname, cbranch)
        check_error(err)

    @property
    def head_id(self):
        """Head of the submodule."""
        head = C.git_submodule_head_id(self._subm)
        return Oid(raw=bytes(ffi.buffer(head)[:]))

    @property
    def index_id(self):
        """Index OID of the submodule."""
        oid = C.git_submodule_index_id(self._subm)
        return Oid(raw=bytes(ffi.buffer(oid)[:]))

    @property
    def wd_id(self):
        """Current working directory OID of the submodule."""
        oid = C.git_submodule_wd_id(self._subm)
        return Oid(raw=bytes(ffi.buffer(oid)[:]))

    @property
    def ignore_rule(self):
        """Get the ignore rule that will be used for the submodule."""
        res = C.git_submodule_ignore(self._subm)
        return res

    @ignore_rule.setter
    def ignore_rule(self, i):
        """Set the ignore rule for the submodule in the configuration."""
        crepo = self._repo._repo
        cname = ffi.new('char[]', to_bytes(self.name))

        err = C.git_submodule_set_ignore(crepo, cname, i)
        check_error(err)


    @property
    def fetch_recurse_rule(self):
        """Get the fetchRecurseSubmodules rule for a submodule."""
        res = C.git_submodule_fetch_recurse_submodules(self._subm)
        return res

    @fetch_recurse_rule.setter
    def fetch_recurse_rule(self, f):
        """Set the fetchRecurseSubmodules rule for a submodule in the configuration."""
        crepo = self._repo._repo
        cname = ffi.new('char[]', to_bytes(self.name))

        C.git_submodule_set_fetch_recurse_submodules(crepo, cname, f)

    @property
    def update_rule(self):
        """Get the update rule that will be used for the submodule."""
        res = C.git_submodule_update_strategy(self._subm)
        return res

    @update_rule.setter
    def update_rule(self, u):
        """Set the ignore rule for the submodule in the configuration."""
        crepo = self._repo._repo
        cname = ffi.new('char[]', to_bytes(self.name))

        err = C.git_submodule_set_update(crepo, cname, u)
        check_error(err)
