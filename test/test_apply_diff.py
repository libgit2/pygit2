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

import os
from pathlib import Path

import pytest

import pygit2
from pygit2 import Diff, Repository
from pygit2.enums import ApplyLocation, CheckoutStrategy, FileStatus


def read_content(testrepo: Repository) -> str:
    with (Path(testrepo.workdir) / 'hello.txt').open('rb') as f:
        return f.read().decode('utf-8')


@pytest.fixture
def new_content() -> str:
    content_list = ['bye world', 'adiós', 'au revoir monde']
    content = ''.join(x + os.linesep for x in content_list)
    return content


@pytest.fixture
def old_content(testrepo: Repository) -> str:
    with (Path(testrepo.workdir) / 'hello.txt').open('rb') as f:
        return f.read().decode('utf-8')


@pytest.fixture
def patch_diff(testrepo: Repository, new_content: str) -> Diff:
    # Create the patch
    with (Path(testrepo.workdir) / 'hello.txt').open('wb') as f:
        f.write(new_content.encode('utf-8'))

    patch = testrepo.diff().patch
    assert patch is not None

    # Rollback all changes
    testrepo.checkout('HEAD', strategy=CheckoutStrategy.FORCE)

    # Return the diff
    return pygit2.Diff.parse_diff(patch)


@pytest.fixture
def foreign_patch_diff() -> Diff:
    patch_contents = """diff --git a/this_file_does_not_exist b/this_file_does_not_exist
index 7f129fd..af431f2 100644
--- a/this_file_does_not_exist
+++ b/this_file_does_not_exist
@@ -1 +1 @@
-a contents 2
+a contents
"""
    return pygit2.Diff.parse_diff(patch_contents)


def test_apply_type_error(testrepo: Repository) -> None:
    # Check apply type error
    with pytest.raises(TypeError):
        testrepo.apply('HEAD')  # type: ignore


def test_apply_diff_to_workdir(
    testrepo: Repository, new_content: str, patch_diff: Diff
) -> None:
    # Apply the patch and compare
    testrepo.apply(patch_diff, ApplyLocation.WORKDIR)

    assert read_content(testrepo) == new_content
    assert testrepo.status_file('hello.txt') == FileStatus.WT_MODIFIED


def test_apply_diff_to_index(
    testrepo: Repository, old_content: str, patch_diff: Diff
) -> None:
    # Apply the patch and compare
    testrepo.apply(patch_diff, ApplyLocation.INDEX)

    assert read_content(testrepo) == old_content
    assert testrepo.status_file('hello.txt') & FileStatus.INDEX_MODIFIED


def test_apply_diff_to_both(
    testrepo: Repository, new_content: str, patch_diff: Diff
) -> None:
    # Apply the patch and compare
    testrepo.apply(patch_diff, ApplyLocation.BOTH)

    assert read_content(testrepo) == new_content
    assert testrepo.status_file('hello.txt') & FileStatus.INDEX_MODIFIED


def test_diff_applies_to_workdir(
    testrepo: Repository, old_content: str, patch_diff: Diff
) -> None:
    # See if patch applies
    assert testrepo.applies(patch_diff, ApplyLocation.WORKDIR)

    # Ensure it was a dry run
    assert read_content(testrepo) == old_content

    # Apply patch for real, then ensure it can't be applied again
    testrepo.apply(patch_diff, ApplyLocation.WORKDIR)
    assert not testrepo.applies(patch_diff, ApplyLocation.WORKDIR)

    # It can still be applied to the index, though
    assert testrepo.applies(patch_diff, ApplyLocation.INDEX)


def test_diff_applies_to_index(
    testrepo: Repository, old_content: str, patch_diff: Diff
) -> None:
    # See if patch applies
    assert testrepo.applies(patch_diff, ApplyLocation.INDEX)

    # Ensure it was a dry run
    assert read_content(testrepo) == old_content

    # Apply patch for real, then ensure it can't be applied again
    testrepo.apply(patch_diff, ApplyLocation.INDEX)
    assert not testrepo.applies(patch_diff, ApplyLocation.INDEX)

    # It can still be applied to the workdir, though
    assert testrepo.applies(patch_diff, ApplyLocation.WORKDIR)


def test_diff_applies_to_both(
    testrepo: Repository, old_content: str, patch_diff: Diff
) -> None:
    # See if patch applies
    assert testrepo.applies(patch_diff, ApplyLocation.BOTH)

    # Ensure it was a dry run
    assert read_content(testrepo) == old_content

    # Apply patch for real, then ensure it can't be applied again
    testrepo.apply(patch_diff, ApplyLocation.BOTH)
    assert not testrepo.applies(patch_diff, ApplyLocation.BOTH)
    assert not testrepo.applies(patch_diff, ApplyLocation.WORKDIR)
    assert not testrepo.applies(patch_diff, ApplyLocation.INDEX)


def test_applies_error(
    testrepo: Repository, old_content: str, patch_diff: Diff, foreign_patch_diff: Diff
) -> None:
    # Try to apply a "foreign" patch that affects files that aren't in the repo;
    # ensure we get OSError about the missing file (due to raise_error)
    with pytest.raises(OSError):
        testrepo.applies(foreign_patch_diff, ApplyLocation.BOTH, raise_error=True)

    # Apply a valid patch
    testrepo.apply(patch_diff, ApplyLocation.BOTH)

    # Ensure it can't be applied again and we get an exception about it (due to raise_error)
    with pytest.raises(pygit2.GitError):
        testrepo.applies(patch_diff, ApplyLocation.BOTH, raise_error=True)
