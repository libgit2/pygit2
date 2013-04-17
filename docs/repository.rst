**********************************************************************
The repository
**********************************************************************

Everything starts either by creating a new repository, or by opening an
existing one.


Creating a repository
===================================

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


The Repository class
===================================

To open an existing repository::

  >>> from pygit2 import Repository
  >>> repo = Repository('pygit2/.git')

.. autoattribute:: pygit2.Repository.path
.. autoattribute:: pygit2.Repository.workdir
.. autoattribute:: pygit2.Repository.is_bare
.. autoattribute:: pygit2.Repository.is_empty
.. automethod:: pygit2.Repository.read
.. automethod:: pygit2.Repository.write
