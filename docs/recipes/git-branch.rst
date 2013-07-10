**********************************************************************
git-branch
**********************************************************************

----------------------------------------------------------------------
Listing branches
----------------------------------------------------------------------

======================================================================
List all branches
======================================================================

.. code-block:: bash

    $> git branch

.. code-block:: python

    >>> regex = re.compile('^refs/heads/')
    >>> branches = filter(lambda r: regex.match(r), repo.listall_references())

`Note that the next release will probably allow` ``repo.listall_branches()``.

----------------------------------------------------------------------
References
----------------------------------------------------------------------

- git-branch_.

.. _git-branch: https://www.kernel.org/pub/software/scm/git/docs/git-branch.html
