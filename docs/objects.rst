**********************************************************************
Git objects
**********************************************************************

.. contents:: Contents
   :local:


In the first place Git is a key-value storage system. The values stored are
called *objects*, there are four types (commits, trees, blobs and tags),
for each type pygit2 has a Python class::

    # Get the last commit
    >>> head = repo.head

    # Show commits and trees
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

This is the common interface for all Git objects::

    Object.type       -- one of the GIT_OBJ_COMMIT, GIT_OBJ_TREE,
                         GIT_OBJ_BLOB or GIT_OBJ_TAG constants
    Object.oid        -- the object id, a byte string 20 bytes long
    Object.hex        -- hexadecimal representation of the object id, a text
                         string 40 chars long
    Object.read_raw() -- returns the byte string with the raw contents of the
                         of the object

Objects can not be modified once they have been created.


Commits
-----------------

A commit is a snapshot of the working dir with meta informations like author,
committer and others.::

    Commit.author    -- the author of the commit
    Commit.committer -- the committer of the commit
    Commit.message   -- the message, a text string
    Commit.tree      -- the tree object attached to the commit
    Commit.parents   -- the list of parent commits


Signatures
.............

The author and committer attributes of commit objects are ``Signature``
objects::

    >>> commit.author
    <pygit2.Signature object at 0x7f75e9b1f5f8>

This is their interface::

    Signature.name   -- person's name
    Signature.email  -- person's email address
    Signature.time   -- unix time
    Signature.offset -- offset from utc in minutes


Creating commits
................

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
-----------------

A tree is a sorted collection of tree entries. It is similar to a folder or
directory in a file system. Each entry points to another tree or a blob.  A
tree can be iterated, and partially implements the sequence and mapping
interfaces::

    # Number of entries
    >>> tree = commit.tree
    >>> len(tree)
    6

    # Iteration
    >>> for entry in tree:
    ...     print(entry.hex, entry.name)
    ...
    7151ca7cd3e59f3eab19c485cfbf3cb30928d7fa .gitignore
    c36f4cf1e38ec1bb9d9ad146ed572b89ecfc9f18 COPYING
    32b30b90b062f66957d6790c3c155c289c34424e README.md
    c87dae4094b3a6d10e08bc6c5ef1f55a7e448659 pygit2.c
    85a67270a49ef16cdd3d328f06a3e4b459f09b27 setup.py
    3d8985bbec338eb4d47c5b01b863ee89d044bd53 test

    # Get an entry by name
    >>> entry = tree['pygit2.c']
    >>> entry
    <pygit2.TreeEntry object at 0xcc10f0>

    # Get the object the entry points to
    >>> blob = repo[entry.oid]
    >>> blob
    <pygit2.Blob object at 0xcc12d0>

This is the interface of a tree entry::

    TreeEntry.name        -- name of the tree entry
    TreeEntry.oid         -- the id of the git object
    TreeEntry.hex         -- hexadecimal representation of the oid
    TreeEntry.filemode    -- the Unix file attributes
    TreeEntry.to_object() -- returns the git object (equivalent to repo[entry.oid])


Diff
-----------------

A diff shows the changes between trees, an index or the working dir::

    # Diff two trees
    >>> t0 = repo.head.tree
    >>> t1 = repo.head.parents[0].tree
    >>> diff = t1.diff(t0)
    >>> diff

    # Diff a tree with the index
    >>> tree = repo.head.tree
    >>> diff = tree.diff(repo.index)

    # Diff a tree with the current working dir
    >>> tree = repo.head.tree
    >>> diff = tree.diff()

The interface for a diff::

    Diff.changes          -- Dict of 'files' and 'hunks' for every change
    Diff.patch            -- a patch for every changeset
    Diff.merge            -- Merge two Diffs


Blobs
-----------------

A blob is equivalent to a file in a file system.::

    # create a blob out of memory
    >>> oid  = repo.create_blob('foo bar')
    >>> blob = repo[oid]

    Blob.data -- the contents of the blob, a byte string

Tags
-----------------

A tag is a static label for a commit. See references for more information.
