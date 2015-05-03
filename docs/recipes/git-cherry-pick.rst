**********************************************************************
git-cherry-pick
**********************************************************************

The convenient way to cherry-pick a commit is to use
:py:meth:`.Repository.cherrypick()`. It is limited to cherry-picking with a
working copy and on-disk index.

.. code-block:: bash

    $> cd /path/to/repo
    $> git checkout basket
    $> git cherry-pick 9e044d03c

.. code-block:: python

    repo = pygit2.Repository('/path/to/repo')
    repo.checkout('basket')

    cherry_id = pygit2.Oid('9e044d03c')
    repo.cherrypick(cherry_id)

    if repo.index.conflicts is None:
        tree_id = repo.index.write_tree()

        cherry    = repo.get(cherry_id)
        committer = pygit2.Signature('Archimedes', 'archy@jpl-classics.org')

        repo.create_commit(basket.name, cherry.author, committer,
                           cherry.message, tree_id, [basket.target])
        del basket # outdated, prevent from accidentally using it

        repo.state_cleanup()


----------------------------------------------------------------------
Cherry-picking a commit without a working copy
----------------------------------------------------------------------

This way of cherry-picking gives you more control over the process and works
on bare repositories as well as repositories with a working copy.
:py:meth:`~.Repository.merge_trees()` can also be used for other tasks, for
example `three-argument rebases`_.

.. _`three-argument rebases`: https://www.kernel.org/pub/software/scm/git/docs/git-rebase.html

.. code-block:: python

    repo = pygit2.Repository('/path/to/repo')

    cherry = repo.revparse_single('9e044d03c')
    basket = repo.lookup_branch('basket')

    base      = repo.merge_base(cherry.oid, basket.target)
    base_tree = cherry.parents[0].tree

    index = repo.merge_trees(base_tree, basket, cherry)
    tree_id = index.write_tree(repo)

    author    = cherry.author
    committer = pygit2.Signature('Archimedes', 'archy@jpl-classics.org')

    repo.create_commit(basket.name, author, committer, cherry.message,
                       tree_id, [basket.target])
    del None # outdated, prevent from accidentally using it

----------------------------------------------------------------------
References
----------------------------------------------------------------------

- git-cherry-pick_.

.. _git-cherry-pick: https://www.kernel.org/pub/software/scm/git/docs/git-cherry-pick.html
