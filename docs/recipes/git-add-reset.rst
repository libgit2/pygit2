**********************************************************************
git-add / git-reset
**********************************************************************

----------------------------------------------------------------------
Add file contents to the index / Stage
----------------------------------------------------------------------

We can add a new (untracked) file or a modified file to the index.

.. code-block:: bash

    $ git add foo.txt

.. code-block:: python

    >>> index = repo.index
    >>> index.add(path)
    >>> index.write()

----------------------------------------------------------------------
Restore the entry in the index / Unstage
----------------------------------------------------------------------

.. code-block:: bash

    $ git reset HEAD src/tree.c

.. code-block:: python

    >>> index = repo.index

    # Remove path from the index
    >>> path = 'src/tree.c'
    >>> index.remove(path)

    # Restore object from db
    >>> obj = repo.revparse_single('HEAD').tree[path] # Get object from db
    >>> index.add(pygit2.IndexEntry(path, obj.oid, obj.filemode)) # Add to index

    # Write index
    >>> index.write()

----------------------------------------------------------------------
Query the index state / Is file staged ?
----------------------------------------------------------------------

.. code-block:: bash

    $ git status foo.txt

.. code-block:: python

    # Return True is the file is modified in the working tree
    >>> repo.status_file(path) & pygit2.GIT_STATUS_WT_MODIFIED

----------------------------------------------------------------------
References
----------------------------------------------------------------------

- git-add_.

.. _git-add: https://www.kernel.org/pub/software/scm/git/docs/git-add.html

- git-reset_.

.. _git-reset: https://www.kernel.org/pub/software/scm/git/docs/git-reset.html
