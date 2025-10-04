**********************************************************************
References
**********************************************************************

.. autoclass:: pygit2.Repository
   :members: lookup_reference, lookup_reference_dwim, raw_listall_references,
             resolve_refish
   :noindex:

   .. attribute:: references

      Returns an instance of the References class (see below).


.. autoclass:: pygit2.repository.References
   :members:
   :undoc-members:
   :special-members: __getitem__, __iter__, __contains__

Example::

    >>> all_refs = list(repo.references)

    >>> master_ref = repo.references["refs/heads/master"]
    >>> commit = master_ref.peel() # or repo[master_ref.target]

    # Create a reference
    >>> ref = repo.references.create('refs/tags/version1', LAST_COMMIT)

    # Delete a reference
    >>> repo.references.delete('refs/tags/version1')

    # Pack loose references
    >>> repo.references.compress()


Functions
===================================

.. autofunction:: pygit2.reference_is_valid_name

Check if the passed string is a valid reference name.

   Example::

     >>> from pygit2 import reference_is_valid_name
     >>> reference_is_valid_name("refs/heads/master")
     True
     >>> reference_is_valid_name("HEAD")
     True
     >>> reference_is_valid_name("refs/heads/..")
     False


The Reference type
====================

.. autoclass:: pygit2.Reference
   :members:
   :special-members: __eq__, __ne__
   :exclude-members: log

   .. automethod:: log

The HEAD
====================

Example. These two lines are equivalent::

    >>> head = repo.references['HEAD'].resolve()
    >>> head = repo.head

.. autoattribute:: pygit2.Repository.head
.. autoattribute:: pygit2.Repository.head_is_detached
.. autoattribute:: pygit2.Repository.head_is_unborn

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

Reference Transactions
=======================

For atomic updates of multiple references, use transactions. See the
:doc:`transactions` documentation for details.

Example::

    # Update multiple refs atomically
    with repo.transaction() as txn:
        txn.lock_ref('refs/heads/master')
        txn.lock_ref('refs/heads/develop')
        txn.set_target('refs/heads/master', new_oid, message='Release')
        txn.set_target('refs/heads/develop', dev_oid, message='Continue dev')

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
