# -*- coding: UTF-8 -*-
#
# Copyright 2010-2015 The pygit2 contributors
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

"""Tests for credentials"""


import unittest
import pygit2
from pygit2 import GIT_CREDTYPE_USERPASS_PLAINTEXT
from pygit2 import UserPass, Keypair, KeypairFromAgent
from pygit2 import UserPass, Keypair
from . import utils

REMOTE_NAME = 'origin'
REMOTE_URL = 'git://github.com/libgit2/pygit2.git'
REMOTE_FETCHSPEC_SRC = 'refs/heads/*'
REMOTE_FETCHSPEC_DST = 'refs/remotes/origin/*'
REMOTE_REPO_OBJECTS = 30
REMOTE_REPO_BYTES = 2758

ORIGIN_REFSPEC = '+refs/heads/*:refs/remotes/origin/*'

class CredentialCreateTest(utils.NoRepoTestCase):
    def test_userpass(self):
        username = "git"
        password = "sekkrit"

        cred = UserPass(username, password)
        self.assertEqual((username, password), cred.credential_tuple)

    def test_ssh_key(self):
        username = "git"
        pubkey = "id_rsa.pub"
        privkey = "id_rsa"
        passphrase = "bad wolf"

        cred = Keypair(username, pubkey, privkey, passphrase)
        self.assertEqual((username, pubkey, privkey, passphrase), cred.credential_tuple)

    def test_ssh_agent(self):
        username = "git"
 
        cred = KeypairFromAgent(username)
        self.assertEqual((username, None, None, None), cred.credential_tuple)


class CredentialCallback(utils.RepoTestCase):
    def test_callback(self):
        class MyCallbacks(pygit2.RemoteCallbacks):
            @staticmethod
            def credentials(url, username, allowed):
                self.assertTrue(allowed & GIT_CREDTYPE_USERPASS_PLAINTEXT)
                raise Exception("I don't know the password")

        url = "https://github.com/github/github"
        remote = self.repo.create_remote("github", url)

        self.assertRaises(Exception, lambda: remote.fetch(callbacks=MyCallbacks()))

    def test_bad_cred_type(self):
        class MyCallbacks(pygit2.RemoteCallbacks):
            @staticmethod
            def credentials(url, username, allowed):
                self.assertTrue(allowed & GIT_CREDTYPE_USERPASS_PLAINTEXT)
                return Keypair("git", "foo.pub", "foo", "sekkrit")

        url = "https://github.com/github/github"
        remote = self.repo.create_remote("github", url)
        self.assertRaises(TypeError, lambda: remote.fetch(callbacks=MyCallbacks()))

class CallableCredentialTest(utils.RepoTestCase):

    def test_user_pass(self):
        credentials = UserPass("libgit2", "libgit2")
        callbacks = pygit2.RemoteCallbacks(credentials=credentials)

        url = "https://bitbucket.org/libgit2/testgitrepository.git"
        remote = self.repo.create_remote("bb", url)
        remote.fetch(callbacks=callbacks)

if __name__ == '__main__':
    unittest.main()
