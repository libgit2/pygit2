**********************************************************************
Installation
**********************************************************************

.. |lq| unicode:: U+00AB
.. |rq| unicode:: U+00BB


.. contents:: Contents
   :local:


Requirements
============

- Python 2.7, 3.2, 3.3, 3.4 or pypy.
  Including the development headers.

- Libgit2 v0.21.1

- cffi 0.8.1+


One common mistake users do is to choose incompatible versions of libgit2 and
pygit2. Be sure to use the latest release of both, double check the versions do
match before filling un bug report.

.. note::

   The version of pygit2 is composed of three numbers separated by dots
   |lq| *major.minor.micro* |rq|, where the first two numbers
   |lq| *major.minor* |rq| match the first two numbers of the libgit2 version,
   while the last number |lq| *.micro* |rq| auto-increments independently.

   As illustration see this table of compatible releases:

   +-----------+-------------------------------+------------------------------+
   |**libgit2**|0.21.1                         |0.20.0                        |
   +-----------+-------------------------------+------------------------------+
   |**pygit2** |0.21.0, 0.21.1, 0.21.2, 0.21.3 |0.20.0, 0.20.1, 0.20.2, 0.20.3|
   +-----------+-------------------------------+------------------------------+

   **Warning!** Backwards compatibility is not guaranteed even between micro
   releases.  Please check the release notes for incompatible changes before
   upgrading to a new release.


Quick install
=============

This works for me, it may work for you:

.. code-block:: sh

   $ wget https://github.com/libgit2/libgit2/archive/v0.21.1.tar.gz
   $ tar xzf v0.21.1.tar.gz
   $ cd libgit2-0.21.1/
   $ cmake .
   $ make
   $ sudo make install

If this does not work for you, check the detailed instructions on building
libgit2 in various platforms, see
https://libgit2.github.com/docs/guides/build-and-link/

Once libgit2 is instaleld, deploying pygit2 should be a snap:

.. code-block:: sh

   $ pip install pygit2


Troobleshooting
===============

You may get an error like this one:

.. code-block:: sh

   $ python -c 'import pygit2'
   Traceback (most recent call last):
     File "<string>", line 1, in <module>
     File "pygit2/__init__.py", line 29, in <module>
       from _pygit2 import *
   ImportError: libgit2.so.0: cannot open shared object file: No such file or directory

It means the linker is not able to find the libgit2 library.

This happens for instance in Ubuntu: the libgit2 library is installed within
the ``/usr/local/lib`` directory, but the linker does not look for it there. To
fix this call ``ldconfig`` between the installation of libgit2 and the
installation of pygit2:

.. code-block:: sh

   ...
   $ cmake .
   $ make
   $ sudo make install
   ...
   $ sudo ldconfig
   ...
   $ pip install pygit2

Now it should work. If it does not...

Advanced: the runpath
---------------------

If it does not work yet, you can always instruct pygit2 to search for libraries
in some extra paths:

.. code-block:: sh

   $ export LIBGIT2="/usr/local"
   $ export LDFLAGS="-Wl,-rpath='$LIBGIT2/lib',--enable-new-dtags $LDFLAGS"
   $ pip install pygit2

This compiles the pygit2 libraries with a ``RUNPATH``, which bakes extra
library search paths directly into the binaries (see the `ld man page`_ for
details).  With ``RUNPATH`` compiled in, you won't have to use
``LD_LIBRARY_PATH``.  You can check to ensure ``RUNPATH`` was set with
readelf_:

.. code-block:: sh

   $ readelf --dynamic build/lib.linux-x86_64-3.2/_pygit2.cpython-32.so | grep PATH
   0x000000000000000f (RPATH)              Library rpath: [/usr/local/lib]
   0x000000000000001d (RUNPATH)            Library runpath: [/usr/local/lib]

.. _Shared libraries: http://tldp.org/HOWTO/Program-Library-HOWTO/shared-libraries.html
.. _ld man page: http://linux.die.net/man/1/ld
.. _readelf: http://www.gnu.org/software/binutils/


The LIBGIT2 environment variable
================================

If libgit2 is installed in some non standard location, you will have to set the
``LIBGIT2`` environment variable before installing pygit2. This variables tells
pygit2 where libgit2 is installed.


Use case: libgit2 within a Virtualenv
-------------------------------------

A use case for this is if you want to install libgit2 inside a virtualenv, so
you may have several virtualenvs with different versions of libgit2/pygit2,
isolated from each other. Or maybe you just don't have root access to install
libgit2 in the system.

Create the virtualenv, activate it, and set the ``LIBGIT2`` environment
variable:

.. code-block:: sh

   $ virtualenv venv
   $ source venv/bin/activate
   $ export LIBGIT2=$VIRTUAL_ENV

Install libgit2 (see we define the installation prefix):

.. code-block:: sh

   $ wget https://github.com/libgit2/libgit2/archive/v0.21.1.tar.gz
   $ tar xzf v0.21.1.tar.gz
   $ cd libgit2-0.21.1/
   $ cmake . -DCMAKE_INSTALL_PREFIX=$LIBGIT2
   $ make
   $ make install

Install pygit2:

.. code-block:: sh

   $ pip install pygit2


Building on Windows
===================================

pygit2 expects to find the libgit2 installed files in the directory specified
in the ``LIBGIT2`` environment variable.

In addition, make sure that libgit2 is build in "__cdecl" mode.
The following recipe shows you how to do it, assuming you're working
from a bash shell:

.. code-block:: sh

   $ export LIBGIT2=C:/Dev/libgit2
   $ wget https://github.com/libgit2/libgit2/archive/v0.21.1.tar.gz
   $ tar xzf v0.21.1.tar.gz
   $ cd libgit2-0.21.1/
   $ mkdir build
   $ cd build
   $ cmake .. -DSTDCALL=OFF -DCMAKE_INSTALL_PREFIX=$LIBGIT2 -G "Visual Studio 9 2008"
   $ cmake --build . --config release --target install
   $ ctest -v

At this point, you're ready to execute the generic pygit2 installation
steps described above.
