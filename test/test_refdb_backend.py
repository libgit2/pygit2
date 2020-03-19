# Copyright 2010-2020 The pygit2 contributors
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

"""Tests for Refdb objects."""

import os
import unittest

from pygit2 import Refdb, RefdbBackend, RefdbFsBackend, Repository
from pygit2 import Reference

from . import utils

# Note: the refdb abstraction from libgit2 is meant to provide information
# which libgit2 transforms into something more useful, and in general YMMV by
# using the backend directly. So some of these tests are a bit vague or
# incomplete, to avoid hitting the semi-valid states that refdbs produce by
# design.
class ProxyRefdbBackend(RefdbBackend):
    def __init__(self, source):
        self.source = source

    def exists(self, ref):
        print(self, self.source, ref)
        return self.source.exists(ref)

    def lookup(self, ref):
        return self.source.lookup(ref)

    def write(self, ref, force, who, message, old, old_target):
        return self.source.write(ref, force, who, message, old, old_target)

    def rename(self, old_name, new_name, force, who, message):
        return self.source.rename(old_name, new_name, force, who, message)

    def delete(self, ref_name, old_id, old_target):
        return self.source.delete(ref_name, old_id, old_target)

    def compress(self):
        return self.source.compress()

    def has_log(self, ref_name):
        return self.source.has_log(ref_name)

    def ensure_log(self, ref_name):
        return self.source.ensure_log(ref_name)

    def __iter__(self):
        return iter(self.source)

class CustomRefdbBackendTest(utils.RepoTestCase):
    def setUp(self):
        super().setUp()
        self.backend = ProxyRefdbBackend(RefdbFsBackend(self.repo))

    def test_exists(self):
        assert not self.backend.exists('refs/heads/does-not-exist')
        assert self.backend.exists('refs/heads/master')

    def test_lookup(self):
        assert self.backend.lookup('refs/heads/does-not-exist') is None
        assert self.backend.lookup('refs/heads/master').name == 'refs/heads/master'

    def test_write(self):
        master = self.backend.lookup('refs/heads/master')
        commit = self.repo.get(master.target)
        ref = Reference("refs/heads/test-write", master.target, None)
        self.backend.write(ref, False, commit.author,
                "Create test-write", None, None)
        assert self.backend.lookup("refs/heads/test-write").target == master.target

    def test_rename(self):
        old_ref = self.backend.lookup('refs/heads/i18n')
        target = self.repo.get(old_ref.target)
        who = target.committer
        self.backend.rename('refs/heads/i18n', 'refs/heads/intl',
                False, target.committer, target.message)
        assert self.backend.lookup('refs/heads/intl').target == target.id

    def test_delete(self):
        old = self.backend.lookup('refs/heads/i18n')
        self.backend.delete('refs/heads/i18n', old.target, None)
        assert not self.backend.lookup('refs/heads/i18n')

    def test_compress(self):
        repo = self.repo
        packed_refs_file = os.path.join(self.repo_path, '.git', 'packed-refs')
        assert not os.path.exists(packed_refs_file)
        self.backend.compress()
        assert os.path.exists(packed_refs_file)

    def test_has_log(self):
        assert self.backend.has_log('refs/heads/master')
        assert not self.backend.has_log('refs/heads/does-not-exist')

    def test_ensure_log(self):
        assert not self.backend.has_log('refs/heads/new-log')
        self.backend.ensure_log('refs/heads/new-log')
        assert self.backend.has_log('refs/heads/new-log')
