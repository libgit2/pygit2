**********************************************************************
The Index file and the Working copy
**********************************************************************

.. autoattribute:: pygit2.Repository.index

Index read::

    >>> index = repo.index
    >>> index.read()
    >>> oid = index['path/to/file'].oid    # from path to object id
    >>> blob = repo[oid]                   # from object id to object

Iterate over all entries of the index::

    >>> for entry in index:
    ...     print entry.path, entry.hex

Index write::

    >>> index.add('path/to/file')          # git add
    >>> del index['path/to/file']          # git rm
    >>> index.write()                      # don't forget to save the changes


The Index type
====================

.. automethod:: pygit2.Index.add
.. automethod:: pygit2.Index.remove
.. automethod:: pygit2.Index.clear
.. automethod:: pygit2.Index.read
.. automethod:: pygit2.Index.write
.. automethod:: pygit2.Index.read_tree
.. automethod:: pygit2.Index.write_tree
.. automethod:: pygit2.Index.diff_to_tree
.. automethod:: pygit2.Index.diff_to_workdir


The IndexEntry type
--------------------

.. autoattribute:: pygit2.IndexEntry.oid
.. autoattribute:: pygit2.IndexEntry.hex
.. autoattribute:: pygit2.IndexEntry.path
.. autoattribute:: pygit2.IndexEntry.mode


Status
====================

.. automethod:: pygit2.Repository.status
.. automethod:: pygit2.Repository.status_file

Inspect the status of the repository::

    >>> from pygit2 import GIT_STATUS_CURRENT
    >>> status = repo.status()
    >>> for filepath, flags in status.items():
    ...     if flags != GIT_STATUS_CURRENT:
    ...         print "Filepath %s isn't clean" % filepath


Checkout
====================

.. automethod:: pygit2.Repository.checkout

Lower level API:

.. automethod:: pygit2.Repository.checkout_head
.. automethod:: pygit2.Repository.checkout_tree
.. automethod:: pygit2.Repository.checkout_index
