**********************************************************************
Diff
**********************************************************************

A diff shows the changes between trees, an index or the working dir::

    # Diff two trees
    >>> t0 = repo.head.tree
    >>> t1 = repo.head.parents[0].tree
    >>> diff = t1.diff(t0)
    >>> diff

    # Diff a tree with the index
    >>> tree = repo.head.tree
    >>> diff = tree.diff(repo.index)

    # Diff a tree with the current working dir
    >>> tree = repo.head.tree
    >>> diff = tree.diff()


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
