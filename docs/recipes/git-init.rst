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

    $> git init --bare relative/path

.. code-block:: python

    >>> pygit2.init_repository('relative/path', True)
    <pygit2.repository.Repository object at 0x10f08b680>

======================================================================
Create standard repository
======================================================================

.. code-block:: bash

    $> git init relative/path

.. code-block:: python

    >>> pygit2.init_repository('relative/path', False)
    <pygit2.repository.Repository object at 0x10f08b680>

----------------------------------------------------------------------
References
----------------------------------------------------------------------

- git-init_.

.. _git-init: https://www.kernel.org/pub/software/scm/git/docs/git-init.html
