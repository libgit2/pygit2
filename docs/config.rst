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

Parsing the values
===================

Instead of a string, a tuple of `(str,type)` can be used to look up a
key and parse it through the Git rules. E.g.

    config['core.bare',bool]

will return True if 'core.bare' is truthy.

Truty values are: 'true', 1, 'on' or 'yes'. Falsy values are: 'false',
0, 'off' and 'no'.

Available types are `bool` and `int`. Not specifying a type returns a
string.
