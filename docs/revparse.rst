**********************************************************************
Revision parsing
**********************************************************************

.. automethod:: pygit2.Repository.revparse_single

You can use any of the fancy `<rev>` forms supported by libgit2::

    >>> commit = repo.revparse_single('HEAD^')
