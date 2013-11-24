
######################################################################
pygit2 - libgit2 bindings in Python
######################################################################

.. image:: https://secure.travis-ci.org/libgit2/pygit2.png
   :target: http://travis-ci.org/libgit2/pygit2

Pygit2 is a set of Python bindings to the libgit2 shared library, libgit2
implements the core of Git.  Pygit2 works with Python 2.6, 2.7, 3.1, 3.2 and
3.3

Pygit2 links:

- http://github.com/libgit2/pygit2 -- Source code and issue tracker
- http://www.pygit2.org/ -- Documentation
- http://pypi.python.org/pypi/pygit2 -- Download


Quick install guide
===================

1. Checkout the libgit2 stable branch::

   $ git clone git://github.com/libgit2/libgit2.git -b master

2. Build and install libgit2
   https://github.com/libgit2/libgit2/#building-libgit2---using-cmake

3. Install pygit2 with *pip*::

   $ pip install pygit2

For detailed instructions check the documentation,
http://www.pygit2.org/install.html


Contributing
============

Fork libgit2/pygit2 on GitHub, make it awesomer (preferably in a branch named
for the topic), send a pull request.


Authors
==============

52 developers have contributed at least 1 commit to pygit2::

  J. David Ibáñez                          Andrey Devyatkin
  Nico von Geyso                           Ben Davis
  Carlos Martín Nieto                      Hervé Cauwelier
  W. Trevor King                           Huang Huang
  Dave Borowitz                            Jared Flatow
  Daniel Rodríguez Troitiño                Jiunn Haur Lim
  Richo Healey                             Sarath Lakshman
  Christian Boos                           Vicent Marti
  Julien Miotte                            Zoran Zaric
  Martin Lenders                           Andrew Chin
  Xavier Delannoy                          András Veres-Szentkirályi
  Yonggang Luo                             Benjamin Kircher
  Valentin Haenel                          Benjamin Pollack
  Xu Tao                                   Bryan O'Sullivan
  Bernardo Heynemann                       David Fischer
  John Szakmeister                         David Sanders
  Brodie Rao                               Eric Davis
  Petr Hosek                               Eric Schrijver
  David Versmisse                          Erik van Zijst
  Rémi Duraffort                           Ferengee
  Sebastian Thiel                          Hugh Cole-Baker
  Fraser Tweedale                          Josh Bleecher Snyder
  Han-Wen Nienhuys                         Jun Omae
  Petr Viktorin                            Ridge Kennedy
  Alex Chamberlain                         Rui Abreu Ferreira
  Amit Bakshi                              pistacchio


Changelog
==============

0.20.0 (2013-11-24)
-------------------

API changes:

- Renamed ``Repository.head_is_orphaned`` to ``Repository.head_is_unborn``

- ``Repository.listall_references`` and ``Repository.listall_branches`` now
  return a list, instead of a tuple

- The prototype of ``clone_repository`` changed from::

    # Before
    pygit2.clone_repository(url, path, bare=False, remote_name='origin',
                            push_url=None, fetch_spec=None, push_spec=None,
                            checkout_branch=None)

    # Now
    pygit2.clone_repository(url, path, bare=False, ignore_cert_errors=False,
                            remote_name='origin', checkout_branch=None)

New API:

- Added support for blame

- New:

  - ``Reference.log_append(...)``
  - ``Reference.shorthand``
  - ``Blog.is_binary``
  - ``len(Diff)``
  - ``Patch.additions``
  - ``Patch.deletions``
  - ``Patch.is_binary``


License
==============

**GPLv2 with linking exception.**

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License,
version 2, as published by the Free Software Foundation.

In addition to the permissions in the GNU General Public License,
the authors give you unlimited permission to link the compiled
version of this file into combinations with other programs,
and to distribute those combinations without any restriction
coming from the use of this file.  (The General Public License
restrictions do apply in other respects; for example, they cover
modification of the file, and distribution when not linked into
a combined executable.)

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; see the file COPYING.  If not, write to
the Free Software Foundation, 51 Franklin Street, Fifth Floor,
Boston, MA 02110-1301, USA.
