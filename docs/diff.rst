**********************************************************************
Diff
**********************************************************************

.. contents::

A diff shows the changes between trees, an index or the working dir.

.. automethod:: pygit2.Repository.diff

Examples

.. code-block:: python

    # Changes between commits
    >>> t0 = revparse_single('HEAD')
    >>> t1 = revparse_single('HEAD^')
    >>> repo.diff(t0, t1)
    >>> t0.diff(t1)           # equivalent
    >>> repo.diff('HEAD', 'HEAD^') # equivalent

    # Get all patches for a diff
    >>> diff = repo.diff('HEAD^', 'HEAD~3')
    >>> patches = [p for p in diff]

    # Get the stats for a diff
    >>> diff = repo.diff('HEAD^', 'HEAD~3')
    >>> diff.stats

    # Diffing the empty tree
    >>> tree = revparse_single('HEAD').tree
    >>> tree.diff_to_tree()

    # Diff empty tree to a tree
    >>> tree = revparse_single('HEAD').tree
    >>> tree.diff_to_tree(swap=True)

The Diff type
====================

.. autoattribute:: pygit2.Diff.patch
.. method:: Diff.__iter__()

   Returns an iterator over the deltas/patches in this diff.

.. method:: Diff.__len__()

   Returns the number of deltas/patches in this diff.

.. automethod:: pygit2.Diff.merge
.. automethod:: pygit2.Diff.find_similar


The Patch type
====================

Attributes:

.. autoattribute:: pygit2.Patch.delta
.. autoattribute:: pygit2.Patch.hunks
.. autoattribute:: pygit2.Patch.line_stats


The DiffDelta type
====================

Attributes:

.. autoattribute:: pygit2.DiffDelta.old_file
.. autoattribute:: pygit2.DiffDelta.new_file
.. autoattribute:: pygit2.DiffDelta.status
.. autoattribute:: pygit2.DiffDelta.similarity

Getters:

.. autoattribute:: pygit2.DiffDelta.is_binary


The DiffFile type
====================

Attributes:

.. autoattribute:: pygit2.DiffFile.path
.. autoattribute:: pygit2.DiffFile.id
.. autoattribute:: pygit2.DiffFile.size
.. autoattribute:: pygit2.DiffFile.flags
.. autoattribute:: pygit2.DiffFile.mode


The DiffHunk type
====================

.. autoattribute:: pygit2.DiffHunk.old_start
.. autoattribute:: pygit2.DiffHunk.old_lines
.. autoattribute:: pygit2.DiffHunk.new_start
.. autoattribute:: pygit2.DiffHunk.new_lines
.. autoattribute:: pygit2.DiffHunk.lines

The DiffStats type
====================

.. autoattribute :: pygit2.DiffStats.insertions
.. autoattribute :: pygit2.DiffStats.deletions
.. autoattribute :: pygit2.DiffStats.files_changed
.. automethod :: pygit2.DiffStats.format

The DiffLine type
====================

.. autoattribute :: pygit2.DiffLine.origin
.. autoattribute :: pygit2.DiffLine.content
.. autoattribute :: pygit2.DiffLine.old_lineno
.. autoattribute :: pygit2.DiffLine.old_lineno
.. autoattribute :: pygit2.DiffLine.num_lines
