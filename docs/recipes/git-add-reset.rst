**********************************************************************
git-add / git-reset
**********************************************************************

----------------------------------------------------------------------
Add file contents to the index / Stage
----------------------------------------------------------------------

We can add a new (untracked) file or a modified file to the index.

.. code-block:: bash

    $> git add foo.txt

.. code-block:: python

    >>> index = repo.index
    >>> index.add(path)
    >>> index.write()

----------------------------------------------------------------------
Restore the entry in the index / Unstage
----------------------------------------------------------------------

.. code-block:: bash

    $> git reset HEAD foo.txt

.. code-block:: python

    >>> index = repo.index
    >>> index.remove(path)
    >>> # Skip the following lines if the file is new, go to "Write index"
    >>> ## Get the entry for this file in HEAD
    >>> tree_entry = repo.revparse_single('HEAD').tree[path]
    >>> ## Restore the entry in the index
    >>> index_entry = pygit2.IndexEntry(tree_entry.name, tree_entry.oid, tree_entry.filemode)
    >>> index.add(index_entry)
    >>> # Write index
    >>> index.write()

----------------------------------------------------------------------
Query the index state / Is file staged ?
----------------------------------------------------------------------

.. code-block:: bash

    $> git status foo.txt

.. code-block:: python

    >>> # Return True is the file was not updated in the index (same hash)
    >>> index[path].oid == repo.revparse_single('HEAD').tree[path].oid

----------------------------------------------------------------------
References
----------------------------------------------------------------------

- git-add_.

.. _git-add: https://www.kernel.org/pub/software/scm/git/docs/git-add.html

- git-reset_.

.. _git-reset: https://www.kernel.org/pub/software/scm/git/docs/git-reset.html
