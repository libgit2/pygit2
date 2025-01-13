import queue
import threading
from io import DEFAULT_BUFFER_SIZE, IOBase
from typing import Any, Callable, Iterator, Literal, Optional, TypeAlias, overload

from pygit2.filter import Filter

from . import Index
from .enums import (
    ApplyLocation,
    BlobFilter,
    BranchType,
    DeltaStatus,
    DiffFind,
    DiffFlag,
    DiffOption,
    DiffStatsFormat,
    FileMode,
    FilterFlag,
    FilterMode,
    MergeAnalysis,
    MergePreference,
    ObjectType,
    Option,
    ReferenceFilter,
    ReferenceType,
    ResetMode,
    SortMode,
)

# version constants
LIBGIT2_VERSION: str
LIBGIT2_VER_MAJOR: int
LIBGIT2_VER_MINOR: int
LIBGIT2_VER_REVISION: int

# libgit2 constants
GIT_OBJECT_BLOB: Literal[3]
GIT_OBJECT_COMMIT: Literal[1]
GIT_OBJECT_TAG: Literal[4]
GIT_OBJECT_TREE: Literal[2]
GIT_OID_HEXSZ: Literal[40]
GIT_OID_HEX_ZERO: Literal['0000000000000000000000000000000000000000']
GIT_OID_MINPREFIXLEN: Literal[4]
GIT_OID_RAWSZ: Literal[20]
GIT_APPLY_LOCATION_BOTH: Literal[2]
GIT_APPLY_LOCATION_INDEX: Literal[1]
GIT_APPLY_LOCATION_WORKDIR: Literal[0]
GIT_BLAME_FIRST_PARENT: Literal[16]
GIT_BLAME_IGNORE_WHITESPACE: Literal[64]
GIT_BLAME_NORMAL: Literal[0]
GIT_BLAME_TRACK_COPIES_ANY_COMMIT_COPIES: Literal[8]
GIT_BLAME_TRACK_COPIES_SAME_COMMIT_COPIES: Literal[4]
GIT_BLAME_TRACK_COPIES_SAME_COMMIT_MOVES: Literal[2]
GIT_BLAME_TRACK_COPIES_SAME_FILE: Literal[1]
GIT_BLAME_USE_MAILMAP: Literal[32]
GIT_BLOB_FILTER_ATTRIBUTES_FROM_COMMIT: Literal[8]
GIT_BLOB_FILTER_ATTRIBUTES_FROM_HEAD: Literal[4]
GIT_BLOB_FILTER_CHECK_FOR_BINARY: Literal[1]
GIT_BLOB_FILTER_NO_SYSTEM_ATTRIBUTES: Literal[2]
GIT_BRANCH_ALL: Literal[3]
GIT_BRANCH_LOCAL: Literal[1]
GIT_BRANCH_REMOTE: Literal[2]
GIT_CHECKOUT_ALLOW_CONFLICTS: Literal[16]
GIT_CHECKOUT_CONFLICT_STYLE_DIFF3: Literal[2097152]
GIT_CHECKOUT_CONFLICT_STYLE_MERGE: Literal[1048576]
GIT_CHECKOUT_CONFLICT_STYLE_ZDIFF3: Literal[33554432]
GIT_CHECKOUT_DISABLE_PATHSPEC_MATCH: Literal[8192]
GIT_CHECKOUT_DONT_OVERWRITE_IGNORED: Literal[524288]
GIT_CHECKOUT_DONT_REMOVE_EXISTING: Literal[4194304]
GIT_CHECKOUT_DONT_UPDATE_INDEX: Literal[256]
GIT_CHECKOUT_DONT_WRITE_INDEX: Literal[8388608]
GIT_CHECKOUT_DRY_RUN: Literal[16777216]
GIT_CHECKOUT_FORCE: Literal[2]
GIT_CHECKOUT_NONE: Literal[0]
GIT_CHECKOUT_NO_REFRESH: Literal[512]
GIT_CHECKOUT_RECREATE_MISSING: Literal[4]
GIT_CHECKOUT_REMOVE_IGNORED: Literal[64]
GIT_CHECKOUT_REMOVE_UNTRACKED: Literal[32]
GIT_CHECKOUT_SAFE: Literal[1]
GIT_CHECKOUT_SKIP_LOCKED_DIRECTORIES: Literal[262144]
GIT_CHECKOUT_SKIP_UNMERGED: Literal[1024]
GIT_CHECKOUT_UPDATE_ONLY: Literal[128]
GIT_CHECKOUT_USE_OURS: Literal[2048]
GIT_CHECKOUT_USE_THEIRS: Literal[4096]
GIT_CONFIG_HIGHEST_LEVEL: Literal[-1]
GIT_CONFIG_LEVEL_APP: Literal[7]
GIT_CONFIG_LEVEL_GLOBAL: Literal[4]
GIT_CONFIG_LEVEL_LOCAL: Literal[5]
GIT_CONFIG_LEVEL_PROGRAMDATA: Literal[1]
GIT_CONFIG_LEVEL_SYSTEM: Literal[2]
GIT_CONFIG_LEVEL_WORKTREE: Literal[6]
GIT_CONFIG_LEVEL_XDG: Literal[3]
GIT_DELTA_ADDED: Literal[1]
GIT_DELTA_CONFLICTED: Literal[10]
GIT_DELTA_COPIED: Literal[5]
GIT_DELTA_DELETED: Literal[2]
GIT_DELTA_IGNORED: Literal[6]
GIT_DELTA_MODIFIED: Literal[3]
GIT_DELTA_RENAMED: Literal[4]
GIT_DELTA_TYPECHANGE: Literal[8]
GIT_DELTA_UNMODIFIED: Literal[0]
GIT_DELTA_UNREADABLE: Literal[9]
GIT_DELTA_UNTRACKED: Literal[7]
GIT_DESCRIBE_ALL: Literal[2]
GIT_DESCRIBE_DEFAULT: Literal[0]
GIT_DESCRIBE_TAGS: Literal[1]
GIT_DIFF_BREAK_REWRITES: Literal[32]
GIT_DIFF_BREAK_REWRITES_FOR_RENAMES_ONLY: Literal[32768]
GIT_DIFF_DISABLE_PATHSPEC_MATCH: Literal[4096]
GIT_DIFF_ENABLE_FAST_UNTRACKED_DIRS: Literal[16384]
GIT_DIFF_FIND_ALL: Literal[255]
GIT_DIFF_FIND_AND_BREAK_REWRITES: Literal[48]
GIT_DIFF_FIND_BY_CONFIG: Literal[0]
GIT_DIFF_FIND_COPIES: Literal[4]
GIT_DIFF_FIND_COPIES_FROM_UNMODIFIED: Literal[8]
GIT_DIFF_FIND_DONT_IGNORE_WHITESPACE: Literal[8192]
GIT_DIFF_FIND_EXACT_MATCH_ONLY: Literal[16384]
GIT_DIFF_FIND_FOR_UNTRACKED: Literal[64]
GIT_DIFF_FIND_IGNORE_LEADING_WHITESPACE: Literal[0]
GIT_DIFF_FIND_IGNORE_WHITESPACE: Literal[4096]
GIT_DIFF_FIND_REMOVE_UNMODIFIED: Literal[65536]
GIT_DIFF_FIND_RENAMES: Literal[1]
GIT_DIFF_FIND_RENAMES_FROM_REWRITES: Literal[2]
GIT_DIFF_FIND_REWRITES: Literal[16]
GIT_DIFF_FLAG_BINARY: Literal[1]
GIT_DIFF_FLAG_EXISTS: Literal[8]
GIT_DIFF_FLAG_NOT_BINARY: Literal[2]
GIT_DIFF_FLAG_VALID_ID: Literal[4]
GIT_DIFF_FLAG_VALID_SIZE: Literal[16]
GIT_DIFF_FORCE_BINARY: Literal[2097152]
GIT_DIFF_FORCE_TEXT: Literal[1048576]
GIT_DIFF_IGNORE_BLANK_LINES: Literal[524288]
GIT_DIFF_IGNORE_CASE: Literal[1024]
GIT_DIFF_IGNORE_FILEMODE: Literal[256]
GIT_DIFF_IGNORE_SUBMODULES: Literal[512]
GIT_DIFF_IGNORE_WHITESPACE: Literal[4194304]
GIT_DIFF_IGNORE_WHITESPACE_CHANGE: Literal[8388608]
GIT_DIFF_IGNORE_WHITESPACE_EOL: Literal[16777216]
GIT_DIFF_INCLUDE_CASECHANGE: Literal[2048]
GIT_DIFF_INCLUDE_IGNORED: Literal[2]
GIT_DIFF_INCLUDE_TYPECHANGE: Literal[64]
GIT_DIFF_INCLUDE_TYPECHANGE_TREES: Literal[128]
GIT_DIFF_INCLUDE_UNMODIFIED: Literal[32]
GIT_DIFF_INCLUDE_UNREADABLE: Literal[65536]
GIT_DIFF_INCLUDE_UNREADABLE_AS_UNTRACKED: Literal[131072]
GIT_DIFF_INCLUDE_UNTRACKED: Literal[8]
GIT_DIFF_INDENT_HEURISTIC: Literal[262144]
GIT_DIFF_MINIMAL: Literal[536870912]
GIT_DIFF_NORMAL: Literal[0]
GIT_DIFF_PATIENCE: Literal[268435456]
GIT_DIFF_RECURSE_IGNORED_DIRS: Literal[4]
GIT_DIFF_RECURSE_UNTRACKED_DIRS: Literal[16]
GIT_DIFF_REVERSE: Literal[1]
GIT_DIFF_SHOW_BINARY: Literal[1073741824]
GIT_DIFF_SHOW_UNMODIFIED: Literal[67108864]
GIT_DIFF_SHOW_UNTRACKED_CONTENT: Literal[33554432]
GIT_DIFF_SKIP_BINARY_CHECK: Literal[8192]
GIT_DIFF_STATS_FULL: Literal[1]
GIT_DIFF_STATS_INCLUDE_SUMMARY: Literal[8]
GIT_DIFF_STATS_NONE: Literal[0]
GIT_DIFF_STATS_NUMBER: Literal[4]
GIT_DIFF_STATS_SHORT: Literal[2]
GIT_DIFF_UPDATE_INDEX: Literal[32768]
GIT_FILEMODE_BLOB: Literal[33188]
GIT_FILEMODE_BLOB_EXECUTABLE: Literal[33261]
GIT_FILEMODE_COMMIT: Literal[57344]
GIT_FILEMODE_LINK: Literal[40960]
GIT_FILEMODE_TREE: Literal[16384]
GIT_FILEMODE_UNREADABLE: Literal[0]
GIT_FILTER_ALLOW_UNSAFE: Literal[1]
GIT_FILTER_ATTRIBUTES_FROM_COMMIT: Literal[8]
GIT_FILTER_ATTRIBUTES_FROM_HEAD: Literal[4]
GIT_FILTER_CLEAN: Literal[1]
GIT_FILTER_DEFAULT: Literal[0]
GIT_FILTER_DRIVER_PRIORITY: Literal[200]
GIT_FILTER_NO_SYSTEM_ATTRIBUTES: Literal[2]
GIT_FILTER_SMUDGE: Literal[0]
GIT_FILTER_TO_ODB: Literal[1]
GIT_FILTER_TO_WORKTREE: Literal[0]
GIT_MERGE_ANALYSIS_FASTFORWARD: Literal[4]
GIT_MERGE_ANALYSIS_NONE: Literal[0]
GIT_MERGE_ANALYSIS_NORMAL: Literal[1]
GIT_MERGE_ANALYSIS_UNBORN: Literal[8]
GIT_MERGE_ANALYSIS_UP_TO_DATE: Literal[2]
GIT_MERGE_PREFERENCE_FASTFORWARD_ONLY: Literal[2]
GIT_MERGE_PREFERENCE_NONE: Literal[0]
GIT_MERGE_PREFERENCE_NO_FASTFORWARD: Literal[1]
GIT_OBJECT_ANY: Literal[-2]
GIT_OBJECT_INVALID: Literal[-1]
GIT_OBJECT_OFS_DELTA: Literal[6]
GIT_OBJECT_REF_DELTA: Literal[7]
GIT_OPT_DISABLE_PACK_KEEP_FILE_CHECKS: Literal[27]
GIT_OPT_ENABLE_CACHING: Literal[8]
GIT_OPT_ENABLE_FSYNC_GITDIR: Literal[19]
GIT_OPT_ENABLE_OFS_DELTA: Literal[18]
GIT_OPT_ENABLE_STRICT_HASH_VERIFICATION: Literal[22]
GIT_OPT_ENABLE_STRICT_OBJECT_CREATION: Literal[14]
GIT_OPT_ENABLE_STRICT_SYMBOLIC_REF_CREATION: Literal[15]
GIT_OPT_ENABLE_UNSAVED_INDEX_SAFETY: Literal[24]
GIT_OPT_GET_CACHED_MEMORY: Literal[9]
GIT_OPT_GET_MWINDOW_FILE_LIMIT: Literal[29]
GIT_OPT_GET_MWINDOW_MAPPED_LIMIT: Literal[2]
GIT_OPT_GET_MWINDOW_SIZE: Literal[0]
GIT_OPT_GET_OWNER_VALIDATION: Literal[35]
GIT_OPT_GET_PACK_MAX_OBJECTS: Literal[25]
GIT_OPT_GET_SEARCH_PATH: Literal[4]
GIT_OPT_GET_TEMPLATE_PATH: Literal[10]
GIT_OPT_GET_USER_AGENT: Literal[17]
GIT_OPT_GET_WINDOWS_SHAREMODE: Literal[20]
GIT_OPT_SET_ALLOCATOR: Literal[23]
GIT_OPT_SET_CACHE_MAX_SIZE: Literal[7]
GIT_OPT_SET_CACHE_OBJECT_LIMIT: Literal[6]
GIT_OPT_SET_MWINDOW_FILE_LIMIT: Literal[30]
GIT_OPT_SET_MWINDOW_MAPPED_LIMIT: Literal[3]
GIT_OPT_SET_MWINDOW_SIZE: Literal[1]
GIT_OPT_SET_OWNER_VALIDATION: Literal[36]
GIT_OPT_SET_PACK_MAX_OBJECTS: Literal[26]
GIT_OPT_SET_SEARCH_PATH: Literal[5]
GIT_OPT_SET_SSL_CERT_LOCATIONS: Literal[12]
GIT_OPT_SET_SSL_CIPHERS: Literal[16]
GIT_OPT_SET_TEMPLATE_PATH: Literal[11]
GIT_OPT_SET_USER_AGENT: Literal[13]
GIT_OPT_SET_WINDOWS_SHAREMODE: Literal[21]
GIT_REFERENCES_ALL: Literal[0]
GIT_REFERENCES_BRANCHES: Literal[1]
GIT_REFERENCES_TAGS: Literal[2]
GIT_RESET_HARD: Literal[3]
GIT_RESET_MIXED: Literal[2]
GIT_RESET_SOFT: Literal[1]
GIT_REVSPEC_MERGE_BASE: Literal[4]
GIT_REVSPEC_RANGE: Literal[2]
GIT_REVSPEC_SINGLE: Literal[1]
GIT_SORT_NONE: Literal[0]
GIT_SORT_REVERSE: Literal[4]
GIT_SORT_TIME: Literal[2]
GIT_SORT_TOPOLOGICAL: Literal[1]
GIT_STASH_APPLY_DEFAULT: Literal[0]
GIT_STASH_APPLY_REINSTATE_INDEX: Literal[1]
GIT_STASH_DEFAULT: Literal[0]
GIT_STASH_INCLUDE_IGNORED: Literal[4]
GIT_STASH_INCLUDE_UNTRACKED: Literal[2]
GIT_STASH_KEEP_ALL: Literal[8]
GIT_STASH_KEEP_INDEX: Literal[1]
GIT_STATUS_CONFLICTED: Literal[32768]
GIT_STATUS_CURRENT: Literal[0]
GIT_STATUS_IGNORED: Literal[16384]
GIT_STATUS_INDEX_DELETED: Literal[4]
GIT_STATUS_INDEX_MODIFIED: Literal[2]
GIT_STATUS_INDEX_NEW: Literal[1]
GIT_STATUS_INDEX_RENAMED: Literal[8]
GIT_STATUS_INDEX_TYPECHANGE: Literal[16]
GIT_STATUS_WT_DELETED: Literal[512]
GIT_STATUS_WT_MODIFIED: Literal[256]
GIT_STATUS_WT_NEW: Literal[128]
GIT_STATUS_WT_RENAMED: Literal[2048]
GIT_STATUS_WT_TYPECHANGE: Literal[1024]
GIT_STATUS_WT_UNREADABLE: Literal[4096]
GIT_SUBMODULE_IGNORE_ALL: Literal[4]
GIT_SUBMODULE_IGNORE_DIRTY: Literal[3]
GIT_SUBMODULE_IGNORE_NONE: Literal[1]
GIT_SUBMODULE_IGNORE_UNSPECIFIED: Literal[-1]
GIT_SUBMODULE_IGNORE_UNTRACKED: Literal[2]
GIT_SUBMODULE_STATUS_INDEX_ADDED: Literal[16]
GIT_SUBMODULE_STATUS_INDEX_DELETED: Literal[32]
GIT_SUBMODULE_STATUS_INDEX_MODIFIED: Literal[64]
GIT_SUBMODULE_STATUS_IN_CONFIG: Literal[4]
GIT_SUBMODULE_STATUS_IN_HEAD: Literal[1]
GIT_SUBMODULE_STATUS_IN_INDEX: Literal[2]
GIT_SUBMODULE_STATUS_IN_WD: Literal[8]
GIT_SUBMODULE_STATUS_WD_ADDED: Literal[256]
GIT_SUBMODULE_STATUS_WD_DELETED: Literal[512]
GIT_SUBMODULE_STATUS_WD_INDEX_MODIFIED: Literal[2048]
GIT_SUBMODULE_STATUS_WD_MODIFIED: Literal[1024]
GIT_SUBMODULE_STATUS_WD_UNINITIALIZED: Literal[128]
GIT_SUBMODULE_STATUS_WD_UNTRACKED: Literal[8192]
GIT_SUBMODULE_STATUS_WD_WD_MODIFIED: Literal[4096]

_OidArg: TypeAlias = 'str | Oid'

class Object:
    _pointer: bytes
    filemode: FileMode
    id: Oid
    name: str | None
    raw_name: bytes | None
    short_id: str
    # GIT_OBJECT_COMMIT | GIT_OBJECT_TREE | GIT_OBJECT_TAG | GIT_OBJECT_BLOB
    type: Literal[1, 2, 4, 3]
    type_str: "Literal['commit'] | Literal['tree'] | Literal['tag'] | Literal['blob']"
    @overload
    def peel(
        self, target_type: Literal[1, ObjectType.COMMIT] | type[Commit]
    ) -> Commit: ...
    @overload
    def peel(self, target_type: Literal[2, ObjectType.TREE] | type[Tree]) -> Tree: ...
    @overload
    def peel(self, target_type: Literal[4, ObjectType.TAG] | type[Tag]) -> Tag: ...
    @overload
    def peel(self, target_type: Literal[3, ObjectType.BLOB] | type[Blob]) -> Blob: ...
    @overload
    def peel(
        self, target_type: Literal[None, ObjectType.ANY]
    ) -> Commit | Tree | Blob | Tag: ...
    def read_raw(self) -> bytes: ...
    def __eq__(self, other: object) -> bool: ...
    def __ge__(self, other: object) -> bool: ...
    def __gt__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def __le__(self, other: object) -> bool: ...
    def __lt__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...

class Reference:
    name: str
    raw_name: bytes
    raw_shorthand: bytes
    raw_target: Oid | bytes
    shorthand: str
    target: Oid | str
    type: ReferenceType

    @overload
    def __init__(self, name: str, target: str) -> None: ...
    @overload
    def __init__(self, name: str, oid: Oid, peel: Oid) -> None: ...
    def delete(self) -> None: ...
    def log(self) -> Iterator[RefLogEntry]: ...
    @overload
    def peel(self, type: Literal[1] | type[Commit]) -> Commit: ...
    @overload
    def peel(self, type: Literal[2, ObjectType.TREE] | type[Tree]) -> Tree: ...
    @overload
    def peel(self, type: Literal[4, ObjectType.TAG] | type[Tag]) -> Tag: ...
    @overload
    def peel(self, type: Literal[3, ObjectType.BLOB] | type[Blob]) -> Blob: ...
    @overload
    def peel(self, type: Literal[None, ObjectType.ANY]) -> Commit | Tree | Blob: ...
    def rename(self, new_name: str) -> None: ...
    def resolve(self) -> Reference: ...
    def set_target(self, target: _OidArg, message: str = ...) -> None: ...
    def __eq__(self, other: object) -> bool: ...
    def __ge__(self, other: object) -> bool: ...
    def __gt__(self, other: object) -> bool: ...
    def __le__(self, other: object) -> bool: ...
    def __lt__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...

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
    def _write_to_queue(
        self,
        queue: queue.Queue[bytes | None],
        closed: threading.Event,
        chunk_size: int = DEFAULT_BUFFER_SIZE,
        *,
        as_path: str | None = None,
        flags: BlobFilter = BlobFilter.CHECK_FOR_BINARY,
        commit_id: Oid | None = None,
    ) -> None: ...

class Branch(Reference):
    branch_name: str
    raw_branch_name: bytes
    remote_name: str
    upstream: Branch
    upstream_name: str
    def delete(self) -> None: ...
    def is_checked_out(self) -> bool: ...
    def is_head(self) -> bool: ...
    def rename(self, name: str, force: bool = False) -> None: ...  # type: ignore

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
    def from_c(diff: Any, repo: Any) -> Diff: ...
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
    def from_c(bytes: bytes) -> DiffFile: ...

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
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
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
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    def add_backend(self, backend: OdbBackend, priority: int) -> None: ...
    def add_disk_alternate(self, path: str) -> None: ...
    def exists(self, oid: _OidArg) -> bool: ...
    def read(self, oid: _OidArg) -> tuple[int, int, bytes]: ...
    def write(self, type: int, data: bytes) -> Oid: ...
    def __contains__(self, other: _OidArg) -> bool: ...
    def __iter__(self) -> Iterator[Oid]: ...  # Odb_as_iter

class OdbBackend:
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    def exists(self, oid: _OidArg) -> bool: ...
    def exists_prefix(self, partial_id: _OidArg) -> Oid: ...
    def read(self, oid: _OidArg) -> tuple[int, bytes]: ...
    def read_header(self, oid: _OidArg) -> tuple[int, int]: ...
    def read_prefix(self, oid: _OidArg) -> tuple[int, bytes, Oid]: ...
    def refresh(self) -> None: ...
    def __iter__(self) -> Iterator[Oid]: ...  # OdbBackend_as_iter

class OdbBackendLoose(OdbBackend):
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class OdbBackendPack(OdbBackend):
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class Oid:
    raw: bytes
    def __init__(self, raw: bytes = ..., hex: str = ...) -> None: ...
    def __eq__(self, other: object) -> bool: ...
    def __ge__(self, other: object) -> bool: ...
    def __gt__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def __le__(self, other: object) -> bool: ...
    def __lt__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    def __str__(self) -> str: ...

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
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

class Refdb:
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    def compress(self) -> None: ...
    @staticmethod
    def new(repo: Repository) -> Refdb: ...
    @staticmethod
    def open(repo: Repository) -> Refdb: ...
    def set_backend(self, backend: RefdbBackend) -> None: ...

class RefdbBackend:
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
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
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...

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
    def __init__(self, *args: Any, **kwargs: Any) -> None: ...
    def TreeBuilder(self, src: Tree | _OidArg = ...) -> TreeBuilder: ...
    def _disown(self, *args: Any, **kwargs: Any) -> None: ...
    def _from_c(self, *args: Any, **kwargs: Any) -> None: ...
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
    def create_branch(
        self, name: str, commit: Commit, force: bool = False
    ) -> Branch: ...
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
        iter: Iterator[Any],
        references_return_type: ReferenceFilter = ReferenceFilter.ALL,
    ) -> Reference: ...
    def reset(self, oid: _OidArg, reset_type: ResetMode) -> None: ...
    def revparse(self, revspec: str | bytes) -> RevSpec: ...
    def revparse_ext(self, revision: str | bytes) -> tuple[Object, Reference]: ...
    def revparse_single(self, revision: str | bytes) -> Object: ...
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
    def __eq__(self, other: object) -> bool: ...
    def __ge__(self, other: object) -> bool: ...
    def __gt__(self, other: object) -> bool: ...
    def __le__(self, other: object) -> bool: ...
    def __lt__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...

class Stash:
    commit_id: Oid
    message: str
    raw_message: bytes
    def __eq__(self, other: object) -> bool: ...
    def __ge__(self, other: object) -> bool: ...
    def __gt__(self, other: object) -> bool: ...
    def __le__(self, other: object) -> bool: ...
    def __lt__(self, other: object) -> bool: ...
    def __ne__(self, other: object) -> bool: ...

class Tag(Object):
    message: str
    name: str | None
    raw_message: bytes
    raw_name: bytes | None
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
    def prune(self, force: bool = False) -> None: ...

class FilterSource:
    filemode: int
    flags: FilterFlag
    mode: FilterMode
    oid: Oid | None
    path: str
    repo: Repository

def discover_repository(
    path: str, across_fs: bool = False, ceiling_dirs: str = ...
) -> str | None: ...
def hash(data: bytes) -> Oid: ...
def hashfile(path: str) -> Oid: ...
def init_file_backend(path: str, flags: int = 0) -> object: ...
def option(opt: Option, *args: Any) -> None: ...
def reference_is_valid_name(refname: str) -> bool: ...
def tree_entry_cmp(a: Object, b: Object) -> int: ...
def filter_register(
    name: str, filter_cls: type[Filter], priority: int = GIT_FILTER_DRIVER_PRIORITY
) -> None: ...
def filter_unregister(name: str) -> None: ...

_cache_enums: Callable[..., None]
