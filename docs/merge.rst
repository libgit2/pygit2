**********************************************************************
Merge
**********************************************************************

.. contents::

.. automethod:: pygit2.Repository.merge_base
.. automethod:: pygit2.Repository.merge

The merge method
=================

The method does a merge over the current working copy.
It gets an Oid object as a parameter and returns a MergeResult object.

As its name says, it only does the merge, does not commit nor update the
branch reference in the case of a fastforward.

For the moment, the merge does not support options, it will perform the
merge with the default ones defined in GIT_MERGE_OPTS_INIT libgit2 constant.

Example::

    >>> branch_head_hex = '5ebeeebb320790caf276b9fc8b24546d63316533'
    >>> branch_id = self.repo.get(branch_head_hex).id
    >>> merge_result = self.repo.merge(branch_id)

The MergeResult object
======================

Represents the result of a merge and contains these fields:

- is_uptodate: bool, if there wasn't any merge because the repo was already
  up to date
- is_fastforward: bool, whether the merge was fastforward or not
- fastforward_id: Oid, in the case it was a fastforward, this is the
  forwarded id.
