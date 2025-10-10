from collections.abc import Generator
from pathlib import Path

import pytest

import pygit2
from pygit2 import Repository

from . import utils


@pytest.fixture(scope='session', autouse=True)
def global_git_config() -> None:
    # Do not use global config for better test reproducibility.
    # https://github.com/libgit2/pygit2/issues/989
    levels = [
        pygit2.enums.ConfigLevel.GLOBAL,
        pygit2.enums.ConfigLevel.XDG,
        pygit2.enums.ConfigLevel.SYSTEM,
    ]
    for level in levels:
        pygit2.settings.search_path[level] = ''


@pytest.fixture
def pygit2_empty_key() -> tuple[Path, str, str]:
    path = Path(__file__).parent / 'keys' / 'pygit2_empty'
    return path, f'{path}.pub', 'empty'


@pytest.fixture
def barerepo(tmp_path: Path) -> Generator[Repository, None, None]:
    with utils.TemporaryRepository('barerepo.zip', tmp_path) as path:
        yield pygit2.Repository(path)


@pytest.fixture
def barerepo_path(tmp_path: Path) -> Generator[tuple[Repository, Path], None, None]:
    with utils.TemporaryRepository('barerepo.zip', tmp_path) as path:
        yield pygit2.Repository(path), path


@pytest.fixture
def blameflagsrepo(tmp_path: Path) -> Generator[Repository, None, None]:
    with utils.TemporaryRepository('blameflagsrepo.zip', tmp_path) as path:
        yield pygit2.Repository(path)


@pytest.fixture
def dirtyrepo(tmp_path: Path) -> Generator[Repository, None, None]:
    with utils.TemporaryRepository('dirtyrepo.zip', tmp_path) as path:
        yield pygit2.Repository(path)


@pytest.fixture
def emptyrepo(
    barerepo: Repository, tmp_path: Path
) -> Generator[Repository, None, None]:
    with utils.TemporaryRepository('emptyrepo.zip', tmp_path) as path:
        repo = pygit2.Repository(path)
        repo.remotes.create('origin', barerepo.path)
        yield repo


@pytest.fixture
def encodingrepo(tmp_path: Path) -> Generator[Repository, None, None]:
    with utils.TemporaryRepository('encoding.zip', tmp_path) as path:
        yield pygit2.Repository(path)


@pytest.fixture
def mergerepo(tmp_path: Path) -> Generator[Repository, None, None]:
    with utils.TemporaryRepository('testrepoformerging.zip', tmp_path) as path:
        yield pygit2.Repository(path)


@pytest.fixture
def testrepo(tmp_path: Path) -> Generator[Repository, None, None]:
    with utils.TemporaryRepository('testrepo.zip', tmp_path) as path:
        yield pygit2.Repository(path)


@pytest.fixture
def testrepo_path(tmp_path: Path) -> Generator[tuple[Repository, Path], None, None]:
    with utils.TemporaryRepository('testrepo.zip', tmp_path) as path:
        yield pygit2.Repository(path), path


@pytest.fixture
def testrepopacked(tmp_path: Path) -> Generator[Repository, None, None]:
    with utils.TemporaryRepository('testrepopacked.zip', tmp_path) as path:
        yield pygit2.Repository(path)


@pytest.fixture
def gpgsigned(tmp_path: Path) -> Generator[Repository, None, None]:
    with utils.TemporaryRepository('gpgsigned.zip', tmp_path) as path:
        yield pygit2.Repository(path)
