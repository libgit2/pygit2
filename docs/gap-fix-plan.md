# pygit2 Gap Fix Plan: Critical Gaps 1-3

## Executive Summary

This document outlines fixes for three critical gaps in pygit2 that block Athena's PR generation workflow. Each gap requires changes to both C extension code and Python wrappers.

**Gaps Fixed:**
- **Gap 1** (CRITICAL): Temporary Index Plumbing - Add `Repository.set_index()` and enhance `Index` class
- **Gap 2** (HIGH): 3-Way Merge Apply - Add `ApplyLocation` flag or new method
- **Gap 3** (MEDIUM): Intent-to-Add with Null OID - Allow null OID entries in index

---

## Gap 1: Temporary Index Plumbing

### Problem
Cannot perform atomic "apply to temp index, then commit-tree" pattern used by PR generation.

### Current State
- `git_repository_set_index()` exists in libgit2 but not exposed by pygit2
- `RepositoryOpenFlag.FROM_ENV` respects `GIT_INDEX_FILE` only at open time
- No way to swap a repository's internal index after opening

### Proposed Fix

#### C Extension Changes (`src/repository.c`)

Add new method to expose `git_repository_set_index()`:

```c
PyDoc_STRVAR(Repository_set_index__doc__,
  "set_index(index: Index) -> None\n\n"
  "Set the repository's internal index to the given Index object.\n"
  "This allows atomic operations on a temporary index without\n"
  "modifying the repository's working tree or commit history.\n"
  "\n"
  "Parameters:\n"
  "\n"
  "index\n"
  "    The Index object to set as the repository's index.\n"
);

PyObject *
Repository_set_index(Repository *self, PyObject *args)
{
    Index *py_index;
    
    if (!PyArg_ParseTuple(args, "O!", &IndexType, &py_index))
        return NULL;
    
    int err = git_repository_set_index(self->repo, py_index->index);
    if (err != 0)
        return Error_set(err);
    
    Py_RETURN_NONE;
}
```

Register in method table:
```c
{"set_index", (PyCFunction) Repository_set_index, METH_VARARGS, Repository_set_index__doc__},
```

#### Python Changes (`pygit2/repository.py`)

Add type hints and documentation:
```python
def set_index(self, index: 'Index') -> None:
    """
    Set the repository's internal index to the given Index object.
    
    This enables atomic workflows where you can:
    1. Create a temporary index from the current tree
    2. Apply changes to the temporary index
    3. Write a new tree and commit
    4. Restore the original index or discard changes
    
    Example::
    
        >>> temp_index = pygit2.Index(temp_path)
        >>> temp_index.read_tree(repo.head.peel().tree)
        >>> # ... modify temp_index ...
        >>> repo.set_index(temp_index)
        >>> new_tree = repo.index.write_tree()
        >>> repo.create_commit('HEAD', sig, sig, 'msg', new_tree, [commit])
        >>> repo.set_index(original_index)  # restore if needed
    """
    pass  # Implemented in C
```

#### Python Changes (`pygit2/index.py`)

Enhance `Index` class to support standalone operations:

```python
def read_tree(self, tree: 'Tree | Oid | str', repo: 'Repository | None' = None) -> None:
    """Read a tree into this index.
    
    Unlike the existing read_tree(), this version works with
    standalone indexes (no associated repository).
    """
    # ... implementation already exists, just needs docs updated
```

Add `copy_from()` method:
```python
def copy_from(self, other: 'Index') -> None:
    """Copy all entries from another index."""
    self.clear()
    for i in range(len(other)):
        entry = other[i]
        self.add(entry)
```

### Workaround (Current State)
```python
# Manual workaround without set_index()
temp_index = pygit2.Index(temp_path)
for i in range(len(repo.index)):
    temp_index.add(repo.index[i])

# Modify temp_index...
new_tree = temp_index.write_tree(repo)
new_commit = repo.create_commit('HEAD', sig, sig, 'msg', new_tree, [repo.head.peel()])
```

---

## Gap 2: 3-Way Merge Apply

### Problem
`repo.apply()` doesn't support 3-way merge fallback for parallel worktree merges.

### Current State
- `repo.apply(diff, location)` only supports WORKDIR/INDEX/BOTH
- No 3-way merge option
- `git_apply` in libgit2 doesn't have a 3-way flag

### Analysis

Looking at libgit2 source and headers, `git_apply` does NOT support 3-way merging. The 3-way merge capability exists in `git_merge_trees()`, not in the apply API.

### Proposed Fix

#### Option A: Wrapper Using merge_trees() (Recommended)

Add a new method `Repository.merge_diff()` that performs 3-way merge:

```python
def merge_diff(self, ours: Tree, theirs: Tree, ancestor: Tree) -> Index:
    """
    Perform a 3-way merge between trees and return the resulting index.
    
    Parameters:
    -----------
    ours : Tree
        Current HEAD tree
    theirs : Tree
        Incoming changes tree
    ancestor : Tree
        Common ancestor tree
    
    Returns:
    --------
    Index
        The merged index with conflicts marked
    """
    from .ffi import C, ffi
    
    ours_ptr = ffi.new('git_tree **')
    ffi.buffer(ours_ptr)[:] = ours._pointer[:]
    
    theirs_ptr = ffi.new('git_tree **')
    ffi.buffer(theirs_ptr)[:] = theirs._pointer[:]
    
    ancestor_ptr = ffi.new('git_tree **')
    ffi.buffer(ancestor_ptr)[:] = ancestor._pointer[:]
    
    merged_tree = ffi.new('git_tree **')
    
    opts = ffi.new('git_merge_tree_options *')
    C.git_merge_tree_options_init(opts, C.GIT_MERGE_TREE_OPTIONS_VERSION)
    
    err = C.git_merge_tree(merged_tree, ours_ptr[0], theirs_ptr[0], 
                           ancestor_ptr[0], opts)
    check_error(err)
    
    # Build index from merged tree
    result = pygit2.Index()
    result.read_tree(merged_tree[0], self)
    return result
```

#### Option B: Extend ApplyLocation Enum

Add a `THREE_WAY` option (requires libgit2 changes first):
```python
class ApplyLocation(IntEnum):
    WORKDIR = _pygit2.GIT_APPLY_LOCATION_WORKDIR
    INDEX = _pygit2.GIT_APPLY_LOCATION_INDEX
    BOTH = _pygit2.GIT_APPLY_LOCATION_BOTH
    THREE_WAY = 4  # Would require libgit2 patch
```

### Recommendation
Go with Option A - wrapper using existing `merge_trees()` API. This is cleaner and doesn't require libgit2 changes.

---

## Gap 3: Intent-to-Add with Null OID

### Problem
Cannot create intent-to-add entries (like `git add -N`) with null blob IDs.

### Current State
- `IndexEntry` accepts null OID in constructor
- `Index.add()` rejects null OID entries
- No `git add -N` equivalent

### Analysis

The issue is in `Index.add()`:
```python
def add(self, path_or_entry):
    if isinstance(path_or_entry, IndexEntry):
        entry = path_or_entry
        centry, str_ref = entry._to_c()
        err = C.git_index_add(self._index, centry)
    # ...
```

The `_to_c()` method copies the OID directly:
```python
def _to_c(self):
    centry = ffi.new('git_index_entry *')
    ffi.buffer(ffi.addressof(centry, 'id'))[:] = self.id.raw[:]
    # ...
```

### Proposed Fix

#### Option A: Allow Null OID in Index.add()

Modify `Index.add()` to explicitly allow null OID:

```python
def add(self, path_or_entry: 'IndexEntry | str | PathLike[str]', 
        allow_null_oid: bool = False) -> None:
    """Add or update an entry in the Index.
    
    Parameters:
    -----------
    path_or_entry : IndexEntry or str
        The entry to add
    allow_null_oid : bool
        If True, allow null OID for intent-to-add semantics
    """
    if isinstance(path_or_entry, IndexEntry):
        entry = path_or_entry
        if entry.id.is_zero and not allow_null_oid:
            raise ValueError(
                "Null OID not allowed. Use git add -N semantics via "
                "create_intent_entry() or set allow_null_oid=True"
            )
        centry, str_ref = entry._to_c()
        err = C.git_index_add(self._index, centry)
    # ...
```

#### Option B: Add New Method `add_intent()`

Add a dedicated method for intent-to-add:

```python
def add_intent(self, path: str) -> None:
    """Add an intent-to-add entry with null OID (like git add -N).
    
    This creates an index entry with a null blob ID, making the file
    visible in git diff without staging its content.
    """
    null_oid = Oid(hex='0000000000000000000000000000000000000000')
    entry = IndexEntry(path, null_oid, 0o100644)
    # Bypass the null OID check
    centry, str_ref = entry._to_c()
    err = C.git_index_add(self._index, centry)
    check_error(err, io=True)
```

### Recommendation
Go with Option B - new method. This is cleaner and more explicit about the intent.

---

## Implementation Priority

1. **Gap 1** (CRITICAL) - `Repository.set_index()`
   - Enables atomic PR generation workflow
   - Blocks: `athena/pr_generator/branch.py` and `quality_pr.py`

2. **Gap 2** (HIGH) - `Repository.merge_diff()`
   - Enables 3-way merge for parallel worktrees
   - Blocks: remediation merge-back in `runner.py`

3. **Gap 3** (MEDIUM) - `Index.add_intent()`
   - Enables intent-to-add semantics
   - Blocks: `gitcapture.py` diff capture for new files

---

## Files to Modify

### C Extension
- `src/repository.c` - Add `Repository_set_index()`
- `src/repository.h` - Add declaration

### Python
- `pygit2/repository.py` - Add type stubs and docs
- `pygit2/index.py` - Add `add_intent()` method
- `pygit2/_pygit2.pyi` - Update type stubs
- `pygit2/enums.py` - Potentially add `MergeAnalysis` flags

### Tests
- `test/test_repository.py` - Test `set_index()`
- `test/test_index.py` - Test `add_intent()`
- `test/test_merge.py` - Test `merge_diff()`

---

## Testing Strategy

### Gap 1 Test
```python
def test_set_index():
    repo = pygit2.Repository('.')
    original_index = repo.index
    
    temp_index = pygit2.Index(tempfile.mktemp())
    temp_index.copy_from(original_index)
    temp_index.add('new_file.txt')
    
    repo.set_index(temp_index)
    assert len(repo.index) == len(original_index) + 1
    
    repo.set_index(original_index)  # restore
```

### Gap 2 Test
```python
def test_merge_diff():
    repo = pygit2.Repository('.')
    theirs = repo.get('theirs_tree').peel(Tree)
    ancestor = repo.get('ancestor_tree').peel(Tree)
    
    merged_index = repo.merge_diff(repo.head.peel().tree, theirs, ancestor)
    assert not merged_index.has_conflicts()
```

### Gap 3 Test
```python
def test_add_intent():
    repo = pygit2.Repository('.')
    repo.index.add_intent('new_file.txt')
    
    entry = repo.index['new_file.txt']
    assert entry.id.is_zero
```

---

## Timeline Estimate

| Gap | Complexity | Est. Time |
|-----|-----------|-----------|
| Gap 1 | Low (1 C method + Python wrapper) | 2-3 hours |
| Gap 2 | Medium (new method with merge logic) | 4-6 hours |
| Gap 3 | Low (new method in Index) | 1-2 hours |
| **Total** | | **7-11 hours** |

---

## References

- libgit2 `git_repository_set_index()`: `/opt/homebrew/include/git2/sys/repository.h`
- libgit2 `git_merge_tree()`: `/opt/homebrew/include/git2/merge.h`
- Current pygit2 `Repository.apply()`: `src/repository.c:2234`
- Current pygit2 `Index.add()`: `pygit2/index.py:208`
