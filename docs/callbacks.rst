**********************************************************************
Callbacks
**********************************************************************

Many pygit2 operations accept callback objects. The callbacks module provides
base classes that you can subclass to customize behavior such as progress
reporting, credential lookup, or checkout notifications.

.. contents:: Contents
   :local:


Remote callbacks
================

.. autoclass:: pygit2.RemoteCallbacks
   :members:


Checkout callbacks
==================

.. autoclass:: pygit2.CheckoutCallbacks
   :members:


Stash apply callbacks
=====================

.. autoclass:: pygit2.StashApplyCallbacks
   :members:


Passthrough
===========

Callbacks may raise :exc:`pygit2.Passthrough` to tell libgit2 to behave as if
the callback had not been set. This is useful when a callback only wants to
handle some cases and let libgit2 use its default behavior for the rest. See
:doc:`general` for the exception reference.
