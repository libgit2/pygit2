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

The Stash type
====================

.. autoclass:: pygit2.Stash
   :members: commit_id, message

Status
====================

.. autoclass:: pygit2.Repository
   :members: status_file
   :noindex:

   .. automethod:: Repository.status

      Example, inspect the status of the repository::

        from pygit2.enums import FileStatus
        status = repo.status()
        for filepath, flags in status.items():
            if flags != FileStatus.CURRENT:
                print(f"Filepath {filepath} isn't clean")

This is the list of status flags for a single file::

    enums.FileStatus.CURRENT
    enums.FileStatus.INDEX_NEW
    enums.FileStatus.INDEX_MODIFIED
    enums.FileStatus.INDEX_DELETED
    enums.FileStatus.INDEX_RENAMED
    enums.FileStatus.INDEX_TYPECHANGE
    enums.FileStatus.WT_NEW
    enums.FileStatus.WT_MODIFIED
    enums.FileStatus.WT_DELETED
    enums.FileStatus.WT_TYPECHANGE
    enums.FileStatus.WT_RENAMED
    enums.FileStatus.WT_UNREADABLE
    enums.FileStatus.IGNORED
    enums.FileStatus.CONFLICTED

A combination of these values will be returned to indicate the status of a
file.  Status compares the working directory, the index, and the current HEAD
of the repository.  The `INDEX_...` set of flags represents the status
of file in the index relative to the HEAD, and the `WT_...` set of flags
represents the status of the file in the working directory relative to the
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
.. automethod:: pygit2.Repository.listall_stashes
