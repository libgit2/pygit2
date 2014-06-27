**********************************************************************
How to Install
**********************************************************************


.. contents::


First you need to install the latest release of libgit2. If you clone
the repository, make sure to use the ``master`` branch. You can find
platform-specific instructions to build the library in the libgit2
website:

  http://libgit2.github.com

Also, make sure you have Python 2.7 or 3.2+ installed together with the Python
development headers.

When those are installed, you can install pygit2:

.. code-block:: sh

    $ git clone git://github.com/libgit2/pygit2.git
    $ cd pygit2
    $ python setup.py install
    $ python setup.py test

.. note:: A minor version of pygit2 must be used with the corresponding minor
   version of libgit2. For example, pygit2 v0.21.x must be used with libgit2
   v0.21.0

Building on \*nix (including OS X)
===================================

If you installed libgit2 and pygit2 in one of the usual places, you
should be able to skip this section and just use the generic pygit2
installation steps described above.  This is the recommended
procedure.

`Shared libraries`_ packaged by your distribution are usually in
``/usr/lib``.  To keep manually installed libraries separate, they are
usually installed in ``/usr/local/lib``.  If you installed libgit2
using the default installation procedure (e.g. without specifying
``CMAKE_INSTALL_PREFIX``), you probably installed it under
``/usr/local/lib``.  On some distributions (e.g. Ubuntu),
``/usr/local/lib`` is not in the linker's default search path (see the
`ld man page`_ for details), and you will get errors like:

.. code-block:: sh

  $ python -c 'import pygit2'
  Traceback (most recent call last):
    File "<string>", line 1, in <module>
    File "pygit2/__init__.py", line 29, in <module>
      from _pygit2 import *
  ImportError: libgit2.so.0: cannot open shared object file: No such file or directory

The following recipe shows how to install libgit2 and pygit2 on these
systems.  First, download and install libgit2 (following the
instructions in the libgit2 ``README.md``):

.. code-block:: sh

  $ git clone -b master git://github.com/libgit2/libgit2.git
  $ mkdir libgit2/build
  $ cd libgit2/build
  $ cmake ..
  $ cmake --build .
  $ sudo cmake --build . --target install
  $ cd ../..

Now, download and install pygit2.  You will probably have to set the
``LIBGIT2`` environment variable so the compiler can find the libgit2
headers and libraries:

.. code-block:: sh

  $ git clone git://github.com/libgit2/pygit2.git
  $ cd pygit2
  $ export LIBGIT2="/usr/local"
  $ export LDFLAGS="-Wl,-rpath='$LIBGIT2/lib',--enable-new-dtags $LDFLAGS"
  $ python setup.py build
  $ sudo python setup.py install

This compiles the pygit2 libraries with a ``RUNPATH``, which bakes
extra library search paths directly into the binaries (see the `ld man
page`_ for details).  With ``RUNPATH`` compiled in, you won't have to
use ``LD_LIBRARY_PATH``.  You can check to ensure ``RUNPATH`` was set
with readelf_:

.. code-block:: sh

  $ readelf --dynamic build/lib.linux-x86_64-3.2/_pygit2.cpython-32.so | grep PATH
   0x000000000000000f (RPATH)              Library rpath: [/usr/local/lib]
   0x000000000000001d (RUNPATH)            Library runpath: [/usr/local/lib]

.. _Shared libraries: http://tldp.org/HOWTO/Program-Library-HOWTO/shared-libraries.html
.. _ld man page: http://linux.die.net/man/1/ld
.. _readelf: http://www.gnu.org/software/binutils/

Building on Windows
===================================

pygit2 expects to find the libgit2 installed files in the directory specified
in the ``LIBGIT2`` environment variable.

In addition, make sure that libgit2 is build in "__cdecl" mode.
The following recipe shows you how to do it, assuming you're working
from a bash shell:

.. code-block:: sh

    $ export LIBGIT2=C:/Dev/libgit2
    $ git clone -b master git://github.com/libgit2/libgit2.git
    $ cd libgit2
    $ mkdir build
    $ cd build
    $ cmake .. -DSTDCALL=OFF -DCMAKE_INSTALL_PREFIX=$LIBGIT2 -G "Visual Studio 9 2008"
    $ cmake --build . --config release --target install
    $ ctest -v

At this point, you're ready to execute the generic pygit2 installation
steps described above.
