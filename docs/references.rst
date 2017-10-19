**********************************************************************
References
**********************************************************************

.. contents::

.. autoclass:: pygit2.repository.References
   :members:
   :undoc-members:
   :special-members: __getitem__, __iter__, __contains__


Example::

    >>> all_refs = list(repo.references)

    >>> master_ref = repo.lookup_reference("refs/heads/master")
    >>> commit = master_ref.peel() # or repo[master_ref.target]

    # Create a reference
    >>> ref = repo.references.create('refs/tags/version1', LAST_COMMIT)

    # Delete a reference
    >>> repo.references.delete('refs/tags/version1')


The Reference type
====================

.. autoclass:: pygit2.Reference

.. autoattribute:: pygit2.Reference.name
.. autoattribute:: pygit2.Reference.shorthand
.. autoattribute:: pygit2.Reference.target
.. autoattribute:: pygit2.Reference.type

.. automethod:: pygit2.Reference.set_target
.. automethod:: pygit2.Reference.delete
.. automethod:: pygit2.Reference.rename
.. automethod:: pygit2.Reference.resolve
.. automethod:: pygit2.Reference.peel
.. automethod:: pygit2.Reference.log

   Example::

      >>> branch = repository.lookup_reference("refs/heads/master")
      >>> branch.target = another_commit.id
      >>> committer = Signature('Cecil Committer', 'cecil@committers.tld')
      >>> branch.log_append(another_commit.id, committer,
                            "changed branch target using pygit2")

   This creates a reflog entry in ``git reflog master`` which looks like::

      7296b92 master@{10}: changed branch target using pygit2

   In order to make an entry in ``git reflog``, ie. the reflog for ``HEAD``, you
   have to get the Reference object for ``HEAD`` and call ``log_append`` on
   that.

.. automethod:: pygit2.Reference.get_object


The HEAD
====================

Example. These two lines are equivalent::

    >>> head = repo.lookup_reference('HEAD').resolve()
    >>> head = repo.head

.. autoattribute:: pygit2.Repository.head
.. autoattribute:: pygit2.Repository.head_is_detached
.. autoattribute:: pygit2.Repository.head_is_unborn

Branches
====================

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

.. autoattribute:: pygit2.Branch.branch_name
.. autoattribute:: pygit2.Branch.remote_name
.. autoattribute:: pygit2.Branch.upstream
.. autoattribute:: pygit2.Branch.upstream_name
.. automethod:: pygit2.Branch.rename
.. automethod:: pygit2.Branch.delete
.. automethod:: pygit2.Branch.is_head
.. automethod:: pygit2.Branch.is_checked_out

The reference log
====================

Example::

    >>> head = repo.references.get('refs/heads/master')  # Returns None if not found
    >>> # Almost equivalent to
    >>> head = repo.references['refs/heads/master']  # Raises KeyError if not found
    >>> for entry in head.log():
    ...     print(entry.message)

.. autoclass:: pygit2.RefLogEntry
   :members:

Notes
====================

.. automethod:: pygit2.Repository.notes
.. automethod:: pygit2.Repository.create_note
.. automethod:: pygit2.Repository.lookup_note


The Note type
--------------------

.. autoattribute:: pygit2.Note.annotated_id
.. autoattribute:: pygit2.Note.id
.. autoattribute:: pygit2.Note.message
.. automethod:: pygit2.Note.remove
