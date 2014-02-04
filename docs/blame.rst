**********************************************************************
Blame
**********************************************************************

.. contents::


.. automethod:: pygit2.Repository.blame


The Blame type
==============

.. automethod:: pygit2.Blame.for_line
.. method:: Blame.__iter__()
.. method:: Blame.__len__()
.. method:: Blame.__getitem__(n)


The BlameHunk type
==================

Attributes:

.. autoattribute:: pygit2.BlameHunk.lines_in_hunk
.. autoattribute:: pygit2.BlameHunk.final_commit_id
.. autoattribute:: pygit2.BlameHunk.final_start_line_number
.. autoattribute:: pygit2.BlameHunk.orig_commit_id
.. autoattribute:: pygit2.BlameHunk.orig_path
.. autoattribute:: pygit2.BlameHunk.orig_start_line_number
.. autoattribute:: pygit2.BlameHunk.boundary

Getters:

.. autoattribute:: pygit2.BlameHunk.final_committer
.. autoattribute:: pygit2.BlameHunk.orig_committer


Constants
=========

.. py:data:: GIT_BLAME_NORMAL
.. py:data:: GIT_BLAME_TRACK_COPIES_SAME_FILE
.. py:data:: GIT_BLAME_TRACK_COPIES_SAME_COMMIT_MOVES
.. py:data:: GIT_BLAME_TRACK_COPIES_SAME_COMMIT_COPIES
.. py:data:: GIT_BLAME_TRACK_COPIES_ANY_COMMIT_COPIES
