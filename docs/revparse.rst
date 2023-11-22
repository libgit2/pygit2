**********************************************************************
Revision parsing
**********************************************************************

.. autoclass:: pygit2.Repository
   :members: revparse, revparse_ext, revparse_single
   :noindex:

You can use any of the fancy `<rev>` forms supported by libgit2::

    >>> commit = repo.revparse_single('HEAD^')

.. autoclass:: pygit2.RevSpec
   :members:


Constants:

.. py:data:: pygit2.enums.RevSpecFlag.SINGLE
.. py:data:: pygit2.enums.RevSpecFlag.RANGE
.. py:data:: pygit2.enums.RevSpecFlag.MERGE_BASE
