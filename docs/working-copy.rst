**********************************************************************
The Index file and the Working copy
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
--------------------

.. autoclass:: pygit2.IndexEntry
   :members:

Status
====================

.. automethod:: pygit2.Repository.status
.. automethod:: pygit2.Repository.status_file

Inspect the status of the repository::

    >>> from pygit2 import GIT_STATUS_CURRENT
    >>> status = repo.status()
    >>> for filepath, flags in status.items():
    ...     if flags != GIT_STATUS_CURRENT:
    ...         print("Filepath %s isn't clean" % filepath)


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
