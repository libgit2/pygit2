**********************************************************************
Remotes
**********************************************************************


.. autoattribute:: pygit2.Repository.remotes
.. automethod:: pygit2.Repository.create_remote


The Remote type
====================

.. autoattribute:: pygit2.Remote.name
.. autoattribute:: pygit2.Remote.url
.. autoattribute:: pygit2.Remote.push_url
.. autoattribute:: pygit2.Remote.refspec_count
.. autoattribute:: pygit2.Remote.push_refspecs
.. autoattribute:: pygit2.Remote.fetch_refspecs
.. automethod:: pygit2.Remote.progress
.. automethod:: pygit2.Remote.transfer_progress
.. automethod:: pygit2.Remote.update_tips
.. automethod:: pygit2.Remote.get_refspec
.. automethod:: pygit2.Remote.fetch
.. automethod:: pygit2.Remote.push
.. automethod:: pygit2.Remote.save
.. automethod:: pygit2.Remote.add_push
.. automethod:: pygit2.Remote.add_fetch

The TransferProgress type
===========================

This class contains the data which is available to us during a fetch.

.. autoattribute:: pygit2.TransferProgress.total_objects
.. autoattribute:: pygit2.TransferProgress.indexed_objects
.. autoattribute:: pygit2.TransferProgress.received_objects
.. autoattribute:: pygit2.TransferProgress.local_objects
.. autoattribute:: pygit2.TransferProgress.total_deltas
.. autoattribute:: pygit2.TransferProgress.indexed_deltas
.. autoattribute:: pygit2.TransferProgress.received_bytes


The Refspec type
===================

.. autoattribute:: pygit2.Refspec.direction
.. autoattribute:: pygit2.Refspec.src
.. autoattribute:: pygit2.Refspec.dst
.. autoattribute:: pygit2.Refspec.force
.. autoattribute:: pygit2.Refspec.string
.. automethod:: pygit2.Refspec.src_matches
.. automethod:: pygit2.Refspec.dst_matches
.. automethod:: pygit2.Refspec.transform
.. automethod:: pygit2.Refspec.rtransform

Credentials
================

.. automethod:: pygit2.Remote.credentials

There are two types of credentials: username/password and SSH key
pairs. Both :py:class:`pygit2.UserPass` and :py:class:`pygit2.Keypair`
are callable objects, with the appropriate signature for the
credentials callback. They will ignore all the arguments and return
themselves. This is useful for scripts where the credentials are known
ahead of time. More complete interfaces would want to look up in their
keychain or ask the user for the data to use in the credentials.

.. autoclass:: pygit2.UserPass
.. autoclass:: pygit2.Keypair
