**********************************************************************
References
**********************************************************************

.. autoclass:: pygit2.Repository
   :members: lookup_reference, lookup_reference_dwim, resolve_refish
   :noindex:

   .. attribute:: Repository.references

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

.. autoattribute:: pygit2.Reference.name
.. autoattribute:: pygit2.Reference.raw_name
.. autoattribute:: pygit2.Reference.shorthand
.. autoattribute:: pygit2.Reference.raw_shorthand
.. autoattribute:: pygit2.Reference.target
.. autoattribute:: pygit2.Reference.type

.. automethod:: pygit2.Reference.__eq__(Reference)
.. automethod:: pygit2.Reference.__ne__(Reference)
.. automethod:: pygit2.Reference.set_target
.. automethod:: pygit2.Reference.delete
.. automethod:: pygit2.Reference.rename
.. automethod:: pygit2.Reference.resolve
.. automethod:: pygit2.Reference.peel
.. automethod:: pygit2.Reference.log

   Example::

      >>> branch = repository.references["refs/heads/master"]
      >>> branch.target = another_commit.id
      >>> committer = Signature('Cecil Committer', 'cecil@committers.tld')
      >>> branch.log_append(another_commit.id, committer,
                            "changed branch target using pygit2")

   This creates a reflog entry in ``git reflog master`` which looks like::

      7296b92 master@{10}: changed branch target using pygit2

   In order to make an entry in ``git reflog``, ie. the reflog for ``HEAD``, you
   have to get the Reference object for ``HEAD`` and call ``log_append`` on
   that.


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
