**********************************************************************
Rebase
**********************************************************************

.. contents::

.. automethod:: pygit2.Repository.rebase_init
.. automethod:: pygit2.Repository.rebase_open

The Rebase type
====================

.. autoclass:: pygit2.Rebase
   :members:
   :special-members: __len__, __getitem__, __next__

.. autoclass:: pygit2.RebaseOperation
   :members:

Example
=======

Rebase the current branch onto its upstream::

    >>> committer = repo.default_signature
    >>> rebase = repo.rebase_init(upstream=repo.branches['origin/master'])
    >>> for operation in rebase:
    ...     # If repo.index.conflicts is not None at this point, the
    ...     # operation left conflicts in the index and conflict markers
    ...     # in the working directory.  Resolve them, stage each
    ...     # resolution with repo.index.add(path), and only then commit.
    ...     rebase.commit(committer=committer)
    >>> rebase.finish(committer)

Use ``abort()`` instead of ``finish()`` to reset the repository and the
working directory to their state before the rebase began.

``commit()`` returns ``None`` for a patch that turns out to be already
present upstream; like ``git rebase``, simply move on to the next
operation.

With ``inmemory=True`` the rebase does not touch HEAD, the repository
state, or the working directory; each step's result is available as
``rebase.inmemory_index`` and updating the branch reference afterwards is
the caller's responsibility.

Working with rebase operations
==============================

Iterating over a ``Rebase`` yields a :py:class:`~pygit2.RebaseOperation`
describing each step.  ``len()`` and indexing expose the same operations
up front, without advancing the rebase, so the plan can be inspected
before applying it::

    >>> rebase = repo.rebase_init(upstream=repo.branches['origin/master'])
    >>> for i in range(len(rebase)):
    ...     print(rebase[i])
    <pygit2.RebaseOperation PICK 4a3fe06...>
    <pygit2.RebaseOperation PICK 8ae4a25...>

A rebase started with ``rebase_init()`` replays the non-merge commits
in ``upstream..branch``; merge commits are skipped, linearizing the
history, just like plain ``git rebase`` (libgit2 has no equivalent of
``--rebase-merges``).  Every operation's ``type`` is therefore
``RebaseOperationType.PICK``, ``id`` names the original commit being
replayed, and ``exec`` is ``None``.  The remaining
``RebaseOperationType`` values mirror the verbs of git's interactive
rebase, which libgit2 does not implement (as of 1.9): they are declared
for completeness but never produced.  Looking the original commit up is
useful for progress reporting or for reusing its metadata::

    >>> from pygit2.enums import RebaseOperationType
    >>> committer = repo.default_signature
    >>> for operation in rebase:
    ...     assert operation.type == RebaseOperationType.PICK
    ...     original = repo[operation.id]
    ...     step, total = rebase.current_index + 1, len(rebase)
    ...     print(f'[{step}/{total}] picking {original.short_id}:',
    ...           original.message.strip())
    ...     rebase.commit(committer=committer)
    [1/2] picking 4a3fe06: Add feature
    [2/2] picking 8ae4a25: Fix tests
    >>> rebase.finish(committer)
