**********************************************************************
References
**********************************************************************

.. automethod:: pygit2.Repository.listall_references
.. automethod:: pygit2.Repository.lookup_reference

Reference lookup::

    >>> all_refs = repo.listall_references()
    >>> master_ref = repo.lookup_reference("refs/heads/master")
    >>> commit = repo[master_ref.oid]

Reference log::

    >>> head = repo.lookup_reference('refs/heads/master')
    >>> for entry in head.log():
    ...     print(entry.message)

The interface for RefLogEntry::

    RefLogEntry.committer -- Signature of Committer
    RefLogEntry.message   -- the message of the RefLogEntry
    RefLogEntry.oid_old   -- oid of old reference
    RefLogEntry.oid_new   -- oid of new reference


The Reference type
====================

.. autoattribute:: pygit2.Reference.name
.. autoattribute:: pygit2.Reference.oid
.. autoattribute:: pygit2.Reference.hex
.. autoattribute:: pygit2.Reference.target
.. autoattribute:: pygit2.Reference.type

.. automethod:: pygit2.Reference.delete
.. automethod:: pygit2.Reference.rename
.. automethod:: pygit2.Reference.resolve
.. automethod:: pygit2.Reference.log


The reference log
--------------------

.. autoattribute:: pygit2.RefLogEntry.oid_new
.. autoattribute:: pygit2.RefLogEntry.oid_old
.. autoattribute:: pygit2.RefLogEntry.message
.. autoattribute:: pygit2.RefLogEntry.committer


Notes
====================

.. automethod:: pygit2.Repository.notes
.. automethod:: pygit2.Repository.create_note
.. automethod:: pygit2.Repository.lookup_note


The Note type
--------------------

.. autoattribute:: pygit2.Note.annotated_id
.. autoattribute:: pygit2.Note.oid
.. autoattribute:: pygit2.Note.message
.. automethod:: pygit2.Note.remove
