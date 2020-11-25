**********************************************************************
Submodules
**********************************************************************

A submodule is a foreign repository that is embedded within a
dedicated subdirectory of the repositories tree.

.. autoclass:: pygit2.Repository
   :members: add_submodule, init_submodules, listall_submodules, lookup_submodule, update_submodules
   :noindex:


The Submodule type
====================

.. automethod:: pygit2.Submodule.open

.. autoattribute:: pygit2.Submodule.name
.. autoattribute:: pygit2.Submodule.path
.. autoattribute:: pygit2.Submodule.url
.. autoattribute:: pygit2.Submodule.branch
.. autoattribute:: pygit2.Submodule.head_id
