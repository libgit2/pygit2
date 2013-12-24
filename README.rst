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

56 developers have contributed at least 1 commit to pygit2::

  J. David Ibáñez                          Andrey Devyatkin
  Nico von Geyso                           Ben Davis
  Carlos Martín Nieto                      Eric Schrijver
  W. Trevor King                           Hervé Cauwelier
  Dave Borowitz                            Huang Huang
  Daniel Rodríguez Troitiño                Jared Flatow
  Richo Healey                             Jiunn Haur Lim
  Christian Boos                           Sarath Lakshman
  Julien Miotte                            Vicent Marti
  Jose Plana                               Zoran Zaric
  Martin Lenders                           Adam Spiers
  Victor Garcia                            Andrew Chin
  Xavier Delannoy                          András Veres-Szentkirályi
  Yonggang Luo                             Benjamin Kircher
  Petr Hosek                               Benjamin Pollack
  Valentin Haenel                          Bryan O'Sullivan
  Xu Tao                                   David Fischer
  Bernardo Heynemann                       David Sanders
  John Szakmeister                         Eric Davis
  Brodie Rao                               Erik van Zijst
  David Versmisse                          Ferengee
  Rémi Duraffort                           Gustavo Di Pietro
  Sebastian Thiel                          Hugh Cole-Baker
  Fraser Tweedale                          Josh Bleecher Snyder
  Han-Wen Nienhuys                         Jun Omae
  Petr Viktorin                            Óscar San José
  Alex Chamberlain                         Ridge Kennedy
  Amit Bakshi                              Rui Abreu Ferreira


Changelog
==============

0.20.1 (2013-12-24)
-------------------

- New remote ref-specs API:
  `#290 <https://github.com/libgit2/pygit2/pull/290>`_

- New ``Repository.reset(...)``:
  `#292 <https://github.com/libgit2/pygit2/pull/292>`_,
  `#294 <https://github.com/libgit2/pygit2/pull/294>`_

- Export ``GIT_DIFF_MINIMAL``:
  `#293 <https://github.com/libgit2/pygit2/pull/293>`_

- New ``Repository.merge(...)``:
  `#295 <https://github.com/libgit2/pygit2/pull/295>`_

- Fix ``Repository.blame`` argument handling:
  `#297 <https://github.com/libgit2/pygit2/pull/297>`_

- Fix build error on Windows:
  `#298 <https://github.com/libgit2/pygit2/pull/298>`_

- Fix typo in the README file, Blog → Blob:
  `#301 <https://github.com/libgit2/pygit2/pull/301>`_

- Now ``Diff.patch`` returns ``None`` if no patch:
  `#232 <https://github.com/libgit2/pygit2/pull/232>`_,
  `#303 <https://github.com/libgit2/pygit2/pull/303>`_

- New ``Walker.simplify_first_parent()``:
  `#304 <https://github.com/libgit2/pygit2/pull/304>`_

0.20.0 (2013-11-24)
-------------------

- Upgrade to libgit2 v0.20.0:
  `#288 <https://github.com/libgit2/pygit2/pull/288>`_

  Rename ``Repository.head_is_orphaned`` to ``Repository.head_is_unborn``

  Prototype of ``pygit2.clone_repository(...)`` changed::

      # Before
      pygit2.clone_repository(url, path, bare=False, remote_name='origin',
                              push_url=None, fetch_spec=None, push_spec=None,
                              checkout_branch=None)

      # Now
      pygit2.clone_repository(url, path, bare=False, ignore_cert_errors=False,
                              remote_name='origin', checkout_branch=None)

- New ``Patch.additions`` and ``Patch.deletions``:
  `#275 <https://github.com/libgit2/pygit2/pull/275>`_

- New ``Patch.is_binary``:
  `#276 <https://github.com/libgit2/pygit2/pull/276>`_

- New ``Reference.log_append(...)``:
  `#277 <https://github.com/libgit2/pygit2/pull/277>`_

- New ``Blob.is_binary``:
  `#278 <https://github.com/libgit2/pygit2/pull/278>`_

- New ``len(Diff)`` shows the number of patches:
  `#281 <https://github.com/libgit2/pygit2/pull/281>`_

- Rewrite ``Repository.status()``:
  `#283 <https://github.com/libgit2/pygit2/pull/283>`_

- New ``Reference.shorthand``:
  `#284 <https://github.com/libgit2/pygit2/pull/284>`_

- New ``Repository.blame(...)``:
  `#285 <https://github.com/libgit2/pygit2/pull/285>`_

- Now ``Repository.listall_references()`` and
  ``Repository.listall_branches()`` return a list, not a tuple:
  `#289 <https://github.com/libgit2/pygit2/pull/289>`_


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
