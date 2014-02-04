**********************************************************************
Configuration files
**********************************************************************

.. autoattribute:: pygit2.Repository.config


The Config type
================

.. automethod:: pygit2.Config.get_system_config
.. automethod:: pygit2.Config.get_global_config
.. automethod:: pygit2.Config.add_file
.. automethod:: pygit2.Config.get_multivar
.. automethod:: pygit2.Config.set_multivar

.. method:: Config.__iter__()

   The :class:`Config` class has an iterator which can be used to loop
   through all the entries in the configuration. Each element is a tuple
   containing the name and the value of each configuration variable. Be
   aware that this may return multiple versions of each entry if they are
   set multiple times in the configuration files.

The :class:`Config` Mapping interface.
