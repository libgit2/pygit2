######################################################################
pygit2 - libgit2 bindings in Python
######################################################################

.. image:: https://travis-ci.org/libgit2/pygit2.svg?branch=master
   :target: http://travis-ci.org/libgit2/pygit2

Pygit2 is a set of Python bindings to the libgit2 shared library, libgit2
implements Git plumbing.  Pygit2 works with Python 2.7, 3.2, 3.3, 3.4, 3.5 and
PyPy 2.6

Links:

- http://github.com/libgit2/pygit2 -- Source code and issue tracker
- http://www.pygit2.org/ -- Documentation
- http://pypi.python.org/pypi/pygit2 -- Download


How to install
==============

- Check http://www.pygit2.org/install.html


Changelog
==============

0.24.1 (2016-06-21)
-------------------------

- New ``Repository.listall_reference_objects()``
  `#634 <https://github.com/libgit2/pygit2/pull/634>`_

- Fix ``Repository.write_archive(...)``
  `#619 <https://github.com/libgit2/pygit2/pull/619>`_
  `#621 <https://github.com/libgit2/pygit2/pull/621>`_

- Reproducible builds
  `#636 <https://github.com/libgit2/pygit2/pull/636>`_

- Documentation fixes
  `#606 <https://github.com/libgit2/pygit2/pull/606>`_
  `#607 <https://github.com/libgit2/pygit2/pull/607>`_
  `#609 <https://github.com/libgit2/pygit2/pull/609>`_
  `#623 <https://github.com/libgit2/pygit2/pull/623>`_

- Test updates
  `#629 <https://github.com/libgit2/pygit2/pull/629>`_


0.24.0 (2016-03-05)
-------------------------

- Update to libgit2 v0.24
  `#594 <https://github.com/libgit2/pygit2/pull/594>`_

- Support Python 3.5

- New dependency, `six <https://pypi.python.org/pypi/six/>`_

- New ``Repository.path_is_ignored(path)``
  `#589 <https://github.com/libgit2/pygit2/pull/589>`_

- Fix error in ``Repository(path)`` when path is a bytes string
  `#588 <https://github.com/libgit2/pygit2/issues/588>`_
  `#593 <https://github.com/libgit2/pygit2/pull/593>`_

- Fix memory issue in ``Repository.describe(...)``
  `#592 <https://github.com/libgit2/pygit2/issues/592>`_
  `#597 <https://github.com/libgit2/pygit2/issues/597>`_
  `#599 <https://github.com/libgit2/pygit2/pull/599>`_

- Allow testing with `tox <https://pypi.python.org/pypi/tox/>`_
  `#600 <https://github.com/libgit2/pygit2/pull/600>`_


0.23.3 (2016-01-01)
-------------------------

- New ``Repository.create_blob_fromiobase(...)``
  `#490 <https://github.com/libgit2/pygit2/pull/490>`_
  `#577 <https://github.com/libgit2/pygit2/pull/577>`_

- New ``Repository.describe(...)``
  `#585 <https://github.com/libgit2/pygit2/pull/585>`_

- Fix ``Signature`` default encoding, UTF-8 now
  `#581 <https://github.com/libgit2/pygit2/issues/581>`_

- Fixing ``pip install pygit2``, should install cffi first

- Unit tests, fix binary diff test
  `#586 <https://github.com/libgit2/pygit2/pull/586>`_

- Document that ``Diff.patch`` can be ``None``
  `#587 <https://github.com/libgit2/pygit2/pull/587>`_


0.23.2 (2015-10-11)
-------------------------

- Unify callbacks system for remotes and clone
  `#568 <https://github.com/libgit2/pygit2/pull/568>`_

- New ``TreeEntry._name``
  `#570 <https://github.com/libgit2/pygit2/pull/570>`_

- Fix segfault in ``Tag._message``
  `#572 <https://github.com/libgit2/pygit2/pull/572>`_

- Documentation improvements
  `#569 <https://github.com/libgit2/pygit2/pull/569>`_
  `#574 <https://github.com/libgit2/pygit2/pull/574>`_

API changes to clone::

  # Before
  clone_repository(..., credentials, certificate)

  # Now
  callbacks = RemoteCallbacks(credentials, certificate)
  clone_repository(..., callbacks)

API changes to remote::

  # Before
  def transfer_progress(stats):
      ...

  remote.credentials = credentials
  remote.transfer_progress = transfer_progress
  remote.fetch()
  remote.push(specs)

  # Now
  class MyCallbacks(RemoteCallbacks):
      def transfer_progress(self, stats):
          ...

  callbacks = MyCallbacks(credentials)
  remote.fetch(callbacks=callbacks)
  remote.push(specs, callbacks=callbacks)


0.23.1 (2015-09-26)
-------------------------

- Improve support for cffi 1.0+
  `#529 <https://github.com/libgit2/pygit2/pull/529>`_
  `#561 <https://github.com/libgit2/pygit2/pull/561>`_

- Fix ``Remote.push``
  `#557 <https://github.com/libgit2/pygit2/pull/557>`_

- New ``TreeEntry.type``
  `#560 <https://github.com/libgit2/pygit2/pull/560>`_

- New ``pygit2.GIT_DIFF_SHOW_BINARY``
  `#566 <https://github.com/libgit2/pygit2/pull/566>`_


0.23.0 (2015-08-14)
-------------------------

- Update to libgit2 v0.23
  `#540 <https://github.com/libgit2/pygit2/pull/540>`_

- Now ``Repository.merge_base(...)`` returns ``None`` if no merge base is found
  `#550 <https://github.com/libgit2/pygit2/pull/550>`_

- Documentation updates
  `#547 <https://github.com/libgit2/pygit2/pull/547>`_

API changes:

- How to set identity (aka signature) in a reflog has changed::

    # Before
    signature = Signature('foo', 'bar')
    ...
    reference.set_target(target, signature=signature, message=message)
    repo.set_head(target, signature=signature)
    remote.fetch(signature=signature)
    remote.push(signature=signature)

    # Now
    repo.set_ident('foo', 'bar')
    ...
    reference.set_target(target, message=message)
    repo.set_head(target)
    remote.push()

    # The current identity can be get with
    repo.ident

- Some remote setters have been replaced by methods::

    # Before                       # Now
    Remote.url = url               Repository.remotes.set_url(name, url)
    Remote.push_url = url          Repository.remotes.set_push_url(name, url)

    Remote.add_fetch(refspec)      Repository.remotes.add_fetch(name, refspec)
    Remote.add_push(refspec)       Repository.remotes.add_push(name, refspec)

    Remote.fetch_refspecs = [...]  removed, use the config API instead
    Remote.push_refspecs = [...]   removed, use the config API instead


0.22.1 (2015-07-12)
-------------------------

Diff interface refactoring
`#346 <https://github.com/libgit2/pygit2/pull/346>`_
(in progress):

- New ``iter(pygit2.Blame)``

- New ``pygit2.DiffDelta``, ``pygit2.DiffFile`` and ``pygit.DiffLine``

- API changes, translation table::

    Hunk                => DiffHunk
    Patch.old_file_path => Patch.delta.old_file.path
    Patch.new_file_path => Patch.delta.new_file.path
    Patch.old_id        => Patch.delta.old_file.id
    Patch.new_id        => Patch.delta.new_file.id
    Patch.status        => Patch.delta.status
    Patch.similarity    => Patch.delta.similarity
    Patch.is_binary     => Patch.delta.is_binary
    Patch.additions     => Patch.line_stats[1]
    Patch.deletions     => Patch.line_stats[2]

- ``DiffHunk.lines`` is now a list of ``DiffLine`` objects, not tuples

New features:

- New ``Repository.expand_id(...)`` and ``Repository.ahead_behind(...)``
  `#448 <https://github.com/libgit2/pygit2/pull/448>`_

- New ``prefix`` parameter in ``Repository.write_archive``
  `#481 <https://github.com/libgit2/pygit2/pull/481>`_

- New ``Repository.merge_trees(...)``
  `#489 <https://github.com/libgit2/pygit2/pull/489>`_

- New ``Repository.cherrypick(...)``
  `#436 <https://github.com/libgit2/pygit2/issues/436>`_
  `#492 <https://github.com/libgit2/pygit2/pull/492>`_

- New support for submodules
  `#499 <https://github.com/libgit2/pygit2/pull/499>`_
  `#514 <https://github.com/libgit2/pygit2/pull/514>`_

- New ``Repository.merge_file_from_index(...)``
  `#503 <https://github.com/libgit2/pygit2/pull/503>`_

- Now ``Repository.diff`` supports diffing two blobs
  `#508 <https://github.com/libgit2/pygit2/pull/508>`_

- New optional ``fetch`` parameter in ``Remote.create``
  `#526 <https://github.com/libgit2/pygit2/pull/526>`_

- New ``pygit2.DiffStats``
  `#406 <https://github.com/libgit2/pygit2/issues/406>`_
  `#525 <https://github.com/libgit2/pygit2/pull/525>`_

- New ``Repository.get_attr(...)``
  `#528 <https://github.com/libgit2/pygit2/pull/528>`_

- New ``level`` optional parameter in ``Index.remove``
  `#533 <https://github.com/libgit2/pygit2/pull/533>`_

- New ``repr(TreeEntry)``
  `#543 <https://github.com/libgit2/pygit2/pull/543>`_

Build and install improvements:

- Make pygit work in a frozen environment
  `#453 <https://github.com/libgit2/pygit2/pull/453>`_

- Make pygit2 work with pyinstaller
  `#510 <https://github.com/libgit2/pygit2/pull/510>`_

Bugs fixed:

- Fix memory issues
  `#477 <https://github.com/libgit2/pygit2/issues/477>`_
  `#487 <https://github.com/libgit2/pygit2/pull/487>`_
  `#520 <https://github.com/libgit2/pygit2/pull/520>`_

- Fix TreeEntry equality testing
  `#458 <https://github.com/libgit2/pygit2/issues/458>`_
  `#488 <https://github.com/libgit2/pygit2/pull/488>`_

- ``Repository.write_archive`` fix handling of symlinks
  `#480 <https://github.com/libgit2/pygit2/pull/480>`_

- Fix type check in ``Diff[...]``
  `#495 <https://github.com/libgit2/pygit2/issues/495>`_

- Fix error when merging files with unicode content
  `#505 <https://github.com/libgit2/pygit2/pull/505>`_

Other:

- Documentation improvements and fixes
  `#448 <https://github.com/libgit2/pygit2/pull/448>`_
  `#491 <https://github.com/libgit2/pygit2/pull/491>`_
  `#497 <https://github.com/libgit2/pygit2/pull/497>`_
  `#507 <https://github.com/libgit2/pygit2/pull/507>`_
  `#517 <https://github.com/libgit2/pygit2/pull/517>`_
  `#518 <https://github.com/libgit2/pygit2/pull/518>`_
  `#519 <https://github.com/libgit2/pygit2/pull/519>`_
  `#521 <https://github.com/libgit2/pygit2/pull/521>`_
  `#523 <https://github.com/libgit2/pygit2/pull/523>`_
  `#527 <https://github.com/libgit2/pygit2/pull/527>`_
  `#536 <https://github.com/libgit2/pygit2/pull/536>`_

- Expose the ``pygit2.GIT_REPOSITORY_INIT_*`` constants
  `#483 <https://github.com/libgit2/pygit2/issues/483>`_


0.22.0 (2015-01-16)
-------------------

New:

- Update to libgit2 v0.22
  `#459 <https://github.com/libgit2/pygit2/pull/459>`_

- Add support for libgit2 feature detection
  (new ``pygit2.features`` and ``pygit2.GIT_FEATURE_*``)
  `#475 <https://github.com/libgit2/pygit2/pull/475>`_

- New ``Repository.remotes`` (``RemoteCollection``)
  `#447 <https://github.com/libgit2/pygit2/pull/447>`_

API Changes:

- Prototype of ``clone_repository`` changed, check documentation

- Removed ``clone_into``, use ``clone_repository`` with callbacks instead

- Use ``Repository.remotes.rename(name, new_name)`` instead of
  ``Remote.rename(new_name)``

- Use ``Repository.remotes.delete(name)`` instead of ``Remote.delete()``

- Now ``Remote.push(...)`` takes a list of refspecs instead of just one

- Change ``Patch.old_id``, ``Patch.new_id``, ``Note.annotated_id``,
  ``RefLogEntry.oid_old`` and ``RefLogEntry.oid_new`` to be ``Oid`` objects
  instead of strings
  `#449 <https://github.com/libgit2/pygit2/pull/449>`_

Other:

- Fix ``init_repository`` when passing optional parameters ``workdir_path``,
  ``description``, ``template_path``, ``initial_head`` or ``origin_url``
  `#466 <https://github.com/libgit2/pygit2/issues/466>`_
  `#471 <https://github.com/libgit2/pygit2/pull/471>`_

- Fix use-after-free when patch outlives diff
  `#457 <https://github.com/libgit2/pygit2/issues/457>`_
  `#461 <https://github.com/libgit2/pygit2/pull/461>`_
  `#474 <https://github.com/libgit2/pygit2/pull/474>`_

- Documentation improvements
  `#456 <https://github.com/libgit2/pygit2/issues/456>`_
  `#462 <https://github.com/libgit2/pygit2/pull/462>`_
  `#465 <https://github.com/libgit2/pygit2/pull/465>`_
  `#472 <https://github.com/libgit2/pygit2/pull/472>`_
  `#473 <https://github.com/libgit2/pygit2/pull/473>`_

- Make the GPL exception explicit in setup.py
  `#450 <https://github.com/libgit2/pygit2/pull/450>`_


0.21.4 (2014-11-04)
-------------------

- Fix credentials callback not set when pushing
  `#431 <https://github.com/libgit2/pygit2/pull/431>`_
  `#435 <https://github.com/libgit2/pygit2/issues/435>`_
  `#437 <https://github.com/libgit2/pygit2/issues/437>`_
  `#438 <https://github.com/libgit2/pygit2/pull/438>`_

- Fix ``Repository.diff(...)`` when treeish is "empty"
  `#432 <https://github.com/libgit2/pygit2/issues/432>`_

- New ``Reference.peel(...)`` renders ``Reference.get_object()`` obsolete
  `#434 <https://github.com/libgit2/pygit2/pull/434>`_

- New, authenticate using ssh agent
  `#424 <https://github.com/libgit2/pygit2/pull/424>`_

- New ``Repository.merge_commits(...)``
  `#445 <https://github.com/libgit2/pygit2/pull/445>`_

- Make it easier to run when libgit2 not in a standard location
  `#441 <https://github.com/libgit2/pygit2/issues/441>`_

- Documentation: review install chapter

- Documentation: many corrections
  `#427 <https://github.com/libgit2/pygit2/pull/427>`_
  `#429 <https://github.com/libgit2/pygit2/pull/429>`_
  `#439 <https://github.com/libgit2/pygit2/pull/439>`_
  `#440 <https://github.com/libgit2/pygit2/pull/440>`_
  `#442 <https://github.com/libgit2/pygit2/pull/442>`_
  `#443 <https://github.com/libgit2/pygit2/pull/443>`_
  `#444 <https://github.com/libgit2/pygit2/pull/444>`_


0.21.3 (2014-09-15)
-------------------

Breaking changes:

- Now ``Repository.blame(...)`` returns ``Oid`` instead of string
  `#413 <https://github.com/libgit2/pygit2/pull/413>`_

- New ``Reference.set_target(...)`` replaces the ``Reference.target`` setter
  and ``Reference.log_append(...)``
  `#414 <https://github.com/libgit2/pygit2/pull/414>`_

- New ``Repository.set_head(...)`` replaces the ``Repository.head`` setter
  `#414 <https://github.com/libgit2/pygit2/pull/414>`_

- ``Repository.merge(...)`` now uses the ``SAFE_CREATE`` strategy by default
  `#417 <https://github.com/libgit2/pygit2/pull/417>`_

Other changes:

- New ``Remote.delete()``
  `#418 <https://github.com/libgit2/pygit2/issues/418>`_
  `#420 <https://github.com/libgit2/pygit2/pull/420>`_

- New ``Repository.write_archive(...)``
  `#421 <https://github.com/libgit2/pygit2/pull/421>`_

- Now ``Repository.checkout(...)`` accepts branch objects
  `#408 <https://github.com/libgit2/pygit2/pull/408>`_

- Fix refcount leak in remotes
  `#403 <https://github.com/libgit2/pygit2/issues/403>`_
  `#404 <https://github.com/libgit2/pygit2/pull/404>`_
  `#419 <https://github.com/libgit2/pygit2/pull/419>`_

- Various fixes to ``clone_repository(...)``
  `#399 <https://github.com/libgit2/pygit2/issues/399>`_
  `#411 <https://github.com/libgit2/pygit2/pull/411>`_
  `#425 <https://github.com/libgit2/pygit2/issues/425>`_
  `#426 <https://github.com/libgit2/pygit2/pull/426>`_

- Fix build error in Python 3
  `#401 <https://github.com/libgit2/pygit2/pull/401>`_

- Now ``pip install pygit2`` installs cffi first
  `#380 <https://github.com/libgit2/pygit2/issues/380>`_
  `#407 <https://github.com/libgit2/pygit2/pull/407>`_

- Add support for PyPy3
  `#422 <https://github.com/libgit2/pygit2/pull/422>`_

- Documentation improvements
  `#398 <https://github.com/libgit2/pygit2/pull/398>`_
  `#409 <https://github.com/libgit2/pygit2/pull/409>`_


0.21.2 (2014-08-09)
-------------------

- Fix regression with Python 2, ``IndexEntry.path`` returns str
  (bytes in Python 2 and unicode in Python 3)

- Get back ``IndexEntry.oid`` for backwards compatibility

- Config, iterate over the keys (instead of the key/value pairs)
  `#395 <https://github.com/libgit2/pygit2/pull/395>`_

- ``Diff.find_similar`` supports new threshold arguments
  `#396 <https://github.com/libgit2/pygit2/pull/396>`_

- Optimization, do not load the object when expanding an oid prefix
  `#397 <https://github.com/libgit2/pygit2/pull/397>`_


0.21.1 (2014-07-22)
-------------------

- Install fix
  `#382 <https://github.com/libgit2/pygit2/pull/382>`_

- Documentation improved, including
  `#383 <https://github.com/libgit2/pygit2/pull/383>`_
  `#385 <https://github.com/libgit2/pygit2/pull/385>`_
  `#388 <https://github.com/libgit2/pygit2/pull/388>`_

- Documentation, use the read-the-docs theme
  `#387 <https://github.com/libgit2/pygit2/pull/387>`_

- Coding style improvements
  `#392 <https://github.com/libgit2/pygit2/pull/392>`_

- New ``Repository.state_cleanup()``
  `#386 <https://github.com/libgit2/pygit2/pull/386>`_

- New ``Index.conflicts``
  `#345 <https://github.com/libgit2/pygit2/issues/345>`_
  `#389 <https://github.com/libgit2/pygit2/pull/389>`_

- New checkout option to define the target directory
  `#390 <https://github.com/libgit2/pygit2/pull/390>`_


Backward incompatible changes:

- Now the checkout strategy must be a keyword argument.

  Change ``Repository.checkout(refname, strategy)`` to
  ``Repository.checkout(refname, strategy=strategy)``

  Idem for ``checkout_head``, ``checkout_index`` and ``checkout_tree``


0.21.0 (2014-06-27)
-------------------

Highlights:

- Drop official support for Python 2.6, and add support for Python 3.4
  `#376 <https://github.com/libgit2/pygit2/pull/376>`_

- Upgrade to libgit2 v0.21.0
  `#374 <https://github.com/libgit2/pygit2/pull/374>`_

- Start using cffi
  `#360 <https://github.com/libgit2/pygit2/pull/360>`_
  `#361 <https://github.com/libgit2/pygit2/pull/361>`_

Backward incompatible changes:

- Replace ``oid`` by ``id`` through the API to follow libgit2 conventions.
- Merge API overhaul following changes in libgit2.
- New ``Remote.rename(...)`` replaces ``Remote.name = ...``
- Now ``Remote.fetch()`` returns a ``TransferProgress`` object.
- Now ``Config.get_multivar(...)`` returns an iterator instead of a list.

New features:

- New ``Config.snapshot()`` and ``Repository.config_snapshot()``

- New ``Config`` methods: ``get_bool(...)``, ``get_int(...)``,
  ``parse_bool(...)`` and ``parse_int(...)``
  `#357 <https://github.com/libgit2/pygit2/pull/357>`_

- Blob: implement the memory buffer interface
  `#362 <https://github.com/libgit2/pygit2/pull/362>`_

- New ``clone_into(...)`` function
  `#368 <https://github.com/libgit2/pygit2/pull/368>`_

- Now ``Index`` can be used alone, without a repository
  `#372 <https://github.com/libgit2/pygit2/pull/372>`_

- Add more options to ``init_repository``
  `#347 <https://github.com/libgit2/pygit2/pull/347>`_

- Support ``Repository.workdir = ...`` and
  support setting detached heads ``Repository.head = <Oid>``
  `#377 <https://github.com/libgit2/pygit2/pull/377>`_

Other:

- Fix again build with VS2008
  `#364 <https://github.com/libgit2/pygit2/pull/364>`_

- Fix ``Blob.diff(...)`` and ``Blob.diff_to_buffer(...)`` arguments passing
  `#366 <https://github.com/libgit2/pygit2/pull/366>`_

- Fail gracefully when compiling against the wrong version of libgit2
  `#365 <https://github.com/libgit2/pygit2/pull/365>`_

- Several documentation improvements and updates
  `#359 <https://github.com/libgit2/pygit2/pull/359>`_
  `#375 <https://github.com/libgit2/pygit2/pull/375>`_
  `#378 <https://github.com/libgit2/pygit2/pull/378>`_



0.20.3 (2014-04-02)
-------------------

- A number of memory issues fixed
  `#328 <https://github.com/libgit2/pygit2/pull/328>`_
  `#348 <https://github.com/libgit2/pygit2/pull/348>`_
  `#353 <https://github.com/libgit2/pygit2/pull/353>`_
  `#355 <https://github.com/libgit2/pygit2/pull/355>`_
  `#356 <https://github.com/libgit2/pygit2/pull/356>`_
- Compatibility fixes for
  PyPy (`#338 <https://github.com/libgit2/pygit2/pull/338>`_),
  Visual Studio 2008 (`#343 <https://github.com/libgit2/pygit2/pull/343>`_)
  and Python 3.3 (`#351 <https://github.com/libgit2/pygit2/pull/351>`_)
- Make the sort mode parameter in ``Repository.walk(...)`` optional
  `#337 <https://github.com/libgit2/pygit2/pull/337>`_
- New ``Object.peel(...)``
  `#342 <https://github.com/libgit2/pygit2/pull/342>`_
- New ``Index.add_all(...)``
  `#344 <https://github.com/libgit2/pygit2/pull/344>`_
- Introduce support for libgit2 options
  `#350 <https://github.com/libgit2/pygit2/pull/350>`_
- More informative repr for ``Repository`` objects
  `#352 <https://github.com/libgit2/pygit2/pull/352>`_
- Introduce support for credentials
  `#354 <https://github.com/libgit2/pygit2/pull/354>`_
- Several documentation fixes
  `#302 <https://github.com/libgit2/pygit2/issues/302>`_
  `#336 <https://github.com/libgit2/pygit2/issues/336>`_
- Tests, remove temporary files
  `#341 <https://github.com/libgit2/pygit2/pull/341>`_


0.20.2 (2014-02-04)
-------------------

- Support PyPy
  `#209 <https://github.com/libgit2/pygit2/issues/209>`_
  `#327 <https://github.com/libgit2/pygit2/pull/327>`_
  `#333 <https://github.com/libgit2/pygit2/pull/333>`_

Repository:

- New ``Repository.default_signature``
  `#310 <https://github.com/libgit2/pygit2/pull/310>`_

Oid:

- New ``str(Oid)`` deprecates ``Oid.hex``
  `#322 <https://github.com/libgit2/pygit2/pull/322>`_

Object:

- New ``Object.id`` deprecates ``Object.oid``
  `#322 <https://github.com/libgit2/pygit2/pull/322>`_

- New ``TreeEntry.id`` deprecates ``TreeEntry.oid``
  `#322 <https://github.com/libgit2/pygit2/pull/322>`_

- New ``Blob.diff(...)`` and ``Blob.diff_to_buffer(...)``
  `#307 <https://github.com/libgit2/pygit2/pull/307>`_

- New ``Commit.tree_id`` and ``Commit.parent_ids``
  `#73 <https://github.com/libgit2/pygit2/issues/73>`_
  `#311 <https://github.com/libgit2/pygit2/pull/311>`_

- New rich comparison between tree entries
  `#305 <https://github.com/libgit2/pygit2/issues/305>`_
  `#313 <https://github.com/libgit2/pygit2/pull/313>`_

- Now ``Tree.__contains__(key)`` supports paths
  `#306 <https://github.com/libgit2/pygit2/issues/306>`_
  `#316 <https://github.com/libgit2/pygit2/pull/316>`_

Index:

- Now possible to create ``IndexEntry(...)``
  `#325 <https://github.com/libgit2/pygit2/pull/325>`_

- Now ``IndexEntry.path``, ``IndexEntry.oid`` and ``IndexEntry.mode`` are
  writable
  `#325 <https://github.com/libgit2/pygit2/pull/325>`_

- Now ``Index.add(...)`` accepts an ``IndexEntry`` too
  `#325 <https://github.com/libgit2/pygit2/pull/325>`_

- Now ``Index.write_tree(...)`` is able to write to a different repository
  `#325 <https://github.com/libgit2/pygit2/pull/325>`_

- Fix memory leak in ``IndexEntry.path`` setter
  `#335 <https://github.com/libgit2/pygit2/pull/335>`_

Config:

- New ``Config`` iterator replaces ``Config.foreach``
  `#183 <https://github.com/libgit2/pygit2/issues/183>`_
  `#312 <https://github.com/libgit2/pygit2/pull/312>`_

Remote:

- New type ``Refspec``
  `#314 <https://github.com/libgit2/pygit2/pull/314>`_

- New ``Remote.push_url``
  `#315 <https://github.com/libgit2/pygit2/pull/314>`_

- New ``Remote.add_push`` and ``Remote.add_fetch``
  `#255 <https://github.com/libgit2/pygit2/issues/255>`_
  `#318 <https://github.com/libgit2/pygit2/pull/318>`_

- New ``Remote.fetch_refspecs`` replaces ``Remote.get_fetch_refspecs()`` and
  ``Remote.set_fetch_refspecs(...)``
  `#319 <https://github.com/libgit2/pygit2/pull/319>`_

- New ``Remote.push_refspecs`` replaces ``Remote.get_push_refspecs()`` and
  ``Remote.set_push_refspecs(...)``
  `#319 <https://github.com/libgit2/pygit2/pull/319>`_

- New ``Remote.progress``, ``Remote.transfer_progress`` and
  ``Remote.update_tips``
  `#274 <https://github.com/libgit2/pygit2/issues/274>`_
  `#324 <https://github.com/libgit2/pygit2/pull/324>`_

- New type ``TransferProgress``
  `#274 <https://github.com/libgit2/pygit2/issues/274>`_
  `#324 <https://github.com/libgit2/pygit2/pull/324>`_

- Fix refcount leak in ``Repository.remotes``
  `#321 <https://github.com/libgit2/pygit2/issues/321>`_
  `#332 <https://github.com/libgit2/pygit2/pull/332>`_

Other: `#331 <https://github.com/libgit2/pygit2/pull/331>`_


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

- New ``Repository.head_is_unborn`` replaces ``Repository.head_is_orphaned``

- Changed ``pygit2.clone_repository(...)``. Drop ``push_url``, ``fetch_spec``
  and ``push_spec`` parameters. Add ``ignore_cert_errors``.

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


Authors
==============

108 developers have contributed at least 1 commit to pygit2::

  J. David Ibáñez           Carlos Martín Nieto       Nico von Geyso
  W. Trevor King            Dave Borowitz             Daniel Rodríguez Troitiño
  Richo Healey              Christian Boos            Julien Miotte
  Richard Möhn              Xu Tao                    Jose Plana
  Matthew Duggan            Matthew Gamble            Martin Lenders
  Petr Hosek                Victor Garcia             Xavier Delannoy
  Yonggang Luo              Patrick Steinhardt        Valentin Haenel
  Michael Jones             Bernardo Heynemann        Brodie Rao
  John Szakmeister          Vlad Temian               Nicolas Dandrimont
  David Versmisse           Rémi Duraffort            Santiago Perez De Rosso
  Sebastian Thiel           Thom Wiggers              Alok Singhal
  Fraser Tweedale           Han-Wen Nienhuys          Leonardo Rhodes
  Petr Viktorin             Ron Cohen                 Thomas Kluyver
  Alex Chamberlain          Alexander Bayandin        Amit Bakshi
  Andrey Devyatkin          Arno van Lumig            Ben Davis
  Dustin Raimondi           Eric Schrijver            Greg Fitzgerald
  Hervé Cauwelier           Huang Huang               Ian P. McCullough
  Igor Gnatenko             Jack O'Connor             Jared Flatow
  Jiunn Haur Lim            Jun Omae                  Kaarel Kitsemets
  Kevin KIN-FOO             Masud Rahman              Michael Sondergaard
  Ondřej Nový               Sarath Lakshman           Vicent Marti
  Zoran Zaric               Adam Spiers               Andrew Chin
  András Veres-Szentkirályi Ash Berlin                Benjamin Kircher
  Benjamin Pollack          Bryan O'Sullivan          Cam Cope
  Chason Chaffin            Chris Rebert              Colin Watson
  Daniel Bruce              David Fischer             David Sanders
  David Six                 Devaev Maxim              Eric Davis
  Erik Meusel               Erik van Zijst            Ferengee
  Guille -bisho-            Gustavo Di Pietro         Holger Frey
  Hugh Cole-Baker           Jasper Lievisse Adriaanse Josh Bleecher Snyder
  Justin Clift              Kyriakos Oikonomakos      Lukas Fleischer
  Mathieu Bridon            Nicolás Sanguinetti       Noah Fontes
  Óscar San José            Peter Dave Hello          Philippe Ombredanne
  Ridge Kennedy             Ross Nicoll               Rui Abreu Ferreira
  Sheeo                     Soasme                    Vladimir Rutsky
  Yu Jianjian               chengyuhang               earl


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
