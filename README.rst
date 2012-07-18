pygit2 - libgit2 bindings in Python
=====================================

pygit2 is a set of Python bindings to the libgit2 linkable C Git library.
The supported versions of Python are 2.6, 2.7, 3.1 and 3.2

Through this text Python 3 is used for the inline examples. Also, the Python
3 terminology is used (for instance we say text strings instead of unicode
strings).

INSTALLING AND RUNNING
========================

First you need to install the latest version of libgit2.
You can find platform-specific instructions to build the library in the libgit2 website:

  http://libgit2.github.com

Also, make sure you have Python 2.6+ installed together with the Python development headers.

When those are installed, you can install pygit2::

    $ git clone git://github.com/libgit2/pygit2.git
    $ cd pygit2
    $ python setup.py install
    $ python setup.py test

Building on Windows
-------------------

pygit2 expects to find the libgit2 installed files in the directory specified
in the ``LIBGIT2`` environment variable.

In addition, make sure that libgit2 is build in "__cdecl" mode.
The following recipe shows you how to do it, assuming you're working
from a bash shell::

    $ export LIBGIT2=C:/Dev/libgit2
    $ git clone git://github.com/libgit2/libgit2.git
    $ cd libgit2
    $ mkdir build
    $ cd build
    $ cmake .. -DSTDCALL=OFF -DCMAKE_INSTALL_PREFIX=$LIBGIT2 -G "Visual Studio 9 2008"
    $ cmake --build . --config release --target install
    $ ctest -v

At this point, you're ready to execute the generic pygit2 installation
steps described above.


The repository
=================

Everything starts by opening an existing repository::

    >>> from pygit2 import Repository
    >>> repo = Repository('pygit2/.git')

Or by creating a new one::

    >>> from pygit2 import init_repository
    >>> bare = False
    >>> repo = init_repository('test', bare)

These are the basic attributes of a repository::

    Repository.path    -- path to the Git repository
    Repository.workdir -- path to the working directory, None in the case of
                          a bare repo


Git objects
===========

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

    >>> from time import time
    >>> author = Signature('Alice Author', 'alice@authors.tld', time(), 0)
    >>> committer = Signature('Cecil Committer', 'cecil@committers.tld', time(), 0)
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
    TreeEntry.attributes  -- the Unix file attributes
    TreeEntry.to_object() -- returns the git object (equivalent to repo[entry.oid])


Diff
-----------------

A diff shows the changes between trees, an index or the working dir::

    # Diff two trees
    >>> t0 = repo.head.tree
    >>> t1 = repo.head.parents[0]
    >>> diff = t0.diff(t1)
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



References
=================

Reference lookup::

    >>> all_refs = repo.listall_references()
    >>> master_ref = repo.lookup_reference("refs/heads/master")
    >>> commit = repo[master_ref.oid]

Reference log::

    >>> head = repo.lookup_reference('refs/heads/master')
    >>> for entry in head.log():
    ...     print(entry.message)

The interface for RefLogEntry::

    RefLogEntry.committer -- Signature of Committer
    RefLogEntry.message   -- the message of the RefLogEntry
    RefLogEntry.oid_old   -- oid of old reference
    RefLogEntry.oid_new   -- oid of new reference


Revision walking
=================

You can iterate through the revision history with repo.walk::

    >>> from pygit2 import GIT_SORT_TIME
    >>> for commit in repo.walk(oid, GIT_SORT_TIME):
    ...     print(commit.hex)

The index file
=================

Index read::

    >>> index = repo.index
    >>> index.read()
    >>> oid = index['path/to/file'].oid    # from path to object id
    >>> blob = repo[oid]                   # from object id to object

Iterate over all entries of the index::

    >>> for entry in index:
    ...     print entry.path, entry.hex

Index write::

    >>> index.add('path/to/file')          # git add
    >>> del index['path/to/file']          # git rm
    >>> index.write()                      # don't forget to save the changes

Status
=================

Inspect the status of the repository::

    >>> from pygit2 import GIT_STATUS_CURRENT
    >>> status = repo.status()
    >>> for filepath, flags in status.items():
    ...     if flags != GIT_STATUS_CURRENT:
    ...         print "Filepath %s isn't clean" % filepath


CONTRIBUTING
==============

Fork libgit2/pygit2 on GitHub, make it awesomer (preferably in a branch named
for the topic), send a pull request.


TODO
----------------

See issues


AUTHORS
==============

The following people have contributed at least one patch to the
pygit2 project (sorted alphabetically):

- Amit Bakshi
- András Veres-Szentkirályi
- Benjamin Kircher
- Bryan O'Sullivan
- Carlos Martín Nieto
- Christian Boos
- David Borowitz (*Original author*)
- David Versmisse
- Erik van Zijst
- Han-Wen Nienhuys
- Hugh Cole-Baker
- J David Ibáñez (*Current maintainer*)
- Jared Flatow
- John Szakmeister
- Josh Bleecher Snyder
- Julien Miotte
- Martin Lenders
- Nico von Geyso
- Petr Hosek
- Petr Viktorin
- Rui Abreu Ferreira
- Sarath Lakshman
- Sebastian Thiel
- Vicent Marti
- Yonggang Luo
- Zoran Zaric
- pistacchio


LICENSE
==============

GPLv2 with linking exception. See COPYING for more details.
