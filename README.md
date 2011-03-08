pygit2 - libgit2 bindings in Python
=====================================

pygit2 is a set of Python 2.6+ bindings to the libgit2 linkable C Git library.

INSTALLING AND RUNNING
========================

First you need to install the latest version of libgit2. 
You can find platform-specific instructions to build the library in the libgit2 website:

  <http://libgit2.github.com>

Next, make sure you have the required library dependencies for pygit2: OpenSSL and ZLib.
For instance, in Debian-based systems run:

    $ sudo apt-get install zlib1g-dev libssl-dev

Also, make sure you have Python 2.6+ installed together with the Python development headers.

When those are installed, you can install pygit2:

    $ git clone git://github.com/libgit2/pygit2.git 
    $ cd pygit2
    $ python setup.py install
    $ python setup.py test

    
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




