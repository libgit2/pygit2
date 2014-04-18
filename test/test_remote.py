# -*- coding: UTF-8 -*-
#
# Copyright 2010-2014 The pygit2 contributors
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

"""Tests for Remote objects."""


import unittest
import pygit2
from pygit2 import Oid
from . import utils

REMOTE_NAME = 'origin'
REMOTE_URL = 'git://github.com/libgit2/pygit2.git'
REMOTE_FETCHSPEC_SRC = 'refs/heads/*'
REMOTE_FETCHSPEC_DST = 'refs/remotes/origin/*'
REMOTE_REPO_OBJECTS = 30
REMOTE_REPO_BYTES = 2758

ORIGIN_REFSPEC = '+refs/heads/*:refs/remotes/origin/*'

class RepositoryTest(utils.RepoTestCase):
    def test_remote_create(self):
        name = 'upstream'
        url = 'git://github.com/libgit2/pygit2.git'

        remote = self.repo.create_remote(name, url)

        self.assertEqual(type(remote), pygit2.Remote)
        self.assertEqual(name, remote.name)
        self.assertEqual(url, remote.url)
        self.assertEqual(None, remote.push_url)

        self.assertRaises(ValueError, self.repo.create_remote, *(name, url))


    def test_remote_rename(self):
        remote = self.repo.remotes[0]

        self.assertEqual(REMOTE_NAME, remote.name)
        remote.name = 'new'
        self.assertEqual('new', remote.name)

        self.assertRaisesAssign(ValueError, remote, 'name', '')
        self.assertRaisesAssign(ValueError, remote, 'name', None)


    def test_remote_set_url(self):
        remote = self.repo.remotes[0]

        self.assertEqual(REMOTE_URL, remote.url)
        new_url = 'git://github.com/cholin/pygit2.git'
        remote.url = new_url
        self.assertEqual(new_url, remote.url)

        self.assertRaisesAssign(ValueError, remote, 'url', '')

        remote.push_url = new_url
        self.assertEqual(new_url, remote.push_url)
        self.assertRaisesAssign(ValueError, remote, 'push_url', '')


    def test_refspec(self):
        remote = self.repo.remotes[0]

        self.assertEqual(remote.refspec_count, 1)
        refspec = remote.get_refspec(0)
        self.assertEqual(refspec.src, REMOTE_FETCHSPEC_SRC)
        self.assertEqual(refspec.dst, REMOTE_FETCHSPEC_DST)
        self.assertEqual(True, refspec.force)
        self.assertEqual(ORIGIN_REFSPEC, refspec.string)

        self.assertEqual(list, type(remote.fetch_refspecs))
        self.assertEqual(1, len(remote.fetch_refspecs))
        self.assertEqual(ORIGIN_REFSPEC, remote.fetch_refspecs[0])

        self.assertTrue(refspec.src_matches('refs/heads/master'))
        self.assertTrue(refspec.dst_matches('refs/remotes/origin/master'))
        self.assertEqual('refs/remotes/origin/master', refspec.transform('refs/heads/master'))
        self.assertEqual('refs/heads/master', refspec.rtransform('refs/remotes/origin/master'))

        self.assertEqual(list, type(remote.push_refspecs))
        self.assertEqual(0, len(remote.push_refspecs))

        push_specs = remote.push_refspecs
        self.assertEqual(list, type(push_specs))
        self.assertEqual(0, len(push_specs))

        remote.fetch_refspecs = ['+refs/*:refs/remotes/*']
        self.assertEqual('+refs/*:refs/remotes/*', remote.fetch_refspecs[0])

        fetch_specs = remote.fetch_refspecs
        self.assertEqual(list, type(fetch_specs))
        self.assertEqual(1, len(fetch_specs))
        self.assertEqual('+refs/*:refs/remotes/*', fetch_specs[0])

        remote.fetch_refspecs = ['+refs/*:refs/remotes/*',
                                 '+refs/test/*:refs/test/remotes/*']
        self.assertEqual('+refs/*:refs/remotes/*', remote.fetch_refspecs[0])
        self.assertEqual('+refs/test/*:refs/test/remotes/*',
                         remote.fetch_refspecs[1])

        remote.push_refspecs = ['+refs/*:refs/remotes/*',
                                '+refs/test/*:refs/test/remotes/*']

        self.assertRaises(TypeError, setattr, remote, 'push_refspecs',
                          '+refs/*:refs/*')
        self.assertRaises(TypeError, setattr, remote, 'fetch_refspecs',
                          '+refs/*:refs/*')
        self.assertRaises(TypeError, setattr, remote, 'fetch_refspecs',
                          ['+refs/*:refs/*', 5])

        self.assertEqual('+refs/*:refs/remotes/*', remote.push_refspecs[0])
        self.assertEqual('+refs/test/*:refs/test/remotes/*',
                         remote.push_refspecs[1])


    def test_remote_list(self):
        self.assertEqual(1, len(self.repo.remotes))
        remote = self.repo.remotes[0]
        self.assertEqual(REMOTE_NAME, remote.name)
        self.assertEqual(REMOTE_URL, remote.url)

        name = 'upstream'
        url = 'git://github.com/libgit2/pygit2.git'
        remote = self.repo.create_remote(name, url)
        self.assertTrue(remote.name in [x.name for x in self.repo.remotes])


    def test_remote_save(self):
        remote = self.repo.remotes[0]

        remote.name = 'new-name'
        remote.url = 'http://example.com/test.git'

        remote.save()

        self.assertEqual('new-name', self.repo.remotes[0].name)
        self.assertEqual('http://example.com/test.git',
                         self.repo.remotes[0].url)

    def test_add_refspec(self):
        remote = self.repo.create_remote('test_add_refspec', REMOTE_URL)
        remote.add_push('refs/heads/*:refs/heads/test_refspec/*')
        self.assertEqual('refs/heads/*:refs/heads/test_refspec/*',
                         remote.push_refspecs[0])
        remote.add_fetch('+refs/heads/*:refs/remotes/test_refspec/*')
        self.assertEqual('+refs/heads/*:refs/remotes/test_refspec/*',
                         remote.fetch_refspecs[1])

    def test_remote_callback_typecheck(self):
        remote = self.repo.remotes[0]
        remote.progress = 5
        self.assertRaises(TypeError, remote, 'fetch')

        remote = self.repo.remotes[0]
        remote.transfer_progress = 5
        self.assertRaises(TypeError, remote, 'fetch')

        remote = self.repo.remotes[0]
        remote.update_tips = 5
        self.assertRaises(TypeError, remote, 'fetch')



class EmptyRepositoryTest(utils.EmptyRepoTestCase):
    def test_fetch(self):
        remote = self.repo.remotes[0]
        stats = remote.fetch()
        self.assertEqual(stats.received_bytes, REMOTE_REPO_BYTES)
        self.assertEqual(stats.indexed_objects, REMOTE_REPO_OBJECTS)
        self.assertEqual(stats.received_objects, REMOTE_REPO_OBJECTS)

    def test_transfer_progress(self):
        self.tp = None
        def tp_cb(stats):
            self.tp = stats

        remote = self.repo.remotes[0]
        remote.transfer_progress = tp_cb
        stats = remote.fetch()
        self.assertEqual(stats.received_bytes, self.tp.received_bytes)
        self.assertEqual(stats.indexed_objects, self.tp.indexed_objects)
        self.assertEqual(stats.received_objects, self.tp.received_objects)

    def test_update_tips(self):
        remote = self.repo.remotes[0]
        self.i = 0
        self.tips = [('refs/remotes/origin/master', Oid(hex='0'*40),
                      Oid(hex='784855caf26449a1914d2cf62d12b9374d76ae78')),
                     ('refs/tags/root', Oid(hex='0'*40),
                      Oid(hex='3d2962987c695a29f1f80b6c3aa4ec046ef44369'))]

        def ut_cb(name, old, new):
            self.assertEqual(self.tips[self.i], (name, old, new))
            self.i += 1

        remote.update_tips = ut_cb
        remote.fetch()

class PushTestCase(unittest.TestCase):
    def setUp(self):
        self.origin_ctxtmgr = utils.TemporaryRepository(('git', 'testrepo.git'))
        self.clone_ctxtmgr = utils.TemporaryRepository(('git', 'testrepo.git'))
        self.origin = pygit2.Repository(self.origin_ctxtmgr.__enter__())
        self.clone = pygit2.Repository(self.clone_ctxtmgr.__enter__())
        self.remote = self.clone.create_remote('origin', self.origin.path)

    def tearDown(self):
        self.origin_ctxtmgr.__exit__(None, None, None)
        self.clone_ctxtmgr.__exit__(None, None, None)

    def test_push_fast_forward_commits_to_remote_succeeds(self):
        tip = self.clone[self.clone.head.target]
        oid = self.clone.create_commit(
            'refs/heads/master', tip.author, tip.author, 'empty commit',
            tip.tree.id, [tip.id]
        )
        self.remote.push('refs/heads/master')
        self.assertEqual(self.origin[self.origin.head.target].id, oid)

    def test_push_when_up_to_date_succeeds(self):
        self.remote.push('refs/heads/master')
        origin_tip = self.origin[self.origin.head.target].id
        clone_tip = self.clone[self.clone.head.target].id
        self.assertEqual(origin_tip, clone_tip)

    def test_push_non_fast_forward_commits_to_remote_fails(self):
        tip = self.origin[self.origin.head.target]
        oid = self.origin.create_commit(
            'refs/heads/master', tip.author, tip.author, 'some commit',
            tip.tree.id, [tip.id]
        )
        tip = self.clone[self.clone.head.target]
        oid = self.clone.create_commit(
            'refs/heads/master', tip.author, tip.author, 'other commit',
            tip.tree.id, [tip.id]
        )
        self.assertRaises(pygit2.GitError, self.remote.push, 'refs/heads/master')

if __name__ == '__main__':
    unittest.main()
