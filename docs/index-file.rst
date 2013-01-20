**********************************************************************
Index file
**********************************************************************

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


.. autoclass:: pygit2.Index
   :members: add, remove, clear, read, write, read_tree, write_tree, diff

.. autoclass:: pygit2.IndexEntry
   :members: oid, hex, path, mode
