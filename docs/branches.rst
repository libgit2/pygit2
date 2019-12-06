**********************************************************************
Branches
**********************************************************************

.. py:attribute:: Repository.branches

Branches inherit from References, and additionally provide specialized
accessors for some unique features.

.. autoclass:: pygit2.repository.Branches
   :members:
   :undoc-members:
   :special-members: __getitem__, __iter__, __contains__

Example::

    >>> # Listing all branches
    >>> branches_list = list(repo.branches)
    >>> # Local only
    >>> local_branches = list(repo.branches.local)
    >>> # Remote only
    >>> remote_branches = list(repo.branches.remote)

    >>> # Get a branch
    >>> branch = repo.branches['master']
    >>> other_branch = repo.branches['does-not-exist']  # Will raise a KeyError
    >>> other_branch = repo.branches.get('does-not-exist')  # Returns None

    >>> remote_branch = repo.branches.remote['upstream/feature']

    >>> # Create a local branch
    >>> new_branch = repo.branches.local.create('new-branch')

    >>> And delete it
    >>> repo.branches.delete('new-branch')


The Branch type
====================

.. autoclass:: pygit2.Branch
   :members:
