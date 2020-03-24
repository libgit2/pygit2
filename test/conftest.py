import pytest
import pygit2


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
