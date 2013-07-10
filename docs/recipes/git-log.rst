**********************************************************************
git-log
**********************************************************************

----------------------------------------------------------------------
Showing HEAD commit logs
----------------------------------------------------------------------

======================================================================
Show HEAD commit
======================================================================

.. code-block:: bash

    $> git log -1

.. code-block:: python

    >>> commit = repo[repo.head.oid]
    >>> commit.message
    'commit message'

======================================================================
Traverse commit history
======================================================================

.. code-block:: bash

    $> git log

.. code-block:: python

    >>> last = repo[repo.head.oid]
    >>> for commit in repo.walk(last.oid, pygit2.GIT_SORT_TIME):
    >>>     print(commit.message) # or some other operation

----------------------------------------------------------------------
References
----------------------------------------------------------------------

- git-log_.

.. _git-log: https://www.kernel.org/pub/software/scm/git/docs/git-log.html
