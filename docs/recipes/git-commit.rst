**********************************************************************
git-commit
**********************************************************************

----------------------------------------------------------------------
Initial commit
----------------------------------------------------------------------

Add everything, and make an initial commit:

.. code-block:: bash

    $ git add .
    $ git commit -m "Initial commit"

.. code-block:: python

    >>> index = repo.index
    >>> index.add_all()
    >>> index.write()
    >>> ref = "HEAD"
    >>> author = Signature('Alice Author', 'alice@authors.tld')
    >>> committer = Signature('Cecil Committer', 'cecil@committers.tld')
    >>> message = "Initial commit"
    >>> tree = index.write_tree()
    >>> parents = []
    >>> repo.create_commit(ref, author, committer, message, tree, parents)


----------------------------------------------------------------------
Subsequent commit
----------------------------------------------------------------------

Once ``HEAD`` has a commit to point to, you can use ``repo.head.name`` as the
reference to be updated by the commit, and you should name parents:

.. code-block:: python

    >>> ref = repo.head.name
    >>> parents = [repo.head.target]

The rest is the same:

.. code-block:: python

    >>> index = repo.index
    >>> index.add_all()
    >>> index.write()
    >>> author = Signature('Alice Author', 'alice@authors.tld')
    >>> committer = Signature('Cecil Committer', 'cecil@committers.tld')
    >>> message = "Initial commit"
    >>> tree = index.write_tree()
    >>> repo.create_commit(ref, author, committer, message, tree, parents)

----------------------------------------------------------------------
References
----------------------------------------------------------------------

- git-commit_.

.. _git-commit: https://www.kernel.org/pub/software/scm/git/docs/git-commit.html
