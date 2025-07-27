# Copyright 2010-2025 The pygit2 contributors
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

from typing import Any, Generic, Literal, NewType, SupportsIndex, TypeVar, overload

from pygit2._pygit2 import Repository

T = TypeVar('T')

NULL_TYPE = NewType('NULL_TYPE', object)
NULL: NULL_TYPE = ...

char = NewType('char', object)
char_pointer = NewType('char_pointer', object)

class _Pointer(Generic[T]):
    def __setitem__(self, item: Literal[0], a: T) -> None: ...
    @overload
    def __getitem__(self, item: Literal[0]) -> T: ...
    @overload
    def __getitem__(self, item: slice[None, None, None]) -> bytes: ...

class GitTimeC:
    # incomplete
    time: int
    offset: int

class GitSignatureC:
    name: char_pointer
    email: char_pointer
    when: GitTimeC

class GitHunkC:
    # incomplete
    boundary: char
    final_start_line_number: int
    final_signature: GitSignatureC
    orig_signature: GitSignatureC
    orig_start_line_number: int
    orig_path: char_pointer
    lines_in_hunk: int

class GitRepositoryC:
    # incomplete
    # TODO: this has to be unified with pygit2._pygit2(pyi).Repository
    def _from_c(cls, ptr: 'GitRepositoryC', owned: bool) -> 'Repository': ...

class GitFetchOptionsC:
    # TODO: FetchOptions exist in _pygit2.pyi
    # incomplete
    depth: int

class GitSubmoduleC:
    pass

class GitSubmoduleUpdateOptionsC:
    fetch_opts: GitFetchOptionsC

class UnsignedIntC:
    def __getitem__(self, item: Literal[0]) -> int: ...

class GitOidC:
    id: _Pointer[bytes]

class GitBlameOptionsC:
    flags: int
    min_match_characters: int
    newest_commit: object
    oldest_commit: object
    min_line: int
    max_line: int

class GitBlameC:
    # incomplete
    pass

class GitMergeOptionsC:
    file_favor: int
    flags: int
    file_flags: int

class GitAnnotatedCommitC:
    pass

class GitAttrOptionsC:
    # incomplete
    version: int
    flags: int

class GitBufC:
    ptr: char_pointer

class GitCheckoutOptionsC:
    # incomplete
    checkout_strategy: int

class GitCommitC:
    pass

class GitConfigC:
    pass

class GitDescribeFormatOptionsC:
    version: int
    abbreviated_size: int
    always_use_long_format: int
    dirty_suffix: char_pointer

class GitDescribeOptionsC:
    version: int
    max_candidates_tags: int
    describe_strategy: int
    pattern: char_pointer
    only_follow_first_parent: int
    show_commit_oid_as_fallback: int

class GitDescribeResultC:
    pass

class GitIndexC:
    pass

class GitMergeFileResultC:
    pass

class GitObjectC:
    pass

class GitStashSaveOptionsC:
    version: int
    flags: int
    stasher: GitSignatureC
    message: char_pointer
    paths: GitStrrayC

class GitStrrayC:
    pass

class GitTreeC:
    pass

class GitRepositoryInitOptionsC:
    version: int
    flags: int
    mode: int
    workdir_path: char_pointer
    description: char_pointer
    template_path: char_pointer
    initial_head: char_pointer
    origin_url: char_pointer

class GitCloneOptionsC:
    pass

class GitProxyTC:
    pass

class GitProxyOptionsC:
    version: int
    type: GitProxyTC
    url: char_pointer
    # credentials
    # certificate_check
    # payload

class GitRemoteC:
    pass

class GitReferenceC:
    pass

def string(a: char_pointer) -> bytes: ...
@overload
def new(a: Literal['git_repository **']) -> _Pointer[GitRepositoryC]: ...
@overload
def new(a: Literal['git_remote **']) -> _Pointer[GitRemoteC]: ...
@overload
def new(a: Literal['git_repository_init_options *']) -> GitRepositoryInitOptionsC: ...
@overload
def new(a: Literal['git_submodule_update_options *']) -> GitSubmoduleUpdateOptionsC: ...
@overload
def new(a: Literal['git_submodule **']) -> _Pointer[GitSubmoduleC]: ...
@overload
def new(a: Literal['unsigned int *']) -> UnsignedIntC: ...
@overload
def new(a: Literal['git_proxy_options *']) -> GitProxyOptionsC: ...
@overload
def new(a: Literal['git_oid *']) -> GitOidC: ...
@overload
def new(a: Literal['git_blame **']) -> _Pointer[GitBlameC]: ...
@overload
def new(a: Literal['git_clone_options *']) -> GitCloneOptionsC: ...
@overload
def new(a: Literal['git_merge_options *']) -> GitMergeOptionsC: ...
@overload
def new(a: Literal['git_blame_options *']) -> GitBlameOptionsC: ...
@overload
def new(a: Literal['git_annotated_commit **']) -> _Pointer[GitAnnotatedCommitC]: ...
@overload
def new(a: Literal['git_attr_options *']) -> GitAttrOptionsC: ...
@overload
def new(a: Literal['git_buf *']) -> GitBufC: ...
@overload
def new(a: Literal['git_checkout_options *']) -> GitCheckoutOptionsC: ...
@overload
def new(a: Literal['git_commit **']) -> _Pointer[GitCommitC]: ...
@overload
def new(a: Literal['git_config *']) -> GitConfigC: ...
@overload
def new(a: Literal['git_describe_format_options *']) -> GitDescribeFormatOptionsC: ...
@overload
def new(a: Literal['git_describe_options *']) -> GitDescribeOptionsC: ...
@overload
def new(a: Literal['git_describe_result *']) -> GitDescribeResultC: ...
@overload
def new(a: Literal['git_describe_result **']) -> _Pointer[GitDescribeResultC]: ...
@overload
def new(a: Literal['struct git_reference **']) -> _Pointer[GitReferenceC]: ...
@overload
def new(a: Literal['git_index **']) -> _Pointer[GitIndexC]: ...
@overload
def new(a: Literal['git_merge_file_result *']) -> GitMergeFileResultC: ...
@overload
def new(a: Literal['git_object *']) -> GitObjectC: ...
@overload
def new(a: Literal['git_object **']) -> _Pointer[GitObjectC]: ...
@overload
def new(a: Literal['git_signature *']) -> GitSignatureC: ...
@overload
def new(a: Literal['git_signature **']) -> _Pointer[GitSignatureC]: ...
@overload
def new(a: Literal['git_stash_save_options *']) -> GitStashSaveOptionsC: ...
@overload
def new(a: Literal['git_tree **']) -> _Pointer[GitTreeC]: ...
@overload
def new(a: Literal['git_buf *'], b: tuple[NULL_TYPE, Literal[0]]) -> GitBufC: ...
@overload
def new(a: Literal['char **']) -> _Pointer[char_pointer]: ...
@overload
def new(a: Literal['char[]', 'char []'], b: bytes | NULL_TYPE) -> char_pointer: ...
def addressof(a: object, attribute: str) -> _Pointer[object]: ...

class buffer(bytes):
    def __init__(self, a: object) -> None: ...
    def __setitem__(self, item: slice[None, None, None], value: bytes) -> None: ...
    @overload
    def __getitem__(self, item: SupportsIndex) -> int: ...
    @overload
    def __getitem__(self, item: slice[Any, Any, Any]) -> bytes: ...

def cast(a: Literal['int'], b: object) -> int: ...
