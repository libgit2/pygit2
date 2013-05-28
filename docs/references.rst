**********************************************************************
References
**********************************************************************

.. contents::

.. automethod:: pygit2.Repository.listall_references
.. automethod:: pygit2.Repository.lookup_reference

Example::

    >>> all_refs = repo.listall_references()
    >>> master_ref = repo.lookup_reference("refs/heads/master")
    >>> commit = master_ref.get_object() # or repo[master_ref.target]


The Reference type
====================

.. autoattribute:: pygit2.Reference.name
.. autoattribute:: pygit2.Reference.target
.. autoattribute:: pygit2.Reference.type

.. automethod:: pygit2.Reference.delete
.. automethod:: pygit2.Reference.rename
.. automethod:: pygit2.Reference.resolve
.. automethod:: pygit2.Reference.log
.. automethod:: pygit2.Reference.get_object


The HEAD
====================

Example. These two lines are equivalent::

    >>> head = repo.lookup_reference('HEAD').resolve()
    >>> head = repo.head

.. autoattribute:: pygit2.Repository.head
.. autoattribute:: pygit2.Repository.head_is_detached
.. autoattribute:: pygit2.Repository.head_is_orphaned


The reference log
====================

Example::

    >>> head = repo.lookup_reference('refs/heads/master')
    >>> for entry in head.log():
    ...     print(entry.message)

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
