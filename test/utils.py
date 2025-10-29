# Copyright 2010-2025 The pygit2 contributors
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

# Standard library
import hashlib
import shutil
import socket
import stat
import sys
import zipfile
from collections.abc import Callable, Iterator
from pathlib import Path
from types import TracebackType
from typing import Any, Optional, ParamSpec, TypeVar

# Requirements
import pytest

# Pygit2
import pygit2

T = TypeVar('T')
P = ParamSpec('P')

requires_future_libgit2 = pytest.mark.xfail(
    pygit2.LIBGIT2_VER < (2, 0, 0),
    reason='This test may work with a future version of libgit2',
)

try:
    socket.gethostbyname('github.com')
    has_network = True
except socket.gaierror:
    has_network = False

requires_network = pytest.mark.skipif(not has_network, reason='Requires network')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    has_proxy = sock.connect_ex(('', 8888)) == 0

requires_proxy = pytest.mark.skipif(not has_proxy, reason='Requires proxy at port 8888')

requires_ssh = pytest.mark.skipif(
    pygit2.enums.Feature.SSH not in pygit2.features, reason='Requires SSH'
)


is_pypy = '__pypy__' in sys.builtin_module_names

requires_refcount = pytest.mark.skipif(is_pypy, reason='skip refcounts checks in pypy')

fails_in_macos = pytest.mark.xfail(
    sys.platform == 'darwin', reason='fails in macOS for an unknown reason'
)


def gen_blob_sha1(data: bytes) -> str:
    # http://stackoverflow.com/questions/552659/assigning-git-sha1s-without-git
    m = hashlib.sha1()
    m.update(f'blob {len(data)}\0'.encode())
    m.update(data)
    return m.hexdigest()


def force_rm_handle(
    # Callable[..., Any], str, , object
    remove_path: Callable[..., Any],
    path_str: str,
    excinfo: tuple[type[BaseException], BaseException, TracebackType],
) -> None:
    path = Path(path_str)
    path.chmod(path.stat().st_mode | stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)
    remove_path(path)


def rmtree(path: str | Path) -> None:
    """In Windows a read-only file cannot be removed, and shutil.rmtree fails.
    So we implement our own version of rmtree to address this issue.
    """
    if Path(path).exists():
        shutil.rmtree(path, onerror=force_rm_handle)


def diff_safeiter(diff: pygit2.Diff) -> Iterator[pygit2.Patch]:
    """
    In rare cases, Diff.__iter__ may yield None (see diff_get_patch_byindex).
    To make mypy happy, use this iterator instead of Diff.__iter__ to ensure
    that all patches in a Diff are valid Patch objects, not None.
    """
    for patch in diff:
        if patch is None:
            raise TypeError('patch is None')
        yield patch


class TemporaryRepository:
    def __init__(self, name: str, tmp_path: Path) -> None:
        self.name = name
        self.tmp_path = tmp_path

    def __enter__(self) -> Path:
        path = Path(__file__).parent / 'data' / self.name
        temp_repo_path = Path(self.tmp_path) / path.stem
        if path.suffix == '.zip':
            with zipfile.ZipFile(path) as zipf:
                zipf.extractall(self.tmp_path)
        elif path.suffix == '.git':
            shutil.copytree(path, temp_repo_path)
        else:
            raise ValueError(f'Unexpected {path.suffix} extension')

        return temp_repo_path

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        pass


def assertRaisesWithArg(
    exc_class: type[Exception],
    arg: object,
    func: Callable[P, T],
    *args: P.args,
    **kwargs: P.kwargs,
) -> None:
    with pytest.raises(exc_class) as excinfo:
        func(*args, **kwargs)
    assert excinfo.value.args == (arg,)

    # Explicitly clear the Exception Info. Citing
    # https://docs.pytest.org/en/latest/reference.html#pytest-raises:
    #
    # Clearing those references breaks a reference cycle
    # (ExceptionInfo –> caught exception –> frame stack raising the exception
    # –> current frame stack –> local variables –> ExceptionInfo) which makes
    # Python keep all objects referenced from that cycle (including all local
    # variables in the current frame) alive until the next cyclic garbage
    # collection run. See the official Python try statement documentation for
    # more detailed information.
    del excinfo
