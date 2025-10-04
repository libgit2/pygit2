# Copyright 2010-2025 The pygit2 contributors
#
# This file is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License, version 2,
# as published by the Free Software Foundation.
#
# In addition to the permissions in the GNU General Public License,
# the authors give you unlimited permission to link the compiled
# version of this file into combinations with other programs,
# and to distribute those combinations without any restriction
# coming from the use of this file.  (The General Public License
# restrictions do apply in other respects; for example, they cover
# modification of the file, and distribution when not linked into
# a combined executable.)
#
# This file is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING.  If not, write to
# the Free Software Foundation, 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301, USA.

import threading

import pytest

from pygit2 import GitError, Oid, Repository
from pygit2.transaction import ReferenceTransaction


def test_transaction_context_manager(testrepo: Repository) -> None:
    """Test basic transaction with context manager."""
    master_ref = testrepo.lookup_reference('refs/heads/master')
    assert str(master_ref.target) == '2be5719152d4f82c7302b1c0932d8e5f0a4a0e98'

    # Create a transaction and update a ref
    new_target = Oid(hex='5ebeeebb320790caf276b9fc8b24546d63316533')

    with testrepo.transaction() as txn:
        txn.lock_ref('refs/heads/master')
        txn.set_target('refs/heads/master', new_target, message='Test update')

    # Verify the update was applied
    master_ref = testrepo.lookup_reference('refs/heads/master')
    assert master_ref.target == new_target


def test_transaction_rollback_on_exception(testrepo: Repository) -> None:
    """Test that transaction rolls back when exception is raised."""
    master_ref = testrepo.lookup_reference('refs/heads/master')
    original_target = master_ref.target

    new_target = Oid(hex='5ebeeebb320790caf276b9fc8b24546d63316533')

    # Transaction should not commit if exception is raised
    with pytest.raises(RuntimeError):
        with testrepo.transaction() as txn:
            txn.lock_ref('refs/heads/master')
            txn.set_target('refs/heads/master', new_target, message='Test update')
            raise RuntimeError('Abort transaction')

    # Verify the update was NOT applied
    master_ref = testrepo.lookup_reference('refs/heads/master')
    assert master_ref.target == original_target


def test_transaction_multiple_refs(testrepo: Repository) -> None:
    """Test updating multiple refs in a single transaction."""
    master_ref = testrepo.lookup_reference('refs/heads/master')
    i18n_ref = testrepo.lookup_reference('refs/heads/i18n')

    new_master = Oid(hex='5ebeeebb320790caf276b9fc8b24546d63316533')
    new_i18n = Oid(hex='2be5719152d4f82c7302b1c0932d8e5f0a4a0e98')

    with testrepo.transaction() as txn:
        txn.lock_ref('refs/heads/master')
        txn.lock_ref('refs/heads/i18n')
        txn.set_target('refs/heads/master', new_master, message='Update master')
        txn.set_target('refs/heads/i18n', new_i18n, message='Update i18n')

    # Verify both updates were applied
    master_ref = testrepo.lookup_reference('refs/heads/master')
    i18n_ref = testrepo.lookup_reference('refs/heads/i18n')
    assert master_ref.target == new_master
    assert i18n_ref.target == new_i18n


def test_transaction_symbolic_ref(testrepo: Repository) -> None:
    """Test updating symbolic reference in transaction."""
    with testrepo.transaction() as txn:
        txn.lock_ref('HEAD')
        txn.set_symbolic_target('HEAD', 'refs/heads/i18n', message='Switch HEAD')

    head = testrepo.lookup_reference('HEAD')
    assert head.target == 'refs/heads/i18n'

    # Restore HEAD to master
    with testrepo.transaction() as txn:
        txn.lock_ref('HEAD')
        txn.set_symbolic_target('HEAD', 'refs/heads/master', message='Restore HEAD')


def test_transaction_remove_ref(testrepo: Repository) -> None:
    """Test removing a reference in a transaction."""
    # Create a test ref
    test_ref_name = 'refs/heads/test-transaction-delete'
    target = Oid(hex='5ebeeebb320790caf276b9fc8b24546d63316533')
    testrepo.create_reference(test_ref_name, target)

    # Verify it exists
    assert test_ref_name in testrepo.references

    # Remove it in a transaction
    with testrepo.transaction() as txn:
        txn.lock_ref(test_ref_name)
        txn.remove(test_ref_name)

    # Verify it's gone
    assert test_ref_name not in testrepo.references


def test_transaction_error_without_lock(testrepo: Repository) -> None:
    """Test that setting target without lock raises error."""
    new_target = Oid(hex='5ebeeebb320790caf276b9fc8b24546d63316533')

    with pytest.raises(KeyError, match='not locked'):
        with testrepo.transaction() as txn:
            # Try to set target without locking first
            txn.set_target('refs/heads/master', new_target, message='Should fail')


def test_transaction_isolated_across_threads(testrepo: Repository) -> None:
    """Test that transactions from different threads are isolated."""
    # Create two test refs
    ref1_name = 'refs/heads/thread-test-1'
    ref2_name = 'refs/heads/thread-test-2'
    target1 = Oid(hex='5ebeeebb320790caf276b9fc8b24546d63316533')
    target2 = Oid(hex='2be5719152d4f82c7302b1c0932d8e5f0a4a0e98')
    testrepo.create_reference(ref1_name, target1)
    testrepo.create_reference(ref2_name, target2)

    results = []
    errors = []
    thread1_ref1_locked = threading.Event()
    thread2_ref2_locked = threading.Event()

    def update_ref1() -> None:
        try:
            with testrepo.transaction() as txn:
                txn.lock_ref(ref1_name)
                thread1_ref1_locked.set()
                thread2_ref2_locked.wait(timeout=5)
                txn.set_target(ref1_name, target2, message='Thread 1 update')
            results.append('thread1_success')
        except Exception as e:
            errors.append(('thread1', str(e)))

    def update_ref2() -> None:
        try:
            with testrepo.transaction() as txn:
                txn.lock_ref(ref2_name)
                thread2_ref2_locked.set()
                thread1_ref1_locked.wait(timeout=5)
                txn.set_target(ref2_name, target1, message='Thread 2 update')
            results.append('thread2_success')
        except Exception as e:
            errors.append(('thread2', str(e)))

    thread1 = threading.Thread(target=update_ref1)
    thread2 = threading.Thread(target=update_ref2)

    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    # Both threads should succeed - transactions are isolated
    assert len(errors) == 0, f'Errors: {errors}'
    assert 'thread1_success' in results
    assert 'thread2_success' in results

    # Verify both updates were applied
    ref1 = testrepo.lookup_reference(ref1_name)
    ref2 = testrepo.lookup_reference(ref2_name)
    assert str(ref1.target) == '2be5719152d4f82c7302b1c0932d8e5f0a4a0e98'
    assert str(ref2.target) == '5ebeeebb320790caf276b9fc8b24546d63316533'


def test_transaction_deadlock_prevention(testrepo: Repository) -> None:
    """Test that acquiring locks in different order raises error instead of deadlock."""
    # Create two test refs
    ref1_name = 'refs/heads/deadlock-test-1'
    ref2_name = 'refs/heads/deadlock-test-2'
    target = Oid(hex='5ebeeebb320790caf276b9fc8b24546d63316533')
    testrepo.create_reference(ref1_name, target)
    testrepo.create_reference(ref2_name, target)

    thread1_ref1_locked = threading.Event()
    thread2_ref2_locked = threading.Event()
    errors = []
    successes = []

    def thread1_task() -> None:
        try:
            with testrepo.transaction() as txn:
                txn.lock_ref(ref1_name)
                thread1_ref1_locked.set()
                thread2_ref2_locked.wait(timeout=5)
                # this would cause a deadlock, so will throw (GitError)
                txn.lock_ref(ref2_name)
                # shouldn't get here
                successes.append('thread1')
        except Exception as e:
            errors.append(('thread1', type(e).__name__, str(e)))

    def thread2_task() -> None:
        try:
            with testrepo.transaction() as txn:
                txn.lock_ref(ref2_name)
                thread2_ref2_locked.set()
                thread1_ref1_locked.wait(timeout=5)
                # this would cause a deadlock, so will throw (GitError)
                txn.lock_ref(ref2_name)
                # shouldn't get here
                successes.append('thread2')
        except Exception as e:
            errors.append(('thread2', type(e).__name__, str(e)))

    thread1 = threading.Thread(target=thread1_task)
    thread2 = threading.Thread(target=thread2_task)

    thread1.start()
    thread2.start()
    thread1.join(timeout=5)
    thread2.join(timeout=5)

    # At least one thread should fail with an error (not deadlock)
    # If both threads are still alive, we have a deadlock
    assert not thread1.is_alive(), 'Thread 1 deadlocked'
    assert not thread2.is_alive(), 'Thread 2 deadlocked'

    # Both can't succeed.
    # libgit2 doesn't *wait* for locks, so it's possible for neither to succeed
    # if they both try to take the second lock at basically the same time.
    # The other possibility is that one thread throws, exits its transaction,
    # and the other thread is able to acquire the second lock.
    assert len(successes) <= 1 and len(errors) >= 1, (
        f'Successes: {successes}; errors: {errors}'
    )


def test_transaction_commit_from_wrong_thread(testrepo: Repository) -> None:
    """Test that committing a transaction from wrong thread raises error."""
    txn: ReferenceTransaction | None = None

    def create_transaction() -> None:
        nonlocal txn
        txn = testrepo.transaction().__enter__()
        ref_name = 'refs/heads/wrong-thread-test'
        target = Oid(hex='5ebeeebb320790caf276b9fc8b24546d63316533')
        testrepo.create_reference(ref_name, target)
        txn.lock_ref(ref_name)

    # Create transaction in thread 1
    thread = threading.Thread(target=create_transaction)
    thread.start()
    thread.join()

    assert txn is not None
    with pytest.raises(RuntimeError):
        # Try to commit from main thread (different from creator) doesn't cause libgit2 to crash,
        # it raises an exception instead
        txn.commit()


def test_transaction_nested_same_thread(testrepo: Repository) -> None:
    """Test that two concurrent transactions from same thread work with different refs."""
    # Create test refs
    ref1_name = 'refs/heads/nested-test-1'
    ref2_name = 'refs/heads/nested-test-2'
    target1 = Oid(hex='5ebeeebb320790caf276b9fc8b24546d63316533')
    target2 = Oid(hex='2be5719152d4f82c7302b1c0932d8e5f0a4a0e98')
    testrepo.create_reference(ref1_name, target1)
    testrepo.create_reference(ref2_name, target2)

    # Nested transactions should work as long as they don't conflict
    with testrepo.transaction() as txn1:
        txn1.lock_ref(ref1_name)

        with testrepo.transaction() as txn2:
            txn2.lock_ref(ref2_name)
            txn2.set_target(ref2_name, target1, message='Inner transaction')

        # Inner transaction committed, now update outer
        txn1.set_target(ref1_name, target2, message='Outer transaction')

    # Both updates should have been applied
    ref1 = testrepo.lookup_reference(ref1_name)
    ref2 = testrepo.lookup_reference(ref2_name)
    assert str(ref1.target) == '2be5719152d4f82c7302b1c0932d8e5f0a4a0e98'
    assert str(ref2.target) == '5ebeeebb320790caf276b9fc8b24546d63316533'


def test_transaction_nested_same_ref_conflict(testrepo: Repository) -> None:
    """Test that nested transactions fail when trying to lock the same ref."""
    ref_name = 'refs/heads/nested-conflict-test'
    target = Oid(hex='5ebeeebb320790caf276b9fc8b24546d63316533')
    new_target = Oid(hex='2be5719152d4f82c7302b1c0932d8e5f0a4a0e98')
    testrepo.create_reference(ref_name, target)

    with testrepo.transaction() as txn1:
        txn1.lock_ref(ref_name)

        # Inner transaction should fail to lock the same ref
        with pytest.raises(GitError):
            with testrepo.transaction() as txn2:
                txn2.lock_ref(ref_name)

        # Outer transaction should still be able to complete
        txn1.set_target(ref_name, new_target, message='Outer transaction')

    # Outer transaction's update should have been applied
    ref = testrepo.lookup_reference(ref_name)
    assert ref.target == new_target
