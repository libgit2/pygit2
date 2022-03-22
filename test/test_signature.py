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

import time

import pytest

from pygit2 import Signature


def test_default():
    signature = Signature(
        'Foo Ibáñez', 'foo@example.com', 1322174594, 60)
    encoding = signature._encoding
    assert encoding == 'utf-8'
    assert signature.name == signature.raw_name.decode(encoding)
    assert signature.name.encode(encoding) == signature.raw_name
    assert signature.email == signature.raw_email.decode(encoding)
    assert signature.email.encode(encoding) == signature.raw_email

def test_ascii():
    with pytest.raises(UnicodeEncodeError):
        Signature('Foo Ibáñez', 'foo@example.com', encoding='ascii')

def test_latin1():
    encoding = 'iso-8859-1'
    signature = Signature(
        'Foo Ibáñez', 'foo@example.com', encoding=encoding)
    assert encoding == signature._encoding
    assert signature.name == signature.raw_name.decode(encoding)
    assert signature.name.encode(encoding) == signature.raw_name
    assert signature.email == signature.raw_email.decode(encoding)
    assert signature.email.encode(encoding) == signature.raw_email

def test_now():
    encoding = 'utf-8'
    signature = Signature(
        'Foo Ibáñez', 'foo@example.com', encoding=encoding)
    assert encoding == signature._encoding
    assert signature.name == signature.raw_name.decode(encoding)
    assert signature.name.encode(encoding) == signature.raw_name
    assert signature.email == signature.raw_email.decode(encoding)
    assert signature.email.encode(encoding) == signature.raw_email
    assert abs(signature.time - time.time()) < 5

def test_str():
    signature = Signature('Foo Ibáñez', 'foo@example.com', encoding='utf-8')
    assert str(signature) == 'Foo Ibáñez <foo@example.com>'

def test_repr():
    signature = Signature(
        'Foo Ibáñez', 'foo@bar.com', 1322174594, 60, encoding='utf-8')
    expected_signature = \
        "pygit2.Signature('Foo Ibáñez', 'foo@bar.com', 1322174594, 60, 'utf-8')"
    assert repr(signature) == expected_signature
