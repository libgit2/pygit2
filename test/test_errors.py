# Copyright 2010-2026 The pygit2 contributors
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

"""Tests for the exception hierarchy."""

import pytest

from pygit2 import (
    AlreadyExistsError,
    AmbiguousError,
    AuthError,
    CertificateError,
    GitError,
    InvalidError,
    InvalidSpecError,
    NotFoundError,
    Repository,
)


def test_already_exists_error_inheritance() -> None:
    assert issubclass(AlreadyExistsError, GitError)
    assert issubclass(AlreadyExistsError, ValueError)


def test_invalid_spec_error_inheritance() -> None:
    assert issubclass(InvalidSpecError, GitError)
    assert issubclass(InvalidSpecError, ValueError)


def test_invalid_error_inheritance() -> None:
    assert issubclass(InvalidError, GitError)
    assert issubclass(InvalidError, ValueError)


def test_not_found_error_inheritance() -> None:
    assert issubclass(NotFoundError, GitError)
    assert issubclass(NotFoundError, KeyError)


def test_ambiguous_error_inheritance() -> None:
    assert issubclass(AmbiguousError, GitError)
    assert issubclass(AmbiguousError, ValueError)


def test_auth_error_inheritance() -> None:
    assert issubclass(AuthError, GitError)


def test_certificate_error_inheritance() -> None:
    assert issubclass(CertificateError, GitError)


def test_create_reference_already_exists(testrepo: Repository) -> None:
    target = testrepo.head.target
    testrepo.create_reference_direct('refs/heads/foo', target, False)

    with pytest.raises(AlreadyExistsError) as excinfo:
        testrepo.create_reference_direct('refs/heads/foo', target, False)

    assert isinstance(excinfo.value, GitError)
    assert isinstance(excinfo.value, ValueError)


def test_create_reference_invalid_spec(testrepo: Repository) -> None:
    target = testrepo.head.target

    with pytest.raises(InvalidSpecError) as excinfo:
        testrepo.create_reference_direct('invalid ref name', target, False)

    assert isinstance(excinfo.value, GitError)
    assert isinstance(excinfo.value, ValueError)


def test_remote_lookup_not_found(emptyrepo: Repository) -> None:
    with pytest.raises(NotFoundError) as excinfo:
        emptyrepo.remotes['nonexistent']

    assert isinstance(excinfo.value, GitError)
    assert isinstance(excinfo.value, KeyError)


def test_revparse_single_not_found(testrepo: Repository) -> None:
    with pytest.raises(NotFoundError) as excinfo:
        testrepo.revparse_single('nonexistent-ref-12345')

    assert isinstance(excinfo.value, GitError)
    assert isinstance(excinfo.value, KeyError)


def test_oid_parse_invalid_error(testrepo: Repository) -> None:
    with pytest.raises(InvalidError) as excinfo:
        testrepo['notahexoid']

    assert isinstance(excinfo.value, GitError)
    assert isinstance(excinfo.value, ValueError)


def test_lookup_short_oid_ambiguous(testrepo: Repository) -> None:
    with pytest.raises(AmbiguousError) as excinfo:
        testrepo['5fe']

    assert isinstance(excinfo.value, GitError)
    assert isinstance(excinfo.value, ValueError)
