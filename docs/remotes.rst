**********************************************************************
Remotes
**********************************************************************

.. py:attribute:: Repository.remotes

   The collection of configured remotes, an instance of
   :py:class:`pygit2.remotes.RemoteCollection`

The remote collection
==========================

.. autoclass:: pygit2.remotes.RemoteCollection
   :members:

The Remote type
====================

.. autoclass:: pygit2.Remote
   :members:

The RemoteCallbacks type
========================

See :doc:`callbacks` for the full reference. The following autoclass is only
included here for discoverability.

.. autoclass:: pygit2.RemoteCallbacks
   :noindex:
   :members:

The TransferProgress type
===========================

This class contains the data which is available to us during a fetch.

.. autoclass:: pygit2.remotes.TransferProgress
   :members:

The RemoteHead type
===================

Description of a reference advertised by a remote server, returned by
:meth:`pygit2.Remote.list_heads`.

.. autoclass:: pygit2.remotes.RemoteHead
   :members:

The PushUpdate type
===================

Represents an update which will be performed on the remote during push.
Passed to :meth:`pygit2.RemoteCallbacks.push_negotiation`.

.. autoclass:: pygit2.remotes.PushUpdate
   :members:

The Refspec type
===================

Refspecs objects are not constructed directly, but returned by
:meth:`pygit2.Remote.get_refspec`.  To create a new a refspec on a Remote, use
:meth:`pygit2.Remote.add_fetch` or :meth:`pygit2.Remote.add_push`.

.. autoclass:: pygit2.refspec.Refspec
   :members:

Credentials
================

There are several types of credentials. All of them are callable objects, with
the appropriate signature for the credentials callback.

They will ignore all the arguments and return themselves. This is useful for
scripts where the credentials are known ahead of time. More complete interfaces
would want to look up in their keychain or ask the user for the data to use in
the credentials.

.. autoclass:: pygit2.Username
.. autoclass:: pygit2.UserPass
.. autoclass:: pygit2.Keypair
.. autoclass:: pygit2.KeypairFromAgent
.. autoclass:: pygit2.KeypairFromMemory
