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

"""Tests for credentials"""

from pathlib import Path

import pytest

import pygit2
from pygit2 import Username, UserPass, Keypair, KeypairFromAgent, KeypairFromMemory
from . import utils


REMOTE_NAME = 'origin'
REMOTE_URL = 'git://github.com/libgit2/pygit2.git'
REMOTE_FETCHSPEC_SRC = 'refs/heads/*'
REMOTE_FETCHSPEC_DST = 'refs/remotes/origin/*'
REMOTE_REPO_OBJECTS = 30
REMOTE_REPO_BYTES = 2758

ORIGIN_REFSPEC = '+refs/heads/*:refs/remotes/origin/*'


def test_username():
    username = "git"
    cred = Username(username)
    assert (username,) == cred.credential_tuple


def test_userpass():
    username = "git"
    password = "sekkrit"

    cred = UserPass(username, password)
    assert (username, password) == cred.credential_tuple

def test_ssh_key():
    username = "git"
    pubkey = "id_rsa.pub"
    privkey = "id_rsa"
    passphrase = "bad wolf"

    cred = Keypair(username, pubkey, privkey, passphrase)
    assert (username, pubkey, privkey, passphrase) == cred.credential_tuple

def test_ssh_key_aspath():
    username = "git"
    pubkey = Path("id_rsa.pub")
    privkey = Path("id_rsa")
    passphrase = "bad wolf"

    cred = Keypair(username, pubkey, privkey, passphrase)
    assert (username, pubkey, privkey, passphrase) == cred.credential_tuple

def test_ssh_agent():
    username = "git"

    cred = KeypairFromAgent(username)
    assert (username, None, None, None) == cred.credential_tuple

def test_ssh_from_memory():
    username = "git"
    pubkey = "public key data"
    privkey = "private key data"
    passphrase = "secret passphrase"

    cred = KeypairFromMemory(username, pubkey, privkey, passphrase)
    assert (username, pubkey, privkey, passphrase) == cred.credential_tuple


@utils.requires_network
@utils.requires_ssh
def test_keypair(tmp_path, pygit2_empty_key):
    url = 'ssh://git@github.com/pygit2/empty'
    with pytest.raises(pygit2.GitError):
        pygit2.clone_repository(url, tmp_path)

    prv, pub, secret = pygit2_empty_key

    keypair = pygit2.Keypair("git", pub, prv, secret)
    callbacks = pygit2.RemoteCallbacks(credentials=keypair)
    pygit2.clone_repository(url, tmp_path, callbacks=callbacks)


@utils.requires_network
@utils.requires_ssh
def test_keypair_from_memory(tmp_path, pygit2_empty_key):
    url = 'ssh://git@github.com/pygit2/empty'
    with pytest.raises(pygit2.GitError):
        pygit2.clone_repository(url, tmp_path)

    prv, pub, secret = pygit2_empty_key
    with open(prv) as f:
        prv_mem = f.read()

    with open(pub) as f:
        pub_mem = f.read()

    keypair = pygit2.KeypairFromMemory("git", pub_mem, prv_mem, secret)
    callbacks = pygit2.RemoteCallbacks(credentials=keypair)
    pygit2.clone_repository(url, tmp_path, callbacks=callbacks)


def test_callback(testrepo):
    class MyCallbacks(pygit2.RemoteCallbacks):
        def credentials(testrepo, url, username, allowed):
            assert allowed & pygit2.GIT_CREDENTIAL_USERPASS_PLAINTEXT
            raise Exception("I don't know the password")

    url = "https://github.com/github/github"
    remote = testrepo.remotes.create("github", url)
    with pytest.raises(Exception): remote.fetch(callbacks=MyCallbacks())

@utils.requires_network
def test_bad_cred_type(testrepo):
    class MyCallbacks(pygit2.RemoteCallbacks):
        def credentials(testrepo, url, username, allowed):
            assert allowed & pygit2.GIT_CREDENTIAL_USERPASS_PLAINTEXT
            return Keypair("git", "foo.pub", "foo", "sekkrit")

    url = "https://github.com/github/github"
    remote = testrepo.remotes.create("github", url)
    with pytest.raises(TypeError): remote.fetch(callbacks=MyCallbacks())

@utils.requires_network
def test_fetch_certificate_check(testrepo):
    class MyCallbacks(pygit2.RemoteCallbacks):
        def certificate_check(testrepo, certificate, valid, host):
            assert certificate is None
            assert valid is True
            assert host == b'github.com'
            return False

    url = 'https://github.com/libgit2/pygit2.git'
    remote = testrepo.remotes.create('https', url)
    with pytest.raises(pygit2.GitError) as exc:
        remote.fetch(callbacks=MyCallbacks())

    # libgit2 uses different error message for Linux and Windows
    # TODO test one or the other depending on the platform
    assert str(exc.value) in (
        'user rejected certificate for github.com', # httpclient
        'user cancelled certificate check') # winhttp

    # TODO Add GitError.error_code
    #assert exc.value.error_code == pygit2.GIT_ERROR_HTTP


@utils.requires_network
def test_user_pass(testrepo):
    credentials = UserPass("libgit2", "libgit2")
    callbacks = pygit2.RemoteCallbacks(credentials=credentials)

    url = 'https://github.com/libgit2/TestGitRepository'
    remote = testrepo.remotes.create("bb", url)
    remote.fetch(callbacks=callbacks)


@utils.requires_proxy
@utils.requires_network
@utils.requires_future_libgit2
def test_proxy(testrepo):
    credentials = UserPass("libgit2", "libgit2")
    callbacks = pygit2.RemoteCallbacks(credentials=credentials)

    url = 'https://github.com/libgit2/TestGitRepository'
    remote = testrepo.remotes.create("bb", url)
    remote.fetch(callbacks=callbacks, proxy='http://localhost:8888')
