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

    # Diffing the empty tree
    >>> tree = revparse_single('HEAD').tree
    >>> tree.diff_to_tree()

    # Diff empty tree to a tree
    >>> tree = revparse_single('HEAD').tree
    >>> tree.diff_to_tree(swap=True)

The Diff type
====================

.. autoattribute:: pygit2.Diff.patch
.. method:: Diff.__len__()

   Returns the number of deltas/patches in this diff.

.. automethod:: pygit2.Diff.merge
.. automethod:: pygit2.Diff.find_similar


The Patch type
====================

Attributes:

.. autoattribute:: pygit2.Patch.old_file_path
.. autoattribute:: pygit2.Patch.new_file_path
.. autoattribute:: pygit2.Patch.old_id
.. autoattribute:: pygit2.Patch.new_id
.. autoattribute:: pygit2.Patch.status
.. autoattribute:: pygit2.Patch.similarity
.. autoattribute:: pygit2.Patch.hunks
.. autoattribute:: pygit2.Patch.additions
.. autoattribute:: pygit2.Patch.deletions

Getters:

.. autoattribute:: pygit2.Patch.is_binary


The Hunk type
====================

.. autoattribute:: pygit2.Hunk.old_start
.. autoattribute:: pygit2.Hunk.old_lines
.. autoattribute:: pygit2.Hunk.new_start
.. autoattribute:: pygit2.Hunk.new_lines
.. autoattribute:: pygit2.Hunk.lines
