**********************************************************************
The repository
**********************************************************************

.. autofunction:: pygit2.init_repository

   This is how to create non-bare repository::

    >>> from pygit2 import init_repository
    >>> repo = init_repository('test')

   And this is how to create a bare repository::

    >>> from pygit2 import init_repository
    >>> repo = init_repository('test', bare=True)

   But one can also do::

    >>> from pygit2 import init_repository
    >>> repo = init_repository('test', True)

.. autofunction:: pygit2.discover_repository

.. autofunction:: pygit2.hashfile

.. autofunction:: pygit2.hash

.. autoclass:: pygit2.Repository
   :members:
   :show-inheritance:
