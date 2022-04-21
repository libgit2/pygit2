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

from . import utils


@pytest.fixture
def repo(tmp_path):
    with utils.TemporaryRepository('gpgsigned.zip', tmp_path) as path:
        yield pygit2.Repository(path)


def test_get_gpg_signature_when_signed(repo):
    signed_hash = 'a00b212d5455ad8c4c1779f778c7d2a81bb5da23'
    expected_signature = (
        '-----BEGIN PGP SIGNATURE-----\n\n'
        'iQFGBAABCgAwFiEEQZu9JtePgJbDk7VC0+mlK74z13oFAlpzXykSHG1hcmtAbWFy\n'
        'a2FkYW1zLm1lAAoJENPppSu+M9d6FRoIAJXeQRRT1V47nnHITiel6426loYkeij7\n'
        '66doGNIyll95H92SwH4LAjPyEEByIG1VsA6NztzUoNgnEvAXI0iAz3LyI7N16M4b\n'
        'dPDkC72pp8tu280H5Qt5b2V5hmlKKSgtOS5iNhdU/FbWVS8MlHsqzQTZfoTdi6ch\n'
        'KWUsjzudVd3F/H/AU+1Jsxt8Iz/oK4T/puUQLnJZKjKlljGP994FA3JIpnZpZmbG\n'
        'FybYJEDXnng7uhx3Fz/Mo3KBJoQfAExTtaToY0n0hSjOe6GN9rEsRSMK3mWdysf2\n'
        'wOdtYMMcT16hG5tAwnD/myZ4rIIpyZJ/9mjymdUsj6UKf7D+vJuqfsI=\n=IyYy\n'
        '-----END PGP SIGNATURE-----'
    ).encode('ascii')

    expected_payload = (
        'tree c36c20831e43e5984c672a714661870b67ab1d95\nauthor Mark Adams '
        '<madams@atlassian.com> 1517510299 -0600\ncommitter Mark Adams <ma'
        'dams@atlassian.com> 1517510441 -0600\n\nMaking a GPG signed commi'
        't\n'
    ).encode('ascii')

    commit = repo.get(signed_hash)
    signature, payload = commit.gpg_signature

    assert signature == expected_signature
    assert payload == expected_payload


def test_get_gpg_signature_when_unsigned(repo):
    unsigned_hash = 'a84938d1d885e80dae24b86b06621cec47ff6edd'
    commit = repo.get(unsigned_hash)
    signature, payload = commit.gpg_signature

    assert signature is None
    assert payload is None
