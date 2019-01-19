**********************************************************************
General
**********************************************************************

.. contents:: Contents
   :local:


Top level constants and exceptions from the library.

Version
=========

The following constants provide information about the version of the libgit2
library that has been built against. The version number has a
``MAJOR.MINOR.REVISION`` format.

.. py:data:: LIBGIT2_VER_MAJOR

   Integer value of the major version number. For example, for the version
   ``0.26.0``::

      >>> print(pygit2.LIBGIT2_VER_MAJOR)
      0

.. py:data:: LIBGIT2_VER_MINOR

   Integer value of the minor version number. For example, for the version
   ``0.26.0``::

      >>> print(pygit2.LIBGIT2_VER_MINOR)
      26

.. py:data:: LIBGIT2_VER_REVISION

   Integer value of the revision version number. For example, for the version
   ``0.26.0``::

      >>> print(pygit2.LIBGIT2_VER_REVISION)
      0

.. py:data:: LIBGIT2_VER

   Tuple value of the revision version numbers. For example, for the version
   ``0.26.0``::

      >>> print(pygit2.LIBGIT2_VER)
      (0, 26, 0)

.. py:data:: LIBGIT2_VERSION

   The libgit2 version number as a string::

      >>> print(pygit2.LIBGIT2_VERSION)
      '0.26.0'

Options
=========

.. autofunction:: pygit2.option

Exceptions
==========

.. autoexception:: pygit2.GitError
   :members:
   :show-inheritance:
   :undoc-members:

.. autoexception:: pygit2.AlreadyExistsError
   :members:
   :show-inheritance:
   :undoc-members:

Exception when trying to create an object (reference, etc) that already exists.

.. autoexception:: pygit2.InvalidSpecError
   :members:
   :show-inheritance:
   :undoc-members:

Exception when an input specification such as a reference name is invalid.
