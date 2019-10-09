**********************************************************************
git-show
**********************************************************************

----------------------------------------------------------------------
Showing a commit
----------------------------------------------------------------------

.. code-block:: bash

    $> git show d370f56

.. code-block:: python

    >>> repo = pygit2.Repository('/path/to/repository')
    >>> commit = repo.revparse_single('d370f56')

======================================================================
Show log message
======================================================================

    >>> message = commit.message

======================================================================
Show SHA hash
======================================================================

    >>> hash = commit.hex

======================================================================
Show diff
======================================================================

    >>> diff = repo.diff(commit.parents[0], commit)

======================================================================
Show all files in commit
======================================================================

    >>> for e in commit.tree:
    >>>     print(e.name)

======================================================================
Produce something like a ``git show`` message
======================================================================

Then you can make your message:

    >>> from datetime import datetime, timezone, timedelta
    >>> tzinfo  = timezone( timedelta(minutes=commit.author.offset) )
    >>>
    >>> dt      = datetime.fromtimestamp(float(commit.author.time), tzinfo)
    >>> timestr = dt.strftime('%c %z')
    >>> msg     = '\n'.join(['commit {}'.format(commit.tree_id.hex),
    ...                      'Author: {} <{}>'.format(commit.author.name, commit.author.email),
    ...                      'Date:   {}'.format(timestr),
    ...                      '',
    ...                      commit.message])

----------------------------------------------------------------------
References
----------------------------------------------------------------------

- git-show_.

.. _git-show: https://www.kernel.org/pub/software/scm/git/docs/git-show.html
