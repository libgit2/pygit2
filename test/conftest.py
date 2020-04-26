import pytest
import pygit2
from . import utils


@pytest.fixture(scope='session', autouse=True)
def disable_global_git_config():
    """
    Do not use global config for better test reproducibility.
    https://github.com/libgit2/pygit2/issues/989
    """
    levels = [pygit2.GIT_CONFIG_LEVEL_GLOBAL,
              pygit2.GIT_CONFIG_LEVEL_XDG,
              pygit2.GIT_CONFIG_LEVEL_SYSTEM]
    for level in levels:
        pygit2.settings.search_path[level] = ""


@pytest.fixture
def barerepo():
    with utils.TemporaryRepository('testrepo.git', 'git') as path:
        yield pygit2.Repository(path)


@pytest.fixture
def barerepo_path():
    with utils.TemporaryRepository('testrepo.git', 'git') as path:
        yield pygit2.Repository(path), path


@pytest.fixture
def dirtyrepo():
    with utils.TemporaryRepository('dirtyrepo') as path:
        yield pygit2.Repository(path)


@pytest.fixture
def emptyrepo():
    with utils.TemporaryRepository('emptyrepo') as path:
        yield pygit2.Repository(path)

@pytest.fixture
def encodingrepo():
    with utils.TemporaryRepository('encoding') as path:
        yield pygit2.Repository(path)


@pytest.fixture
def mergerepo():
    with utils.TemporaryRepository('testrepoformerging') as path:
        yield pygit2.Repository(path)


@pytest.fixture
def testrepo():
    with utils.TemporaryRepository('testrepo') as path:
        yield pygit2.Repository(path)


@pytest.fixture
def testrepo_path():
    with utils.TemporaryRepository('testrepo') as path:
        yield pygit2.Repository(path), path
