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
Signing a commit
----------------------------------------------------------------------

Add everything, and commit with a GPG signature:

.. code-block:: bash

    $ git add .
    $ git commit -S -m "Signed commit"

.. code-block:: python

    >>> index = repo.index
    >>> index.add_all()
    >>> index.write()
    >>> author = Signature('Alice Author', 'alice@authors.tld')
    >>> committer = Signature('Cecil Committer', 'cecil@committers.tld')
    >>> message = "Signed commit"
    >>> tree = index.write_tree()
    >>> parents = []
    >>> commit_string = repo.create_commit_string(
    >>>     author, committer, message, tree, parents
    >>> )

The ``commit_string`` can then be signed by a third party library:

.. code-block:: python
    >>> gpg = YourGPGToolHere()
    >>> signed_commit = gpg.sign(
    >>>     commit_string,
    >>>     passphrase='secret',
    >>>     detach=True,
    >>> )

.. note::
    The commit signature should resemble:

    .. code-block:: none
        >>> -----BEGIN PGP SIGNATURE-----
        >>>
        >>> < base64 encoded hash here >
        >>> -----END PGP SIGNATURE-----

The signed commit can then be added to the branch:

.. code-block:: python

    >>> commit = repo.create_commit_with_signature(
    >>>     commit_string, signed_commit.data.decode('utf-8')
    >>> )
    >>> repo.head.set_target(commit)


----------------------------------------------------------------------
References
----------------------------------------------------------------------

- git-commit_.

.. _git-commit: https://www.kernel.org/pub/software/scm/git/docs/git-commit.html
