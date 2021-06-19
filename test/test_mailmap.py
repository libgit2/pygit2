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

"""Tests for Mailmap."""

from pygit2 import Mailmap


TEST_MAILMAP = """\
# Simple Comment line
<cto@company.xx>                       <cto@coompany.xx>
Some Dude <some@dude.xx>         nick1 <bugs@company.xx>
Other Author <other@author.xx>   nick2 <bugs@company.xx>
Other Author <other@author.xx>         <nick2@company.xx>
Phil Hill <phil@company.xx>  # Comment at end of line
<joseph@company.xx>             Joseph <bugs@company.xx>
Santa Claus <santa.claus@northpole.xx> <me@company.xx>
"""

TEST_ENTRIES = [
    (None, "cto@company.xx", None, "cto@coompany.xx"),
    ("Some Dude", "some@dude.xx", "nick1", "bugs@company.xx"),
    ("Other Author", "other@author.xx", "nick2", "bugs@company.xx"),
    ("Other Author", "other@author.xx", None, "nick2@company.xx"),
    ("Phil Hill", None, None, "phil@company.xx"),
    (None, "joseph@company.xx", "Joseph", "bugs@company.xx"),
    ("Santa Claus", "santa.claus@northpole.xx", None, "me@company.xx")
]

TEST_RESOLVE = [
    ("Brad", "cto@company.xx", "Brad", "cto@coompany.xx"),
    ("Brad L", "cto@company.xx", "Brad L", "cto@coompany.xx"),
    ("Some Dude", "some@dude.xx", "nick1", "bugs@company.xx"),
    ("Other Author", "other@author.xx", "nick2", "bugs@company.xx"),
    ("nick3", "bugs@company.xx", "nick3", "bugs@company.xx"),
    ("Other Author", "other@author.xx", "Some Garbage", "nick2@company.xx"),
    ("Phil Hill", "phil@company.xx", "unknown", "phil@company.xx"),
    ("Joseph", "joseph@company.xx", "Joseph", "bugs@company.xx"),
    ("Santa Claus", "santa.claus@northpole.xx", "Clause", "me@company.xx"),
    ("Charles", "charles@charles.xx", "Charles", "charles@charles.xx")
]


def test_empty():
    mailmap = Mailmap()

    for (_, _, name, email) in TEST_RESOLVE:
        assert mailmap.resolve(name, email) == (name, email)


def test_new():
    mailmap = Mailmap()

    # Add entries to the mailmap
    for entry in TEST_ENTRIES:
        mailmap.add_entry(*entry)

    for (real_name, real_email, name, email) in TEST_RESOLVE:
        assert mailmap.resolve(name, email) == (real_name, real_email)


def test_parsed():
    mailmap = Mailmap.from_buffer(TEST_MAILMAP)

    for (real_name, real_email, name, email) in TEST_RESOLVE:
        assert mailmap.resolve(name, email) == (real_name, real_email)


# TODO: Add a testcase which uses .mailmap in a repo
