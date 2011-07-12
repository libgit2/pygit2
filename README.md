pygit2 - libgit2 bindings in Python
=====================================

pygit2 is a set of Python 2.5+ bindings to the libgit2 linkable C Git library.

INSTALLING AND RUNNING
========================

First you need to install the latest version of libgit2.
You can find platform-specific instructions to build the library in the libgit2 website:

  <http://libgit2.github.com>

Next, make sure you have the required library dependencies for pygit2: OpenSSL and ZLib.
For instance, in Debian-based systems run:

    $ sudo apt-get install zlib1g-dev libssl-dev

Also, make sure you have Python 2.5+ installed together with the Python development headers.

When those are installed, you can install pygit2:

    $ git clone git://github.com/libgit2/pygit2.git
    $ cd pygit2
    $ python setup.py install
    $ python setup.py test


USING
======

Initialize a Git repository:

    >>> from pygit2 import init_repository
    >>> bare = False
    >>> repo = init_repository('test', bare)

Open a repository:

    >>> from pygit2 import Repository
    >>> repo = Repository('test/.git')

Index read:

    >>> index = repo.index
    >>> index.read()
    >>> sha = index['path/to/file'].sha    # from path to sha
    >>> blob = repo[sha]                   # from sha to blob

Iterate over all entries of the index:

    >>> for i in xrange(len(index)):
    ...     entry = index[i]
    ...     print entry.path, entry.sha

Index write:

    >>> index.add('path/to/file')          # git add
    >>> del index['path/to/file']          # git rm
    >>> index.write()                      # don't forget to save the changes

Revision walking:

    >>> from pygit2 import GIT_SORT_TIME
    >>> for commit in repo.walk(sha, GIT_SORT_TIME):
    ...     print commit.sha

Read commit information:

    >>> master_ref = repo.lookup_reference("refs/heads/master")   # Getting the Reference object
    >>> commit = repo[master_ref.sha]
    >>> [name, email, timestamp, tz_offset] = commit.author       # Read the commit authored infos
    >>> tree = commit.tree                                        # Access the tree of the commit

Iterate over all entries of the tree:

    >>> for entry in tree:
    ...     print entry.name, entry.sha, entry.attributes


CONTRIBUTING
==============

Fork libgit2/pygit2 on GitHub, make it awesomer (preferably in a branch named
for the topic), send a pull request.


AUTHORS
==============

* David Borowitz <dborowitz@google.com>
* J. David Ibáñez <jdavid@itaapy.com>


LICENSE
==============

GPLv2 with linking exception. See COPYING for more details.
