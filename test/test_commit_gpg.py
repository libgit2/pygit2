# Copyright 2010-2022 The pygit2 contributors
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

from pygit2 import GIT_OBJ_COMMIT, Oid, Signature

content = """\
tree 4b825dc642cb6eb9a060e54bf8d69288fbee4904
parent 8496071c1b46c854b31185ea97743be6a8774479
author Ben Burkert <ben@benburkert.com> 1358451456 -0800
committer Ben Burkert <ben@benburkert.com> 1358451456 -0800

a simple commit which works\
"""

gpgsig = """\
-----BEGIN PGP SIGNATURE-----
Version: GnuPG v1.4.12 (Darwin)

iQIcBAABAgAGBQJQ+FMIAAoJEH+LfPdZDSs1e3EQAJMjhqjWF+WkGLHju7pTw2al
o6IoMAhv0Z/LHlWhzBd9e7JeCnanRt12bAU7yvYp9+Z+z+dbwqLwDoFp8LVuigl8
JGLcnwiUW3rSvhjdCp9irdb4+bhKUnKUzSdsR2CK4/hC0N2i/HOvMYX+BRsvqweq
AsAkA6dAWh+gAfedrBUkCTGhlNYoetjdakWqlGL1TiKAefEZrtA1TpPkGn92vbLq
SphFRUY9hVn1ZBWrT3hEpvAIcZag3rTOiRVT1X1flj8B2vGCEr3RrcwOIZikpdaW
who/X3xh/DGbI2RbuxmmJpxxP/8dsVchRJJzBwG+yhwU/iN3MlV2c5D69tls/Dok
6VbyU4lm/ae0y3yR83D9dUlkycOnmmlBAHKIZ9qUts9X7mWJf0+yy2QxJVpjaTGG
cmnQKKPeNIhGJk2ENnnnzjEve7L7YJQF6itbx5VCOcsGh3Ocb3YR7DMdWjt7f8pu
c6j+q1rP7EpE2afUN/geSlp5i3x8aXZPDj67jImbVCE/Q1X9voCtyzGJH7MXR0N9
ZpRF8yzveRfMH8bwAJjSOGAFF5XkcR/RNY95o+J+QcgBLdX48h+ZdNmUf6jqlu3J
7KmTXXQcOVpN6dD3CmRFsbjq+x6RHwa8u1iGn+oIkX908r97ckfB/kHKH7ZdXIJc
cpxtDQQMGYFpXK/71stq
=ozeK
-----END PGP SIGNATURE-----\
"""

gpgsig_content = """\
tree 4b825dc642cb6eb9a060e54bf8d69288fbee4904
parent 8496071c1b46c854b31185ea97743be6a8774479
author Ben Burkert <ben@benburkert.com> 1358451456 -0800
committer Ben Burkert <ben@benburkert.com> 1358451456 -0800
gpgsig -----BEGIN PGP SIGNATURE-----
 Version: GnuPG v1.4.12 (Darwin)
 
 iQIcBAABAgAGBQJQ+FMIAAoJEH+LfPdZDSs1e3EQAJMjhqjWF+WkGLHju7pTw2al
 o6IoMAhv0Z/LHlWhzBd9e7JeCnanRt12bAU7yvYp9+Z+z+dbwqLwDoFp8LVuigl8
 JGLcnwiUW3rSvhjdCp9irdb4+bhKUnKUzSdsR2CK4/hC0N2i/HOvMYX+BRsvqweq
 AsAkA6dAWh+gAfedrBUkCTGhlNYoetjdakWqlGL1TiKAefEZrtA1TpPkGn92vbLq
 SphFRUY9hVn1ZBWrT3hEpvAIcZag3rTOiRVT1X1flj8B2vGCEr3RrcwOIZikpdaW
 who/X3xh/DGbI2RbuxmmJpxxP/8dsVchRJJzBwG+yhwU/iN3MlV2c5D69tls/Dok
 6VbyU4lm/ae0y3yR83D9dUlkycOnmmlBAHKIZ9qUts9X7mWJf0+yy2QxJVpjaTGG
 cmnQKKPeNIhGJk2ENnnnzjEve7L7YJQF6itbx5VCOcsGh3Ocb3YR7DMdWjt7f8pu
 c6j+q1rP7EpE2afUN/geSlp5i3x8aXZPDj67jImbVCE/Q1X9voCtyzGJH7MXR0N9
 ZpRF8yzveRfMH8bwAJjSOGAFF5XkcR/RNY95o+J+QcgBLdX48h+ZdNmUf6jqlu3J
 7KmTXXQcOVpN6dD3CmRFsbjq+x6RHwa8u1iGn+oIkX908r97ckfB/kHKH7ZdXIJc
 cpxtDQQMGYFpXK/71stq
 =ozeK
 -----END PGP SIGNATURE-----

a simple commit which works\
"""
# NOTE: ^^^ mind the gap (space must exist after GnuPG header) ^^^
# XXX: seems macos wants the space while linux does not


def test_commit_signing(gpgsigned):
    repo = gpgsigned
    message = "a simple commit which works"
    author = Signature(
        name="Ben Burkert",
        email="ben@benburkert.com",
        time=1358451456,
        offset=-480,
    )
    committer = Signature(
        name="Ben Burkert",
        email="ben@benburkert.com",
        time=1358451456,
        offset=-480,
    )
    tree = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
    parents = ["8496071c1b46c854b31185ea97743be6a8774479"]

    # create commit string
    commit_string = repo.create_commit_string(
        author, committer, message, tree, parents
    )
    assert commit_string == content

    # create/retrieve signed commit
    oid = repo.create_commit_with_signature(content, gpgsig)
    commit = repo.get(oid)
    signature, payload = commit.gpg_signature

    # validate signed commit
    assert content == payload.decode("utf-8")
    assert gpgsig == signature.decode("utf-8")
    assert gpgsig_content == commit.read_raw().decode("utf-8")

    # perform sanity checks
    assert GIT_OBJ_COMMIT == commit.type
    assert "6569fdf71dbd99081891154641869c537784a3ba" == commit.hex
    assert commit.message_encoding is None
    assert message == commit.message
    assert 1358451456 == commit.commit_time
    assert committer == commit.committer
    assert author == commit.author
    assert tree == commit.tree.hex
    assert Oid(hex=tree) == commit.tree_id
    assert 1 == len(commit.parents)
    assert parents[0] == commit.parents[0].hex
    assert Oid(hex=parents[0]) == commit.parent_ids[0]


def test_get_gpg_signature_when_unsigned(gpgsigned):
    unhash = "5b5b025afb0b4c913b4c338a42934a3863bf3644"

    repo = gpgsigned
    commit = repo.get(unhash)
    signature, payload = commit.gpg_signature

    assert signature is None
    assert payload is None
