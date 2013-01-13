**********************************************************************
The repository
**********************************************************************


Everything starts by opening an existing repository::

    >>> from pygit2 import Repository
    >>> repo = Repository('pygit2/.git')


Or by creating a new one::

    >>> from pygit2 import init_repository
    >>> bare = False
    >>> repo = init_repository('test', bare)



These are the basic attributes of a repository::

    Repository.path    -- path to the Git repository
    Repository.workdir -- path to the working directory, None in the case of
                          a bare repo
