**********************************************************************
The development version
**********************************************************************

Unit tests
==========

.. image:: https://travis-ci.org/libgit2/pygit2.svg?branch=master
   :target: http://travis-ci.org/libgit2/pygit2

.. image:: https://ci.appveyor.com/api/projects/status/edmwc0dctk5nacx0/branch/master?svg=true
   :target: https://ci.appveyor.com/project/jdavid/pygit2/branch/master

.. code-block:: sh

    $ git clone git://github.com/libgit2/pygit2.git
    $ cd pygit2
    $ python setup.py install
    $ python setup.py test

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
