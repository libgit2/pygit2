**********************************************************************
Git Objects
**********************************************************************

There are four types of Git objects: blobs, trees, commits and tags. For each
one pygit2 has a type, and all four types inherit from the base ``Object``
type.


.. contents:: Contents
   :local:


Object lookup
=================

In the previous chapter we learnt about Object IDs. With an Oid we can ask the
repository to get the associated object. To do that the ``Repository`` class
implementes a subset of the mapping interface.

.. automethod:: pygit2.Repository.get

   Return the Git object for the given *id*, returns the *default* value if
   there's no object in the repository with that id. The id can be an Oid
   object, or an hexadecimal string.

   Example::

     >>> from pygit2 import Repository
     >>> repo = Repository('path/to/pygit2')
     >>> obj = repo.get("101715bf37440d32291bde4f58c3142bcf7d8adb")
     >>> obj
     <_pygit2.Commit object at 0x7ff27a6b60f0>

.. method:: Repository.__getitem__(id)

   Return the Git object for the given id, raise ``KeyError`` if there's no
   object in the repository with that id. The id can be an Oid object, or
   an hexadecimal string.

.. method:: Repository.__contains__(id)

   Returns True if there is an object in the Repository with that id, False
   if there is not.  The id can be an Oid object, or an hexadecimal string.


The Object base type
====================

The Object type is a base type, it is not possible to make instances of it, in
any way.

It is the base type of the ``Blob``, ``Tree``, ``Commit`` and ``Tag`` types, so
it is possible to check whether a Python value is an Object or not::

  >>> from pygit2 import Object
  >>> commit = repository.revparse_single('HEAD')
  >>> print isinstance(commit, Object)
  True

All Objects are immutable, they cannot be modified once they are created::

  >>> commit.message = u"foobar"
  Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
  AttributeError: attribute 'message' of '_pygit2.Commit' objects is not writable

Derived types (blobs, trees, etc.) don't have a constructor, this means they
cannot be created with the common idiom::

  >>> from pygit2 import Blob
  >>> blob = Blob("data")
  Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
  TypeError: cannot create '_pygit2.Blob' instances

New objects are created using an specific API we will see later.

This is the common interface for all Git objects:

.. autoattribute:: pygit2.Object.id
.. autoattribute:: pygit2.Object.type
.. automethod:: pygit2.Object.read_raw
.. automethod:: pygit2.Object.peel


Blobs
=================

A blob is just a raw byte string. They are the Git equivalent to files in
a filesytem.

This is their API:

.. autoattribute:: pygit2.Blob.data

   Example, print the contents of the ``.gitignore`` file::

     >>> blob = repo["d8022420bf6db02e906175f64f66676df539f2fd"]
     >>> print blob.data
     MANIFEST
     build
     dist

.. autoattribute:: pygit2.Blob.size

   Example::

     >>> print blob.size
     130

.. autoattribute:: pygit2.Blob.is_binary

.. automethod:: pygit2.Blob.diff
.. automethod:: pygit2.Blob.diff_to_buffer


Creating blobs
--------------

There are a number of methods in the repository to create new blobs, and add
them to the Git object database:

.. automethod:: pygit2.Repository.create_blob

   Example:

     >>> id  = repo.create_blob('foo bar')   # Creates blob from bytes string
     >>> blob = repo[id]
     >>> blob.data
     'foo bar'

.. automethod:: pygit2.Repository.create_blob_fromworkdir
.. automethod:: pygit2.Repository.create_blob_fromdisk

There are also some functions to calculate the id for a byte string without
creating the blob object:

.. autofunction:: pygit2.hash
.. autofunction:: pygit2.hashfile


Trees
=================

A tree is a sorted collection of tree entries. It is similar to a folder or
directory in a file system. Each entry points to another tree or a blob.  A
tree can be iterated, and partially implements the sequence and mapping
interfaces.

.. method:: Tree.__getitem__(name)

   Return the TreeEntry object for the given *name*. Raise ``KeyError`` if
   there is not a tree entry with that name.

.. method:: Tree.__contains__(name)

   Return True if there is a tree entry with the given name, False otherwise.

.. method:: Tree.__len__()

   Return the number of entries in the tree.

.. method:: Tree.__iter__()

   Return an iterator over the entries of the tree.

.. automethod:: pygit2.Tree.diff_to_tree
.. automethod:: pygit2.Tree.diff_to_workdir
.. automethod:: pygit2.Tree.diff_to_index

Tree entries
------------

.. autoattribute:: pygit2.TreeEntry.name
.. autoattribute:: pygit2.TreeEntry.id
.. autoattribute:: pygit2.TreeEntry.hex
.. autoattribute:: pygit2.TreeEntry.filemode

.. method:: TreeEntry.__cmp__(TreeEntry)

   Rich comparison between tree entries.

Example::

    >>> tree = commit.tree
    >>> len(tree)                        # Number of entries
    6

    >>> for entry in tree:               # Iteration
    ...     print(entry.id, entry.name)
    ...
    7151ca7cd3e59f3eab19c485cfbf3cb30928d7fa .gitignore
    c36f4cf1e38ec1bb9d9ad146ed572b89ecfc9f18 COPYING
    32b30b90b062f66957d6790c3c155c289c34424e README.md
    c87dae4094b3a6d10e08bc6c5ef1f55a7e448659 pygit2.c
    85a67270a49ef16cdd3d328f06a3e4b459f09b27 setup.py
    3d8985bbec338eb4d47c5b01b863ee89d044bd53 test

    >>> entry = tree['pygit2.c']         # Get an entry by name
    >>> entry
    <pygit2.TreeEntry object at 0xcc10f0>

    >>> blob = repo[entry.id]           # Get the object the entry points to
    >>> blob
    <pygit2.Blob object at 0xcc12d0>

Creating trees
--------------------

.. automethod:: pygit2.Repository.TreeBuilder

.. automethod:: pygit2.TreeBuilder.insert
.. automethod:: pygit2.TreeBuilder.remove
.. automethod:: pygit2.TreeBuilder.clear
.. automethod:: pygit2.TreeBuilder.write
.. automethod:: pygit2.TreeBuilder.get


Commits
=================

A commit is a snapshot of the working dir with meta informations like author,
committer and others.

.. autoattribute:: pygit2.Commit.author
.. autoattribute:: pygit2.Commit.committer
.. autoattribute:: pygit2.Commit.message
.. autoattribute:: pygit2.Commit.message_encoding
.. autoattribute:: pygit2.Commit.raw_message
.. autoattribute:: pygit2.Commit.tree
.. autoattribute:: pygit2.Commit.tree_id
.. autoattribute:: pygit2.Commit.parents
.. autoattribute:: pygit2.Commit.parent_ids
.. autoattribute:: pygit2.Commit.commit_time
.. autoattribute:: pygit2.Commit.commit_time_offset


Signatures
-------------

The author and committer attributes of commit objects are ``Signature``
objects::

    >>> commit.author
    <pygit2.Signature object at 0x7f75e9b1f5f8>

.. autoattribute:: pygit2.Signature.name
.. autoattribute:: pygit2.Signature.raw_name
.. autoattribute:: pygit2.Signature.email
.. autoattribute:: pygit2.Signature.raw_email
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


Tags
=================

A tag is a static label for a commit. See references for more information.

.. autoattribute:: pygit2.Tag.name
.. autoattribute:: pygit2.Tag.target
.. autoattribute:: pygit2.Tag.tagger
.. autoattribute:: pygit2.Tag.message

.. automethod:: pygit2.Tag.get_object


Creating tags
--------------------

.. automethod:: pygit2.Repository.create_tag
