**********************************************************************
git-init
**********************************************************************

----------------------------------------------------------------------
Creating a new repository
----------------------------------------------------------------------

======================================================================
Create bare repository
======================================================================

.. code-block:: bash

    $ git init --bare path/to/git

.. code-block:: python

    >>> pygit2.init_repository('path/to/git', True)
    <pygit2.repository.Repository object at 0x10f08b680>

======================================================================
Create standard repository
======================================================================

.. code-block:: bash

    $ git init path/to/git

.. code-block:: python

    >>> pygit2.init_repository('path/to/git', False)
    <pygit2.repository.Repository object at 0x10f08b680>

----------------------------------------------------------------------
References
----------------------------------------------------------------------

- git-init_

.. _git-init: https://www.kernel.org/pub/software/scm/git/docs/git-init.html
