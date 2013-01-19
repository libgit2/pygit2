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

The interface for a diff::

    Diff.changes          -- Dict of 'files' and 'hunks' for every change
    Diff.patch            -- a patch for every changeset
    Diff.merge            -- Merge two Diffs
