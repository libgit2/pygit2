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
    repo_spec = 'git', 'testrepo.git'
    with utils.TemporaryRepository(repo_spec) as path:
        yield pygit2.Repository(path)


@pytest.fixture
def barerepo_path():
    repo_spec = 'git', 'testrepo.git'
    with utils.TemporaryRepository(repo_spec) as path:
        yield pygit2.Repository(path), path


@pytest.fixture
def dirtyrepo():
    repo_spec = 'tar', 'dirtyrepo'
    with utils.TemporaryRepository(repo_spec) as path:
        yield pygit2.Repository(path)


@pytest.fixture
def emptyrepo():
    repo_spec = 'tar', 'emptyrepo'
    with utils.TemporaryRepository(repo_spec) as path:
        yield pygit2.Repository(path)

@pytest.fixture
def encodingrepo():
    repo_spec = 'tar', 'encoding'
    with utils.TemporaryRepository(repo_spec) as path:
        yield pygit2.Repository(path)


@pytest.fixture
def mergerepo():
    repo_spec = 'tar', 'testrepoformerging'
    with utils.TemporaryRepository(repo_spec) as path:
        yield pygit2.Repository(path)
