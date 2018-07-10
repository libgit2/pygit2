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

    >>> commit = repo[repo.head.target]
    >>> commit.message
    'commit message'

======================================================================
Traverse commit history
======================================================================

.. code-block:: bash

    $> git log

.. code-block:: python

    >>> last = repo[repo.head.target]
    >>> for commit in repo.walk(last.id, pygit2.GIT_SORT_TIME):
    >>>     print(commit.message) # or some other operation

----------------------------------------------------------------------
References
----------------------------------------------------------------------

- git-log_.

- `libgit2 discussion about walker behavior
  <https://github.com/libgit2/libgit2/issues/3041>`_. Note that the libgit2's
  walker functions differently than ``git-log`` in some ways.

.. _git-log: https://www.kernel.org/pub/software/scm/git/docs/git-log.html
