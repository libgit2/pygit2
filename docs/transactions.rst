**********************************************************************
Reference Transactions
**********************************************************************

Reference transactions allow you to update multiple references atomically.
All reference updates within a transaction either succeed together or fail
together, ensuring repository consistency.

Basic Usage
===========

Use the :meth:`Repository.transaction` method as a context manager. The
transaction commits automatically when the context exits successfully, or
rolls back if an exception is raised::

    with repo.transaction() as txn:
        txn.lock_ref('refs/heads/master')
        txn.set_target('refs/heads/master', new_oid, message='Update master')

Atomic Multi-Reference Updates
===============================

Transactions are useful when you need to update multiple references
atomically::

    # Swap two branches atomically
    with repo.transaction() as txn:
        txn.lock_ref('refs/heads/branch-a')
        txn.lock_ref('refs/heads/branch-b')

        # Get current targets
        ref_a = repo.lookup_reference('refs/heads/branch-a')
        ref_b = repo.lookup_reference('refs/heads/branch-b')

        # Swap them
        txn.set_target('refs/heads/branch-a', ref_b.target, message='Swap')
        txn.set_target('refs/heads/branch-b', ref_a.target, message='Swap')

Automatic Rollback
==================

If an exception occurs during the transaction, changes are automatically
rolled back::

    try:
        with repo.transaction() as txn:
            txn.lock_ref('refs/heads/master')
            txn.set_target('refs/heads/master', new_oid)

            # If this raises an exception, the ref update is rolled back
            validate_commit(new_oid)
    except ValidationError:
        # Master still points to its original target
        pass

Manual Commit
=============

While the context manager is recommended, you can manually manage
transactions::

    from pygit2 import ReferenceTransaction

    txn = ReferenceTransaction(repo)
    try:
        txn.lock_ref('refs/heads/master')
        txn.set_target('refs/heads/master', new_oid, message='Update')
        txn.commit()
    finally:
        del txn  # Ensure transaction is freed

API Reference
=============

Repository Methods
------------------

.. automethod:: pygit2.Repository.transaction

The ReferenceTransaction Type
------------------------------

.. autoclass:: pygit2.ReferenceTransaction
   :members:
   :special-members: __enter__, __exit__

Usage Notes
===========

- Always lock a reference with :meth:`~ReferenceTransaction.lock_ref` before
  modifying it
- Transactions operate on reference names, not Reference objects
- Symbolic references can be updated with
  :meth:`~ReferenceTransaction.set_symbolic_target`
- References can be deleted with :meth:`~ReferenceTransaction.remove`
- The signature parameter defaults to the repository's configured identity

Thread Safety
=============

Transactions are thread-local and must be used from the thread that created
them. Attempting to use a transaction from a different thread raises
:exc:`RuntimeError`::

    # This is safe - each thread has its own transaction
    def thread1():
        with repo.transaction() as txn:
            txn.lock_ref('refs/heads/branch1')
            txn.set_target('refs/heads/branch1', oid1)

    def thread2():
        with repo.transaction() as txn:
            txn.lock_ref('refs/heads/branch2')
            txn.set_target('refs/heads/branch2', oid2)

    # Both threads can run concurrently without conflicts

Different threads can hold transactions simultaneously as long as they don't
attempt to lock the same references. If two threads try to acquire locks in
different orders, libgit2 will detect potential deadlocks and raise an error.
