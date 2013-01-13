**********************************************************************
Commit log
**********************************************************************

You can iterate through the revision history with repo.walk::

    >>> from pygit2 import GIT_SORT_TIME
    >>> for commit in repo.walk(oid, GIT_SORT_TIME):
    ...     print(commit.hex)
