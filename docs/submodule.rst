**********************************************************************
The submodule
**********************************************************************

A submodule is a foreign repository that is embedded within a
dedicated subdirectory of the repositories tree.

.. automethod:: pygit2.Repository.lookup_submodule
.. automethod:: pygit2.Repository.listall_submodules

The Submodule type
====================

.. autoattribute:: pygit2.Submodule.name
.. autoattribute:: pygit2.Submodule.path
.. autoattribute:: pygit2.Submodule.url
.. automethod:: pygit2.Submodule.open
