**********************************************************************
Git objects
**********************************************************************

.. contents:: Contents
   :local:

In the first place Git is a key-value storage system. The keys are called
OIDs, for Object id, and the  values stored are called Objects.

Oids
=================

The oid is the `SHA-1 <http://en.wikipedia.org/wiki/SHA-1>`_ hash of an
object. It is 20 bytes long:

- When we represent an oid as a 20 bytes Python string, we say it is a raw
  oid.

- When we represent an oid as a 40 chars Python string, we sayt it is a hex
  oid.

However, most of the time we will use the Oid type. We can explicetly create
an Oid object from its raw or hexadecimal form::

  >>> hex = "cff3ceaefc955f0dbe1957017db181bc49913781"
  >>> oid1 = Oid(hex=hex)

  >>> from binascii import unhexlify
  >>> raw = unhexlify(hex)
  >>> oid2 = Oid(raw=raw)

  >>> print oid1 == oid2
  True

And in the opposite direction, we can get the raw or hexadecimal form from
an Oid object:

.. autoattribute:: pygit2.Oid.raw
.. autoattribute:: pygit2.Oid.hex

The Oid type supports:

- rich comparisons, not just for equality, also: lesser-than, lesser-or-equal,
  etc.

- hashing, so Oid objects can be used as keys in a dictionary


Python 2 and Python 3
---------------------

There is a difference on how the library handles hex oids, depending on
whether we are using Python 2 or 3.

- In Python 2, we can represent an hexadecimal oid using a bytes string
  (``str``) or a text string (``unicode``)

- In Python 3, hexadecimal oids can only be represented using unicode
  strings.


Objects
=================

There are four types (commits, trees, blobs and tags), for each type pygit2
has a Python class::

    >>> # Show commits and trees
    >>> commit
    <pygit2.Commit object at 0x7f9d2f3000b0>
    >>> commit.tree
    <pygit2.Tree object at 0x7f9d2f3000f0>

These four classes (``Commit``, ``Tree``, ``Blob`` and ``Tag``) inherit from
the ``Object`` base class, which provides shared behaviour. A Git object is
identified by a unique *object id*, which is a binary byte string; this is
often represented as an hexadecimal text string::

    >>> commit.oid
    b'x\xde\xb5W\x8d\x01<\xdb\xdf\x08o\xa1\xd1\xa3\xe7\xd9\x82\xe8\x88\x8f'
    >>> commit.hex
    '78deb5578d013cdbdf086fa1d1a3e7d982e8888f'

The API of pygit2 accepts both the raw object id and its hexadecimal
representation, the difference is done based on its type (a byte or a text
string).

Objects can not be modified once they have been created.

This is the common interface for all Git objects:

.. autoattribute:: pygit2.Object.oid
.. autoattribute:: pygit2.Object.hex
.. autoattribute:: pygit2.Object.type
.. automethod:: pygit2.Object.read_raw


Commits
=================

A commit is a snapshot of the working dir with meta informations like author,
committer and others.

.. autoattribute:: pygit2.Commit.author
.. autoattribute:: pygit2.Commit.committer
.. autoattribute:: pygit2.Commit.message
.. autoattribute:: pygit2.Commit.message_encoding
.. autoattribute:: pygit2.Commit.tree
.. autoattribute:: pygit2.Commit.parents
.. autoattribute:: pygit2.Commit.commit_time
.. autoattribute:: pygit2.Commit.commit_time_offset


Signatures
-------------

The author and committer attributes of commit objects are ``Signature``
objects::

    >>> commit.author
    <pygit2.Signature object at 0x7f75e9b1f5f8>

.. autoattribute:: pygit2.Signature.name
.. autoattribute:: pygit2.Signature.email
.. autoattribute:: pygit2.Signature.time
.. autoattribute:: pygit2.Signature.offset


Creating commits
----------------

.. automethod:: pygit2.Repository.create_commit

Commits can be created by calling the ``create_commit`` method of the
repository with the following parameters::

    >>> author = Signature('Alice Author', 'alice@authors.tld')
    >>> committer = Signature('Cecil Committer', 'cecil@committers.tld')
    >>> tree = repo.TreeBuilder().write()
    >>> repo.create_commit(
    ... 'refs/heads/master', # the name of the reference to update
    ... author, committer, 'one line commit message\n\ndetailed commit message',
    ... tree, # binary string representing the tree object ID
    ... [] # list of binary strings representing parents of the new commit
    ... )
    '#\xe4<u\xfe\xd6\x17\xa0\xe6\xa2\x8b\xb6\xdc35$\xcf-\x8b~'


Trees
=================

A tree is a sorted collection of tree entries. It is similar to a folder or
directory in a file system. Each entry points to another tree or a blob.  A
tree can be iterated, and partially implements the sequence and mapping
interfaces::

    >>> # Number of entries
    >>> tree = commit.tree
    >>> len(tree)
    6

    >>> # Iteration
    >>> for entry in tree:
    ...     print(entry.hex, entry.name)
    ...
    7151ca7cd3e59f3eab19c485cfbf3cb30928d7fa .gitignore
    c36f4cf1e38ec1bb9d9ad146ed572b89ecfc9f18 COPYING
    32b30b90b062f66957d6790c3c155c289c34424e README.md
    c87dae4094b3a6d10e08bc6c5ef1f55a7e448659 pygit2.c
    85a67270a49ef16cdd3d328f06a3e4b459f09b27 setup.py
    3d8985bbec338eb4d47c5b01b863ee89d044bd53 test

    >>> # Get an entry by name
    >>> entry = tree['pygit2.c']
    >>> entry
    <pygit2.TreeEntry object at 0xcc10f0>

    >>> # Get the object the entry points to
    >>> blob = repo[entry.oid]
    >>> blob
    <pygit2.Blob object at 0xcc12d0>

.. automethod:: pygit2.Tree.diff

.. autoattribute:: pygit2.TreeEntry.name
.. autoattribute:: pygit2.TreeEntry.oid
.. autoattribute:: pygit2.TreeEntry.hex
.. autoattribute:: pygit2.TreeEntry.filemode


Creating trees
--------------------

.. automethod:: pygit2.Repository.TreeBuilder

.. automethod:: pygit2.TreeBuilder.insert
.. automethod:: pygit2.TreeBuilder.remove
.. automethod:: pygit2.TreeBuilder.clear
.. automethod:: pygit2.TreeBuilder.write


Blobs
=================

A blob is equivalent to a file in a file system.::

    >>> # create a blob out of memory
    >>> oid  = repo.create_blob('foo bar')
    >>> blob = repo[oid]
    >>> blob.data
    'foo bar'
    >>> oid
    '\x96\xc9\x06um{\x91\xc4S"a|\x92\x95\xe4\xa8\rR\xd1\xc5'

.. autoattribute:: pygit2.Blob.data
.. autoattribute:: pygit2.Blob.size

Creating blobs
--------------------

.. automethod:: pygit2.Repository.create_blob
.. automethod:: pygit2.Repository.create_blob_fromworkdir
.. automethod:: pygit2.Repository.create_blob_fromdisk

Tags
=================

A tag is a static label for a commit. See references for more information.

.. autoattribute:: pygit2.Tag.name
.. autoattribute:: pygit2.Tag.target
.. autoattribute:: pygit2.Tag.tagger
.. autoattribute:: pygit2.Tag.message


Creating tags
--------------------

.. automethod:: pygit2.Repository.create_tag
