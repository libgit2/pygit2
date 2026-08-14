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
   ``1.9.7``::

      >>> print(pygit2.LIBGIT2_VER_MAJOR)
      1

.. py:data:: LIBGIT2_VER_MINOR

   Integer value of the minor version number. For example, for the version
   ``1.9.7``::

      >>> print(pygit2.LIBGIT2_VER_MINOR)
      9

.. py:data:: LIBGIT2_VER_REVISION

   Integer value of the revision version number. For example, for the version
   ``1.9.7``::

      >>> print(pygit2.LIBGIT2_VER_REVISION)
      6

.. py:data:: LIBGIT2_VER

   Tuple value of the revision version numbers. For example, for the version
   ``1.9.7``::

      >>> print(pygit2.LIBGIT2_VER)
      (1, 9, 6)

.. py:data:: LIBGIT2_VERSION

   The libgit2 version number as a string::

      >>> print(pygit2.LIBGIT2_VERSION)
      '1.9.7'

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

.. autoexception:: pygit2.InvalidError
   :members:
   :show-inheritance:
   :undoc-members:

Exception when an operation or input is invalid.

.. autoexception:: pygit2.NotFoundError
   :members:
   :show-inheritance:
   :undoc-members:

Exception when a requested object could not be found.

.. autoexception:: pygit2.AmbiguousError
   :members:
   :show-inheritance:
   :undoc-members:

Exception when more than one object matches.

.. autoexception:: pygit2.AuthError
   :members:
   :show-inheritance:
   :undoc-members:

Exception when an authentication error occurs.

.. autoexception:: pygit2.CertificateError
   :members:
   :show-inheritance:
   :undoc-members:

Exception when a server certificate is invalid.

.. autoexception:: pygit2.Passthrough
   :members:
   :show-inheritance:
   :undoc-members:

Exception that can be raised from a callback to tell libgit2 to behave as if
that callback had not been set. See :doc:`callbacks` for details.

Error mapping
=============

The following table shows how libgit2 error codes map to pygit2 exceptions.
The new exception classes inherit from :py:exc:`pygit2.GitError` and, where
noted, from a Python built-in exception for backward compatibility.

.. list-table::
   :header-rows: 1
   :widths: 35 35 30

   * - pygit2 exception
     - libgit2 code / class
     - Built-in base

   * - :py:exc:`AlreadyExistsError`
     - ``GIT_EEXISTS``
     - ``ValueError``

   * - :py:exc:`InvalidSpecError`
     - ``GIT_EINVALIDSPEC``
     - ``ValueError``

   * - :py:exc:`InvalidError`
     - ``GIT_EINVALID``, ``GIT_ERROR_INVALID``
     - ``ValueError``

   * - :py:exc:`NotFoundError`
     - ``GIT_ENOTFOUND``
     - ``KeyError``

   * - :py:exc:`AmbiguousError`
     - ``GIT_EAMBIGUOUS``
     - ``ValueError``

   * - :py:exc:`AuthError`
     - ``GIT_EAUTH``
     -

   * - :py:exc:`CertificateError`
     - ``GIT_ECERTIFICATE``
     -

   * - :py:exc:`GitError`
     - generic / other errors
     -
