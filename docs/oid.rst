**********************************************************************
Object IDs
**********************************************************************

In the first place Git is a key-value storage system. The keys are called
OIDs, for Object ID, and the  values stored are called Objects.

.. contents:: Contents
   :local:


The three forms of an object id
===============================

The oid is the `SHA-1 <http://en.wikipedia.org/wiki/SHA-1>`_ hash of an
object. It is 20 bytes long.

These are the three forms of an oid in pygit2:

Raw oid
  A raw oid is represented as a Python byte string of 20 bytes length.
  This form can only be used to create an Oid object.

Hex oid
  A hex oid is represented as a Python string of 40 hexadecimal chars.  This
  form can be used to create Oid objects, just like raw oids. Also, the pygit2
  API directly accepts hex oids everywhere.

  .. note::

     In Python 3 hexadecimal oids are represented using the ``str`` type.
     In Python 2 both ``str`` and ``unicode`` are accepted.

Oid object
  An ``Oid`` object can be built from the raw or hexadecimal representations
  (see below). The pygit2 API always returns, and accepts, ``Oid`` objects.

  This is the preferred way to represent an Oid, with the hexadecimal form
  being used for interaction with the user.


The Oid type
============

.. c:type:: pygit2.Oid(raw=None, hex=None)

   The constructor expects either a raw or a hex oid, but not both.

   An Oid object is created from the hexadecimal form this way::

     >>> from pygit2 import Oid

     >>> hex = "cff3ceaefc955f0dbe1957017db181bc49913781"
     >>> oid1 = Oid(hex=hex)

   An Oid object is created from the raw form this way::

     >>> from binascii import unhexlify
     >>> from pygit2 import Oid

     >>> raw = unhexlify("cff3ceaefc955f0dbe1957017db181bc49913781")
     >>> oid2 = Oid(raw=raw)

And the other way around, from an Oid object we can get the hexadecimal and raw
forms. You can use the built-in `str()` (or `unicode()` in python 2) to get the
hexadecimal representation of the Oid.

.. method:: Oid.__str__()
.. autoattribute:: pygit2.Oid.raw

The Oid type supports:

- rich comparisons, not just for equality, also: lesser-than, lesser-or-equal,
  etc.

- hashing, so Oid objects can be used as keys in a dictionary.


Constants
=========

.. py:data:: GIT_OID_RAWSZ
.. py:data:: GIT_OID_HEXSZ
.. py:data:: GIT_OID_HEX_ZERO
.. py:data:: GIT_OID_MINPREFIXLEN
