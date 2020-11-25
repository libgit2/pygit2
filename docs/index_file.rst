**********************************************************************
Index file & Working copy
**********************************************************************

.. autoattribute:: pygit2.Repository.index

Index read::

    >>> index = repo.index
    >>> index.read()
    >>> id = index['path/to/file'].id    # from path to object id
    >>> blob = repo[id]                  # from object id to object

Iterate over all entries of the index::

    >>> for entry in index:
    ...     print(entry.path, entry.hex)

Index write::

    >>> index.add('path/to/file')          # git add
    >>> index.remove('path/to/file')       # git rm
    >>> index.write()                      # don't forget to save the changes

Custom entries::
   >>> entry = pygit2.IndexEntry('README.md', blob_id, blob_filemode)
   >>> repo.index.add(entry)

The index fulfills a dual role as the in-memory representation of the
index file and data structure which represents a flat list of a
tree. You can use it independently of the index file, e.g.

  >>> index = pygit2.Index()
  >>> entry = pygit2.IndexEntry('README.md', blob_id, blob_filemode)
  >>> index.add(entry)

The Index type
====================

.. autoclass:: pygit2.Index
   :members:

The IndexEntry type
====================

.. autoclass:: pygit2.IndexEntry
   :members:

   .. automethod:: __eq__
   .. automethod:: __ne__
   .. automethod:: __repr__
   .. automethod:: __str__

Status
====================

.. autoclass:: pygit2.Repository
   :members: status_file
   :noindex:

   .. automethod:: Repository.status

      Example, inspect the status of the repository::

        from pygit2 import GIT_STATUS_CURRENT
        status = repo.status()
        for filepath, flags in status.items():
            if flags != GIT_STATUS_CURRENT:
                print("Filepath %s isn't clean" % filepath)

This is the list of status flags for a single file::

    GIT_STATUS_CURRENT
    GIT_STATUS_INDEX_NEW
    GIT_STATUS_INDEX_MODIFIED
    GIT_STATUS_INDEX_DELETED
    GIT_STATUS_INDEX_RENAMED
    GIT_STATUS_INDEX_TYPECHANGE
    GIT_STATUS_WT_NEW
    GIT_STATUS_WT_MODIFIED
    GIT_STATUS_WT_DELETED
    GIT_STATUS_WT_TYPECHANGE
    GIT_STATUS_WT_RENAMED
    GIT_STATUS_WT_UNREADABLE
    GIT_STATUS_IGNORED
    GIT_STATUS_CONFLICTED

A combination of these values will be returned to indicate the status of a
file.  Status compares the working directory, the index, and the current HEAD
of the repository.  The `GIT_STATUS_INDEX` set of flags represents the status
of file in the index relative to the HEAD, and the `GIT_STATUS_WT` set of flags
represent the status of the file in the working directory relative to the
index.


Checkout
====================

.. automethod:: pygit2.Repository.checkout

Lower level API:

.. automethod:: pygit2.Repository.checkout_head
.. automethod:: pygit2.Repository.checkout_tree
.. automethod:: pygit2.Repository.checkout_index

Stash
====================

.. automethod:: pygit2.Repository.stash
.. automethod:: pygit2.Repository.stash_apply
.. automethod:: pygit2.Repository.stash_drop
.. automethod:: pygit2.Repository.stash_pop
