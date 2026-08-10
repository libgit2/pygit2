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

# Import from pygit2
from ._pygit2 import (
    AlreadyExistsError,
    AmbiguousError,
    AuthError,
    CertificateError,
    GitError,
    InvalidError,
    InvalidSpecError,
    NotFoundError,
)
from .ffi import C, ffi

__all__ = [
    'AlreadyExistsError',
    'AmbiguousError',
    'AuthError',
    'CertificateError',
    'GitError',
    'InvalidError',
    'InvalidSpecError',
    'NotFoundError',
    'Passthrough',
]

# Docstrings for C-defined exception classes
GitError.__doc__ = 'Generic libgit2 error.'
AlreadyExistsError.__doc__ = 'Object already exists.'
InvalidSpecError.__doc__ = 'Invalid name/ref spec.'
NotFoundError.__doc__ = 'Requested object could not be found.'
AmbiguousError.__doc__ = 'More than one object matches.'
AuthError.__doc__ = 'Authentication error.'
CertificateError.__doc__ = 'Server certificate is invalid.'
InvalidError.__doc__ = 'Invalid operation or input.'


def check_error(err: int, io: bool = False) -> None:
    if err >= 0:
        return

    # These are special error codes, they should never reach here
    test = err != C.GIT_EUSER and err != C.GIT_PASSTHROUGH
    assert test, f'Unexpected error code {err}'

    # Error message
    giterr = C.git_error_last()
    if giterr != ffi.NULL:
        message = ffi.string(giterr.message).decode('utf8', errors='surrogateescape')
    else:
        message = f'err {err} (no message provided)'

    # Translate to Python errors
    if err == C.GIT_EEXISTS:
        raise AlreadyExistsError(message)

    if err == C.GIT_EINVALIDSPEC:
        raise InvalidSpecError(message)

    if err == C.GIT_EINVALID:
        raise InvalidError(message)

    if err == C.GIT_EAMBIGUOUS:
        raise AmbiguousError(message)

    if err == C.GIT_EBUFS:
        raise ValueError(message)

    if err == C.GIT_EAUTH:
        raise AuthError(message)

    if err == C.GIT_ECERTIFICATE:
        raise CertificateError(message)

    if err == C.GIT_ENOTFOUND:
        if io:
            raise IOError(message)

        raise NotFoundError(message)

    if err == C.GIT_ITEROVER:
        raise StopIteration()

    # Generic Git error
    raise GitError(message)


# Indicate that we want libgit2 to pretend a function was not set
class Passthrough(Exception):
    def __init__(self) -> None:
        super().__init__('The function asked for pass-through')
