**********************************************************************
Configuration files
**********************************************************************

.. autoclass:: pygit2.repository.BaseRepository
   :members: config, config_snapshot


The Config types
================

.. autoclass:: pygit2.Config
   :members:
   :undoc-members:
   :special-members: __contains__, __delitem__, __getitem__, __init__, __iter__, __setitem__

.. autoclass:: pygit2.DefaultConfig
   :members: __enter__, __exit__
   :undoc-members:
   :special-members: __init__

.. autoclass:: pygit2.RepositoryConfig
   :members: __enter__, __exit__
   :undoc-members:
   :special-members: __init__


The ConfigEntry type
====================

.. autoclass:: pygit2.config.ConfigEntry
   :members: name, value, level
