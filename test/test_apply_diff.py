# Copyright 2010-2021 The pygit2 contributors
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

import pygit2
import pytest

import os
from pathlib import Path


def read_content(testrepo):
    with (Path(testrepo.workdir) / 'hello.txt').open('rb') as f:
        return f.read().decode('utf-8')

@pytest.fixture
def new_content():
    content = ['bye world', 'adiós', 'au revoir monde']
    content = ''.join(x + os.linesep for x in content)
    return content

@pytest.fixture
def old_content(testrepo):
    with (Path(testrepo.workdir) / 'hello.txt').open('rb') as f:
        return f.read().decode('utf-8')

@pytest.fixture
def patch_diff(testrepo, new_content):
    # Create the patch
    with (Path(testrepo.workdir) / 'hello.txt').open('wb') as f:
        f.write(new_content.encode('utf-8'))

    patch = testrepo.diff().patch

    # Rollback all changes
    testrepo.checkout('HEAD', strategy=pygit2.GIT_CHECKOUT_FORCE)

    # Return the diff
    return pygit2.Diff.parse_diff(patch)


def test_apply_type_error(testrepo):
    # Check apply type error
    with pytest.raises(TypeError):
        testrepo.apply('HEAD')

def test_apply_diff_to_workdir(testrepo, new_content, patch_diff):
    # Apply the patch and compare
    testrepo.apply(patch_diff, pygit2.GIT_APPLY_LOCATION_WORKDIR)

    assert read_content(testrepo) == new_content
    assert testrepo.status_file('hello.txt') == pygit2.GIT_STATUS_WT_MODIFIED

def test_apply_diff_to_index(testrepo, old_content, patch_diff):
    # Apply the patch and compare
    testrepo.apply(patch_diff, pygit2.GIT_APPLY_LOCATION_INDEX)

    assert read_content(testrepo) == old_content
    assert testrepo.status_file('hello.txt') & pygit2.GIT_STATUS_INDEX_MODIFIED

def test_apply_diff_to_both(testrepo, new_content, patch_diff):
    # Apply the patch and compare
    testrepo.apply(patch_diff, pygit2.GIT_APPLY_LOCATION_BOTH)

    assert read_content(testrepo) == new_content
    assert testrepo.status_file('hello.txt') & pygit2.GIT_STATUS_INDEX_MODIFIED

def test_diff_applies_to_workdir(testrepo, old_content, patch_diff):
    # See if patch applies
    assert testrepo.applies(patch_diff, pygit2.GIT_APPLY_LOCATION_WORKDIR)

    # Ensure it was a dry run
    assert read_content(testrepo) == old_content

    # Apply patch for real, then ensure it can't be applied again
    testrepo.apply(patch_diff, pygit2.GIT_APPLY_LOCATION_WORKDIR)
    assert not testrepo.applies(patch_diff, pygit2.GIT_APPLY_LOCATION_WORKDIR)

    # It can still be applied to the index, though
    assert testrepo.applies(patch_diff, pygit2.GIT_APPLY_LOCATION_INDEX)

def test_diff_applies_to_index(testrepo, old_content, patch_diff):
    # See if patch applies
    assert testrepo.applies(patch_diff, pygit2.GIT_APPLY_LOCATION_INDEX)

    # Ensure it was a dry run
    assert read_content(testrepo) == old_content

    # Apply patch for real, then ensure it can't be applied again
    testrepo.apply(patch_diff, pygit2.GIT_APPLY_LOCATION_INDEX)
    assert not testrepo.applies(patch_diff, pygit2.GIT_APPLY_LOCATION_INDEX)

    # It can still be applied to the workdir, though
    assert testrepo.applies(patch_diff, pygit2.GIT_APPLY_LOCATION_WORKDIR)

def test_diff_applies_to_both(testrepo, old_content, patch_diff):
    # See if patch applies
    assert testrepo.applies(patch_diff, pygit2.GIT_APPLY_LOCATION_BOTH)

    # Ensure it was a dry run
    assert read_content(testrepo) == old_content

    # Apply patch for real, then ensure it can't be applied again
    testrepo.apply(patch_diff, pygit2.GIT_APPLY_LOCATION_BOTH)
    assert not testrepo.applies(patch_diff, pygit2.GIT_APPLY_LOCATION_BOTH)
    assert not testrepo.applies(patch_diff, pygit2.GIT_APPLY_LOCATION_WORKDIR)
    assert not testrepo.applies(patch_diff, pygit2.GIT_APPLY_LOCATION_INDEX)

