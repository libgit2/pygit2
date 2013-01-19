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


.. autofunction:: pygit2.init_repository

.. autofunction:: pygit2.discover_repository

.. autoclass:: pygit2.Repository
   :members:
