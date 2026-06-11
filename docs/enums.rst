**********************************************************************
Enums
**********************************************************************

pygit2 exposes libgit2 constants as Python enums in the :mod:`pygit2.enums`
module. They are preferred over the top-level ``GIT_*`` integer constants.

.. contents:: Contents
   :local:


Repository
==========

.. autoclass:: pygit2.enums.RepositoryInitFlag
   :members:

.. autoclass:: pygit2.enums.RepositoryInitMode
   :members:

.. autoclass:: pygit2.enums.RepositoryOpenFlag
   :members:

.. autoclass:: pygit2.enums.RepositoryState
   :members:


References and branches
=======================

.. autoclass:: pygit2.enums.BranchType
   :members:

.. autoclass:: pygit2.enums.ReferenceFilter
   :members:

.. autoclass:: pygit2.enums.ReferenceType
   :members:

.. autoclass:: pygit2.enums.ResetMode
   :members:

.. autoclass:: pygit2.enums.RevSpecFlag
   :members:


Objects
=======

.. autoclass:: pygit2.enums.ObjectType
   :members:

.. autoclass:: pygit2.enums.FileMode
   :members:


Diff
====

.. autoclass:: pygit2.enums.DeltaStatus
   :members:

.. autoclass:: pygit2.enums.DiffFind
   :members:

.. autoclass:: pygit2.enums.DiffFlag
   :members:

.. autoclass:: pygit2.enums.DiffOption
   :members:

.. autoclass:: pygit2.enums.DiffStatsFormat
   :members:


Status
======

.. autoclass:: pygit2.enums.FileStatus
   :members:


Checkout
========

.. autoclass:: pygit2.enums.CheckoutNotify
   :members:

.. autoclass:: pygit2.enums.CheckoutStrategy
   :members:


Merge
=====

.. autoclass:: pygit2.enums.MergeAnalysis
   :members:

.. autoclass:: pygit2.enums.MergeFavor
   :members:

.. autoclass:: pygit2.enums.MergeFileFlag
   :members:

.. autoclass:: pygit2.enums.MergeFlag
   :members:

.. autoclass:: pygit2.enums.MergePreference
   :members:


Blame
=====

.. autoclass:: pygit2.enums.BlameFlag
   :members:


Filters
=======

.. autoclass:: pygit2.enums.FilterMode
   :members:

.. autoclass:: pygit2.enums.FilterFlag
   :members:

.. autoclass:: pygit2.enums.BlobFilter
   :members:


Attributes
==========

.. autoclass:: pygit2.enums.AttrCheck
   :members:


Remotes
=======

.. autoclass:: pygit2.enums.CredentialType
   :members:

.. autoclass:: pygit2.enums.FetchPrune
   :members:


Submodules
==========

.. autoclass:: pygit2.enums.SubmoduleIgnore
   :members:

.. autoclass:: pygit2.enums.SubmoduleStatus
   :members:


Stash
=====

.. autoclass:: pygit2.enums.StashApplyProgress
   :members:


Revwalk
=======

.. autoclass:: pygit2.enums.SortMode
   :members:

.. autoclass:: pygit2.enums.DescribeStrategy
   :members:


Apply
=====

.. autoclass:: pygit2.enums.ApplyLocation
   :members:


Library
=======

.. autoclass:: pygit2.enums.Feature
   :members:

.. autoclass:: pygit2.enums.Option
   :members:

.. autoclass:: pygit2.enums.ConfigLevel
   :members:
