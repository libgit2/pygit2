**********************************************************************
The development version
**********************************************************************

Unit tests
==========

.. image:: https://github.com/libgit2/pygit2/actions/workflows/tests.yml/badge.svg
   :target: https://github.com/libgit2/pygit2/actions/workflows/tests.yml

.. image:: https://ci.appveyor.com/api/projects/status/edmwc0dctk5nacx0/branch/master?svg=true
   :target: https://ci.appveyor.com/project/jdavid/pygit2/branch/master

.. code-block:: sh

    $ git clone git://github.com/libgit2/pygit2.git
    $ cd pygit2
    $ python setup.py build_ext --inplace
    $ pytest test

Coding style: documentation strings
===================================

Example::

  def f(a, b):
      """
      The general description goes here.

      Returns: bla bla.

      Parameters:

      a : <type>
          Bla bla.

      b : <type>
          Bla bla.

      Examples::

          >>> f(...)
      """

Running Valgrind
===================================

Step 1. Build libc and libgit2 with debug symbols. See your distribution
documentation.

Step 2. Build Python to be used with valgrind, e.g.::

  $ ./configure --prefix=~/Python-3.7.4 --without-pymalloc --with-pydebug --with-valgrind
  $ make
  $ make install
  $ export PYTHONBIN=~/Python-3.7.4/bin

Step 3. Build pygit2 with debug symbols::

  $ rm build -rf && $PYTHONBIN/python3 setup.py build_ext --inplace -g

Step 4. Install requirements::

  $ $PYTHONBIN/python3 setup.py install
  $ pip insall pytest

Step 4. Run valgrind:

  $ valgrind -v --leak-check=full --suppressions=misc/valgrind-python.supp $PYTHONBIN/pytest &> valgrind.txt
