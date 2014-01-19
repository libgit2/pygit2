**********************************************************************
Remotes
**********************************************************************


.. autoattribute:: pygit2.Repository.remotes
.. automethod:: pygit2.Repository.create_remote


The Remote type
====================

.. autoattribute:: pygit2.Remote.name
.. autoattribute:: pygit2.Remote.url
.. autoattribute:: pygit2.Remote.refspec_count
.. automethod:: pygit2.Remote.get_push_refspecs
.. automethod:: pygit2.Remote.get_fetch_refspecs
.. automethod:: pygit2.Remote.set_push_refspecs
.. automethod:: pygit2.Remote.set_fetch_refspecs
.. automethod:: pygit2.Remote.get_refspec
.. automethod:: pygit2.Remote.fetch
.. automethod:: pygit2.Remote.push
.. automethod:: pygit2.Remote.save

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
