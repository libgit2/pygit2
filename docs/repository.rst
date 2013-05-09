**********************************************************************
The repository
**********************************************************************

Everything starts either by creating a new repository, or by opening an
existing one.

.. contents:: Contents
   :local:


Creating a repository
===================================

.. autofunction:: pygit2.init_repository

Example::

  >>> from pygit2 import init_repository
  >>> repo = init_repository('test')            # Creates a non-bare repository
  >>> repo = init_repository('test', bare=True) # Creates a bare repository


The Repository class
===================================

.. py:class:: pygit2.Repository(path)

   The Repository constructor only takes one argument, the path of the
   repository to open.

   Example::

     >>> from pygit2 import Repository
     >>> repo = Repository('pygit2/.git')

The API of the Repository class is quite large. Since this documentation is
orgaized by features, the related bits are explained in the related chapters,
for instance the :py:meth:`pygit2.Repository.checkout` method are explained in
the Checkout section.

Below there are some general attributes and methods:

.. autoattribute:: pygit2.Repository.path
.. autoattribute:: pygit2.Repository.workdir
.. autoattribute:: pygit2.Repository.is_bare
.. autoattribute:: pygit2.Repository.is_empty
.. automethod:: pygit2.Repository.read
.. automethod:: pygit2.Repository.write


Utilities
=========

.. autofunction:: pygit2.discover_repository
