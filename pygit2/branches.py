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

from __future__ import annotations
from typing import TYPE_CHECKING

from .enums import BranchType, ReferenceType
from ._pygit2 import Commit, Oid

# Need BaseRepository for type hints, but don't let it cause a circular dependency
if TYPE_CHECKING:
    from .repository import BaseRepository


class Branches:
    def __init__(
        self, repository: BaseRepository, flag: BranchType = BranchType.ALL, commit=None
    ):
        self._repository = repository
        self._flag = flag
        if commit is not None:
            if isinstance(commit, Commit):
                commit = commit.id
            elif not isinstance(commit, Oid):
                commit = self._repository.expand_id(commit)
        self._commit = commit

        if flag == BranchType.ALL:
            self.local = Branches(repository, flag=BranchType.LOCAL, commit=commit)
            self.remote = Branches(repository, flag=BranchType.REMOTE, commit=commit)

    def __getitem__(self, name: str):
        branch = None
        if self._flag & BranchType.LOCAL:
            branch = self._repository.lookup_branch(name, BranchType.LOCAL)

        if branch is None and self._flag & BranchType.REMOTE:
            branch = self._repository.lookup_branch(name, BranchType.REMOTE)

        if branch is None or not self._valid(branch):
            raise KeyError(f'Branch not found: {name}')

        return branch

    def get(self, key: str):
        try:
            return self[key]
        except KeyError:
            return None

    def __iter__(self):
        for branch_name in self._repository.listall_branches(self._flag):
            if self._commit is None or self.get(branch_name) is not None:
                yield branch_name

    def create(self, name: str, commit, force=False):
        return self._repository.create_branch(name, commit, force)

    def delete(self, name: str):
        self[name].delete()

    def _valid(self, branch):
        if branch.type == ReferenceType.SYMBOLIC:
            branch = branch.resolve()

        return (
            self._commit is None
            or branch.target == self._commit
            or self._repository.descendant_of(branch.target, self._commit)
        )

    def with_commit(self, commit):
        assert self._commit is None
        return Branches(self._repository, self._flag, commit)

    def __contains__(self, name):
        return self.get(name) is not None
