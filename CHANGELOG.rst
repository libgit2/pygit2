1.8.0 (2022-02-04)
-------------------------

- Rename ``RemoteCallbacks.progress(...)`` callback to ``.sideband_progress(...)``
  `#1120 <https://github.com/libgit2/pygit2/pull/1120>`_

- New ``Repository.merge_base_many(...)`` and ``Repository.merge_base_octopus(...)``
  `#1112 <https://github.com/libgit2/pygit2/pull/1112>`_

- New ``Repository.listall_stashes()``
  `#1117 <https://github.com/libgit2/pygit2/pull/1117>`_

- Code cleanup
  `#1118 <https://github.com/libgit2/pygit2/pull/1118>`_

Backward incompatible changes:

- The ``RemoteCallbacks.progress(...)`` callback has been renamed to
  ``RemoteCallbacks.sideband_progress(...)``. This matches the documentation,
  but may break existing code that still uses the old name.


1.7.2 (2021-12-06)
-------------------------

- Universal wheels for macOS
  `#1109 <https://github.com/libgit2/pygit2/pull/1109>`_


1.7.1 (2021-11-19)
-------------------------

- New ``Repository.amend_commit(...)``
  `#1098 <https://github.com/libgit2/pygit2/pull/1098>`_

- New ``Commit.message_trailers``
  `#1101 <https://github.com/libgit2/pygit2/pull/1101>`_

- Windows wheels for Python 3.10
  `#1103 <https://github.com/libgit2/pygit2/pull/1103>`_

- Changed: now ``DiffDelta.is_binary`` returns ``None`` if the file data has
  not yet been loaded, cf. `#962 <https://github.com/libgit2/pygit2/issues/962>`_

- Document ``Repository.get_attr(...)`` and update theme
  `#1017 <https://github.com/libgit2/pygit2/issues/1017>`_
  `#1105 <https://github.com/libgit2/pygit2/pull/1105>`_


1.7.0 (2021-10-08)
-------------------------

- Upgrade to libgit2 1.3.0
  `#1089 <https://github.com/libgit2/pygit2/pull/1089>`_

- Linux wheels now bundled with libssh2 1.10.0 (instead of 1.9.0)

- macOS wheels now include libssh2

- Add support for Python 3.10
  `#1092 <https://github.com/libgit2/pygit2/pull/1092>`_
  `#1093 <https://github.com/libgit2/pygit2/pull/1093>`_

- Drop support for Python 3.6

- New `pygit2.GIT_CHECKOUT_SKIP_LOCKED_DIRECTORIES`
  `#1087 <https://github.com/libgit2/pygit2/pull/1087>`_

- New optional argument ``location`` in ``Repository.applies(..)`` and
  ``Repository.apply(..)``
  `#1091 <https://github.com/libgit2/pygit2/pull/1091>`_

- Fix: Now the `flags` argument in `Repository.blame()` is passed through
  `#1083 <https://github.com/libgit2/pygit2/pull/1083>`_

- CI: Stop using Travis, move to GitHub actions

Caveats:

- Windows wheels for Python 3.10 not yet available.


1.6.1 (2021-06-19)
-------------------------

- Fix a number of reference leaks
- Review custom object backends

Breaking changes:

- In custom backends the callbacks have been renamed from ``read`` to
  ``read_cb``, ``write`` to ``write_cb``, and so on.


1.6.0 (2021-06-01)
-------------------------

- New optional ``proxy`` argument in ``Remote`` methods
  `#642 <https://github.com/libgit2/pygit2/issues/642>`_
  `#1063 <https://github.com/libgit2/pygit2/pull/1063>`_
  `#1069 <https://github.com/libgit2/pygit2/issues/1069>`_

- New GIT_MERGE_PREFERENCE constants
  `#1071 <https://github.com/libgit2/pygit2/pull/1071>`_

- Don't require cached-property with Python 3.8 or later
  `#1066 <https://github.com/libgit2/pygit2/pull/1066>`_

- Add wheels for aarch64
  `#1077 <https://github.com/libgit2/pygit2/issues/1077>`_
  `#1078 <https://github.com/libgit2/pygit2/pull/1078>`_

- Documentation fixes
  `#1068 <https://github.com/libgit2/pygit2/pull/1068>`_
  `#1072 <https://github.com/libgit2/pygit2/pull/1072>`_

- Refactored build and CI, new ``build.sh`` script

Breaking changes:

- Remove deprecated ``GIT_CREDTYPE_XXX`` contants, use ``GIT_CREDENTIAL_XXX``
  instead.

- Remove deprecated ``Patch.patch`` getter, use ``Patch.text`` instead.


1.5.0 (2021-01-23)
-------------------------

- New ``PackBuilder`` class and ``Repository.pack(...)``
  `#1048 <https://github.com/libgit2/pygit2/pull/1048>`_

- New ``Config.delete_multivar(...)``
  `#1056 <https://github.com/libgit2/pygit2/pull/1056>`_

- New ``Repository.is_shallow``
  `#1058 <https://github.com/libgit2/pygit2/pull/1058>`_

- New optional ``message`` argument in ``Repository.create_reference(...)``
  `#1061 <https://github.com/libgit2/pygit2/issues/1061>`_
  `#1062 <https://github.com/libgit2/pygit2/pull/1062>`_

- Fix truncated diff when there are nulls
  `#1047 <https://github.com/libgit2/pygit2/pull/1047>`_
  `#1043 <https://github.com/libgit2/pygit2/issues/1043>`_

- Unit tests & Continuous integration
  `#1039 <https://github.com/libgit2/pygit2/issues/1039>`_
  `#1052 <https://github.com/libgit2/pygit2/pull/1052>`_

Breaking changes:

- Fix ``Index.add(...)`` raise ``TypeError`` instead of ``AttributeError`` when
  arguments are of unexpected type


1.4.0 (2020-11-06)
-------------------------

- Upgrade to libgit2 1.1, new ``GIT_BLAME_IGNORE_WHITESPACE`` constant
  `#1040 <https://github.com/libgit2/pygit2/issues/1040>`_

- Add wheels for Python 3.9
  `#1038 <https://github.com/libgit2/pygit2/issues/1038>`_

- Drop support for PyPy3 7.2

- New optional ``flags`` argument in ``Repository.__init__(...)``,
  new ``GIT_REPOSITORY_OPEN_*`` constants
  `#1044 <https://github.com/libgit2/pygit2/pull/1044>`_

- Documentation
  `#509 <https://github.com/libgit2/pygit2/issues/509>`_
  `#752 <https://github.com/libgit2/pygit2/issues/752>`_
  `#1037 <https://github.com/libgit2/pygit2/issues/1037>`_
  `#1045 <https://github.com/libgit2/pygit2/issues/1045>`_


1.3.0 (2020-09-18)
-------------------------

- New ``Repository.add_submodule(...)``
  `#1011 <https://github.com/libgit2/pygit2/pull/1011>`_

- New ``Repository.applies(...)``
  `#1019 <https://github.com/libgit2/pygit2/pull/1019>`_

- New ``Repository.revparse(...)`` and ``Repository.revparse_ext(...)``
  `#1022 <https://github.com/libgit2/pygit2/pull/1022>`_

- New optional ``flags`` and ``file_flags`` arguments in
  ``Repository.merge_commits`` and ``Repository.merge_trees``
  `#1008 <https://github.com/libgit2/pygit2/pull/1008>`_

- New ``Reference.raw_target``, ``Repository.raw_listall_branches(...)`` and
  ``Repository.raw_listall_references()``; allow bytes in
  ``Repository.lookup_branch(...)`` and ``Repository.diff(...)``
  `#1029 <https://github.com/libgit2/pygit2/pull/1029>`_

- New ``GIT_BLAME_FIRST_PARENT`` and ``GIT_BLAME_USE_MAILMAP`` constants
  `#1031 <https://github.com/libgit2/pygit2/pull/1031>`_

- New ``IndexEntry`` supports ``repr()``, ``str()``, ``==`` and ``!=``
  `#1009 <https://github.com/libgit2/pygit2/pull/1009>`_

- New ``Object`` supports ``repr()``
  `#1022 <https://github.com/libgit2/pygit2/pull/1022>`_

- New accept tuples of strings (not only lists) in a number of places
  `#1025 <https://github.com/libgit2/pygit2/pull/1025>`_

- Fix compatibility with old macOS 10.9
  `#1026 <https://github.com/libgit2/pygit2/issues/1026>`_
  `#1027 <https://github.com/libgit2/pygit2/pull/1027>`_

- Fix check argument type in ``Repository.apply(...)``
  `#1033 <https://github.com/libgit2/pygit2/issues/1033>`_

- Fix raise exception if error in ``Repository.listall_submodules()`` commit 32133974

- Fix a couple of refcount errors in ``OdbBackend.refresh()`` and
  ``Worktree_is_prunable`` commit fed0c19c

- Unit tests
  `#800 <https://github.com/libgit2/pygit2/issues/800>`_
  `#1015 <https://github.com/libgit2/pygit2/pull/1015>`_

- Documentation
  `#705 <https://github.com/libgit2/pygit2/pull/705>`_


1.2.1 (2020-05-01)
-------------------------

- Fix segfault in ``Object.raw_name`` when not reached through a tree
  `#1002 <https://github.com/libgit2/pygit2/pull/1002>`_

- Internal: Use @ffi.def_extern instead of @ffi.callback
  `#899 <https://github.com/libgit2/pygit2/issues/899>`_

- Internal: callbacks code refactored

- Test suite completely switched to pytest
  `#824 <https://github.com/libgit2/pygit2/issues/824>`_

- New unit tests
  `#538 <https://github.com/libgit2/pygit2/pull/538>`_
  `#996 <https://github.com/libgit2/pygit2/issues/996>`_

- Documentation changes
  `#999 <https://github.com/libgit2/pygit2/issues/999>`_

Deprecations:

- Deprecate ``Repository.create_remote(...)``, use instead
  ``Repository.remotes.create(...)``

- Deprecate ``GIT_CREDTYPE_XXX`` contants, use ``GIT_CREDENTIAL_XXX`` instead.


1.2.0 (2020-04-05)
-------------------------

- Drop support for Python 3.5
  `#991 <https://github.com/libgit2/pygit2/issues/991>`_

- Upgrade to libgit2 1.0
  `#982 <https://github.com/libgit2/pygit2/pull/982>`_

- New support for custom reference database backends
  `#982 <https://github.com/libgit2/pygit2/pull/982>`_

- New support for path objects
  `#990 <https://github.com/libgit2/pygit2/pull/990>`_
  `#955 <https://github.com/libgit2/pygit2/issues/955>`_

- New ``index`` optional parameter in ``Repository.checkout_index``
  `#987 <https://github.com/libgit2/pygit2/pull/987>`_

- New MacOS wheels
  `#988 <https://github.com/libgit2/pygit2/pull/988>`_

- Fix re-raise exception from credentials callback in clone_repository
  `#996 <https://github.com/libgit2/pygit2/issues/996>`_

- Fix warning with ``pip install pygit2``
  `#986 <https://github.com/libgit2/pygit2/issues/986>`_

- Tests: disable global Git config
  `#989 <https://github.com/libgit2/pygit2/issues/989>`_


1.1.1 (2020-03-06)
-------------------------

- Fix crash in tree iteration
  `#984 <https://github.com/libgit2/pygit2/pull/984>`_
  `#980 <https://github.com/libgit2/pygit2/issues/980>`_

- Do not include the docs in dist files, so they're much smaller now


1.1.0 (2020-03-01)
-------------------------

- Upgrade to libgit2 0.99
  `#959 <https://github.com/libgit2/pygit2/pull/959>`_

- Continued work on custom odb backends
  `#948 <https://github.com/libgit2/pygit2/pull/948>`_

- New ``Diff.patchid`` getter
  `#960 <https://github.com/libgit2/pygit2/pull/960>`_
  `#877 <https://github.com/libgit2/pygit2/issues/877>`_

- New ``settings.disable_pack_keep_file_checks(...)``
  `#908 <https://github.com/libgit2/pygit2/pull/908>`_

- New ``GIT_DIFF_`` and ``GIT_DELTA_`` constants
  `#738 <https://github.com/libgit2/pygit2/issues/738>`_

- Fix crash in iteration of config entries
  `#970 <https://github.com/libgit2/pygit2/issues/970>`_

- Travis: fix printing features when building Linux wheels
  `#977 <https://github.com/libgit2/pygit2/pull/977>`_

- Move ``_pygit2`` to ``pygit2._pygit2``
  `#978 <https://github.com/libgit2/pygit2/pull/978>`_

Requirements changes:

- Now libgit2 0.99 is required
- New requirement: cached-property

Breaking changes:

- In the rare case you're directly importing the low level ``_pygit2``, the
  import has changed::

    # Before
    import _pygit2

    # Now
    from pygit2 import _pygit2


1.0.3 (2020-01-31)
-------------------------

- Fix memory leak in DiffFile
  `#943 <https://github.com/libgit2/pygit2/issues/943>`_


1.0.2 (2020-01-11)
-------------------------

- Fix enumerating tree entries with submodules
  `#967 <https://github.com/libgit2/pygit2/issues/967>`_


1.0.1 (2019-12-21)
-------------------------

- Fix build in Mac OS
  `#963 <https://github.com/libgit2/pygit2/issues/963>`_


1.0.0 (2019-12-06)
-------------------------

- Drop Python 2.7 and 3.4 support, six no longer required
  `#941 <https://github.com/libgit2/pygit2/issues/941>`_

- Add Python 3.8 support
  `#918 <https://github.com/libgit2/pygit2/issues/918>`_

- New support for ``/`` operator to traverse trees
  `#903 <https://github.com/libgit2/pygit2/pull/903>`_
  `#924 <https://github.com/libgit2/pygit2/issues/924>`_

- New ``Branch.raw_branch_name``
  `#954 <https://github.com/libgit2/pygit2/pull/954>`_

- New ``Index.remove_all()``
  `#920 <https://github.com/libgit2/pygit2/pull/920>`_

- New ``Remote.ls_remotes(..)``
  `#935 <https://github.com/libgit2/pygit2/pull/935>`_
  `#936 <https://github.com/libgit2/pygit2/issues/936>`_

- New ``Repository.lookup_reference_dwim(..)`` and ``Repository.resolve_refish(..)``
  `#922 <https://github.com/libgit2/pygit2/issues/922>`_
  `#923 <https://github.com/libgit2/pygit2/pull/923>`_

- New ``Repository.odb`` returns new ``Odb`` type instance. And new
  ``OdbBackend`` type.
  `#940 <https://github.com/libgit2/pygit2/pull/940>`_
  `#942 <https://github.com/libgit2/pygit2/pull/942>`_

- New ``Repository.references.compress()``
  `#961 <https://github.com/libgit2/pygit2/pull/961>`_

- Optimization: Load notes lazily
  `#958 <https://github.com/libgit2/pygit2/pull/958>`_

- Fix spurious exception in config
  `#916 <https://github.com/libgit2/pygit2/issues/916>`_
  `#917 <https://github.com/libgit2/pygit2/pull/917>`_

- Minor documentation and cosmetic changes
  `#919 <https://github.com/libgit2/pygit2/pull/919>`_
  `#921 <https://github.com/libgit2/pygit2/pull/921>`_
  `#946 <https://github.com/libgit2/pygit2/pull/946>`_
  `#950 <https://github.com/libgit2/pygit2/pull/950>`_

Breaking changes:

- Now the Repository has a new attribue ``odb`` for object database::

    # Before
    repository.read(...)
    repository.write(...)

    # Now
    repository.odb.read(...)
    repository.odb.write(...)

- Now ``Tree[x]`` returns a ``Object`` instance instead of a ``TreeEntry``;
  ``Object.type`` returns an integer while ``TreeEntry.type`` returned a
  string::

    # Before
    if tree[x].type == 'tree':

    # Now
    if tree[x].type == GIT_OBJ_TREE:
    if tree[x].type_str == 'tree':

- Renamed ``TreeEntry._name`` to ``Object.raw_name``::

    # Before
    tree[x]._name

    # Now
    tree[x].raw_name

- Object comparison is done by id. In the rare case you need to do tree-entry
  comparison or sorting::

    # Before
    tree[x] < tree[y]
    sorted(list(tree))

    # Now
    pygit2.tree_entry_cmp(x, y) < 0
    sorted(list(tree), key=pygit2.tree_entry_key)


0.28.2 (2019-05-26)
-------------------------

- Fix crash in reflog iteration
  `#901 <https://github.com/libgit2/pygit2/issues/901>`_

- Support symbolic references in ``branches.with_commit(..)``
  `#910 <https://github.com/libgit2/pygit2/issues/910>`_

- Documentation updates
  `#909 <https://github.com/libgit2/pygit2/pull/909>`_

- Test updates
  `#911 <https://github.com/libgit2/pygit2/pull/911>`_


0.28.1 (2019-04-19)
-------------------------

- Now works with pycparser 2.18 and above
  `#846 <https://github.com/libgit2/pygit2/issues/846>`_

- Now ``Repository.write_archive(..)`` keeps the file mode
  `#616 <https://github.com/libgit2/pygit2/issues/616>`_
  `#898 <https://github.com/libgit2/pygit2/pull/898>`_

- New ``Patch.data`` returns the raw contents of the patch as a byte string
  `#790 <https://github.com/libgit2/pygit2/pull/790>`_
  `#893 <https://github.com/libgit2/pygit2/pull/893>`_

- New ``Patch.text`` returns the contents of the patch as a text string,
  deprecates `Patch.patch`
  `#790 <https://github.com/libgit2/pygit2/pull/790>`_
  `#893 <https://github.com/libgit2/pygit2/pull/893>`_

Deprecations:

- ``Patch.patch`` is deprecated, use ``Patch.text`` instead


0.28.0 (2019-03-19)
-------------------------

- Upgrade to libgit2 0.28
  `#878 <https://github.com/libgit2/pygit2/issues/878>`_

- Add binary wheels for Linux
  `#793 <https://github.com/libgit2/pygit2/issues/793>`_
  `#869 <https://github.com/libgit2/pygit2/pull/869>`_
  `#874 <https://github.com/libgit2/pygit2/pull/874>`_
  `#875 <https://github.com/libgit2/pygit2/pull/875>`_
  `#883 <https://github.com/libgit2/pygit2/pull/883>`_

- New ``pygit2.Mailmap``, see documentation
  `#804 <https://github.com/libgit2/pygit2/pull/804>`_

- New ``Repository.apply(...)`` wraps ``git_apply(..)``
  `#841 <https://github.com/libgit2/pygit2/issues/841>`_
  `#843 <https://github.com/libgit2/pygit2/pull/843>`_

- Now ``Repository.merge_analysis(...)`` accepts an optional reference parameter
  `#888 <https://github.com/libgit2/pygit2/pull/888>`_
  `#891 <https://github.com/libgit2/pygit2/pull/891>`_

- Now ``Repository.add_worktree(...)`` accepts an optional reference parameter
  `#814 <https://github.com/libgit2/pygit2/issues/814>`_
  `#889 <https://github.com/libgit2/pygit2/pull/889>`_

- Now it's possible to set SSL certificate locations
  `#876 <https://github.com/libgit2/pygit2/issues/876>`_
  `#879 <https://github.com/libgit2/pygit2/pull/879>`_
  `#884 <https://github.com/libgit2/pygit2/pull/884>`_
  `#886 <https://github.com/libgit2/pygit2/pull/886>`_

- Test and documentation improvements
  `#873 <https://github.com/libgit2/pygit2/pull/873>`_
  `#887 <https://github.com/libgit2/pygit2/pull/887>`_

Breaking changes:

- Now ``worktree.path`` returns the path to the worktree directory, not to the
  `.git` file within
  `#803 <https://github.com/libgit2/pygit2/issues/803>`_

- Remove undocumented ``worktree.git_path``
  `#803 <https://github.com/libgit2/pygit2/issues/803>`_


0.27.4 (2019-01-19)
-------------------------

- New ``pygit2.LIBGIT2_VER`` tuple
  `#845 <https://github.com/libgit2/pygit2/issues/845>`_
  `#848 <https://github.com/libgit2/pygit2/pull/848>`_

- New objects now support (in)equality comparison and hash
  `#852 <https://github.com/libgit2/pygit2/issues/852>`_
  `#853 <https://github.com/libgit2/pygit2/pull/853>`_

- New references now support (in)equality comparison
  `#860 <https://github.com/libgit2/pygit2/issues/860>`_
  `#862 <https://github.com/libgit2/pygit2/pull/862>`_

- New ``paths`` optional argument in ``Repository.checkout()``
  `#858 <https://github.com/libgit2/pygit2/issues/858>`_
  `#859 <https://github.com/libgit2/pygit2/pull/859>`_

- Fix speed and windows package regression
  `#849 <https://github.com/libgit2/pygit2/issues/849>`_
  `#857 <https://github.com/libgit2/pygit2/issues/857>`_
  `#851 <https://github.com/libgit2/pygit2/pull/851>`_

- Fix deprecation warning
  `#850 <https://github.com/libgit2/pygit2/pull/850>`_

- Documentation fixes
  `#855 <https://github.com/libgit2/pygit2/pull/855>`_

- Add Python classifiers to setup.py
  `#861 <https://github.com/libgit2/pygit2/pull/861>`_

- Speeding up tests in Travis
  `#854 <https://github.com/libgit2/pygit2/pull/854>`_

Breaking changes:

- Remove deprecated `Reference.get_object()`, use `Reference.peel()` instead


0.27.3 (2018-12-15)
-------------------------

- Move to pytest, drop support for Python 3.3 and cffi 0.x
  `#824 <https://github.com/libgit2/pygit2/issues/824>`_
  `#826 <https://github.com/libgit2/pygit2/pull/826>`_
  `#833 <https://github.com/libgit2/pygit2/pull/833>`_
  `#834 <https://github.com/libgit2/pygit2/pull/834>`_

- New support comparing signatures for (in)equality

- New ``Submodule.head_id``
  `#817 <https://github.com/libgit2/pygit2/pull/817>`_

- New ``Remote.prune(...)``
  `#825 <https://github.com/libgit2/pygit2/pull/825>`_

- New ``pygit2.reference_is_valid_name(...)``
  `#827 <https://github.com/libgit2/pygit2/pull/827>`_

- New ``AlreadyExistsError`` and ``InvalidSpecError``
  `#828 <https://github.com/libgit2/pygit2/issues/828>`_
  `#829 <https://github.com/libgit2/pygit2/pull/829>`_

- New ``Reference.raw_name``, ``Reference.raw_shorthand``, ``Tag.raw_name``,
  ``Tag.raw_message`` and ``DiffFile.raw_path``
  `#840 <https://github.com/libgit2/pygit2/pull/840>`_

- Fix decode error in commit messages and signatures
  `#839 <https://github.com/libgit2/pygit2/issues/839>`_

- Fix, raise error in ``Repository.descendant_of(...)`` if commit doesn't exist
  `#822 <https://github.com/libgit2/pygit2/issues/822>`_
  `#842 <https://github.com/libgit2/pygit2/pull/842>`_

- Documentation fixes
  `#821 <https://github.com/libgit2/pygit2/pull/821>`_

Breaking changes:

- Remove undocumented ``Tag._message``, replaced by ``Tag.raw_message``


0.27.2 (2018-09-16)
-------------------------

- Add support for Python 3.7
  `#809 <https://github.com/libgit2/pygit2/issues/809>`_

- New ``Object.short_id``
  `#799 <https://github.com/libgit2/pygit2/issues/799>`_
  `#806 <https://github.com/libgit2/pygit2/pull/806>`_
  `#807 <https://github.com/libgit2/pygit2/pull/807>`_

- New ``Repository.descendant_of`` and ``Repository.branches.with_commit``
  `#815 <https://github.com/libgit2/pygit2/issues/815>`_
  `#816 <https://github.com/libgit2/pygit2/pull/816>`_

- Fix repository initialization in ``clone_repository(...)``
  `#818 <https://github.com/libgit2/pygit2/issues/818>`_

- Fix several warnings and errors, commits
  `cd896ddc <https://github.com/libgit2/pygit2/commit/cd896ddc>`_
  and
  `dfa536a3 <https://github.com/libgit2/pygit2/commit/dfa536a3>`_

- Documentation fixes and improvements
  `#805 <https://github.com/libgit2/pygit2/pull/805>`_
  `#808 <https://github.com/libgit2/pygit2/pull/808>`_


0.27.1 (2018-06-02)
-------------------------

Breaking changes:

- Now ``discover_repository`` returns ``None`` if repository not found, instead
  of raising ``KeyError``
  `#531 <https://github.com/libgit2/pygit2/issues/531>`_

Other changes:

- New ``DiffLine.raw_content``
  `#610 <https://github.com/libgit2/pygit2/issues/610>`_

- Fix tests failing in some cases
  `#795 <https://github.com/libgit2/pygit2/issues/795>`_

- Automatize wheels upload to pypi
  `#563 <https://github.com/libgit2/pygit2/issues/563>`_


0.27.0 (2018-03-30)
-------------------------

- Update to libgit2 v0.27
  `#783 <https://github.com/libgit2/pygit2/pull/783>`_

- Fix for GCC 4
  `#786 <https://github.com/libgit2/pygit2/pull/786>`_


0.26.4 (2018-03-23)
-------------------------

Backward incompatible changes:

- Now iterating over a configuration returns ``ConfigEntry`` objects
  `#778 <https://github.com/libgit2/pygit2/pull/778>`_

  ::

    # Before
    for name in config:
        value = config[name]

    # Now
    for entry in config:
        name = entry.name
        value = entry.value

Other changes:

- Added support for worktrees
  `#779 <https://github.com/libgit2/pygit2/pull/779>`_

- New ``Commit.gpg_signature``
  `#766 <https://github.com/libgit2/pygit2/pull/766>`_

- New static ``Diff.parse_diff(...)``
  `#774 <https://github.com/libgit2/pygit2/pull/774>`_

- New optional argument ``callbacks`` in ``Repository.update_submodules(...)``
  `#763 <https://github.com/libgit2/pygit2/pull/763>`_

- New ``KeypairFromMemory`` credentials
  `#771 <https://github.com/libgit2/pygit2/pull/771>`_

- Add missing status constants
  `#781 <https://github.com/libgit2/pygit2/issues/781>`_

- Fix segfault
  `#775 <https://github.com/libgit2/pygit2/issues/775>`_

- Fix some unicode decode errors with Python 2
  `#767 <https://github.com/libgit2/pygit2/pull/767>`_
  `#768 <https://github.com/libgit2/pygit2/pull/768>`_

- Documentation improvements
  `#721 <https://github.com/libgit2/pygit2/pull/721>`_
  `#769 <https://github.com/libgit2/pygit2/pull/769>`_
  `#770 <https://github.com/libgit2/pygit2/pull/770>`_


0.26.3 (2017-12-24)
-------------------------

- New ``Diff.deltas``
  `#736 <https://github.com/libgit2/pygit2/issues/736>`_

- Improvements to ``Patch.create_from``
  `#753 <https://github.com/libgit2/pygit2/pull/753>`_
  `#756 <https://github.com/libgit2/pygit2/pull/756>`_
  `#759 <https://github.com/libgit2/pygit2/pull/759>`_

- Fix build and tests in Windows, broken in the previous release
  `#749 <https://github.com/libgit2/pygit2/pull/749>`_
  `#751 <https://github.com/libgit2/pygit2/pull/751>`_

- Review ``Patch.patch``
  `#757 <https://github.com/libgit2/pygit2/issues/757>`_

- Workaround bug `#4442 <https://github.com/libgit2/libgit2/issues/4442>`_
  in libgit2, and improve unit tests
  `#748 <https://github.com/libgit2/pygit2/issues/748>`_
  `#754 <https://github.com/libgit2/pygit2/issues/754>`_
  `#758 <https://github.com/libgit2/pygit2/pull/758>`_
  `#761 <https://github.com/libgit2/pygit2/pull/761>`_


0.26.2 (2017-12-01)
-------------------------

- New property ``Patch.patch``
  `#739 <https://github.com/libgit2/pygit2/issues/739>`_
  `#741 <https://github.com/libgit2/pygit2/pull/741>`_

- New static method ``Patch.create_from``
  `#742 <https://github.com/libgit2/pygit2/issues/742>`_
  `#744 <https://github.com/libgit2/pygit2/pull/744>`_

- New parameter ``prune`` in ``Remote.fetch``
  `#743 <https://github.com/libgit2/pygit2/pull/743>`_

- Tests: skip tests that require network when there is not
  `#737 <https://github.com/libgit2/pygit2/issues/737>`_

- Tests: other improvements
  `#740 <https://github.com/libgit2/pygit2/pull/740>`_

- Documentation improvements


0.26.1 (2017-11-19)
-------------------------

- New ``Repository.free()``
  `#730 <https://github.com/libgit2/pygit2/pull/730>`_

- Improve credentials handling for ssh cloning
  `#718 <https://github.com/libgit2/pygit2/pull/718>`_

- Documentation improvements
  `#714 <https://github.com/libgit2/pygit2/pull/714>`_
  `#715 <https://github.com/libgit2/pygit2/pull/715>`_
  `#728 <https://github.com/libgit2/pygit2/pull/728>`_
  `#733 <https://github.com/libgit2/pygit2/pull/733>`_
  `#734 <https://github.com/libgit2/pygit2/pull/734>`_
  `#735 <https://github.com/libgit2/pygit2/pull/735>`_


0.26.0 (2017-07-06)
-------------------------

- Update to libgit2 v0.26
  `#713 <https://github.com/libgit2/pygit2/pull/713>`_

- Drop support for Python 3.2, add support for cffi 1.10
  `#706 <https://github.com/libgit2/pygit2/pull/706>`_
  `#694 <https://github.com/libgit2/pygit2/issues/694>`_

- New ``Repository.revert_commit(...)``
  `#711 <https://github.com/libgit2/pygit2/pull/711>`_
  `#710 <https://github.com/libgit2/pygit2/issues/710>`_

- New ``Branch.is_checked_out()``
  `#696 <https://github.com/libgit2/pygit2/pull/696>`_

- Various fixes
  `#706 <https://github.com/libgit2/pygit2/pull/706>`_
  `#707 <https://github.com/libgit2/pygit2/pull/707>`_
  `#708 <https://github.com/libgit2/pygit2/pull/708>`_


0.25.1 (2017-04-25)
-------------------------

- Add support for Python 3.6

- New support for stash: repository methods ``stash``, ``stash_apply``,
  ``stash_drop`` and ``stash_pop``
  `#695 <https://github.com/libgit2/pygit2/pull/695>`_

- Improved support for submodules: new repository methods ``init_submodules``
  and ``update_submodules``
  `#692 <https://github.com/libgit2/pygit2/pull/692>`_

- New friendlier API for branches & references: ``Repository.branches`` and
  ``Repository.references``
  `#700 <https://github.com/libgit2/pygit2/pull/700>`_
  `#701 <https://github.com/libgit2/pygit2/pull/701>`_

- New support for custom backends
  `#690 <https://github.com/libgit2/pygit2/pull/690>`_

- Fix ``init_repository`` crash on None input
  `#688 <https://github.com/libgit2/pygit2/issues/688>`_
  `#697 <https://github.com/libgit2/pygit2/pull/697>`_

- Fix checkout with an orphan master branch
  `#669 <https://github.com/libgit2/pygit2/issues/669>`_
  `#685 <https://github.com/libgit2/pygit2/pull/685>`_

- Better error messages for opening repositories
  `#645 <https://github.com/libgit2/pygit2/issues/645>`_
  `#698 <https://github.com/libgit2/pygit2/pull/698>`_


0.25.0 (2016-12-26)
-------------------------

- Upgrade to libgit2 0.25
  `#670 <https://github.com/libgit2/pygit2/pull/670>`_

- Now Commit.tree raises an error if tree is not found
  `#682 <https://github.com/libgit2/pygit2/pull/682>`_

- New settings.mwindow_mapped_limit, cached_memory, enable_caching,
  cache_max_size and cache_object_limit
  `#677 <https://github.com/libgit2/pygit2/pull/677>`_


0.24.2 (2016-11-01)
-------------------------

- Unit tests pass on Windows, integration with AppVeyor
  `#641 <https://github.com/libgit2/pygit2/pull/641>`_
  `#655 <https://github.com/libgit2/pygit2/issues/655>`_
  `#657 <https://github.com/libgit2/pygit2/pull/657>`_
  `#659 <https://github.com/libgit2/pygit2/pull/659>`_
  `#660 <https://github.com/libgit2/pygit2/pull/660>`_
  `#661 <https://github.com/libgit2/pygit2/pull/661>`_
  `#667 <https://github.com/libgit2/pygit2/pull/667>`_

- Fix when libgit2 error messages have non-ascii chars
  `#651 <https://github.com/libgit2/pygit2/pull/651>`_

- Documentation improvements
  `#643 <https://github.com/libgit2/pygit2/pull/643>`_
  `#653 <https://github.com/libgit2/pygit2/pull/653>`_
  `#663 <https://github.com/libgit2/pygit2/pull/663>`_


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
