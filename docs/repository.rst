**********************************************************************
The repository
**********************************************************************

.. autofunction:: pygit2.init_repository

   This is how to create non-bare repository::

    >>> from pygit2 import init_repository
    >>> bare = False
    >>> repo = init_repository('test', bare)


.. autofunction:: pygit2.discover_repository


.. autoclass:: pygit2.Repository
   :members: path, workdir, is_bare, is_empty, revparse_single, read, write,
             create_blob, create_blob_fromfile, create_commit, create_tag,
             TreeBuilder, walk, create_reference, listall_references,
             lookup_reference, packall_references, head, head_is_detached,
             head_is_orphaned, index, status, status_file, config

   To open an existing repository::

    >>> from pygit2 import Repository
    >>> repo = Repository('pygit2/.git')
