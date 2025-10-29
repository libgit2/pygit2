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

"""Tests for Diff objects."""

import textwrap
from collections.abc import Iterator
from itertools import chain
from pathlib import Path

import pytest

import pygit2
from pygit2 import Diff, Repository
from pygit2.enums import DeltaStatus, DiffFlag, DiffOption, DiffStatsFormat, FileMode

from .utils import diff_safeiter

COMMIT_SHA1_1 = '5fe808e8953c12735680c257f56600cb0de44b10'
COMMIT_SHA1_2 = 'c2792cfa289ae6321ecf2cd5806c2194b0fd070c'
COMMIT_SHA1_3 = '2cdae28389c059815e951d0bb9eed6533f61a46b'
COMMIT_SHA1_4 = 'ccca47fbb26183e71a7a46d165299b84e2e6c0b3'
COMMIT_SHA1_5 = '056e626e51b1fc1ee2182800e399ed8d84c8f082'
COMMIT_SHA1_6 = 'f5e5aa4e36ab0fe62ee1ccc6eb8f79b866863b87'
COMMIT_SHA1_7 = '784855caf26449a1914d2cf62d12b9374d76ae78'


PATCH = """diff --git a/a b/a
index 7f129fd..af431f2 100644
--- a/a
+++ b/a
@@ -1 +1 @@
-a contents 2
+a contents
diff --git a/c/d b/c/d
deleted file mode 100644
index 297efb8..0000000
--- a/c/d
+++ /dev/null
@@ -1 +0,0 @@
-c/d contents
"""

PATCHID = 'f31412498a17e6c3fbc635f2c5f9aa3ef4c1a9b7'

DIFF_HEAD_TO_INDEX_EXPECTED = [
    '.gitignore',
    'staged_changes',
    'staged_changes_file_deleted',
    'staged_changes_file_modified',
    'staged_delete',
    'staged_delete_file_modified',
    'staged_new',
    'staged_new_file_deleted',
    'staged_new_file_modified',
]

DIFF_HEAD_TO_WORKDIR_EXPECTED = [
    'file_deleted',
    'modified_file',
    'staged_changes',
    'staged_changes_file_deleted',
    'staged_changes_file_modified',
    'staged_delete',
    'staged_delete_file_modified',
    'subdir/deleted_file',
    'subdir/modified_file',
]

DIFF_INDEX_TO_WORK_EXPECTED = [
    '.gitignore',
    'file_deleted',
    'modified_file',
    'staged_changes_file_deleted',
    'staged_changes_file_modified',
    'staged_new_file_deleted',
    'staged_new_file_modified',
    'subdir/deleted_file',
    'subdir/modified_file',
]

HUNK_EXPECTED = """- a contents 2
+ a contents
"""

STATS_EXPECTED = """ a   | 2 +-
 c/d | 1 -
 2 files changed, 1 insertion(+), 2 deletions(-)
 delete mode 100644 c/d
"""

TEXT_BLOB1 = """Common header of the file
Blob 1 line 1
Common middle line 1
Common middle line 2
Common middle line 3
Blob 1 line 2
Common footer of the file
"""

TEXT_BLOB2 = """Common header of the file
Blob 2 line 1
Common middle line 1
Common middle line 2
Common middle line 3
Blob 2 line 2
Common footer of the file
"""

PATCH_BLOBS_DEFAULT = """diff --git a/file b/file
index 0b5ac93..ddfdbcc 100644
--- a/file
+++ b/file
@@ -1,7 +1,7 @@
 Common header of the file
-Blob 1 line 1
+Blob 2 line 1
 Common middle line 1
 Common middle line 2
 Common middle line 3
-Blob 1 line 2
+Blob 2 line 2
 Common footer of the file
"""

PATCH_BLOBS_NO_LEEWAY = """diff --git a/file b/file
index 0b5ac93..ddfdbcc 100644
--- a/file
+++ b/file
@@ -2 +2 @@ Common header of the file
-Blob 1 line 1
+Blob 2 line 1
@@ -6 +6 @@ Common middle line 3
-Blob 1 line 2
+Blob 2 line 2
"""

PATCH_BLOBS_ONE_CONTEXT_LINE = """diff --git a/file b/file
index 0b5ac93..ddfdbcc 100644
--- a/file
+++ b/file
@@ -1,3 +1,3 @@
 Common header of the file
-Blob 1 line 1
+Blob 2 line 1
 Common middle line 1
@@ -5,3 +5,3 @@ Common middle line 2
 Common middle line 3
-Blob 1 line 2
+Blob 2 line 2
 Common footer of the file
"""


def test_diff_empty_index(dirtyrepo: Repository) -> None:
    repo = dirtyrepo
    head = repo[repo.lookup_reference('HEAD').resolve().target]

    diff = head.tree.diff_to_index(repo.index)
    files = [patch.delta.new_file.path for patch in diff_safeiter(diff)]
    assert DIFF_HEAD_TO_INDEX_EXPECTED == files

    diff = repo.diff('HEAD', cached=True)
    files = [patch.delta.new_file.path for patch in diff_safeiter(diff)]
    assert DIFF_HEAD_TO_INDEX_EXPECTED == files


def test_workdir_to_tree(dirtyrepo: Repository) -> None:
    repo = dirtyrepo
    head = repo[repo.lookup_reference('HEAD').resolve().target]

    diff = head.tree.diff_to_workdir()
    files = [patch.delta.new_file.path for patch in diff_safeiter(diff)]
    assert DIFF_HEAD_TO_WORKDIR_EXPECTED == files

    diff = repo.diff('HEAD')
    files = [patch.delta.new_file.path for patch in diff_safeiter(diff)]
    assert DIFF_HEAD_TO_WORKDIR_EXPECTED == files


def test_index_to_workdir(dirtyrepo: Repository) -> None:
    diff = dirtyrepo.diff()
    files = [patch.delta.new_file.path for patch in diff_safeiter(diff)]
    assert DIFF_INDEX_TO_WORK_EXPECTED == files


def test_diff_invalid(barerepo: Repository) -> None:
    commit_a = barerepo[COMMIT_SHA1_1]
    commit_b = barerepo[COMMIT_SHA1_2]
    with pytest.raises(TypeError):
        commit_a.tree.diff_to_tree(commit_b)  # type: ignore
    with pytest.raises(TypeError):
        commit_a.tree.diff_to_index(commit_b)  # type: ignore


def test_diff_empty_index_bare(barerepo: Repository) -> None:
    repo = barerepo
    head = repo[repo.lookup_reference('HEAD').resolve().target]

    diff = barerepo.index.diff_to_tree(head.tree)
    files = [patch.delta.new_file.path.split('/')[0] for patch in diff_safeiter(diff)]
    assert [x.name for x in head.tree] == files

    diff = head.tree.diff_to_index(repo.index)
    files = [patch.delta.new_file.path.split('/')[0] for patch in diff_safeiter(diff)]
    assert [x.name for x in head.tree] == files

    diff = repo.diff('HEAD', cached=True)
    files = [patch.delta.new_file.path.split('/')[0] for patch in diff_safeiter(diff)]
    assert [x.name for x in head.tree] == files


def test_diff_tree(barerepo: Repository) -> None:
    commit_a = barerepo[COMMIT_SHA1_1]
    commit_b = barerepo[COMMIT_SHA1_2]

    def _test(diff: Diff) -> None:
        assert diff is not None
        assert 2 == sum(map(lambda x: len(x.hunks), diff_safeiter(diff)))

        patch = diff[0]
        assert patch is not None
        hunk = patch.hunks[0]
        assert hunk.old_start == 1
        assert hunk.old_lines == 1
        assert hunk.new_start == 1
        assert hunk.new_lines == 1

        assert not patch.delta.is_binary
        assert patch.delta.flags & DiffFlag.NOT_BINARY

        for dfile in patch.delta.old_file, patch.delta.new_file:
            assert dfile.path == 'a'
            assert (
                dfile.flags
                == DiffFlag.NOT_BINARY
                | DiffFlag.VALID_ID
                | DiffFlag.VALID_SIZE
                | DiffFlag.EXISTS
            )
            assert dfile.mode == FileMode.BLOB

    _test(commit_a.tree.diff_to_tree(commit_b.tree))
    _test(barerepo.diff(COMMIT_SHA1_1, COMMIT_SHA1_2))


def test_diff_empty_tree(barerepo: Repository) -> None:
    commit_a = barerepo[COMMIT_SHA1_1]
    diff = commit_a.tree.diff_to_tree()

    def get_context_for_lines(diff: Diff) -> Iterator[str]:
        hunks = chain.from_iterable(map(lambda x: x.hunks, diff_safeiter(diff)))
        lines = chain.from_iterable(map(lambda x: x.lines, hunks))
        return map(lambda x: x.origin, lines)

    entries = [p.delta.new_file.path for p in diff_safeiter(diff)]
    assert all(commit_a.tree[x] for x in entries)
    assert all('-' == x for x in get_context_for_lines(diff))

    diff_swaped = commit_a.tree.diff_to_tree(swap=True)
    entries = [p.delta.new_file.path for p in diff_safeiter(diff_swaped)]
    assert all(commit_a.tree[x] for x in entries)
    assert all('+' == x for x in get_context_for_lines(diff_swaped))


def test_diff_revparse(barerepo: Repository) -> None:
    diff = barerepo.diff('HEAD', 'HEAD~6')
    assert type(diff) is pygit2.Diff


def test_diff_tree_opts(barerepo: Repository) -> None:
    commit_c = barerepo[COMMIT_SHA1_3]
    commit_d = barerepo[COMMIT_SHA1_4]

    for flag in [DiffOption.IGNORE_WHITESPACE, DiffOption.IGNORE_WHITESPACE_EOL]:
        diff = commit_c.tree.diff_to_tree(commit_d.tree, flag)
        assert diff is not None
        patch = diff[0]
        assert patch is not None
        assert 0 == len(patch.hunks)

    diff = commit_c.tree.diff_to_tree(commit_d.tree)
    assert diff is not None
    patch = diff[0]
    assert patch is not None
    assert 1 == len(patch.hunks)


def test_diff_merge(barerepo: Repository) -> None:
    commit_a = barerepo[COMMIT_SHA1_1]
    commit_b = barerepo[COMMIT_SHA1_2]
    commit_c = barerepo[COMMIT_SHA1_3]

    diff_b = commit_a.tree.diff_to_tree(commit_b.tree)
    assert diff_b is not None

    diff_c = commit_b.tree.diff_to_tree(commit_c.tree)
    assert diff_c is not None
    assert 'b' not in [patch.delta.new_file.path for patch in diff_safeiter(diff_b)]
    assert 'b' in [patch.delta.new_file.path for patch in diff_safeiter(diff_c)]

    diff_b.merge(diff_c)
    assert 'b' in [patch.delta.new_file.path for patch in diff_safeiter(diff_b)]

    patch = diff_b[0]
    assert patch is not None
    hunk = patch.hunks[0]
    assert hunk.old_start == 1
    assert hunk.old_lines == 1
    assert hunk.new_start == 1
    assert hunk.new_lines == 1

    assert patch.delta.old_file.path == 'a'
    assert patch.delta.new_file.path == 'a'


def test_diff_patch(barerepo: Repository) -> None:
    commit_a = barerepo[COMMIT_SHA1_1]
    commit_b = barerepo[COMMIT_SHA1_2]

    diff = commit_a.tree.diff_to_tree(commit_b.tree)
    assert diff.patch == PATCH
    assert len(diff) == len([patch for patch in diff])


def test_diff_ids(barerepo: Repository) -> None:
    commit_a = barerepo[COMMIT_SHA1_1]
    commit_b = barerepo[COMMIT_SHA1_2]
    patch = commit_a.tree.diff_to_tree(commit_b.tree)[0]
    assert patch is not None
    delta = patch.delta
    assert delta.old_file.id == '7f129fd57e31e935c6d60a0c794efe4e6927664b'
    assert delta.new_file.id == 'af431f20fc541ed6d5afede3e2dc7160f6f01f16'


def test_diff_patchid(barerepo: Repository) -> None:
    commit_a = barerepo[COMMIT_SHA1_1]
    commit_b = barerepo[COMMIT_SHA1_2]
    diff = commit_a.tree.diff_to_tree(commit_b.tree)
    assert diff.patch == PATCH
    assert diff.patchid == PATCHID


def test_hunk_content(barerepo: Repository) -> None:
    commit_a = barerepo[COMMIT_SHA1_1]
    commit_b = barerepo[COMMIT_SHA1_2]
    patch = commit_a.tree.diff_to_tree(commit_b.tree)[0]
    assert patch is not None
    hunk = patch.hunks[0]
    lines = (f'{x.origin} {x.content}' for x in hunk.lines)
    assert HUNK_EXPECTED == ''.join(lines)
    for line in hunk.lines:
        assert line.content == line.raw_content.decode()


def test_find_similar(barerepo: Repository) -> None:
    commit_a = barerepo[COMMIT_SHA1_6]
    commit_b = barerepo[COMMIT_SHA1_7]

    # ~ Must pass INCLUDE_UNMODIFIED if you expect to emulate
    # ~ --find-copies-harder during rename transformion...
    diff = commit_a.tree.diff_to_tree(commit_b.tree, DiffOption.INCLUDE_UNMODIFIED)
    assert all(
        patch.delta.status != DeltaStatus.RENAMED for patch in diff_safeiter(diff)
    )
    assert all(patch.delta.status_char() != 'R' for patch in diff_safeiter(diff))
    diff.find_similar()
    assert any(
        patch.delta.status == DeltaStatus.RENAMED for patch in diff_safeiter(diff)
    )
    assert any(patch.delta.status_char() == 'R' for patch in diff_safeiter(diff))


def test_diff_stats(barerepo: Repository) -> None:
    commit_a = barerepo[COMMIT_SHA1_1]
    commit_b = barerepo[COMMIT_SHA1_2]

    diff = commit_a.tree.diff_to_tree(commit_b.tree)
    stats = diff.stats
    assert 1 == stats.insertions
    assert 2 == stats.deletions
    assert 2 == stats.files_changed
    formatted = stats.format(
        format=DiffStatsFormat.FULL | DiffStatsFormat.INCLUDE_SUMMARY, width=80
    )
    assert STATS_EXPECTED == formatted


def test_deltas(barerepo: Repository) -> None:
    commit_a = barerepo[COMMIT_SHA1_1]
    commit_b = barerepo[COMMIT_SHA1_2]
    diff = commit_a.tree.diff_to_tree(commit_b.tree)
    deltas = list(diff.deltas)
    patches = list(diff_safeiter(diff))
    assert len(deltas) == len(patches)
    for i, delta in enumerate(deltas):
        patch_delta = patches[i].delta
        assert isinstance(delta.status, DeltaStatus)
        assert isinstance(patch_delta.status, DeltaStatus)
        assert delta.status == patch_delta.status
        assert delta.similarity == patch_delta.similarity
        assert delta.nfiles == patch_delta.nfiles
        assert delta.old_file.id == patch_delta.old_file.id
        assert delta.new_file.id == patch_delta.new_file.id
        assert delta.old_file.mode == patch_delta.old_file.mode
        assert delta.new_file.mode == patch_delta.new_file.mode

        # As explained in the libgit2 documentation, flags are not set
        # assert delta.flags == patch_delta.flags


def test_diff_parse(barerepo: Repository) -> None:
    diff = pygit2.Diff.parse_diff(PATCH)

    stats = diff.stats
    assert 2 == stats.deletions
    assert 1 == stats.insertions
    assert 2 == stats.files_changed

    deltas = list(diff.deltas)
    assert 2 == len(deltas)


def test_parse_diff_null() -> None:
    with pytest.raises(TypeError):
        pygit2.Diff.parse_diff(None)  # type: ignore


def test_parse_diff_bad() -> None:
    diff = textwrap.dedent(
        """
    diff --git a/file1 b/file1
    old mode 0644
    new mode 0644
    @@ -1,1 +1,1 @@
    -Hi!
    """
    )
    with pytest.raises(pygit2.GitError):
        pygit2.Diff.parse_diff(diff)


def test_diff_blobs(emptyrepo: Repository) -> None:
    repo = emptyrepo
    blob1 = repo.create_blob(TEXT_BLOB1.encode())
    blob2 = repo.create_blob(TEXT_BLOB2.encode())
    diff_default = repo.diff(blob1, blob2)
    assert diff_default.text == PATCH_BLOBS_DEFAULT
    diff_no_leeway = repo.diff(blob1, blob2, context_lines=0)
    assert diff_no_leeway.text == PATCH_BLOBS_NO_LEEWAY
    diff_one_context_line = repo.diff(blob1, blob2, context_lines=1)
    assert diff_one_context_line.text == PATCH_BLOBS_ONE_CONTEXT_LINE
    diff_all_together = repo.diff(blob1, blob2, context_lines=1, interhunk_lines=1)
    assert diff_all_together.text == PATCH_BLOBS_DEFAULT


def test_diff_unchanged_file_no_patch(testrepo: Repository) -> None:
    repo = testrepo

    # Convert hello.txt line endings to CRLF
    path = Path(repo.workdir) / 'hello.txt'
    data = path.read_bytes()
    data = data.replace(b'\n', b'\r\n')
    path.write_bytes(data)

    # Enable CRLF filter
    repo.config['core.autocrlf'] = 'input'

    diff = repo.diff()
    assert len(diff) == 1

    # Get patch #0 in the same diff several times.
    # git_patch_from_diff eventually decides that the file is "unchanged";
    # it returns a NULL patch in this case.
    # https://libgit2.org/docs/reference/main/patch/git_patch_from_diff
    for i in range(10):  # loop typically exits in the third iteration
        patch = diff[0]
        if patch is None:  # libgit2 decides the file is unchanged
            break
        assert patch.delta.new_file.path == path.name
        assert patch.text == ''  # no content change (just line endings)
    else:
        # Didn't find the edge case that this test is supposed to exercise.
        assert False, 'libgit2 rebuilt a new patch every time'
