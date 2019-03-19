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

   $ pip install pygit2

The line above will install binary wheels if available in your platform.

To install the source package:

.. code-block:: sh

   $ pip install pygit2 --no-binary

It's preferable to install the source package, if it works for you. But the
binary package will often be easier to install.


Requirements
============

Supported versions of Python:

- Python 2.7 and 3.4+
- PyPy 2.7 and 3.5

Python requirements (these are specified in ``setup.py``):

- cffi 1.0+
- six

.. warning::

   cffi requires pycparser, but versions 2.18 and 2.19 of pycparser do not
   work, see https://github.com/libgit2/pygit2/issues/846 for details.

Libgit2 **v0.28.x** (see the version numbering section below for details).
Binary wheels already include libgit2, so you only need to worry about this if
you install the source package

Optional libgit2 dependecies to support ssh and https:

- https: WinHTTP (Windows), SecureTransport (OS X) or OpenSSL.
- ssh: libssh2, pkg-config

To run the tests:

- pytest
- tox (optional)

Version numbers
===============

.. warning::

   One common mistake users do is to choose incompatible versions of libgit2
   and pygit2. Double check the versions do match before filing a bug report.
   Though you don't need to worry about this if you install a binary wheel.

The version number of pygit2 is composed of three numbers separated by dots
|lq| *major.minor.micro* |rq|, where the first two numbers
|lq| *major.minor* |rq| match the first two numbers of the libgit2 version,
while the last number |lq| *.micro* |rq| auto-increments independently.

It is recommended to use the latest version in each series. Example of
compatible releases:

+-----------+--------+--------+--------+--------+--------+
|**libgit2**| 0.28.1 | 0.27.8 | 0.26.8 | 0.25.1 | 0.24.6 |
+-----------+--------+--------+--------+--------+--------+
|**pygit2** | 0.28.0 | 0.27.4 | 0.26.4 | 0.25.1 | 0.24.2 |
+-----------+--------+--------+--------+--------+--------+

.. warning::

   Backwards compatibility is not guaranteed even between micro releases.
   Please check the release notes for incompatible changes before upgrading to
   a new release.


Advanced
===========================

Install libgit2 from source
---------------------------

To install the latest version of libgit2 system wide, in the ``/usr/local``
directory, do:

.. code-block:: sh

   $ wget https://github.com/libgit2/libgit2/archive/v0.28.1.tar.gz
   $ tar xzf v0.28.1.tar.gz
   $ cd libgit2-0.28.1/
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
       from _pygit2 import *
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
from ``$LIBGIT2/lib``.


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

   $ wget https://github.com/libgit2/libgit2/archive/v0.28.1.tar.gz
   $ tar xzf v0.28.1.tar.gz
   $ cd libgit2-0.28.1/
   $ cmake . -DCMAKE_INSTALL_PREFIX=$LIBGIT2
   $ make
   $ make install

Install pygit2:

.. code-block:: sh

   $ export LDFLAGS="-Wl,-rpath='$LIBGIT2/lib',--enable-new-dtags $LDFLAGS"
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

   $ readelf --dynamic lib/python2.7/site-packages/pygit2-0.27.0-py2.7-linux-x86_64.egg/_pygit2.so | grep PATH
    0x000000000000001d (RUNPATH)            Library runpath: [/tmp/venv/lib]


Installing on Windows
===================================

`pygit2` for Windows is packaged into wheels and can be easily
installed with `pip`:

.. code-block:: console

   pip install pygit2

For development it is also possible to build `pygit2` with `libgit2`
from sources. `libgit2` location is specified by the ``LIBGIT2``
environment variable. `libgit2` should be built in "__cdecl" mode.
The following recipe shows you how to do it from a bash shell:

.. code-block:: sh

   $ export LIBGIT2=C:/Dev/libgit2
   $ git clone --depth=1 -b maint/v0.26 https://github.com/libgit2/libgit2.git
   $ cd libgit2
   $ cmake . -DSTDCALL=OFF -DCMAKE_INSTALL_PREFIX=$LIBGIT2 -G "Visual Studio 9 2008"
   $ cmake --build . --config release --target install
   $ ctest -v

At this point, you're ready to execute the generic `pygit2`
installation steps described at the start of this page.


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
