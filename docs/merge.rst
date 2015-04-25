**********************************************************************
Merge & Cherrypick
**********************************************************************

.. contents::

.. automethod:: pygit2.Repository.merge_base
.. automethod:: pygit2.Repository.merge
.. automethod:: pygit2.Repository.merge_analysis

The merge method
=================

The method does a merge over the current working copy.
It gets an Oid object as a parameter.

As its name says, it only does the merge, does not commit nor update the
branch reference in the case of a fastforward.

For the moment, the merge does not support options, it will perform the
merge with the default ones defined in GIT_MERGE_OPTS_INIT libgit2 constant.

Example::

    >>> other_branch_tip = '5ebeeebb320790caf276b9fc8b24546d63316533'
    >>> repo.merge(other_branch_tip)

You can now inspect the index file for conflicts and get back to the
user to resolve if there are. Once there are no conflicts left, you
can create a commit with these two parents.

   >>> user = repo.default_signature
   >>> tree = repo.index.write_tree()
   >>> new_commit = repo.create_commit('HEAD', user, user, tree,
                                       [repo.head.target, other_branch_tip])


Cherrypick
===================

.. automethod:: pygit2.Repository.cherrypick

Note that after a successful cherrypick you have to run
:py:meth:`.Repository.state_cleanup` in order to get the repository out
of cherrypicking mode.


Lower-level methods
===================

These methods allow more direct control over how to perform the
merging. They do not modify the working directory and return an
in-memory Index representing the result of the merge.

.. automethod:: pygit2.Repository.merge_commits
.. automethod:: pygit2.Repository.merge_trees
