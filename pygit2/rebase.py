# Copyright 2010-2026 The pygit2 contributors
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

from typing import TYPE_CHECKING

# Import from pygit2
from ._pygit2 import Oid, Signature
from .enums import RebaseOperationType
from .errors import check_error
from .ffi import C, ffi
from .index import Index
from .utils import decode_string

if TYPE_CHECKING:
    from ._libgit2.ffi import GitRebaseC, GitRebaseOperationC
    from .repository import BaseRepository


def _signature_ptr(signature: 'Signature | None'):
    """Return a git_signature* cdata for the given signature, or ffi.NULL.

    The returned pointer borrows the memory owned by the Signature object,
    which the caller must keep alive for the duration of the C call.
    """
    if signature is None:
        return ffi.NULL
    ptr = ffi.new('git_signature **')
    ffi.buffer(ptr)[:] = signature._pointer[:]
    return ptr[0]


class RebaseOperation:
    """A single instruction to be performed during a rebase."""

    def __init__(self, type: RebaseOperationType, id: Oid, exec: 'str | None') -> None:
        self.type = type
        'The type of rebase operation.'

        self.id = id
        """The commit ID being cherry-picked.  For operations of type
        RebaseOperationType.EXEC this is the zero OID."""

        self.exec = exec
        """The executable the user has requested be run.  This will only
        be populated for operations of type RebaseOperationType.EXEC."""

    @classmethod
    def _from_c(cls, coperation: 'GitRebaseOperationC') -> 'RebaseOperation':
        type = RebaseOperationType(coperation.type)
        id = Oid(raw=bytes(ffi.buffer(ffi.addressof(coperation, 'id'))[:]))
        exec = decode_string(coperation.exec)
        return cls(type, id, exec)

    def __repr__(self) -> str:
        return f'<pygit2.RebaseOperation {self.type.name} {self.id}>'


class Rebase:
    """An in-progress rebase.

    Returned by Repository.rebase_init() and Repository.rebase_open().
    Iterating over this object performs the rebase operations one by one;
    each must be committed with commit(), after resolving any conflicts
    that were left in the repository's index.  Finalize with finish(), or
    roll everything back with abort().
    """

    def __init__(
        self, repo: 'BaseRepository', crebase: 'GitRebaseC', refs: list
    ) -> None:
        """The constructor is for internal use only."""
        self._repo = repo
        self._rebase = ffi.gc(crebase, C.git_rebase_free)
        # Keep alive the git_rebase_options and every cdata it points into:
        # libgit2 reads the options during __next__() and abort(), long
        # after rebase_init() returned.
        self._refs = refs

    def __len__(self) -> int:
        """The total number of rebase operations."""
        return C.git_rebase_operation_entrycount(self._rebase)

    def __getitem__(self, index: int) -> RebaseOperation:
        """The rebase operation at the given index."""
        if index < 0:
            index += len(self)
        if index < 0:
            raise IndexError('rebase operation index out of range')
        coperation = C.git_rebase_operation_byindex(self._rebase, index)
        if coperation == ffi.NULL:
            raise IndexError('rebase operation index out of range')
        return RebaseOperation._from_c(coperation)

    def __iter__(self) -> 'Rebase':
        return self

    def __next__(self) -> RebaseOperation:
        """
        Perform the next rebase operation and return it.

        If the operation is one that applies a patch (which is any
        operation except RebaseOperationType.EXEC) then the patch will be
        applied and the index and working directory will be updated with
        the changes.  If there are conflicts, you will need to address
        those before calling commit().

        Raises StopIteration when there are no more operations to perform.
        """
        coperation = ffi.new('git_rebase_operation **')
        err = C.git_rebase_next(coperation, self._rebase)
        check_error(err)  # raises StopIteration on GIT_ITEROVER
        return RebaseOperation._from_c(coperation[0])

    @property
    def current_index(self) -> 'int | None':
        """The index of the rebase operation that is currently being
        applied, or None if the first operation has not yet been applied
        (because __next__() has not been called yet)."""
        index = C.git_rebase_operation_current(self._rebase)
        if index == C.GIT_REBASE_NO_OPERATION:
            return None
        return index

    @property
    def inmemory_index(self) -> Index:
        """
        The index produced by the last operation, which is the result of
        __next__() and which will be committed by the next invocation of
        commit().  This is useful for resolving conflicts in an in-memory
        rebase before committing them.

        This is only applicable for in-memory rebases; for rebases within
        a working directory, the changes were applied to the repository's
        index.
        """
        cindex = ffi.new('git_index **')
        err = C.git_rebase_inmemory_index(cindex, self._rebase)
        check_error(err)
        return Index.from_c(self._repo, cindex)

    def commit(
        self,
        committer: Signature,
        author: 'Signature | None' = None,
        message: 'str | None' = None,
    ) -> 'Oid | None':
        """
        Commit the current patch and return the id of the new commit, or
        None if the current commit has already been applied to the upstream
        and there is nothing to commit — mirroring how `git rebase` skips
        already-applied patches.  You must have resolved any conflicts that
        were introduced during the patch application from the last
        __next__() invocation.

        Raises GitError if there are unmerged changes in the index.

        Parameters:

        committer : Signature
            The committer of the rebase.

        author : Signature
            The author of the updated commit, or None to keep the author
            from the original commit.

        message : str
            The message for this commit, or None to use the message from
            the original commit.
        """
        cmessage = (
            ffi.new('char[]', message.encode('utf-8'))
            if message is not None
            else ffi.NULL
        )
        coid = ffi.new('git_oid *')
        err = C.git_rebase_commit(
            coid,
            self._rebase,
            _signature_ptr(author),
            _signature_ptr(committer),
            ffi.NULL,
            cmessage,
        )
        if err == C.GIT_EAPPLIED:
            return None
        check_error(err)
        return Oid(raw=bytes(ffi.buffer(coid)[:]))

    def finish(self, signature: 'Signature | None' = None) -> None:
        """
        Finish the rebase once all patches have been applied.

        Parameters:

        signature : Signature
            The identity that is finishing the rebase (optional).
        """
        err = C.git_rebase_finish(self._rebase, _signature_ptr(signature))
        check_error(err)

    def abort(self) -> None:
        """Abort the rebase, resetting the repository and working
        directory to their state before the rebase began."""
        err = C.git_rebase_abort(self._rebase)
        check_error(err)

    @property
    def orig_head_name(self) -> 'str | None':
        """The original HEAD ref name."""
        return decode_string(C.git_rebase_orig_head_name(self._rebase))

    @property
    def orig_head_id(self) -> Oid:
        """The original HEAD id."""
        coid = C.git_rebase_orig_head_id(self._rebase)
        return Oid(raw=bytes(ffi.buffer(coid)[:]))

    @property
    def onto_name(self) -> 'str | None':
        """The onto ref name."""
        return decode_string(C.git_rebase_onto_name(self._rebase))

    @property
    def onto_id(self) -> Oid:
        """The onto id."""
        coid = C.git_rebase_onto_id(self._rebase)
        return Oid(raw=bytes(ffi.buffer(coid)[:]))
