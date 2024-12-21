from io import IOBase
from typing import Iterator, Literal, Optional, overload

from . import Index
from .enums import (
    ApplyLocation,
    BranchType,
    DeltaStatus,
    DiffFind,
    DiffFlag,
    DiffOption,
    DiffStatsFormat,
    FileMode,
    MergeAnalysis,
    MergePreference,
    ObjectType,
    Option,
    ReferenceFilter,
    ReferenceType,
    ResetMode,
    SortMode,
)

GIT_OBJ_BLOB: Literal[3]
GIT_OBJ_COMMIT: Literal[1]
GIT_OBJ_TAG: Literal[4]
GIT_OBJ_TREE: Literal[2]
GIT_OID_HEXSZ: int
GIT_OID_HEX_ZERO: str
GIT_OID_MINPREFIXLEN: int
GIT_OID_RAWSZ: int
LIBGIT2_VERSION: str
LIBGIT2_VER_MAJOR: int
LIBGIT2_VER_MINOR: int
LIBGIT2_VER_REVISION: int

class Object:
    _pointer: bytes
    filemode: FileMode
    hex: str
    id: Oid
    name: str | None
    oid: Oid
    raw_name: bytes | None
    short_id: str
    type: 'Literal[GIT_OBJ_COMMIT] | Literal[GIT_OBJ_TREE] | Literal[GIT_OBJ_TAG] | Literal[GIT_OBJ_BLOB]'
    type_str: "Literal['commit'] | Literal['tree'] | Literal['tag'] | Literal['blob']"
    @overload
    def peel(self, target_type: 'Literal[GIT_OBJ_COMMIT]') -> 'Commit': ...
    @overload
    def peel(self, target_type: 'Literal[GIT_OBJ_TREE]') -> 'Tree': ...
    @overload
    def peel(self, target_type: 'Literal[GIT_OBJ_TAG]') -> 'Tag': ...
    @overload
    def peel(self, target_type: 'Literal[GIT_OBJ_BLOB]') -> 'Blob': ...
    @overload
    def peel(self, target_type: 'None') -> 'Commit|Tree|Blob': ...
    def read_raw(self) -> bytes: ...
    def __eq__(self, other) -> bool: ...
    def __ge__(self, other) -> bool: ...
    def __gt__(self, other) -> bool: ...
    def __hash__(self) -> int: ...
    def __le__(self, other) -> bool: ...
    def __lt__(self, other) -> bool: ...
    def __ne__(self, other) -> bool: ...

class Reference:
    name: str
    raw_name: bytes
    raw_shorthand: bytes
    raw_target: Oid | bytes
    shorthand: str
    target: Oid | str
    type: ReferenceType
    def __init__(self, *args) -> None: ...
    def delete(self) -> None: ...
    def log(self) -> Iterator[RefLogEntry]: ...
    @overload
    def peel(self, type: 'Literal[GIT_OBJ_COMMIT]') -> 'Commit': ...
    @overload
    def peel(self, type: 'Literal[GIT_OBJ_TREE]') -> 'Tree': ...
    @overload
    def peel(self, type: 'Literal[GIT_OBJ_TAG]') -> 'Tag': ...
    @overload
    def peel(self, type: 'Literal[GIT_OBJ_BLOB]') -> 'Blob': ...
    @overload
    def peel(self, type: 'None') -> 'Commit|Tree|Blob': ...
    def rename(self, new_name: str) -> None: ...
    def resolve(self) -> Reference: ...
    def set_target(self, target: _OidArg, message: str = ...) -> None: ...
    def __eq__(self, other) -> bool: ...
    def __ge__(self, other) -> bool: ...
    def __gt__(self, other) -> bool: ...
    def __le__(self, other) -> bool: ...
    def __lt__(self, other) -> bool: ...
    def __ne__(self, other) -> bool: ...

class AlreadyExistsError(ValueError): ...

class Blob(Object):
    data: bytes
    is_binary: bool
    size: int
    def diff(
        self,
        blob: Blob = ...,
        flag: int = ...,
        old_as_path: str = ...,
        new_as_path: str = ...,
    ) -> Patch: ...
    def diff_to_buffer(
        self,
        buffer: Optional[bytes] = None,
        flag: DiffOption = DiffOption.NORMAL,
        old_as_path: str = ...,
        buffer_as_path: str = ...,
    ) -> Patch: ...

class Branch(Reference):
    branch_name: str
    raw_branch_name: bytes
    remote_name: str
    upstream: Branch
    upstream_name: str
    def delete(self) -> None: ...
    def is_checked_out(self) -> bool: ...
    def is_head(self) -> bool: ...
    def rename(self, name: str, force: bool = False) -> None: ...

class Commit(Object):
    author: Signature
    commit_time: int
    commit_time_offset: int
    committer: Signature
    gpg_signature: tuple[bytes, bytes]
    message: str
    message_encoding: str
    message_trailers: dict[str, str]
    parent_ids: list[Oid]
    parents: list[Commit]
    raw_message: bytes
    tree: Tree
    tree_id: Oid

class Diff:
    deltas: Iterator[DiffDelta]
    patch: str | None
    patchid: Oid
    stats: DiffStats
    def find_similar(
        self,
        flags: DiffFind = DiffFind.FIND_BY_CONFIG,
        rename_threshold: int = 50,
        copy_threshold: int = 50,
        rename_from_rewrite_threshold: int = 50,
        break_rewrite_threshold: int = 60,
        rename_limit: int = 1000,
    ) -> None: ...
    def merge(self, diff: Diff) -> None: ...
    @staticmethod
    def from_c(diff, repo) -> Diff: ...
    @staticmethod
    def parse_diff(git_diff: str | bytes) -> Diff: ...
    def __getitem__(self, index: int) -> Patch: ...  # Diff_getitem
    def __iter__(self) -> Iterator[Patch]: ...  # -> DiffIter
    def __len__(self) -> int: ...

class DiffDelta:
    flags: DiffFlag
    is_binary: bool
    nfiles: int
    new_file: DiffFile
    old_file: DiffFile
    similarity: int
    status: DeltaStatus
    def status_char(self) -> str: ...

class DiffFile:
    flags: DiffFlag
    id: Oid
    mode: FileMode
    path: str
    raw_path: bytes
    size: int
    @staticmethod
    def from_c(bytes) -> DiffFile: ...

class DiffHunk:
    header: str
    lines: list[DiffLine]
    new_lines: int
    new_start: int
    old_lines: int
    old_start: int

class DiffLine:
    content: str
    content_offset: int
    new_lineno: int
    num_lines: int
    old_lineno: int
    origin: str
    raw_content: bytes

class DiffStats:
    deletions: int
    files_changed: int
    insertions: int
    def format(self, format: DiffStatsFormat, width: int) -> str: ...

class GitError(Exception): ...
class InvalidSpecError(ValueError): ...

class Mailmap:
    def __init__(self, *args) -> None: ...
    def add_entry(
        self,
        real_name: str = ...,
        real_email: str = ...,
        replace_name: str = ...,
        replace_email: str = ...,
    ) -> None: ...
    @staticmethod
    def from_buffer(buffer: str | bytes) -> Mailmap: ...
    @staticmethod
    def from_repository(repository: Repository) -> Mailmap: ...
    def resolve(self, name: str, email: str) -> tuple[str, str]: ...
    def resolve_signature(self, sig: Signature) -> Signature: ...

class Note:
    annotated_id: Oid
    id: Oid
    message: str
    def remove(
        self, author: Signature, committer: Signature, ref: str = 'refs/notes/commits'
    ) -> None: ...

class Odb:
    backends: Iterator[OdbBackend]
    def __init__(self, *args, **kwargs) -> None: ...
    def add_backend(self, backend: OdbBackend, priority: int) -> None: ...
    def add_disk_alternate(self, path: str) -> None: ...
    def exists(self, oid: _OidArg) -> bool: ...
    def read(self, oid: _OidArg) -> tuple[int, int, bytes]: ...
    def write(self, type: int, data: bytes) -> Oid: ...
    def __contains__(self, other: _OidArg) -> bool: ...
    def __iter__(self) -> Iterator[Oid]: ...  # Odb_as_iter

class OdbBackend:
    def __init__(self, *args, **kwargs) -> None: ...
    def exists(self, oid: _OidArg) -> bool: ...
    def exists_prefix(self, partial_id: _OidArg) -> Oid: ...
    def read(self, oid: _OidArg) -> tuple[int, bytes]: ...
    def read_header(self, oid: _OidArg) -> tuple[int, int]: ...
    def read_prefix(self, oid: _OidArg) -> tuple[int, bytes, Oid]: ...
    def refresh(self) -> None: ...
    def __iter__(self) -> Iterator[Oid]: ...  # OdbBackend_as_iter

class OdbBackendLoose(OdbBackend):
    def __init__(self, *args, **kwargs) -> None: ...

class OdbBackendPack(OdbBackend):
    def __init__(self, *args, **kwargs) -> None: ...

class Oid:
    hex: str
    raw: bytes
    def __init__(self, raw: bytes = ..., hex: str = ...) -> None: ...
    def __eq__(self, other) -> bool: ...
    def __ge__(self, other) -> bool: ...
    def __gt__(self, other) -> bool: ...
    def __hash__(self) -> int: ...
    def __le__(self, other) -> bool: ...
    def __lt__(self, other) -> bool: ...
    def __ne__(self, other) -> bool: ...

class Patch:
    data: bytes
    delta: DiffDelta
    hunks: list[DiffHunk]
    line_stats: tuple[int, int, int]  # context, additions, deletions
    text: str | None

    @staticmethod
    def create_from(
        old: Blob | bytes | None,
        new: Blob | bytes | None,
        old_as_path: str = ...,
        new_as_path: str = ...,
        flag: DiffOption = DiffOption.NORMAL,
        context_lines: int = 3,
        interhunk_lines: int = 0,
    ) -> Patch: ...

class RefLogEntry:
    committer: Signature
    message: str
    oid_new: Oid
    oid_old: Oid
    def __init__(self, *args, **kwargs) -> None: ...

class Refdb:
    def __init__(self, *args, **kwargs) -> None: ...
    def compress(self) -> None: ...
    @staticmethod
    def new(repo: Repository) -> Refdb: ...
    @staticmethod
    def open(repo: Repository) -> Refdb: ...
    def set_backend(self, backend: RefdbBackend) -> None: ...

class RefdbBackend:
    def __init__(self, *args, **kwargs) -> None: ...
    def compress(self) -> None: ...
    def delete(self, ref_name: str, old_id: _OidArg, old_target: str) -> None: ...
    def ensure_log(self, ref_name: str) -> bool: ...
    def exists(self, refname: str) -> bool: ...
    def has_log(self, ref_name: str) -> bool: ...
    def lookup(self, refname: str) -> Reference: ...
    def rename(
        self, old_name: str, new_name: str, force: bool, who: Signature, message: str
    ) -> Reference: ...
    def write(
        self,
        ref: Reference,
        force: bool,
        who: Signature,
        message: str,
        old: _OidArg,
        old_target: str,
    ) -> None: ...

class RefdbFsBackend(RefdbBackend):
    def __init__(self, *args, **kwargs) -> None: ...

class Repository:
    _pointer: bytes
    default_signature: Signature
    head: Reference
    head_is_detached: bool
    head_is_unborn: bool
    is_bare: bool
    is_empty: bool
    is_shallow: bool
    odb: Odb
    path: str
    refdb: Refdb
    workdir: str
    def __init__(self, *args, **kwargs) -> None: ...
    def TreeBuilder(self, src: Tree | _OidArg = ...) -> TreeBuilder: ...
    def _disown(self, *args, **kwargs) -> None: ...
    def _from_c(self, *args, **kwargs) -> None: ...
    def add_worktree(self, name: str, path: str, ref: Reference = ...) -> Worktree: ...
    def applies(
        self,
        diff: Diff,
        location: ApplyLocation = ApplyLocation.INDEX,
        raise_error: bool = False,
    ) -> bool: ...
    def apply(
        self, diff: Diff, location: ApplyLocation = ApplyLocation.WORKDIR
    ) -> None: ...
    def cherrypick(self, id: _OidArg) -> None: ...
    def compress_references(self) -> None: ...
    def create_blob(self, data: bytes) -> Oid: ...
    def create_blob_fromdisk(self, path: str) -> Oid: ...
    def create_blob_fromiobase(self, iobase: IOBase) -> Oid: ...
    def create_blob_fromworkdir(self, path: str) -> Oid: ...
    def create_branch(self, name: str, commit: Commit, force=False) -> Branch: ...
    def create_commit(
        self,
        reference_name: Optional[str],
        author: Signature,
        committer: Signature,
        message: str | bytes,
        tree: _OidArg,
        parents: list[_OidArg],
        encoding: str = ...,
    ) -> Oid: ...
    def create_commit_string(
        self,
        author: Signature,
        committer: Signature,
        message: str | bytes,
        tree: _OidArg,
        parents: list[_OidArg],
        encoding: str = ...,
    ) -> Oid: ...
    def create_commit_with_signature(
        self, content: str, signature: str, signature_field: Optional[str] = None
    ) -> Oid: ...
    def create_note(
        self,
        message: str,
        author: Signature,
        committer: Signature,
        annotated_id: str,
        ref: str = 'refs/notes/commits',
        force: bool = False,
    ) -> Oid: ...
    def create_reference_direct(
        self, name: str, target: _OidArg, force: bool, message: Optional[str] = None
    ) -> Reference: ...
    def create_reference_symbolic(
        self, name: str, target: str, force: bool, message: Optional[str] = None
    ) -> Reference: ...
    def create_tag(
        self, name: str, oid: _OidArg, type: ObjectType, tagger: Signature, message: str
    ) -> Oid: ...
    def descendant_of(self, oid1: _OidArg, oid2: _OidArg) -> bool: ...
    def expand_id(self, hex: str) -> Oid: ...
    def free(self) -> None: ...
    def git_object_lookup_prefix(self, oid: _OidArg) -> Object: ...
    def list_worktrees(self) -> list[str]: ...
    def listall_branches(self, flag: BranchType = BranchType.LOCAL) -> list[str]: ...
    def listall_mergeheads(self) -> list[Oid]: ...
    def listall_stashes(self) -> list[Stash]: ...
    def listall_submodules(self) -> list[str]: ...
    def lookup_branch(
        self, branch_name: str, branch_type: BranchType = BranchType.LOCAL
    ) -> Branch: ...
    def lookup_note(
        self, annotated_id: str, ref: str = 'refs/notes/commits'
    ) -> Note: ...
    def lookup_reference(self, name: str) -> Reference: ...
    def lookup_reference_dwim(self, name: str) -> Reference: ...
    def lookup_worktree(self, name: str) -> Worktree: ...
    def merge_analysis(
        self, their_head: _OidArg, our_ref: str = 'HEAD'
    ) -> tuple[MergeAnalysis, MergePreference]: ...
    def merge_base(self, oid1: _OidArg, oid2: _OidArg) -> Oid: ...
    def merge_base_many(self, oids: list[_OidArg]) -> Oid: ...
    def merge_base_octopus(self, oids: list[_OidArg]) -> Oid: ...
    def notes(self) -> Iterator[Note]: ...
    def path_is_ignored(self, path: str) -> bool: ...
    def raw_listall_branches(
        self, flag: BranchType = BranchType.LOCAL
    ) -> list[bytes]: ...
    def raw_listall_references(self) -> list[bytes]: ...
    def references_iterator_init(self) -> Iterator[Reference]: ...
    def references_iterator_next(
        self,
        iter: Iterator,
        references_return_type: ReferenceFilter = ReferenceFilter.ALL,
    ) -> Reference: ...
    def reset(self, oid: _OidArg, reset_type: ResetMode) -> None: ...
    def revparse(self, revspec: str) -> RevSpec: ...
    def revparse_ext(self, revision: str) -> tuple[Object, Reference]: ...
    def revparse_single(self, revision: str) -> Object: ...
    def set_odb(self, odb: Odb) -> None: ...
    def set_refdb(self, refdb: Refdb) -> None: ...
    def status(
        self, untracked_files: str = 'all', ignored: bool = False
    ) -> dict[str, int]: ...
    def status_file(self, path: str) -> int: ...
    def walk(
        self, oid: _OidArg | None, sort_mode: SortMode = SortMode.NONE
    ) -> Walker: ...

class RevSpec:
    flags: int
    from_object: Object
    to_object: Object

class Signature:
    _encoding: str | None
    _pointer: bytes
    email: str
    name: str
    offset: int
    raw_email: bytes
    raw_name: bytes
    time: int
    def __init__(
        self,
        name: str,
        email: str,
        time: int = -1,
        offset: int = 0,
        encoding: Optional[str] = None,
    ) -> None: ...
    def __eq__(self, other) -> bool: ...
    def __ge__(self, other) -> bool: ...
    def __gt__(self, other) -> bool: ...
    def __le__(self, other) -> bool: ...
    def __lt__(self, other) -> bool: ...
    def __ne__(self, other) -> bool: ...

class Stash:
    commit_id: Oid
    message: str
    raw_message: bytes
    def __eq__(self, other) -> bool: ...
    def __ge__(self, other) -> bool: ...
    def __gt__(self, other) -> bool: ...
    def __le__(self, other) -> bool: ...
    def __lt__(self, other) -> bool: ...
    def __ne__(self, other) -> bool: ...

class Tag(Object):
    message: str
    name: str
    raw_message: bytes
    raw_name: bytes
    tagger: Signature
    target: Oid
    def get_object(self) -> Object: ...

class Tree(Object):
    def diff_to_index(
        self,
        index: Index,
        flags: DiffOption = DiffOption.NORMAL,
        context_lines: int = 3,
        interhunk_lines: int = 0,
    ) -> Diff: ...
    def diff_to_tree(
        self,
        tree: Tree = ...,
        flags: DiffOption = DiffOption.NORMAL,
        context_lines: int = 3,
        interhunk_lines: int = 3,
        swap: bool = False,
    ) -> Diff: ...
    def diff_to_workdir(
        self,
        flags: DiffOption = DiffOption.NORMAL,
        context_lines: int = 3,
        interhunk_lines: int = 0,
    ) -> Diff: ...
    def __contains__(self, other: str) -> bool: ...  # Tree_contains
    def __getitem__(self, index: str | int) -> Object: ...  # Tree_subscript
    def __iter__(self) -> Iterator[Object]: ...
    def __len__(self) -> int: ...  # Tree_len
    def __rtruediv__(self, other: str) -> Object: ...
    def __truediv__(self, other: str) -> Object: ...  # Tree_divide

class TreeBuilder:
    def clear(self) -> None: ...
    def get(self, name: str) -> Object: ...
    def insert(self, name: str, oid: _OidArg, attr: int) -> None: ...
    def remove(self, name: str) -> None: ...
    def write(self) -> Oid: ...
    def __len__(self) -> int: ...

class Walker:
    def hide(self, oid: _OidArg) -> None: ...
    def push(self, oid: _OidArg) -> None: ...
    def reset(self) -> None: ...
    def simplify_first_parent(self) -> None: ...
    def sort(self, mode: SortMode) -> None: ...
    def __iter__(self) -> Iterator[Commit]: ...  # Walker: ...
    def __next__(self) -> Commit: ...

class Worktree:
    is_prunable: bool
    name: str
    path: str
    def prune(self, force=False) -> None: ...

def discover_repository(
    path: str, across_fs: bool = False, ceiling_dirs: str = ...
) -> str | None: ...
def hash(data: bytes) -> Oid: ...
def hashfile(path: str) -> Oid: ...
def init_file_backend(path: str, flags: int = 0) -> object: ...
def option(opt: Option, *args) -> None: ...
def reference_is_valid_name(refname: str) -> bool: ...
def tree_entry_cmp(a: Object, b: Object) -> int: ...

_OidArg = str | Oid
