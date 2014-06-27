**********************************************************************
General
**********************************************************************

.. contents:: Contents
   :local:


Top level constants and exceptions from the library.

Constants
=========

The following constants provide information about the version of the libgit2
library that has been built against. The version number has a
``MAJOR.MINOR.REVISION`` format.

.. py:data:: LIBGIT2_VER_MAJOR

   Integer value of the major version number. For example, for the version
   ``0.21.0``::

      >>> print LIBGIT2_VER_MAJOR
      0

.. py:data:: LIBGIT2_VER_MINOR

   Integer value of the minor version number. For example, for the version
   ``0.21.0``::

      >>> print LIBGIT2_VER_MINOR
      21

.. py:data:: LIBGIT2_VER_REVISION

   Integer value of the revision version number. For example, for the version
   ``0.20.0``::

      >>> print LIBGIT2_VER_REVISION
      0

.. py:data:: LIBGIT2_VERSION

   The libgit2 version number as a string::

      >>> print LIBGIT2_VERSION
      '0.21.0'

Errors
======

.. autoexception:: pygit2.GitError
   :members:
   :show-inheritance:
   :undoc-members:

