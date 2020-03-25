**********************************************************************
Backends
**********************************************************************

The use of custom backends for the git object database (odb) and reference
database (refdb) are supported by pygit2.

.. contents:: Contents
   :local:

The OdbBackend class
===================================

The OdbBackend class is subclassable and can be used to build a custom object
database.

.. autoclass:: pygit2.OdbBackend
   :members:

Built-in OdbBackend implementations
===================================

.. autoclass:: pygit2.OdbBackendLoose
   :members:

.. autoclass:: pygit2.OdbBackendPack
   :members:

The RefdbBackend class
===================================

The RefdbBackend class is subclassable and can be used to build a custom
reference database.

.. autoclass:: pygit2.RefdbBackend
   :members:

Built-in RefdbBackend implementations
=====================================

.. autoclass:: pygit2.RefdbFsBackend
   :members:
