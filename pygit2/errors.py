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

# Import from pygit2
from .ffi import ffi, C
from ._pygit2 import GitError
from typing import Callable, Type, Any


class Passthrough(Exception):
    """
    Indicate that we want libgit2 to pretend a function was not set.

    This class is here for backward compatibility.
    For new code, GitPassthroughError should be used.
    """
    # TODO drop legacy support
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        super().__init__("The function asked for pass-through.")


class BaseGitException(GitError):
    """
    The base exception class of PyGit2. Inherits from the pygit.c GitError exception for backward compatibility.
    Do not directly inherit from this class but rather use the GitException subclass for custom exceptions.
    """

    def __new__(cls, exc: Type["BaseGitException"] = None, *args, **kwargs):
        if BaseGitException._is_subclass(cl=exc):
            # If a more explicit subclass of BaseGitException was provided, use that.
            return exc(exc=None, *args, **kwargs)

        try:
            # Any subclasses that inherit from BaseGitException are fine with this
            return super().__new__(cls, exc=None, *args, **kwargs)
        except TypeError:
            # Some of the exception classes one might inherit from do only
            # accept *args. This could be explicitly handled but would require
            # any class that inherits from BaseGitException to define __new__ and
            # probably handle such cases there. To be more pythonic let's just
            # try and except it here.
            return super().__new__(cls, *args)

    def __init__(self, message: str = None, exitcode: int = None, *args, **kwargs):
        """
        Provides the most explicit exception based on it's input.

        If a message was provided, it will be used as exception message.
        Else the message will be generated from the libgit2 error stack, if any.
        If no proper error is found in the Git error stack, a generic message using the provided exitcode
        as hint will be used. If no exitcode was provided a generic message without an exitcode is raised.

        If a BaseGitException subclass was provided, will raise that more explicit class. See __new__() for details.

        Args:
            message:    the message to use for the generated exception
            exitcode:   the exit code to use when constructing a generic message
        """
        if not message:
            # If no message was provided, generate one on best effort
            message = BaseGitException._git_error_last(exitcode=exitcode)

        super().__init__(message)

    @staticmethod
    def _is_subclass(cl: Type[Any]):
        try:
            return issubclass(cl, BaseGitException)
        except TypeError:
            return False

    @staticmethod
    def _translate(exitcode: int, *args, **kwargs) -> "BaseGitException":
        """
        Translates C based libgit2 exceptions into Python exceptions, if possible.
        If no matching Python exception is found a generic BaseGitException will be returned.

        Args:
            exitcode: the exit code that's known to be an error as returned from libgit2

        Returns:
            a matching Python exception that inherits from BaseGitException
        """
        """
        TODO implement not yet explicitly implemented libgit2 error codes as exceptions and handle them here
        GIT_ERROR      		= -1
        GIT_EBUFS      		= -6
        GIT_EBAREREPO       = -8
        GIT_EUNBORNBRANCH   = -9
        GIT_EUNMERGED       = -10
        GIT_ENONFASTFORWARD = -11
        GIT_ECONFLICT       = -13
        GIT_ELOCKED         = -14
        GIT_EMODIFIED       = -15
        GIT_EAUTH           = -16
        GIT_ECERTIFICATE    = -17
        GIT_EAPPLIED        = -18
        GIT_EPEEL           = -19
        GIT_EEOF            = -20
        GIT_EINVALID        = -21
        GIT_EUNCOMMITTED    = -22
        GIT_EDIRECTORY      = -23
        GIT_EMERGECONFLICT  = -24
        GIT_PASSTHROUGH     = -30
        GIT_RETRY           = -32
        GIT_EMISMATCH       = -33
        GIT_EINDEXDIRTY     = -34
        GIT_EAPPLYFAIL      = -35
        """
        if exitcode == C.GIT_EEXISTS:
            return GitExistsError(exitcode=exitcode, *args, **kwargs)
        elif exitcode == C.GIT_EINVALIDSPEC:
            return GitInvalidSpecError(exitcode=exitcode, *args, **kwargs)
        elif exitcode == C.GIT_EAMBIGUOUS:
            return GitAmbiguousError(exitcode=exitcode, *args, **kwargs)
        elif exitcode == C.GIT_ENOTFOUND:
            return GitNotFoundError(exitcode=exitcode, *args, **kwargs)
        elif exitcode == C.GIT_ITEROVER:
            return GitIterOverError(exitcode=exitcode, *args, **kwargs)
        elif exitcode == C.GIT_EUSER:
            return GitUserError(exitcode=exitcode, *args, **kwargs)
        else:
            return GitException(exitcode=exitcode, *args, **kwargs)

    @staticmethod
    def _git_error_last(exitcode:int = None) -> str:
        """
        Get the error message of the last known error from Git.
        If no last known error exists, a generic message including the provided exitcode will be returned.
        If no exitcode was provided, a generic error message will be returned.

        Returns:
            the most explicit error message.
        """
        git_error = C.git_error_last()
        if git_error != ffi.NULL:
            return ffi.string(git_error.message).decode("utf8")
        if isinstance(exitcode, int):
            return f"Git exited with exit code '{exitcode}'. No message was provided."
        return "A unknown Git error occurred."

    @staticmethod
    def check_result(fn: Callable, message: str = None, exc: Type["BaseGitException"] = None, *oargs, **okwargs):
        """
        Wraps any libgit2 call that returns a exit code. Returns the result on success (exit code >= 0).
        If an error occures (exit code < 0), a best-matching Python exception will be raised.
        If a specific message or exception should be raised in case of error they can be provided.

        Args:
            fn:         the callable to wrap.
            message:    the message to use in the exception in case of error.
            exception:  the exception to use in case of error.

        Returns:
            The result of the function call.

        Raises:
            BaseGitException or a subclass of it.
        """
        def wrapped(*iargs, **ikwargs):
            # If exceptions occure while calling fn, they'll raise natively
            result = fn(*iargs, **ikwargs)
            try:
                if result and result < C.GIT_OK:
                    # Translate the exit code returned from Libgit2 to a BaseGitException
                    # If a more specific BaseGitException subclass and/or a more specific
                    # message was provided, use it.
                    raise BaseGitException._translate(exitcode=result, message=message, exc=exc, *oargs, **okwargs)
                return result
            except Exception as ex:
                # Raise all exceptions
                raise ex
        return wrapped

class GitException(BaseGitException):
    """
    Subclass of BaseGitException that should be used to inherit from when implementing new exception subclasses in PyGit2.
    """
    def __new__(cls, *args, **kwargs):
        # Just leave this here for easier debugging
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        # Just leave this here for easier debugging
        super().__init__(*args, **kwargs)

    @classmethod
    def check_result(cls, fn: Callable, message: str = None, exc: Type["BaseGitException"] = None, *oargs, **okwargs):
        # Override the check_result behavior from BaseGitException so the calling subclass is used by default
        if not exc and cls is not GitException:
            # Only auto-set for subclasses of GitException
            exc = cls
        return BaseGitException.check_result(fn=fn, message=message, exc=exc, *oargs, **okwargs)


class GitExistsError(GitException, ValueError):
    def __new__(cls, *args, **kwargs):
        # Just leave this here for easier debugging
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        # Just leave this here for easier debugging
        super().__init__(*args, **kwargs)


class GitInvalidSpecError(GitException, ValueError):
    def __new__(cls, *args, **kwargs):
        # Just leave this here for easier debugging
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        # Just leave this here for easier debugging
        super().__init__(*args, **kwargs)


class GitAmbiguousError(GitException, ValueError):
    def __new__(cls, *args, **kwargs):
        # Just leave this here for easier debugging
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        # Just leave this here for easier debugging
        super().__init__(*args, **kwargs)


class GitNotFoundError(GitException,KeyError):
    def __new__(cls, *args, **kwargs):
        # Just leave this here for easier debugging
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        # Just leave this here for easier debugging
        super().__init__(*args, **kwargs)


class GitIterOverError(GitException,StopIteration):
    def __new__(cls, *args, **kwargs):
        # Just leave this here for easier debugging
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        # Just leave this here for easier debugging
        super().__init__(*args, **kwargs)


class GitUserError(GitException,TypeError):
    def __new__(cls, *args, **kwargs):
        # Just leave this here for easier debugging
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        # Just leave this here for easier debugging
        super().__init__(*args, **kwargs)

class GitPassthroughError(GitException, Passthrough):
    # Inherits from Passthrough purely for backward compatibility
    def __new__(cls, *args, **kwargs):
        # Just leave this here for easier debugging
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        # Just leave this here for easier debugging
        super().__init__(*args, **kwargs)

class GitIOError(GitException, IOError):
    """
    This class should be replaced by better matching error definitions from libgit2
    It's here as a temporary replacement to support explicitly throwing IOErrors in some
    of the PyGit2 classes and should not be used for new code.
    """
    # TODO drop legacy support
    def __new__(cls, *args, **kwargs):
        # Just leave this here for easier debugging
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        # Just leave this here for easier debugging
        super().__init__(*args, **kwargs)
