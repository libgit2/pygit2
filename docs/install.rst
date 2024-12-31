**********************************************************************
Installation
**********************************************************************

.. |lq| unicode:: U+00AB
.. |rq| unicode:: U+00BB


.. contents:: Contents
   :local:


Quick install
=============

Install pygit2:

.. code-block:: sh

   $ pip install -U pip
   $ pip install pygit2

The line above will install binary wheels if available in your platform.

.. note::

   It is recommended to first update the version of pip, as it will increase
   the chances for it to install a binary wheel instead of the source
   distribution. At least version 19.3 of pip is required.

If you get the error::

    fatal error: git2.h: No such file or directory

It means that pip did not find a binary wheel for your platform, so it tried to
build from source, but it failed because it could not find the libgit2 headers.
Then:

- Verify pip is updated
- Verify there is a binary wheel of pygit2 for your platform
- Otherwise install from the source distribution

Caveats:

- Binary wheels for Windows are available, but they don't have support for ssh.


Requirements
============

Supported versions of Python:

- Python 3.10 to 3.13
- PyPy3 7.3+

Python requirements (these are specified in ``setup.py``):

- cffi 1.17.0 or later

Libgit2 **v1.9.x**; binary wheels already include libgit2, so you only need to
worry about this if you install the source package.

Optional libgit2 dependecies to support ssh and https:

- https: WinHTTP (Windows), SecureTransport (OS X) or OpenSSL.
- ssh: libssh2 1.9.0 or later, pkg-config

To run the tests:

- pytest

Version numbers
===============

The version number of pygit2 is composed of three numbers separated by dots
|lq| *major.medium.minor* |rq|:

- *major* will always be 1 (until we release 2.0 in a far undefined future)
- *medium* will increase whenever we make breaking changes, or upgrade to new
  versions of libgit2.
- *minor* will increase for bug fixes.

The table below summarizes the latest pygit2 versions with the supported versions
of Python and the required libgit2 version.

+-----------+----------------+------------+
| pygit2    | Python         | libgit2    |
+-----------+----------------+------------+
| 1.17      | 3.10 - 3.13    | 1.9        |
+-----------+----------------+------------+
| 1.16      | 3.10 - 3.13    | 1.8        |
+-----------+----------------+------------+
| 1.15      | 3.9 - 3.12     | 1.8        |
+-----------+----------------+------------+
| 1.14      | 3.9 - 3.12     | 1.7        |
+-----------+----------------+------------+
| 1.13      | 3.8 - 3.12     | 1.7        |
+-----------+----------------+------------+
| 1.12      | 3.8 - 3.11     | 1.6        |
+-----------+----------------+------------+
| 1.11      | 3.8 - 3.11     | 1.5        |
+-----------+----------------+------------+
| 1.10      | 3.7 - 3.10     | 1.5        |
+-----------+----------------+------------+
| 1.9       | 3.7 - 3.10     | 1.4        |
+-----------+----------------+------------+
| 1.7 - 1.8 | 3.7 - 3.10     | 1.3        |
+-----------+----------------+------------+
| 1.4 - 1.6 | 3.6 - 3.9      | 1.1        |
+-----------+----------------+------------+
| 1.2 - 1.3 | 3.6 - 3.8      | 1.0        |
+-----------+----------------+------------+
| 1.1       | 3.5 - 3.8      | 0.99 - 1.0 |
+-----------+----------------+------------+
| 1.0       | 3.5 - 3.8      | 0.28       |
+-----------+----------------+------------+
| 0.28.2    | 2.7, 3.4 - 3.7 | 0.28       |
+-----------+----------------+------------+

.. warning::

   It is recommended to use the latest 1.x.y release. Because only the latest
   is supported.

.. warning::

   Backwards compatibility is not guaranteed in minor releases. Please check
   the release notes for incompatible changes before upgrading to a new
   release.

History: the 0.x series
-----------------------

The development of pygit2 started in October 2010, the release of 1.0.0
happened in December 2019. In the 0.x series the version numbering was
lockstep with libgit2, e.g. pygit2 0.28.x worked with libgit2 0.28.x


Advanced
===========================

Install libgit2 from source
---------------------------

To install the latest version of libgit2 system wide, in the ``/usr/local``
directory, do:

.. code-block:: sh

   $ wget https://github.com/libgit2/libgit2/archive/refs/tags/v1.9.0.tar.gz -O libgit2-1.9.0.tar.gz
   $ tar xzf libgit2-1.9.0.tar.gz
   $ cd libgit2-1.9.0/
   $ cmake .
   $ make
   $ sudo make install

.. seealso::

   For detailed instructions on building libgit2 check
   https://libgit2.github.com/docs/guides/build-and-link/

Now install pygit2, and then verify it is correctly installed:

.. code-block:: sh

   $ pip install pygit2
   ...
   $ python -c 'import pygit2'


Troubleshooting
---------------------------

The verification step may fail if the dynamic linker does not find the libgit2
library:

.. code-block:: sh

   $ python -c 'import pygit2'
   Traceback (most recent call last):
     File "<string>", line 1, in <module>
     File "pygit2/__init__.py", line 29, in <module>
       from ._pygit2 import *
   ImportError: libgit2.so.0: cannot open shared object file: No such file or directory

This happens for instance in Ubuntu, the libgit2 library is installed within
the ``/usr/local/lib`` directory, but the linker does not look for it there. To
fix this call ``ldconfig``:

.. code-block:: sh

   $ sudo ldconfig
   $ python -c 'import pygit2'

If it still does not work, please open an issue at
https://github.com/libgit2/pygit2/issues


Build options
---------------------------

``LIBGIT2`` -- If you install libgit2 in an unusual place, you will need to set
the ``LIBGIT2`` environment variable before installing pygit2.  This variable
tells pygit2 where libgit2 is installed.  We will see a concrete example later,
when explaining how to install libgit2 within a virtual environment.

``LIBGIT2_LIB`` -- This is a more rarely used build option, it allows to
override the library directory where libgit2 is installed, useful if different
from ``$LIBGIT2/lib`` and ``$LIBGIT2/lib64``.


libgit2 within a virtual environment
------------------------------------

This is how to install both libgit2 and pygit2 within a virtual environment.

This is useful if you don't have root acces to install libgit2 system wide.
Or if you wish to have different versions of libgit2/pygit2 installed in
different virtual environments, isolated from each other.

Create the virtualenv, activate it, and set the ``LIBGIT2`` environment
variable:

.. code-block:: sh

   $ virtualenv venv
   $ source venv/bin/activate
   $ export LIBGIT2=$VIRTUAL_ENV

Install libgit2 (see we define the installation prefix):

.. code-block:: sh

   $ wget https://github.com/libgit2/libgit2/archive/refs/tags/v1.9.0.tar.gz -O libgit2-1.9.0.tar.gz
   $ tar xzf libgit2-1.9.0.tar.gz
   $ cd libgit2-1.9.0/
   $ cmake . -DCMAKE_INSTALL_PREFIX=$LIBGIT2
   $ cmake --build . --target install

Install pygit2:

.. code-block:: sh

   $ export LDFLAGS="-Wl,-rpath,'$LIBGIT2/lib',--enable-new-dtags $LDFLAGS"
   # on OSX: export LDFLAGS="-Wl,-rpath,'$LIBGIT2/lib' $LDFLAGS"
   $ pip install pygit2
   $ python -c 'import pygit2'


The run-path
------------------------------------------

Did you notice we set the `rpath <http://en.wikipedia.org/wiki/Rpath>`_ before
installing pygit2?  Since libgit2 is installed in a non standard location, the
dynamic linker will not find it at run-time, and ``lddconfig`` will not help
this time.

So you need to either set ``LD_LIBRARY_PATH`` before using pygit2, like:

.. code-block:: sh

   $ export LD_LIBRARY_PATH=$LIBGIT2/lib
   $ python -c 'import pygit2'

Or, like we have done in the instructions above, use the `rpath
<http://en.wikipedia.org/wiki/Rpath>`_, it hard-codes extra search paths within
the pygit2 extension modules, so you don't need to set ``LD_LIBRARY_PATH``
everytime. Verify yourself if curious:

.. code-block:: sh

   $ readelf --dynamic lib/python2.7/site-packages/pygit2-0.27.0-py2.7-linux-x86_64.egg/pygit2/_pygit2.so | grep PATH
    0x000000000000001d (RUNPATH)            Library runpath: [/tmp/venv/lib]


Installing on Windows
===================================

`pygit2` for Windows is packaged into wheels and can be easily installed with
`pip`:

.. code-block:: console

   pip install pygit2

For development it is also possible to build `pygit2` with `libgit2` from
sources. `libgit2` location is specified by the ``LIBGIT2`` environment
variable.  The following recipe shows you how to do it from a bash shell:

.. code-block:: sh

   $ export LIBGIT2=C:/Dev/libgit2
   $ git clone --depth=1 -b v1.9.0 https://github.com/libgit2/libgit2.git
   $ cd libgit2
   $ cmake . -DCMAKE_INSTALL_PREFIX=$LIBGIT2 -G "Visual Studio 14 Win64"
   $ cmake --build . --config release --target install
   $ ctest -v

At this point, you're ready to execute the generic `pygit2` installation steps
described at the start of this page.


Installing on OS X
===================================

There are not binary wheels available for OS X, so you will need to install the
source package.

.. note::

   You will need the `XCode <https://developer.apple.com/xcode/>`_ Developer
   Tools from Apple. This free download from the Mac App Store will provide the
   clang compiler needed for the installation of pygit2.

   This section was tested on OS X 10.9 Mavericks and OS X 10.10 Yosemite with
   Python 3.3 in a virtual environment.

The easiest way is to first install libgit2 with the `Homebrew <http://brew.sh>`_
package manager and then use pip3 for pygit2. The following example assumes that
XCode and Hombrew are already installed.

.. code-block:: sh

   $ brew update
   $ brew install libgit2
   $ pip3 install pygit2

To build from a non-Homebrew libgit2 follow the guide in `libgit2 within a virtual environment`_.
