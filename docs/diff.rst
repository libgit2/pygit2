**********************************************************************
Diff
**********************************************************************

A diff shows the changes between trees, an index or the working dir::

    # Changes in the working tree not yet staged for the next commit
    >>> repo.diff()

    # Changes between the index and your last commit
    >>> self.diff(cached=True)

    # Changes in the working tree since your last commit
    >>> self.diff('HEAD')

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
.. automethod:: pygit2.Diff.merge
.. automethod:: pygit2.Diff.find_similar


The Patch type
====================

.. autoattribute:: pygit2.Patch.old_file_path
.. autoattribute:: pygit2.Patch.new_file_path
.. autoattribute:: pygit2.Patch.old_oid
.. autoattribute:: pygit2.Patch.new_oid
.. autoattribute:: pygit2.Patch.status
.. autoattribute:: pygit2.Patch.similarity
.. autoattribute:: pygit2.Patch.hunks


The Hunk type
====================

.. autoattribute:: pygit2.Hunk.old_start
.. autoattribute:: pygit2.Hunk.old_lines
.. autoattribute:: pygit2.Hunk.new_start
.. autoattribute:: pygit2.Hunk.new_lines
.. autoattribute:: pygit2.Hunk.lines
