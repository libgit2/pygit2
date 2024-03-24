**********************************************************************
Submodules
**********************************************************************

A submodule is a foreign repository that is embedded within a
dedicated subdirectory of the repositories tree.

.. autoclass:: pygit2.Repository
   :members: listall_submodules

   .. py:attribute:: Repository.submodules

      The collection of submodules, an instance of
      :py:class:`pygit2.submodules.SubmoduleCollection`

.. autoclass:: pygit2.submodules.SubmoduleCollection
   :members:


The Submodule type
====================

.. autoclass:: pygit2.Submodule
   :members:
