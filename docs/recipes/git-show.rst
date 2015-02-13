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

In order to display time zone information you have to create a subclass
of tzinfo. In Python 3.2+ you can do this fairly directly. In older
versions you have to make your own class as described in the `Python
datetime documentation`_::

    from datetime import tzinfo, timedelta
    class FixedOffset(tzinfo):
        """Fixed offset in minutes east from UTC."""

        def __init__(self, offset):
            self.__offset = timedelta(minutes = offset)

        def utcoffset(self, dt):
            return self.__offset

        def tzname(self, dt):
            return None # we don't know the time zone's name

        def dst(self, dt):
            return timedelta(0) # we don't know about DST

.. _Python datetime documentation: https://docs.python.org/2/library/datetime.html#tzinfo-objects

Then you can make your message:

    >>> # Until Python 2.7.9:
    >>> from __future__ import unicode_literals
    >>> from datetime import datetime
    >>> tzinfo  = FixedOffset(commit.author.offset)

    >>> # From Python 3.2:
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
