**********************************************************************
Repository
**********************************************************************

Everything starts either by creating a new repository, or by opening an
existing one.

.. contents:: Contents
   :local:


Functions
===================================

.. autofunction:: pygit2.init_repository

   Example::

     >>> from pygit2 import init_repository
     >>> repo = init_repository('test')            # Creates a non-bare repository
     >>> repo = init_repository('test', bare=True) # Creates a bare repository

.. autofunction:: pygit2.clone_repository

   Example::

     >>> from pygit2 import clone_repository
     >>> repo_url = 'git://github.com/libgit2/pygit2.git'
     >>> repo_path = '/path/to/create/repository'
     >>> repo = clone_repository(repo_url, repo_path) # Clones a non-bare repository
     >>> repo = clone_repository(repo_url, repo_path, bare=True) # Clones a bare repository


.. autofunction:: pygit2.discover_repository

   Example::

     >>> current_working_directory = os.getcwd()
     >>> repository_path = discover_repository(current_working_directory)
     >>> repo = Repository(repository_path)

.. autofunction:: pygit2.tree_entry_cmp(object, other)


The Repository class
===================================

The API of the Repository class is quite large. Since this documentation is
organized by features, the related bits are explained in the related chapters,
for instance the :py:meth:`pygit2.Repository.checkout` method is explained in
the Checkout section.

Below there are some general attributes and methods:

.. autoclass:: pygit2.Repository
   :members: ahead_behind, amend_commit, applies, apply, create_reference,
             default_signature, descendant_of, describe, free, get_attr,
             is_bare, is_empty, is_shallow, odb, path, path_is_ignored, reset,
             revert_commit, state_cleanup, workdir, write, write_archive,
             set_odb, set_refdb

   The Repository constructor will most commonly be called with one argument, the path of the repository to open.

   Alternatively, constructing a repository with no arguments will create a repository with no backends. You can
   use this path to create repositories with custom backends. Note that most operations on the repository are
   considered invalid and may lead to undefined behavior if attempted before providing an odb and refdb via
   :py:meth:`set_odb` and :py:meth:`set_refdb`.

   Parameters:

   path
       The path to open — if not provided, the repository will have no backend.

   flags
       Flags controlling how to open the repository can optionally be provided — any combination of:

   * GIT_REPOSITORY_OPEN_NO_SEARCH
   * GIT_REPOSITORY_OPEN_CROSS_FS
   * GIT_REPOSITORY_OPEN_BARE
   * GIT_REPOSITORY_OPEN_NO_DOTGIT
   * GIT_REPOSITORY_OPEN_FROM_ENV

   Example::

     >>> from pygit2 import Repository
     >>> repo = Repository('pygit2/.git')


The Odb class
===================================

.. autoclass:: pygit2.Odb
   :members:

The Refdb class
===================================

.. autoclass:: pygit2.Refdb
   :members:
