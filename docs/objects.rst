**********************************************************************
Objects
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
implements a subset of the mapping interface.

.. autoclass:: pygit2.Repository
   :noindex:

   .. automethod:: Repository.get

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
  >>> print(isinstance(commit, Object))
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

.. autoclass:: pygit2.Object
   :members: id, type, type_str, short_id, read_raw, peel, name, filemode
   :special-members: __eq__, __ne__, __hash__, __repr__


Blobs
=================

A blob is just a raw byte string. They are the Git equivalent to files in
a filesystem.

This is their API:

.. autoclass:: pygit2.Blob
   :members:


Creating blobs
--------------

There are a number of methods in the repository to create new blobs, and add
them to the Git object database:

.. autoclass:: pygit2.Repository
   :members: create_blob_fromworkdir, create_blob_fromdisk, create_blob_fromiobase
   :noindex:

   .. automethod:: Repository.create_blob

      Example:

        >>> id  = repo.create_blob('foo bar')   # Creates blob from a byte string
        >>> blob = repo[id]
        >>> blob.data
        'foo bar'

There are also some functions to calculate the id for a byte string without
creating the blob object:

.. autofunction:: pygit2.hash
.. autofunction:: pygit2.hashfile

Streaming blob content
----------------------

`pygit2.Blob.data` and `pygit2.Blob.read_raw()` read the full contents of the
blob into memory and return Python ``bytes``. They also return the raw contents
of the blob, and do not apply any filters which would be applied upon checkout
to the working directory.

Raw and filtered blob data can be accessed as a Python Binary I/O stream
(i.e. a file-like object):

.. autoclass:: pygit2.BlobIO
   :members:


Trees
=================

At the low level (libgit2) a tree is a sorted collection of tree entries. In
pygit2 accessing an entry directly returns the object.

A tree can be iterated, and partially implements the sequence and mapping
interfaces.

.. autoclass:: pygit2.Tree
   :members: diff_to_tree, diff_to_workdir, diff_to_index

   .. method:: Tree.__getitem__(name)

      ``Tree[name]``

      Return the Object subclass instance for the given *name*. Raise ``KeyError``
      if there is not a tree entry with that name.

   .. method:: Tree.__truediv__(name)

      ``Tree / name``

      Return the Object subclass instance for the given *name*. Raise ``KeyError``
      if there is not a tree entry with that name. This allows navigating the tree
      similarly to Pathlib using the slash operator via.

      Example::

          >>> entry = tree / 'path' / 'deeper' / 'some.file'

   .. method:: Tree.__contains__(name)

      ``name in Tree``

      Return True if there is a tree entry with the given name, False otherwise.

   .. method:: Tree.__len__()

      ``len(Tree)``

      Return the number of objects in the tree.

   .. method:: Tree.__iter__()

      ``for object in Tree``

      Return an iterator over the objects in the tree.

Example::

    >>> tree = commit.tree
    >>> len(tree)                        # Number of entries
    6

    >>> for obj in tree:                 # Iteration
    ...     print(obj.id, obj.type_str, obj.name)
    ...
    7151ca7cd3e59f3eab19c485cfbf3cb30928d7fa blob .gitignore
    c36f4cf1e38ec1bb9d9ad146ed572b89ecfc9f18 blob COPYING
    32b30b90b062f66957d6790c3c155c289c34424e blob README.md
    c87dae4094b3a6d10e08bc6c5ef1f55a7e448659 blob pygit2.c
    85a67270a49ef16cdd3d328f06a3e4b459f09b27 blob setup.py
    3d8985bbec338eb4d47c5b01b863ee89d044bd53 tree test

    >>> obj = tree / 'pygit2.c'          # Get an object by name
    >>> obj
    <_pygit2.Blob at 0x7f08a70acc10>

Creating trees
--------------------

.. autoclass:: pygit2.Repository
   :members: TreeBuilder
   :noindex:

.. autoclass:: pygit2.TreeBuilder
   :members:


Commits
=================

A commit is a snapshot of the working dir with meta information like author,
committer and others.

.. autoclass:: pygit2.Commit
   :members:


Signatures
-------------

The author and committer attributes of commit objects are ``Signature``
objects::

    >>> commit.author
    pygit2.Signature('Foo Ibáñez', 'foo@example.com', 1322174594, 60, 'utf-8')

Signatures can be compared for (in)equality.

.. autoclass:: pygit2.Signature
   :members:


Creating commits
----------------

.. autoclass:: pygit2.Repository
   :members: create_commit
   :noindex:

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

.. autoclass:: pygit2.Tag
   :members:


Creating tags
--------------------

.. autoclass:: pygit2.Repository
   :members: create_tag
   :noindex:
