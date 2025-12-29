# 1.19.1 (2025-12-29)

- Update wheels to libgit2 1.9.2 and OpenSSL 3.5

- Fix: now diff's getitem/iter returns `None` for unchanged or binary files
  [#1412](https://github.com/libgit2/pygit2/pull/1412)

- CI (macOS): arm, intel and pypy wheels (instead of universal)
  [#1441](https://github.com/libgit2/pygit2/pull/1441)

- CI (pypy): fix tests
  [#1437](https://github.com/libgit2/pygit2/pull/1437)


# 1.19.0 (2025-10-23)

- Add support for Python 3.14 and drop 3.10

- Support threaded builds (experimental)
  [#1430](https://github.com/libgit2/pygit2/pull/1430)
  [#1435](https://github.com/libgit2/pygit2/pull/1435)

- Add Linux musl wheels for AArch64

- Add Windows wheels for AArch64;
  CI: build Windows wheels with cibuildwheel on GitHub
  [#1423](https://github.com/libgit2/pygit2/pull/1423)

- New `Repository.transaction()` context manager, returns new `ReferenceTransaction`
  [#1420](https://github.com/libgit2/pygit2/pull/1420)

- CI: add GitHub releases and other improvements
  [#1433](https://github.com/libgit2/pygit2/pull/1433)
  [#1432](https://github.com/libgit2/pygit2/pull/1432)
  [#1425](https://github.com/libgit2/pygit2/pull/1425)
  [#1431](https://github.com/libgit2/pygit2/pull/1431)

- Documentation improvements and other changes
  [#1426](https://github.com/libgit2/pygit2/pull/1426)
  [#1424](https://github.com/libgit2/pygit2/pull/1424)

Breaking changes:

- Remove deprecated `IndexEntry.hex`, use `str(entry.id)` instead of `entry.hex`

Deprecations:

- Deprecate `IndexEntry.oid`, use `entry.id` instead of `entry.oid`

# 1.18.2 (2025-08-16)

- Add support for almost all global options
  [#1409](https://github.com/libgit2/pygit2/pull/1409)

- Now it's possible to set `Submodule.url = url`
  [#1395](https://github.com/libgit2/pygit2/pull/1395)

- New `RemoteCallbacks.push_negotiation(...)`
  [#1396](https://github.com/libgit2/pygit2/pull/1396)

- New optional boolean argument `connect` in `Remote.ls_remotes(...)`
  [#1396](https://github.com/libgit2/pygit2/pull/1396)

- New `Remote.list_heads(...)` returns a list of `RemoteHead` objects
  [#1397](https://github.com/libgit2/pygit2/pull/1397)
  [#1410](https://github.com/libgit2/pygit2/pull/1410)

- Documentation fixes
  [#1388](https://github.com/libgit2/pygit2/pull/1388)

- Typing improvements
  [#1387](https://github.com/libgit2/pygit2/pull/1387)
  [#1389](https://github.com/libgit2/pygit2/pull/1389)
  [#1390](https://github.com/libgit2/pygit2/pull/1390)
  [#1391](https://github.com/libgit2/pygit2/pull/1391)
  [#1392](https://github.com/libgit2/pygit2/pull/1392)
  [#1393](https://github.com/libgit2/pygit2/pull/1393)
  [#1394](https://github.com/libgit2/pygit2/pull/1394)
  [#1398](https://github.com/libgit2/pygit2/pull/1398)
  [#1399](https://github.com/libgit2/pygit2/pull/1399)
  [#1400](https://github.com/libgit2/pygit2/pull/1400)
  [#1402](https://github.com/libgit2/pygit2/pull/1402)
  [#1403](https://github.com/libgit2/pygit2/pull/1403)
  [#1406](https://github.com/libgit2/pygit2/pull/1406)
  [#1407](https://github.com/libgit2/pygit2/pull/1407)
  [#1408](https://github.com/libgit2/pygit2/pull/1408)

Deprecations:

- `Remote.ls_remotes(...)` is deprecated, use `Remote.list_heads(...)`:

      # Before
      for head in remote.ls_remotes():
          head['name']
          head['oid']
          head['loid']  # None when local is False
          head['local']
          head['symref_target']

      # Now
      for head in remote.list_heads():
          head.name
          head.oid
          head.loid  # The zero oid when local is False
          head.local
          head.symref_target


# 1.18.1 (2025-07-26)

- Update wheels to libgit2 1.9.1 and OpenSSL 3.3

- New `Index.remove_directory(...)`
  [#1377](https://github.com/libgit2/pygit2/pull/1377)

- New `Index.add_conflict(...)`
  [#1382](https://github.com/libgit2/pygit2/pull/1382)

- Now `Repository.merge_file_from_index(...)` returns a `MergeFileResult` object when
  called with `use_deprecated=False`
  [#1376](https://github.com/libgit2/pygit2/pull/1376)

- Typing improvements
  [#1369](https://github.com/libgit2/pygit2/pull/1369)
  [#1370](https://github.com/libgit2/pygit2/pull/1370)
  [#1371](https://github.com/libgit2/pygit2/pull/1371)
  [#1373](https://github.com/libgit2/pygit2/pull/1373)
  [#1384](https://github.com/libgit2/pygit2/pull/1384)
  [#1386](https://github.com/libgit2/pygit2/pull/1386)

Deprecations:

- Update your code:

      # Before
      contents = Repository.merge_file_from_index(...)

      # Now
      result = Repository.merge_file_from_index(..., use_deprecated=False)
      contents = result.contents

  At some point in the future `use_deprecated=False` will be the default.


# 1.18.0 (2025-04-24)

- Upgrade Linux Glibc wheels to `manylinux_2_28`

- Add `RemoteCallbacks.push_transfer_progress(...)` callback
  [#1345](https://github.com/libgit2/pygit2/pull/1345)

- New `bool(oid)`
  [#1347](https://github.com/libgit2/pygit2/pull/1347)

- Now `Repository.merge(...)` accepts a commit or reference object
  [#1348](https://github.com/libgit2/pygit2/pull/1348)

- New `threads` optional argument in `Remote.push(...)`
  [#1352](https://github.com/libgit2/pygit2/pull/1352)

- New `proxy` optional argument in `clone_repository(...)`
  [#1354](https://github.com/libgit2/pygit2/pull/1354)

- New optional arguments `context_lines` and `interhunk_lines` in `Blob.diff(...)` ; and
  now `Repository.diff(...)` honors these two arguments when the objects diffed are blobs.
  [#1360](https://github.com/libgit2/pygit2/pull/1360)

- Now `Tree.diff_to_workdir(...)` accepts keyword arguments, not just positional.

- Fix when a reference name has non UTF-8 chars
  [#1329](https://github.com/libgit2/pygit2/pull/1329)

- Fix condition check in `Repository.remotes.rename(...)`
  [#1342](https://github.com/libgit2/pygit2/pull/1342)

- Add codespell workflow, fix a number of typos
  [#1344](https://github.com/libgit2/pygit2/pull/1344)

- Documentation and typing
  [#1343](https://github.com/libgit2/pygit2/pull/1343)
  [#1347](https://github.com/libgit2/pygit2/pull/1347)
  [#1356](https://github.com/libgit2/pygit2/pull/1356)

- CI: Use ARM runner for tests and wheels
  [#1346](https://github.com/libgit2/pygit2/pull/1346)

- Build and CI updates
  [#1363](https://github.com/libgit2/pygit2/pull/1363)
  [#1365](https://github.com/libgit2/pygit2/pull/1365)

Deprecations:

- Passing str to `Repository.merge(...)` is deprecated,
  instead pass an oid object (or a commit, or a reference)
  [#1349](https://github.com/libgit2/pygit2/pull/1349)

Breaking changes:

- Keyword argument `flag` has been renamed to `flags` in `Blob.diff(...)` and
  `Blob.diff_to_buffer(...)`


# 1.17.0 (2025-01-08)

- Upgrade to libgit2 1.9

- Add `certificate_check` callback to `Remote.ls_remotes(...)`
  [#1326](https://github.com/libgit2/pygit2/pull/1326)

- Fix build with GCC 14
  [#1324](https://github.com/libgit2/pygit2/pull/1324)

- Release wheels for PyPy
  [#1336](https://github.com/libgit2/pygit2/pull/1336)
  [#1339](https://github.com/libgit2/pygit2/pull/1339)

- CI: update tests for macOS to use OpenSSL 3
  [#1335](https://github.com/libgit2/pygit2/pull/1335)

- Documentation: fix typo in `Repository.status(...)` docstring
  [#1327](https://github.com/libgit2/pygit2/pull/1327)


# 1.16.0 (2024-10-11)

- Add support for Python 3.13

- Drop support for Python 3.9

- New `Repository.hashfile(...)`
  [#1298](https://github.com/libgit2/pygit2/pull/1298)

- New `Option.GET_MWINDOW_FILE_LIMIT` and `Option.SET_MWINDOW_FILE_LIMIT`
  [#1312](https://github.com/libgit2/pygit2/pull/1312)

- Fix overriding `certificate_check(...)` callback via argument to `RemoteCallbacks(...)`
  [#1321](https://github.com/libgit2/pygit2/pull/1321)

- Add py.typed
  [#1310](https://github.com/libgit2/pygit2/pull/1310)

- Fix `discover_repository(...)` annotation
  [#1313](https://github.com/libgit2/pygit2/pull/1313)


# 1.15.1 (2024-07-07)

- New `Repository.revert(...)`
  [#1297](https://github.com/libgit2/pygit2/pull/1297)

- New optional `depth` argument in submodules `add()` and `update()` methods
  [#1296](https://github.com/libgit2/pygit2/pull/1296)

- Now `Submodule.url` returns `None` when the submodule does not have a url
  [#1294](https://github.com/libgit2/pygit2/pull/1294)

- Fix use after free bug in error reporting
  [#1299](https://github.com/libgit2/pygit2/pull/1299)

- Fix `Submodule.head_id` when the submodule is not in the current HEAD tree
  [#1300](https://github.com/libgit2/pygit2/pull/1300)

- Fix `Submodule.open()` when subclassing `Repository`
  [#1295](https://github.com/libgit2/pygit2/pull/1295)

- Fix error in the test suite when running with address sanitizer
  [#1304](https://github.com/libgit2/pygit2/pull/1304)
  [#1301](https://github.com/libgit2/pygit2/issues/1301)

- Annotations and documentation fixes
  [#1293](https://github.com/libgit2/pygit2/pull/1293)


# 1.15.0 (2024-05-18)

- Many deprecated features have been removed, see below

- Upgrade to libgit2 v1.8.1

- New `push_options` optional argument in `Repository.push(...)`
  [#1282](https://github.com/libgit2/pygit2/pull/1282)

- New support comparison of `Oid` with text string

- Fix `CheckoutNotify.IGNORED`
  [#1288](https://github.com/libgit2/pygit2/issues/1288)

- Use default error handler when decoding/encoding paths
  [#537](https://github.com/libgit2/pygit2/issues/537)

- Remove setuptools runtime dependency
  [#1281](https://github.com/libgit2/pygit2/pull/1281)

- Coding style with ruff
  [#1280](https://github.com/libgit2/pygit2/pull/1280)

- Add wheels for ppc64le
  [#1279](https://github.com/libgit2/pygit2/pull/1279)

- Fix tests on EPEL8 builds for s390x
  [#1283](https://github.com/libgit2/pygit2/pull/1283)

Deprecations:

- Deprecate `IndexEntry.hex`, use `str(IndexEntry.id)`

Breaking changes:

- Remove deprecated `oid.hex`, use `str(oid)`
- Remove deprecated `object.hex`, use `str(object.id)`
- Remove deprecated `object.oid`, use `object.id`

- Remove deprecated `Repository.add_submodule(...)`, use `Repository.submodules.add(...)`
- Remove deprecated `Repository.lookup_submodule(...)`, use `Repository.submodules[...]`
- Remove deprecated `Repository.init_submodules(...)`, use `Repository.submodules.init(...)`
- Remove deprecated `Repository.update_submodule(...)`, use `Repository.submodules.update(...)`

- Remove deprecated constants `GIT_OBJ_XXX`, use `ObjectType`
- Remove deprecated constants `GIT_REVPARSE_XXX`, use `RevSpecFlag`
- Remove deprecated constants `GIT_REF_XXX`, use `ReferenceType`
- Remove deprecated `ReferenceType.OID`, use instead `ReferenceType.DIRECT`
- Remove deprecated `ReferenceType.LISTALL`, use instead `ReferenceType.ALL`

- Remove deprecated support for passing dicts to repository\'s `merge(...)`,
  `merge_commits(...)` and `merge_trees(...)`. Instead pass `MergeFlag` for `flags`, and
  `MergeFileFlag` for `file_flags`.

- Remove deprecated support for passing a string for the favor argument to repository\'s
  `merge(...)`, `merge_commits(...)` and `merge_trees(...)`. Instead pass `MergeFavor`.


# 1.14.1 (2024-02-10)

- Update wheels to libgit2 v1.7.2

- Now `Object.filemode` returns `enums.FileMode` and `Reference.type` returns
  `enums.ReferenceType`
  [#1273](https://github.com/libgit2/pygit2/pull/1273)

- Fix tests on Fedora 40
  [#1275](https://github.com/libgit2/pygit2/pull/1275)

Deprecations:

- Deprecate `ReferenceType.OID`, use `ReferenceType.DIRECT`
- Deprecate `ReferenceType.LISTALL`, use `ReferenceType.ALL`

# 1.14.0 (2024-01-26)

- Drop support for Python 3.8

- Add Linux wheels for musl on x86\_64
  [#1266](https://github.com/libgit2/pygit2/pull/1266)

- New `Repository.submodules` namespace
  [#1250](https://github.com/libgit2/pygit2/pull/1250)

- New `Repository.listall_mergeheads()`, `Repository.message`,
  `Repository.raw_message` and `Repository.remove_message()`
  [#1261](https://github.com/libgit2/pygit2/pull/1261)

- New `pygit2.enums` supersedes the `GIT_` constants
  [#1251](https://github.com/libgit2/pygit2/pull/1251)

- Now `Repository.status()`, `Repository.status_file()`,
  `Repository.merge_analysis()`, `DiffFile.flags`, `DiffFile.mode`,
  `DiffDelta.flags` and `DiffDelta.status` return enums
  [#1263](https://github.com/libgit2/pygit2/pull/1263)

- Now repository\'s `merge()`, `merge_commits()` and `merge_trees()`
  take enums/flags for their `favor`, `flags` and `file_flags` arguments.
  [#1271](https://github.com/libgit2/pygit2/pull/1271)
  [#1272](https://github.com/libgit2/pygit2/pull/1272)

- Fix crash in filter cleanup
  [#1259](https://github.com/libgit2/pygit2/pull/1259)

- Documentation fixes
  [#1255](https://github.com/libgit2/pygit2/pull/1255)
  [#1258](https://github.com/libgit2/pygit2/pull/1258)
  [#1268](https://github.com/libgit2/pygit2/pull/1268)
  [#1270](https://github.com/libgit2/pygit2/pull/1270)

Breaking changes:

-   Remove deprecated `Repository.create_remote(...)` function, use
    instead `Repository.remotes.create(...)`

Deprecations:

- Deprecate `Repository.add_submodule(...)`, use `Repository.submodules.add(...)`
- Deprecate `Repository.lookup_submodule(...)`, use `Repository.submodules[...]`
- Deprecate `Repository.init_submodules(...)`, use `Repository.submodules.init(...)`
- Deprecate `Repository.update_submodule(...)`, use `Repository.submodules.update(...)`
- Deprecate `GIT_*` constants, use `pygit2.enums`

- Passing dicts to repository\'s `merge(...)`, `merge_commits(...)` and `merge_trees(...)`
  is deprecated. Instead pass `MergeFlag` for the `flags` argument, and `MergeFileFlag` for
  `file_flags`.

- Passing a string for the favor argument to repository\'s `merge(...)`, `merge_commits(...)`
  and `merge_trees(...)` is deprecated. Instead pass `MergeFavor`.

# 1.13.3 (2023-11-21)

-   New API for filters in Python
    [#1237](https://github.com/libgit2/pygit2/pull/1237)
    [#1244](https://github.com/libgit2/pygit2/pull/1244)
-   Shallow repositories: New `depth` optional argument for
    `clone_repository(...)` and `Remote.fetch(...)`
    [#1245](https://github.com/libgit2/pygit2/pull/1245)
    [#1246](https://github.com/libgit2/pygit2/pull/1246)
-   New submodule `init(...)`, `update(...)` and `reload(...)` functions
    [#1248](https://github.com/libgit2/pygit2/pull/1248)
-   Release GIL in `Walker.__next__`
    [#1249](https://github.com/libgit2/pygit2/pull/1249)
-   Type hints for submodule functions in `Repository`
    [#1247](https://github.com/libgit2/pygit2/pull/1247)

# 1.13.2 (2023-10-30)

-   Support Python 3.12
-   Documentation updates
    [#1242](https://github.com/libgit2/pygit2/pull/1242)

# 1.13.1 (2023-09-24)

-   Fix crash in reference rename
    [#1233](https://github.com/libgit2/pygit2/issues/1233)

# 1.13.0 (2023-09-07)

-   Upgrade to libgit2 v1.7.1
-   Don\'t distribute wheels for pypy, only universal wheels for macOS
-   New `Repository.remotes.create_anonymous(url)`
    [#1229](https://github.com/libgit2/pygit2/pull/1229)
-   docs: update links to pypi, pygit2.org
    [#1228](https://github.com/libgit2/pygit2/pull/1228)
-   Prep work for Python 3.12 (not yet supported)
    [#1223](https://github.com/libgit2/pygit2/pull/1223)

# 1.12.2 (2023-06-25)

-   Update wheels to bundle libssh2 1.11.0 and OpenSSL 3.0.9
-   Remove obsolete `Remote.save()`
    [#1219](https://github.com/libgit2/pygit2/issues/1219)

# 1.12.1 (2023-05-07)

-   Fix segfault in signature when encoding is incorrect
    [#1210](https://github.com/libgit2/pygit2/pull/1210)
-   Typing improvements
    [#1212](https://github.com/libgit2/pygit2/pull/1212)
    [#1214](https://github.com/libgit2/pygit2/pull/1214)
-   Update wheels to libgit2 v1.6.4

# 1.12.0 (2023-04-01)

-   Upgrade to libgit2 v1.6.3
-   Update Linux wheels to bundle OpenSSL 3.0.8
-   Downgrade Linux wheels to manylinux2014
-   New `ConflictCollection.__contains__`
    [#1181](https://github.com/libgit2/pygit2/pull/1181)
-   New `Repository.references.iterator(...)`
    [#1191](https://github.com/libgit2/pygit2/pull/1191)
-   New `favor`, `flags` and `file_flags` optional arguments for
    `Repository.merge(...)`
    [#1192](https://github.com/libgit2/pygit2/pull/1192)
-   New `keep_all` and `paths` optional arguments for
    `Repository.stash(...)`
    [#1202](https://github.com/libgit2/pygit2/pull/1202)
-   New `Repository.state()`
    [#1204](https://github.com/libgit2/pygit2/pull/1204)
-   Improve `Repository.write_archive(...)` performance
    [#1183](https://github.com/libgit2/pygit2/pull/1183)
-   Sync type annotations
    [#1203](https://github.com/libgit2/pygit2/pull/1203)

# 1.11.1 (2022-11-09)

-   Fix Linux wheels, downgrade to manylinux 2_24
    [#1176](https://github.com/libgit2/pygit2/issues/1176)
-   Windows wheels for Python 3.11
    [#1177](https://github.com/libgit2/pygit2/pull/1177)
-   CI: Use 3.11 final release for testing
    [#1178](https://github.com/libgit2/pygit2/pull/1178)

# 1.11.0 (2022-11-06)

-   Drop support for Python 3.7
-   Update Linux wheels to manylinux 2_28
    [#1136](https://github.com/libgit2/pygit2/issues/1136)
-   Fix crash in signature representation
    [#1162](https://github.com/libgit2/pygit2/pull/1162)
-   Fix memory leak in `Signature`
    [#1173](https://github.com/libgit2/pygit2/pull/1173)
-   New optional argument `raise_error` in `Repository.applies(...)`
    [#1166](https://github.com/libgit2/pygit2/pull/1166)
-   New notify/progress callbacks for checkout and stash
    [#1167](https://github.com/libgit2/pygit2/pull/1167)
    [#1169](https://github.com/libgit2/pygit2/pull/1169)
-   New `Repository.remotes.names()`
    [#1159](https://github.com/libgit2/pygit2/pull/1159)
-   Now `refname` argument in
    `RemoteCallbacks.push_update_reference(...)` is a string, not bytes
    [#1168](https://github.com/libgit2/pygit2/pull/1168)
-   Add missing newline at end of `pygit2/decl/pack.h`
    [#1163](https://github.com/libgit2/pygit2/pull/1163)

# 1.10.1 (2022-08-28)

-   Fix segfault in `Signature` repr
    [#1155](https://github.com/libgit2/pygit2/pull/1155)
-   Linux and macOS wheels for Python 3.11
    [#1154](https://github.com/libgit2/pygit2/pull/1154)

# 1.10.0 (2022-07-24)

-   Upgrade to libgit2 1.5
-   Add support for `GIT_OPT_GET_OWNER_VALIDATION` and
    `GIT_OPT_SET_OWNER_VALIDATION`
    [#1150](https://github.com/libgit2/pygit2/pull/1150)
-   New `untracked_files` and `ignored` optional arguments for
    `Repository.status(...)`
    [#1151](https://github.com/libgit2/pygit2/pull/1151)

# 1.9.2 (2022-05-24)

-   New `Repository.create_commit_string(...)` and
    `Repository.create_commit_with_signature(...)`
    [#1142](https://github.com/libgit2/pygit2/pull/1142)
-   Linux and macOS wheels updated to libgit2 v1.4.3
-   Remove redundant line
    [#1139](https://github.com/libgit2/pygit2/pull/1139)

# 1.9.1 (2022-03-22)

-   Type hints: added to C code and Branches/References
    [#1121](https://github.com/libgit2/pygit2/pull/1121)
    [#1132](https://github.com/libgit2/pygit2/pull/1132)
-   New `Signature` supports `str()` and `repr()`
    [#1135](https://github.com/libgit2/pygit2/pull/1135)
-   Fix ODB backend\'s read in big endian architectures
    [#1130](https://github.com/libgit2/pygit2/pull/1130)
-   Fix install with poetry
    [#1129](https://github.com/libgit2/pygit2/pull/1129)
    [#1128](https://github.com/libgit2/pygit2/issues/1128)
-   Wheels: update to libgit2 v1.4.2
-   Tests: fix testing `parse_diff`
    [#1131](https://github.com/libgit2/pygit2/pull/1131)
-   CI: various fixes after migration to libgit2 v1.4

# 1.9.0 (2022-02-22)

-   Upgrade to libgit2 v1.4
-   Documentation, new recipes for committing and cloning
    [#1125](https://github.com/libgit2/pygit2/pull/1125)

# 1.8.0 (2022-02-04)

-   Rename `RemoteCallbacks.progress(...)` callback to
    `.sideband_progress(...)`
    [#1120](https://github.com/libgit2/pygit2/pull/1120)
-   New `Repository.merge_base_many(...)` and
    `Repository.merge_base_octopus(...)`
    [#1112](https://github.com/libgit2/pygit2/pull/1112)
-   New `Repository.listall_stashes()`
    [#1117](https://github.com/libgit2/pygit2/pull/1117)
-   Code cleanup [#1118](https://github.com/libgit2/pygit2/pull/1118)

Backward incompatible changes:

-   The `RemoteCallbacks.progress(...)` callback has been renamed to
    `RemoteCallbacks.sideband_progress(...)`. This matches the
    documentation, but may break existing code that still uses the old
    name.

# 1.7.2 (2021-12-06)

-   Universal wheels for macOS
    [#1109](https://github.com/libgit2/pygit2/pull/1109)

# 1.7.1 (2021-11-19)

-   New `Repository.amend_commit(...)`
    [#1098](https://github.com/libgit2/pygit2/pull/1098)
-   New `Commit.message_trailers`
    [#1101](https://github.com/libgit2/pygit2/pull/1101)
-   Windows wheels for Python 3.10
    [#1103](https://github.com/libgit2/pygit2/pull/1103)
-   Changed: now `DiffDelta.is_binary` returns `None` if the file data
    has not yet been loaded, cf.
    [#962](https://github.com/libgit2/pygit2/issues/962)
-   Document `Repository.get_attr(...)` and update theme
    [#1017](https://github.com/libgit2/pygit2/issues/1017)
    [#1105](https://github.com/libgit2/pygit2/pull/1105)

# 1.7.0 (2021-10-08)

-   Upgrade to libgit2 1.3.0
    [#1089](https://github.com/libgit2/pygit2/pull/1089)
-   Linux wheels now bundled with libssh2 1.10.0 (instead of 1.9.0)
-   macOS wheels now include libssh2
-   Add support for Python 3.10
    [#1092](https://github.com/libgit2/pygit2/pull/1092)
    [#1093](https://github.com/libgit2/pygit2/pull/1093)
-   Drop support for Python 3.6
-   New [pygit2.GIT_CHECKOUT_SKIP_LOCKED_DIRECTORIES]{.title-ref}
    [#1087](https://github.com/libgit2/pygit2/pull/1087)
-   New optional argument `location` in `Repository.applies(..)` and
    `Repository.apply(..)`
    [#1091](https://github.com/libgit2/pygit2/pull/1091)
-   Fix: Now the [flags]{.title-ref} argument in
    [Repository.blame()]{.title-ref} is passed through
    [#1083](https://github.com/libgit2/pygit2/pull/1083)
-   CI: Stop using Travis, move to GitHub actions

Caveats:

-   Windows wheels for Python 3.10 not yet available.

# 1.6.1 (2021-06-19)

-   Fix a number of reference leaks
-   Review custom object backends

Breaking changes:

-   In custom backends the callbacks have been renamed from `read` to
    `read_cb`, `write` to `write_cb`, and so on.

# 1.6.0 (2021-06-01)

-   New optional `proxy` argument in `Remote` methods
    [#642](https://github.com/libgit2/pygit2/issues/642)
    [#1063](https://github.com/libgit2/pygit2/pull/1063)
    [#1069](https://github.com/libgit2/pygit2/issues/1069)
-   New GIT_MERGE_PREFERENCE constants
    [#1071](https://github.com/libgit2/pygit2/pull/1071)
-   Don\'t require cached-property with Python 3.8 or later
    [#1066](https://github.com/libgit2/pygit2/pull/1066)
-   Add wheels for aarch64
    [#1077](https://github.com/libgit2/pygit2/issues/1077)
    [#1078](https://github.com/libgit2/pygit2/pull/1078)
-   Documentation fixes
    [#1068](https://github.com/libgit2/pygit2/pull/1068)
    [#1072](https://github.com/libgit2/pygit2/pull/1072)
-   Refactored build and CI, new `build.sh` script

Breaking changes:

-   Remove deprecated `GIT_CREDTYPE_XXX` constants, use
    `GIT_CREDENTIAL_XXX` instead.
-   Remove deprecated `Patch.patch` getter, use `Patch.text` instead.

# 1.5.0 (2021-01-23)

-   New `PackBuilder` class and `Repository.pack(...)`
    [#1048](https://github.com/libgit2/pygit2/pull/1048)
-   New `Config.delete_multivar(...)`
    [#1056](https://github.com/libgit2/pygit2/pull/1056)
-   New `Repository.is_shallow`
    [#1058](https://github.com/libgit2/pygit2/pull/1058)
-   New optional `message` argument in
    `Repository.create_reference(...)`
    [#1061](https://github.com/libgit2/pygit2/issues/1061)
    [#1062](https://github.com/libgit2/pygit2/pull/1062)
-   Fix truncated diff when there are nulls
    [#1047](https://github.com/libgit2/pygit2/pull/1047)
    [#1043](https://github.com/libgit2/pygit2/issues/1043)
-   Unit tests & Continuous integration
    [#1039](https://github.com/libgit2/pygit2/issues/1039)
    [#1052](https://github.com/libgit2/pygit2/pull/1052)

Breaking changes:

-   Fix `Index.add(...)` raise `TypeError` instead of `AttributeError`
    when arguments are of unexpected type

# 1.4.0 (2020-11-06)

-   Upgrade to libgit2 1.1, new `GIT_BLAME_IGNORE_WHITESPACE` constant
    [#1040](https://github.com/libgit2/pygit2/issues/1040)
-   Add wheels for Python 3.9
    [#1038](https://github.com/libgit2/pygit2/issues/1038)
-   Drop support for PyPy3 7.2
-   New optional `flags` argument in `Repository.__init__(...)`, new
    `GIT_REPOSITORY_OPEN_*` constants
    [#1044](https://github.com/libgit2/pygit2/pull/1044)
-   Documentation [#509](https://github.com/libgit2/pygit2/issues/509)
    [#752](https://github.com/libgit2/pygit2/issues/752)
    [#1037](https://github.com/libgit2/pygit2/issues/1037)
    [#1045](https://github.com/libgit2/pygit2/issues/1045)

# 1.3.0 (2020-09-18)

-   New `Repository.add_submodule(...)`
    [#1011](https://github.com/libgit2/pygit2/pull/1011)
-   New `Repository.applies(...)`
    [#1019](https://github.com/libgit2/pygit2/pull/1019)
-   New `Repository.revparse(...)` and `Repository.revparse_ext(...)`
    [#1022](https://github.com/libgit2/pygit2/pull/1022)
-   New optional `flags` and `file_flags` arguments in
    `Repository.merge_commits` and `Repository.merge_trees`
    [#1008](https://github.com/libgit2/pygit2/pull/1008)
-   New `Reference.raw_target`, `Repository.raw_listall_branches(...)`
    and `Repository.raw_listall_references()`; allow bytes in
    `Repository.lookup_branch(...)` and `Repository.diff(...)`
    [#1029](https://github.com/libgit2/pygit2/pull/1029)
-   New `GIT_BLAME_FIRST_PARENT` and `GIT_BLAME_USE_MAILMAP` constants
    [#1031](https://github.com/libgit2/pygit2/pull/1031)
-   New `IndexEntry` supports `repr()`, `str()`, `==` and `!=`
    [#1009](https://github.com/libgit2/pygit2/pull/1009)
-   New `Object` supports `repr()`
    [#1022](https://github.com/libgit2/pygit2/pull/1022)
-   New accept tuples of strings (not only lists) in a number of places
    [#1025](https://github.com/libgit2/pygit2/pull/1025)
-   Fix compatibility with old macOS 10.9
    [#1026](https://github.com/libgit2/pygit2/issues/1026)
    [#1027](https://github.com/libgit2/pygit2/pull/1027)
-   Fix check argument type in `Repository.apply(...)`
    [#1033](https://github.com/libgit2/pygit2/issues/1033)
-   Fix raise exception if error in `Repository.listall_submodules()`
    commit 32133974
-   Fix a couple of refcount errors in `OdbBackend.refresh()` and
    `Worktree_is_prunable` commit fed0c19c
-   Unit tests [#800](https://github.com/libgit2/pygit2/issues/800)
    [#1015](https://github.com/libgit2/pygit2/pull/1015)
-   Documentation [#705](https://github.com/libgit2/pygit2/pull/705)

# 1.2.1 (2020-05-01)

-   Fix segfault in `Object.raw_name` when not reached through a tree
    [#1002](https://github.com/libgit2/pygit2/pull/1002)
-   Internal: Use \@ffi.def_extern instead of \@ffi.callback
    [#899](https://github.com/libgit2/pygit2/issues/899)
-   Internal: callbacks code refactored
-   Test suite completely switched to pytest
    [#824](https://github.com/libgit2/pygit2/issues/824)
-   New unit tests [#538](https://github.com/libgit2/pygit2/pull/538)
    [#996](https://github.com/libgit2/pygit2/issues/996)
-   Documentation changes
    [#999](https://github.com/libgit2/pygit2/issues/999)

Deprecations:

-   Deprecate `Repository.create_remote(...)`, use instead
    `Repository.remotes.create(...)`
-   Deprecate `GIT_CREDTYPE_XXX` constants, use `GIT_CREDENTIAL_XXX`
    instead.

# 1.2.0 (2020-04-05)

-   Drop support for Python 3.5
    [#991](https://github.com/libgit2/pygit2/issues/991)
-   Upgrade to libgit2 1.0
    [#982](https://github.com/libgit2/pygit2/pull/982)
-   New support for custom reference database backends
    [#982](https://github.com/libgit2/pygit2/pull/982)
-   New support for path objects
    [#990](https://github.com/libgit2/pygit2/pull/990)
    [#955](https://github.com/libgit2/pygit2/issues/955)
-   New `index` optional parameter in `Repository.checkout_index`
    [#987](https://github.com/libgit2/pygit2/pull/987)
-   New MacOS wheels [#988](https://github.com/libgit2/pygit2/pull/988)
-   Fix re-raise exception from credentials callback in clone_repository
    [#996](https://github.com/libgit2/pygit2/issues/996)
-   Fix warning with `pip install pygit2`
    [#986](https://github.com/libgit2/pygit2/issues/986)
-   Tests: disable global Git config
    [#989](https://github.com/libgit2/pygit2/issues/989)

# 1.1.1 (2020-03-06)

-   Fix crash in tree iteration
    [#984](https://github.com/libgit2/pygit2/pull/984)
    [#980](https://github.com/libgit2/pygit2/issues/980)
-   Do not include the docs in dist files, so they\'re much smaller now

# 1.1.0 (2020-03-01)

-   Upgrade to libgit2 0.99
    [#959](https://github.com/libgit2/pygit2/pull/959)
-   Continued work on custom odb backends
    [#948](https://github.com/libgit2/pygit2/pull/948)
-   New `Diff.patchid` getter
    [#960](https://github.com/libgit2/pygit2/pull/960)
    [#877](https://github.com/libgit2/pygit2/issues/877)
-   New `settings.disable_pack_keep_file_checks(...)`
    [#908](https://github.com/libgit2/pygit2/pull/908)
-   New `GIT_DIFF_` and `GIT_DELTA_` constants
    [#738](https://github.com/libgit2/pygit2/issues/738)
-   Fix crash in iteration of config entries
    [#970](https://github.com/libgit2/pygit2/issues/970)
-   Travis: fix printing features when building Linux wheels
    [#977](https://github.com/libgit2/pygit2/pull/977)
-   Move `_pygit2` to `pygit2._pygit2`
    [#978](https://github.com/libgit2/pygit2/pull/978)

Requirements changes:

-   Now libgit2 0.99 is required
-   New requirement: cached-property

Breaking changes:

-   In the rare case you\'re directly importing the low level `_pygit2`,
    the import has changed:

        # Before
        import _pygit2

        # Now
        from pygit2 import _pygit2

# 1.0.3 (2020-01-31)

-   Fix memory leak in DiffFile
    [#943](https://github.com/libgit2/pygit2/issues/943)

# 1.0.2 (2020-01-11)

-   Fix enumerating tree entries with submodules
    [#967](https://github.com/libgit2/pygit2/issues/967)

# 1.0.1 (2019-12-21)

-   Fix build in Mac OS
    [#963](https://github.com/libgit2/pygit2/issues/963)

# 1.0.0 (2019-12-06)

-   Drop Python 2.7 and 3.4 support, six no longer required
    [#941](https://github.com/libgit2/pygit2/issues/941)
-   Add Python 3.8 support
    [#918](https://github.com/libgit2/pygit2/issues/918)
-   New support for `/` operator to traverse trees
    [#903](https://github.com/libgit2/pygit2/pull/903)
    [#924](https://github.com/libgit2/pygit2/issues/924)
-   New `Branch.raw_branch_name`
    [#954](https://github.com/libgit2/pygit2/pull/954)
-   New `Index.remove_all()`
    [#920](https://github.com/libgit2/pygit2/pull/920)
-   New `Remote.ls_remotes(..)`
    [#935](https://github.com/libgit2/pygit2/pull/935)
    [#936](https://github.com/libgit2/pygit2/issues/936)
-   New `Repository.lookup_reference_dwim(..)` and
    `Repository.resolve_refish(..)`
    [#922](https://github.com/libgit2/pygit2/issues/922)
    [#923](https://github.com/libgit2/pygit2/pull/923)
-   New `Repository.odb` returns new `Odb` type instance. And new
    `OdbBackend` type.
    [#940](https://github.com/libgit2/pygit2/pull/940)
    [#942](https://github.com/libgit2/pygit2/pull/942)
-   New `Repository.references.compress()`
    [#961](https://github.com/libgit2/pygit2/pull/961)
-   Optimization: Load notes lazily
    [#958](https://github.com/libgit2/pygit2/pull/958)
-   Fix spurious exception in config
    [#916](https://github.com/libgit2/pygit2/issues/916)
    [#917](https://github.com/libgit2/pygit2/pull/917)
-   Minor documentation and cosmetic changes
    [#919](https://github.com/libgit2/pygit2/pull/919)
    [#921](https://github.com/libgit2/pygit2/pull/921)
    [#946](https://github.com/libgit2/pygit2/pull/946)
    [#950](https://github.com/libgit2/pygit2/pull/950)

Breaking changes:

-   Now the Repository has a new attribute `odb` for object database:

        # Before
        repository.read(...)
        repository.write(...)

        # Now
        repository.odb.read(...)
        repository.odb.write(...)

-   Now `Tree[x]` returns a `Object` instance instead of a `TreeEntry`;
    `Object.type` returns an integer while `TreeEntry.type` returned a
    string:

        # Before
        if tree[x].type == 'tree':

        # Now
        if tree[x].type == GIT_OBJ_TREE:
        if tree[x].type_str == 'tree':

-   Renamed `TreeEntry._name` to `Object.raw_name`:

        # Before
        tree[x]._name

        # Now
        tree[x].raw_name

-   Object comparison is done by id. In the rare case you need to do
    tree-entry comparison or sorting:

        # Before
        tree[x] < tree[y]
        sorted(list(tree))

        # Now
        pygit2.tree_entry_cmp(x, y) < 0
        sorted(list(tree), key=pygit2.tree_entry_key)

# 0.28.2 (2019-05-26)

-   Fix crash in reflog iteration
    [#901](https://github.com/libgit2/pygit2/issues/901)
-   Support symbolic references in `branches.with_commit(..)`
    [#910](https://github.com/libgit2/pygit2/issues/910)
-   Documentation updates
    [#909](https://github.com/libgit2/pygit2/pull/909)
-   Test updates [#911](https://github.com/libgit2/pygit2/pull/911)

# 0.28.1 (2019-04-19)

-   Now works with pycparser 2.18 and above
    [#846](https://github.com/libgit2/pygit2/issues/846)
-   Now `Repository.write_archive(..)` keeps the file mode
    [#616](https://github.com/libgit2/pygit2/issues/616)
    [#898](https://github.com/libgit2/pygit2/pull/898)
-   New `Patch.data` returns the raw contents of the patch as a byte
    string [#790](https://github.com/libgit2/pygit2/pull/790)
    [#893](https://github.com/libgit2/pygit2/pull/893)
-   New `Patch.text` returns the contents of the patch as a text string,
    deprecates [Patch.patch]{.title-ref}
    [#790](https://github.com/libgit2/pygit2/pull/790)
    [#893](https://github.com/libgit2/pygit2/pull/893)

Deprecations:

-   `Patch.patch` is deprecated, use `Patch.text` instead

# 0.28.0 (2019-03-19)

-   Upgrade to libgit2 0.28
    [#878](https://github.com/libgit2/pygit2/issues/878)
-   Add binary wheels for Linux
    [#793](https://github.com/libgit2/pygit2/issues/793)
    [#869](https://github.com/libgit2/pygit2/pull/869)
    [#874](https://github.com/libgit2/pygit2/pull/874)
    [#875](https://github.com/libgit2/pygit2/pull/875)
    [#883](https://github.com/libgit2/pygit2/pull/883)
-   New `pygit2.Mailmap`, see documentation
    [#804](https://github.com/libgit2/pygit2/pull/804)
-   New `Repository.apply(...)` wraps `git_apply(..)`
    [#841](https://github.com/libgit2/pygit2/issues/841)
    [#843](https://github.com/libgit2/pygit2/pull/843)
-   Now `Repository.merge_analysis(...)` accepts an optional reference
    parameter [#888](https://github.com/libgit2/pygit2/pull/888)
    [#891](https://github.com/libgit2/pygit2/pull/891)
-   Now `Repository.add_worktree(...)` accepts an optional reference
    parameter [#814](https://github.com/libgit2/pygit2/issues/814)
    [#889](https://github.com/libgit2/pygit2/pull/889)
-   Now it\'s possible to set SSL certificate locations
    [#876](https://github.com/libgit2/pygit2/issues/876)
    [#879](https://github.com/libgit2/pygit2/pull/879)
    [#884](https://github.com/libgit2/pygit2/pull/884)
    [#886](https://github.com/libgit2/pygit2/pull/886)
-   Test and documentation improvements
    [#873](https://github.com/libgit2/pygit2/pull/873)
    [#887](https://github.com/libgit2/pygit2/pull/887)

Breaking changes:

-   Now `worktree.path` returns the path to the worktree directory, not
    to the [.git]{.title-ref} file within
    [#803](https://github.com/libgit2/pygit2/issues/803)
-   Remove undocumented `worktree.git_path`
    [#803](https://github.com/libgit2/pygit2/issues/803)

# 0.27.4 (2019-01-19)

-   New `pygit2.LIBGIT2_VER` tuple
    [#845](https://github.com/libgit2/pygit2/issues/845)
    [#848](https://github.com/libgit2/pygit2/pull/848)
-   New objects now support (in)equality comparison and hash
    [#852](https://github.com/libgit2/pygit2/issues/852)
    [#853](https://github.com/libgit2/pygit2/pull/853)
-   New references now support (in)equality comparison
    [#860](https://github.com/libgit2/pygit2/issues/860)
    [#862](https://github.com/libgit2/pygit2/pull/862)
-   New `paths` optional argument in `Repository.checkout()`
    [#858](https://github.com/libgit2/pygit2/issues/858)
    [#859](https://github.com/libgit2/pygit2/pull/859)
-   Fix speed and windows package regression
    [#849](https://github.com/libgit2/pygit2/issues/849)
    [#857](https://github.com/libgit2/pygit2/issues/857)
    [#851](https://github.com/libgit2/pygit2/pull/851)
-   Fix deprecation warning
    [#850](https://github.com/libgit2/pygit2/pull/850)
-   Documentation fixes
    [#855](https://github.com/libgit2/pygit2/pull/855)
-   Add Python classifiers to setup.py
    [#861](https://github.com/libgit2/pygit2/pull/861)
-   Speeding up tests in Travis
    [#854](https://github.com/libgit2/pygit2/pull/854)

Breaking changes:

-   Remove deprecated [Reference.get_object()]{.title-ref}, use
    [Reference.peel()]{.title-ref} instead

# 0.27.3 (2018-12-15)

-   Move to pytest, drop support for Python 3.3 and cffi 0.x
    [#824](https://github.com/libgit2/pygit2/issues/824)
    [#826](https://github.com/libgit2/pygit2/pull/826)
    [#833](https://github.com/libgit2/pygit2/pull/833)
    [#834](https://github.com/libgit2/pygit2/pull/834)
-   New support comparing signatures for (in)equality
-   New `Submodule.head_id`
    [#817](https://github.com/libgit2/pygit2/pull/817)
-   New `Remote.prune(...)`
    [#825](https://github.com/libgit2/pygit2/pull/825)
-   New `pygit2.reference_is_valid_name(...)`
    [#827](https://github.com/libgit2/pygit2/pull/827)
-   New `AlreadyExistsError` and `InvalidSpecError`
    [#828](https://github.com/libgit2/pygit2/issues/828)
    [#829](https://github.com/libgit2/pygit2/pull/829)
-   New `Reference.raw_name`, `Reference.raw_shorthand`, `Tag.raw_name`,
    `Tag.raw_message` and `DiffFile.raw_path`
    [#840](https://github.com/libgit2/pygit2/pull/840)
-   Fix decode error in commit messages and signatures
    [#839](https://github.com/libgit2/pygit2/issues/839)
-   Fix, raise error in `Repository.descendant_of(...)` if commit
    doesn\'t exist [#822](https://github.com/libgit2/pygit2/issues/822)
    [#842](https://github.com/libgit2/pygit2/pull/842)
-   Documentation fixes
    [#821](https://github.com/libgit2/pygit2/pull/821)

Breaking changes:

-   Remove undocumented `Tag._message`, replaced by `Tag.raw_message`

# 0.27.2 (2018-09-16)

-   Add support for Python 3.7
    [#809](https://github.com/libgit2/pygit2/issues/809)
-   New `Object.short_id`
    [#799](https://github.com/libgit2/pygit2/issues/799)
    [#806](https://github.com/libgit2/pygit2/pull/806)
    [#807](https://github.com/libgit2/pygit2/pull/807)
-   New `Repository.descendant_of` and `Repository.branches.with_commit`
    [#815](https://github.com/libgit2/pygit2/issues/815)
    [#816](https://github.com/libgit2/pygit2/pull/816)
-   Fix repository initialization in `clone_repository(...)`
    [#818](https://github.com/libgit2/pygit2/issues/818)
-   Fix several warnings and errors, commits
    [cd896ddc](https://github.com/libgit2/pygit2/commit/cd896ddc) and
    [dfa536a3](https://github.com/libgit2/pygit2/commit/dfa536a3)
-   Documentation fixes and improvements
    [#805](https://github.com/libgit2/pygit2/pull/805)
    [#808](https://github.com/libgit2/pygit2/pull/808)

# 0.27.1 (2018-06-02)

Breaking changes:

-   Now `discover_repository` returns `None` if repository not found,
    instead of raising `KeyError`
    [#531](https://github.com/libgit2/pygit2/issues/531)

Other changes:

-   New `DiffLine.raw_content`
    [#610](https://github.com/libgit2/pygit2/issues/610)
-   Fix tests failing in some cases
    [#795](https://github.com/libgit2/pygit2/issues/795)
-   Automate wheels upload to pypi
    [#563](https://github.com/libgit2/pygit2/issues/563)

# 0.27.0 (2018-03-30)

-   Update to libgit2 v0.27
    [#783](https://github.com/libgit2/pygit2/pull/783)
-   Fix for GCC 4 [#786](https://github.com/libgit2/pygit2/pull/786)

# 0.26.4 (2018-03-23)

Backward incompatible changes:

-   Now iterating over a configuration returns `ConfigEntry` objects
    [#778](https://github.com/libgit2/pygit2/pull/778)

        # Before
        for name in config:
            value = config[name]

        # Now
        for entry in config:
            name = entry.name
            value = entry.value

Other changes:

-   Added support for worktrees
    [#779](https://github.com/libgit2/pygit2/pull/779)
-   New `Commit.gpg_signature`
    [#766](https://github.com/libgit2/pygit2/pull/766)
-   New static `Diff.parse_diff(...)`
    [#774](https://github.com/libgit2/pygit2/pull/774)
-   New optional argument `callbacks` in
    `Repository.update_submodules(...)`
    [#763](https://github.com/libgit2/pygit2/pull/763)
-   New `KeypairFromMemory` credentials
    [#771](https://github.com/libgit2/pygit2/pull/771)
-   Add missing status constants
    [#781](https://github.com/libgit2/pygit2/issues/781)
-   Fix segfault [#775](https://github.com/libgit2/pygit2/issues/775)
-   Fix some unicode decode errors with Python 2
    [#767](https://github.com/libgit2/pygit2/pull/767)
    [#768](https://github.com/libgit2/pygit2/pull/768)
-   Documentation improvements
    [#721](https://github.com/libgit2/pygit2/pull/721)
    [#769](https://github.com/libgit2/pygit2/pull/769)
    [#770](https://github.com/libgit2/pygit2/pull/770)

# 0.26.3 (2017-12-24)

-   New `Diff.deltas`
    [#736](https://github.com/libgit2/pygit2/issues/736)
-   Improvements to `Patch.create_from`
    [#753](https://github.com/libgit2/pygit2/pull/753)
    [#756](https://github.com/libgit2/pygit2/pull/756)
    [#759](https://github.com/libgit2/pygit2/pull/759)
-   Fix build and tests in Windows, broken in the previous release
    [#749](https://github.com/libgit2/pygit2/pull/749)
    [#751](https://github.com/libgit2/pygit2/pull/751)
-   Review `Patch.patch`
    [#757](https://github.com/libgit2/pygit2/issues/757)
-   Workaround bug
    [#4442](https://github.com/libgit2/libgit2/issues/4442) in libgit2,
    and improve unit tests
    [#748](https://github.com/libgit2/pygit2/issues/748)
    [#754](https://github.com/libgit2/pygit2/issues/754)
    [#758](https://github.com/libgit2/pygit2/pull/758)
    [#761](https://github.com/libgit2/pygit2/pull/761)

# 0.26.2 (2017-12-01)

-   New property `Patch.patch`
    [#739](https://github.com/libgit2/pygit2/issues/739)
    [#741](https://github.com/libgit2/pygit2/pull/741)
-   New static method `Patch.create_from`
    [#742](https://github.com/libgit2/pygit2/issues/742)
    [#744](https://github.com/libgit2/pygit2/pull/744)
-   New parameter `prune` in `Remote.fetch`
    [#743](https://github.com/libgit2/pygit2/pull/743)
-   Tests: skip tests that require network when there is not
    [#737](https://github.com/libgit2/pygit2/issues/737)
-   Tests: other improvements
    [#740](https://github.com/libgit2/pygit2/pull/740)
-   Documentation improvements

# 0.26.1 (2017-11-19)

-   New `Repository.free()`
    [#730](https://github.com/libgit2/pygit2/pull/730)
-   Improve credentials handling for ssh cloning
    [#718](https://github.com/libgit2/pygit2/pull/718)
-   Documentation improvements
    [#714](https://github.com/libgit2/pygit2/pull/714)
    [#715](https://github.com/libgit2/pygit2/pull/715)
    [#728](https://github.com/libgit2/pygit2/pull/728)
    [#733](https://github.com/libgit2/pygit2/pull/733)
    [#734](https://github.com/libgit2/pygit2/pull/734)
    [#735](https://github.com/libgit2/pygit2/pull/735)

# 0.26.0 (2017-07-06)

-   Update to libgit2 v0.26
    [#713](https://github.com/libgit2/pygit2/pull/713)
-   Drop support for Python 3.2, add support for cffi 1.10
    [#706](https://github.com/libgit2/pygit2/pull/706)
    [#694](https://github.com/libgit2/pygit2/issues/694)
-   New `Repository.revert_commit(...)`
    [#711](https://github.com/libgit2/pygit2/pull/711)
    [#710](https://github.com/libgit2/pygit2/issues/710)
-   New `Branch.is_checked_out()`
    [#696](https://github.com/libgit2/pygit2/pull/696)
-   Various fixes [#706](https://github.com/libgit2/pygit2/pull/706)
    [#707](https://github.com/libgit2/pygit2/pull/707)
    [#708](https://github.com/libgit2/pygit2/pull/708)

# 0.25.1 (2017-04-25)

-   Add support for Python 3.6
-   New support for stash: repository methods `stash`, `stash_apply`,
    `stash_drop` and `stash_pop`
    [#695](https://github.com/libgit2/pygit2/pull/695)
-   Improved support for submodules: new repository methods
    `init_submodules` and `update_submodules`
    [#692](https://github.com/libgit2/pygit2/pull/692)
-   New friendlier API for branches & references: `Repository.branches`
    and `Repository.references`
    [#700](https://github.com/libgit2/pygit2/pull/700)
    [#701](https://github.com/libgit2/pygit2/pull/701)
-   New support for custom backends
    [#690](https://github.com/libgit2/pygit2/pull/690)
-   Fix `init_repository` crash on None input
    [#688](https://github.com/libgit2/pygit2/issues/688)
    [#697](https://github.com/libgit2/pygit2/pull/697)
-   Fix checkout with an orphan master branch
    [#669](https://github.com/libgit2/pygit2/issues/669)
    [#685](https://github.com/libgit2/pygit2/pull/685)
-   Better error messages for opening repositories
    [#645](https://github.com/libgit2/pygit2/issues/645)
    [#698](https://github.com/libgit2/pygit2/pull/698)

# 0.25.0 (2016-12-26)

-   Upgrade to libgit2 0.25
    [#670](https://github.com/libgit2/pygit2/pull/670)
-   Now Commit.tree raises an error if tree is not found
    [#682](https://github.com/libgit2/pygit2/pull/682)
-   New settings.mwindow_mapped_limit, cached_memory, enable_caching,
    cache_max_size and cache_object_limit
    [#677](https://github.com/libgit2/pygit2/pull/677)

# 0.24.2 (2016-11-01)

-   Unit tests pass on Windows, integration with AppVeyor
    [#641](https://github.com/libgit2/pygit2/pull/641)
    [#655](https://github.com/libgit2/pygit2/issues/655)
    [#657](https://github.com/libgit2/pygit2/pull/657)
    [#659](https://github.com/libgit2/pygit2/pull/659)
    [#660](https://github.com/libgit2/pygit2/pull/660)
    [#661](https://github.com/libgit2/pygit2/pull/661)
    [#667](https://github.com/libgit2/pygit2/pull/667)
-   Fix when libgit2 error messages have non-ascii chars
    [#651](https://github.com/libgit2/pygit2/pull/651)
-   Documentation improvements
    [#643](https://github.com/libgit2/pygit2/pull/643)
    [#653](https://github.com/libgit2/pygit2/pull/653)
    [#663](https://github.com/libgit2/pygit2/pull/663)

# 0.24.1 (2016-06-21)

-   New `Repository.listall_reference_objects()`
    [#634](https://github.com/libgit2/pygit2/pull/634)
-   Fix `Repository.write_archive(...)`
    [#619](https://github.com/libgit2/pygit2/pull/619)
    [#621](https://github.com/libgit2/pygit2/pull/621)
-   Reproducible builds
    [#636](https://github.com/libgit2/pygit2/pull/636)
-   Documentation fixes
    [#606](https://github.com/libgit2/pygit2/pull/606)
    [#607](https://github.com/libgit2/pygit2/pull/607)
    [#609](https://github.com/libgit2/pygit2/pull/609)
    [#623](https://github.com/libgit2/pygit2/pull/623)
-   Test updates [#629](https://github.com/libgit2/pygit2/pull/629)

# 0.24.0 (2016-03-05)

-   Update to libgit2 v0.24
    [#594](https://github.com/libgit2/pygit2/pull/594)
-   Support Python 3.5
-   New dependency, [six](https://pypi.org/project/six/)
-   New `Repository.path_is_ignored(path)`
    [#589](https://github.com/libgit2/pygit2/pull/589)
-   Fix error in `Repository(path)` when path is a bytes string
    [#588](https://github.com/libgit2/pygit2/issues/588)
    [#593](https://github.com/libgit2/pygit2/pull/593)
-   Fix memory issue in `Repository.describe(...)`
    [#592](https://github.com/libgit2/pygit2/issues/592)
    [#597](https://github.com/libgit2/pygit2/issues/597)
    [#599](https://github.com/libgit2/pygit2/pull/599)
-   Allow testing with [tox](https://pypi.org/project/tox/)
    [#600](https://github.com/libgit2/pygit2/pull/600)

# 0.23.3 (2016-01-01)

-   New `Repository.create_blob_fromiobase(...)`
    [#490](https://github.com/libgit2/pygit2/pull/490)
    [#577](https://github.com/libgit2/pygit2/pull/577)
-   New `Repository.describe(...)`
    [#585](https://github.com/libgit2/pygit2/pull/585)
-   Fix `Signature` default encoding, UTF-8 now
    [#581](https://github.com/libgit2/pygit2/issues/581)
-   Fixing `pip install pygit2`, should install cffi first
-   Unit tests, fix binary diff test
    [#586](https://github.com/libgit2/pygit2/pull/586)
-   Document that `Diff.patch` can be `None`
    [#587](https://github.com/libgit2/pygit2/pull/587)

# 0.23.2 (2015-10-11)

-   Unify callbacks system for remotes and clone
    [#568](https://github.com/libgit2/pygit2/pull/568)
-   New `TreeEntry._name`
    [#570](https://github.com/libgit2/pygit2/pull/570)
-   Fix segfault in `Tag._message`
    [#572](https://github.com/libgit2/pygit2/pull/572)
-   Documentation improvements
    [#569](https://github.com/libgit2/pygit2/pull/569)
    [#574](https://github.com/libgit2/pygit2/pull/574)

API changes to clone:

    # Before
    clone_repository(..., credentials, certificate)

    # Now
    callbacks = RemoteCallbacks(credentials, certificate)
    clone_repository(..., callbacks)

API changes to remote:

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

# 0.23.1 (2015-09-26)

-   Improve support for cffi 1.0+
    [#529](https://github.com/libgit2/pygit2/pull/529)
    [#561](https://github.com/libgit2/pygit2/pull/561)
-   Fix `Remote.push` [#557](https://github.com/libgit2/pygit2/pull/557)
-   New `TreeEntry.type`
    [#560](https://github.com/libgit2/pygit2/pull/560)
-   New `pygit2.GIT_DIFF_SHOW_BINARY`
    [#566](https://github.com/libgit2/pygit2/pull/566)

# 0.23.0 (2015-08-14)

-   Update to libgit2 v0.23
    [#540](https://github.com/libgit2/pygit2/pull/540)
-   Now `Repository.merge_base(...)` returns `None` if no merge base is
    found [#550](https://github.com/libgit2/pygit2/pull/550)
-   Documentation updates
    [#547](https://github.com/libgit2/pygit2/pull/547)

API changes:

-   How to set identity (aka signature) in a reflog has changed:

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

-   Some remote setters have been replaced by methods:

        # Before                       # Now
        Remote.url = url               Repository.remotes.set_url(name, url)
        Remote.push_url = url          Repository.remotes.set_push_url(name, url)

        Remote.add_fetch(refspec)      Repository.remotes.add_fetch(name, refspec)
        Remote.add_push(refspec)       Repository.remotes.add_push(name, refspec)

        Remote.fetch_refspecs = [...]  removed, use the config API instead
        Remote.push_refspecs = [...]   removed, use the config API instead

# 0.22.1 (2015-07-12)

Diff interface refactoring
[#346](https://github.com/libgit2/pygit2/pull/346) (in progress):

-   New `iter(pygit2.Blame)`

-   New `pygit2.DiffDelta`, `pygit2.DiffFile` and `pygit.DiffLine`

-   API changes, translation table:

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

-   `DiffHunk.lines` is now a list of `DiffLine` objects, not tuples

New features:

-   New `Repository.expand_id(...)` and `Repository.ahead_behind(...)`
    [#448](https://github.com/libgit2/pygit2/pull/448)
-   New `prefix` parameter in `Repository.write_archive`
    [#481](https://github.com/libgit2/pygit2/pull/481)
-   New `Repository.merge_trees(...)`
    [#489](https://github.com/libgit2/pygit2/pull/489)
-   New `Repository.cherrypick(...)`
    [#436](https://github.com/libgit2/pygit2/issues/436)
    [#492](https://github.com/libgit2/pygit2/pull/492)
-   New support for submodules
    [#499](https://github.com/libgit2/pygit2/pull/499)
    [#514](https://github.com/libgit2/pygit2/pull/514)
-   New `Repository.merge_file_from_index(...)`
    [#503](https://github.com/libgit2/pygit2/pull/503)
-   Now `Repository.diff` supports diffing two blobs
    [#508](https://github.com/libgit2/pygit2/pull/508)
-   New optional `fetch` parameter in `Remote.create`
    [#526](https://github.com/libgit2/pygit2/pull/526)
-   New `pygit2.DiffStats`
    [#406](https://github.com/libgit2/pygit2/issues/406)
    [#525](https://github.com/libgit2/pygit2/pull/525)
-   New `Repository.get_attr(...)`
    [#528](https://github.com/libgit2/pygit2/pull/528)
-   New `level` optional parameter in `Index.remove`
    [#533](https://github.com/libgit2/pygit2/pull/533)
-   New `repr(TreeEntry)`
    [#543](https://github.com/libgit2/pygit2/pull/543)

Build and install improvements:

-   Make pygit work in a frozen environment
    [#453](https://github.com/libgit2/pygit2/pull/453)
-   Make pygit2 work with pyinstaller
    [#510](https://github.com/libgit2/pygit2/pull/510)

Bugs fixed:

-   Fix memory issues
    [#477](https://github.com/libgit2/pygit2/issues/477)
    [#487](https://github.com/libgit2/pygit2/pull/487)
    [#520](https://github.com/libgit2/pygit2/pull/520)
-   Fix TreeEntry equality testing
    [#458](https://github.com/libgit2/pygit2/issues/458)
    [#488](https://github.com/libgit2/pygit2/pull/488)
-   `Repository.write_archive` fix handling of symlinks
    [#480](https://github.com/libgit2/pygit2/pull/480)
-   Fix type check in `Diff[...]`
    [#495](https://github.com/libgit2/pygit2/issues/495)
-   Fix error when merging files with unicode content
    [#505](https://github.com/libgit2/pygit2/pull/505)

Other:

-   Documentation improvements and fixes
    [#448](https://github.com/libgit2/pygit2/pull/448)
    [#491](https://github.com/libgit2/pygit2/pull/491)
    [#497](https://github.com/libgit2/pygit2/pull/497)
    [#507](https://github.com/libgit2/pygit2/pull/507)
    [#517](https://github.com/libgit2/pygit2/pull/517)
    [#518](https://github.com/libgit2/pygit2/pull/518)
    [#519](https://github.com/libgit2/pygit2/pull/519)
    [#521](https://github.com/libgit2/pygit2/pull/521)
    [#523](https://github.com/libgit2/pygit2/pull/523)
    [#527](https://github.com/libgit2/pygit2/pull/527)
    [#536](https://github.com/libgit2/pygit2/pull/536)
-   Expose the `pygit2.GIT_REPOSITORY_INIT_*` constants
    [#483](https://github.com/libgit2/pygit2/issues/483)

# 0.22.0 (2015-01-16)

New:

-   Update to libgit2 v0.22
    [#459](https://github.com/libgit2/pygit2/pull/459)
-   Add support for libgit2 feature detection (new `pygit2.features` and
    `pygit2.GIT_FEATURE_*`)
    [#475](https://github.com/libgit2/pygit2/pull/475)
-   New `Repository.remotes` (`RemoteCollection`)
    [#447](https://github.com/libgit2/pygit2/pull/447)

API Changes:

-   Prototype of `clone_repository` changed, check documentation
-   Removed `clone_into`, use `clone_repository` with callbacks instead
-   Use `Repository.remotes.rename(name, new_name)` instead of
    `Remote.rename(new_name)`
-   Use `Repository.remotes.delete(name)` instead of `Remote.delete()`
-   Now `Remote.push(...)` takes a list of refspecs instead of just one
-   Change `Patch.old_id`, `Patch.new_id`, `Note.annotated_id`,
    `RefLogEntry.oid_old` and `RefLogEntry.oid_new` to be `Oid` objects
    instead of strings
    [#449](https://github.com/libgit2/pygit2/pull/449)

Other:

-   Fix `init_repository` when passing optional parameters
    `workdir_path`, `description`, `template_path`, `initial_head` or
    `origin_url` [#466](https://github.com/libgit2/pygit2/issues/466)
    [#471](https://github.com/libgit2/pygit2/pull/471)
-   Fix use-after-free when patch outlives diff
    [#457](https://github.com/libgit2/pygit2/issues/457)
    [#461](https://github.com/libgit2/pygit2/pull/461)
    [#474](https://github.com/libgit2/pygit2/pull/474)
-   Documentation improvements
    [#456](https://github.com/libgit2/pygit2/issues/456)
    [#462](https://github.com/libgit2/pygit2/pull/462)
    [#465](https://github.com/libgit2/pygit2/pull/465)
    [#472](https://github.com/libgit2/pygit2/pull/472)
    [#473](https://github.com/libgit2/pygit2/pull/473)
-   Make the GPL exception explicit in setup.py
    [#450](https://github.com/libgit2/pygit2/pull/450)

# 0.21.4 (2014-11-04)

-   Fix credentials callback not set when pushing
    [#431](https://github.com/libgit2/pygit2/pull/431)
    [#435](https://github.com/libgit2/pygit2/issues/435)
    [#437](https://github.com/libgit2/pygit2/issues/437)
    [#438](https://github.com/libgit2/pygit2/pull/438)
-   Fix `Repository.diff(...)` when treeish is \"empty\"
    [#432](https://github.com/libgit2/pygit2/issues/432)
-   New `Reference.peel(...)` renders `Reference.get_object()` obsolete
    [#434](https://github.com/libgit2/pygit2/pull/434)
-   New, authenticate using ssh agent
    [#424](https://github.com/libgit2/pygit2/pull/424)
-   New `Repository.merge_commits(...)`
    [#445](https://github.com/libgit2/pygit2/pull/445)
-   Make it easier to run when libgit2 not in a standard location
    [#441](https://github.com/libgit2/pygit2/issues/441)
-   Documentation: review install chapter
-   Documentation: many corrections
    [#427](https://github.com/libgit2/pygit2/pull/427)
    [#429](https://github.com/libgit2/pygit2/pull/429)
    [#439](https://github.com/libgit2/pygit2/pull/439)
    [#440](https://github.com/libgit2/pygit2/pull/440)
    [#442](https://github.com/libgit2/pygit2/pull/442)
    [#443](https://github.com/libgit2/pygit2/pull/443)
    [#444](https://github.com/libgit2/pygit2/pull/444)

# 0.21.3 (2014-09-15)

Breaking changes:

-   Now `Repository.blame(...)` returns `Oid` instead of string
    [#413](https://github.com/libgit2/pygit2/pull/413)
-   New `Reference.set_target(...)` replaces the `Reference.target`
    setter and `Reference.log_append(...)`
    [#414](https://github.com/libgit2/pygit2/pull/414)
-   New `Repository.set_head(...)` replaces the `Repository.head` setter
    [#414](https://github.com/libgit2/pygit2/pull/414)
-   `Repository.merge(...)` now uses the `SAFE_CREATE` strategy by
    default [#417](https://github.com/libgit2/pygit2/pull/417)

Other changes:

-   New `Remote.delete()`
    [#418](https://github.com/libgit2/pygit2/issues/418)
    [#420](https://github.com/libgit2/pygit2/pull/420)
-   New `Repository.write_archive(...)`
    [#421](https://github.com/libgit2/pygit2/pull/421)
-   Now `Repository.checkout(...)` accepts branch objects
    [#408](https://github.com/libgit2/pygit2/pull/408)
-   Fix refcount leak in remotes
    [#403](https://github.com/libgit2/pygit2/issues/403)
    [#404](https://github.com/libgit2/pygit2/pull/404)
    [#419](https://github.com/libgit2/pygit2/pull/419)
-   Various fixes to `clone_repository(...)`
    [#399](https://github.com/libgit2/pygit2/issues/399)
    [#411](https://github.com/libgit2/pygit2/pull/411)
    [#425](https://github.com/libgit2/pygit2/issues/425)
    [#426](https://github.com/libgit2/pygit2/pull/426)
-   Fix build error in Python 3
    [#401](https://github.com/libgit2/pygit2/pull/401)
-   Now `pip install pygit2` installs cffi first
    [#380](https://github.com/libgit2/pygit2/issues/380)
    [#407](https://github.com/libgit2/pygit2/pull/407)
-   Add support for PyPy3
    [#422](https://github.com/libgit2/pygit2/pull/422)
-   Documentation improvements
    [#398](https://github.com/libgit2/pygit2/pull/398)
    [#409](https://github.com/libgit2/pygit2/pull/409)

# 0.21.2 (2014-08-09)

-   Fix regression with Python 2, `IndexEntry.path` returns str (bytes
    in Python 2 and unicode in Python 3)
-   Get back `IndexEntry.oid` for backwards compatibility
-   Config, iterate over the keys (instead of the key/value pairs)
    [#395](https://github.com/libgit2/pygit2/pull/395)
-   `Diff.find_similar` supports new threshold arguments
    [#396](https://github.com/libgit2/pygit2/pull/396)
-   Optimization, do not load the object when expanding an oid prefix
    [#397](https://github.com/libgit2/pygit2/pull/397)

# 0.21.1 (2014-07-22)

-   Install fix [#382](https://github.com/libgit2/pygit2/pull/382)
-   Documentation improved, including
    [#383](https://github.com/libgit2/pygit2/pull/383)
    [#385](https://github.com/libgit2/pygit2/pull/385)
    [#388](https://github.com/libgit2/pygit2/pull/388)
-   Documentation, use the read-the-docs theme
    [#387](https://github.com/libgit2/pygit2/pull/387)
-   Coding style improvements
    [#392](https://github.com/libgit2/pygit2/pull/392)
-   New `Repository.state_cleanup()`
    [#386](https://github.com/libgit2/pygit2/pull/386)
-   New `Index.conflicts`
    [#345](https://github.com/libgit2/pygit2/issues/345)
    [#389](https://github.com/libgit2/pygit2/pull/389)
-   New checkout option to define the target directory
    [#390](https://github.com/libgit2/pygit2/pull/390)

Backward incompatible changes:

-   Now the checkout strategy must be a keyword argument.

    Change `Repository.checkout(refname, strategy)` to
    `Repository.checkout(refname, strategy=strategy)`

    Idem for `checkout_head`, `checkout_index` and `checkout_tree`

# 0.21.0 (2014-06-27)

Highlights:

-   Drop official support for Python 2.6, and add support for Python 3.4
    [#376](https://github.com/libgit2/pygit2/pull/376)
-   Upgrade to libgit2 v0.21.0
    [#374](https://github.com/libgit2/pygit2/pull/374)
-   Start using cffi [#360](https://github.com/libgit2/pygit2/pull/360)
    [#361](https://github.com/libgit2/pygit2/pull/361)

Backward incompatible changes:

-   Replace `oid` by `id` through the API to follow libgit2 conventions.
-   Merge API overhaul following changes in libgit2.
-   New `Remote.rename(...)` replaces `Remote.name = ...`
-   Now `Remote.fetch()` returns a `TransferProgress` object.
-   Now `Config.get_multivar(...)` returns an iterator instead of a
    list.

New features:

-   New `Config.snapshot()` and `Repository.config_snapshot()`
-   New `Config` methods: `get_bool(...)`, `get_int(...)`,
    `parse_bool(...)` and `parse_int(...)`
    [#357](https://github.com/libgit2/pygit2/pull/357)
-   Blob: implement the memory buffer interface
    [#362](https://github.com/libgit2/pygit2/pull/362)
-   New `clone_into(...)` function
    [#368](https://github.com/libgit2/pygit2/pull/368)
-   Now `Index` can be used alone, without a repository
    [#372](https://github.com/libgit2/pygit2/pull/372)
-   Add more options to `init_repository`
    [#347](https://github.com/libgit2/pygit2/pull/347)
-   Support `Repository.workdir = ...` and support setting detached
    heads `Repository.head = <Oid>`
    [#377](https://github.com/libgit2/pygit2/pull/377)

Other:

-   Fix again build with VS2008
    [#364](https://github.com/libgit2/pygit2/pull/364)
-   Fix `Blob.diff(...)` and `Blob.diff_to_buffer(...)` arguments
    passing [#366](https://github.com/libgit2/pygit2/pull/366)
-   Fail gracefully when compiling against the wrong version of libgit2
    [#365](https://github.com/libgit2/pygit2/pull/365)
-   Several documentation improvements and updates
    [#359](https://github.com/libgit2/pygit2/pull/359)
    [#375](https://github.com/libgit2/pygit2/pull/375)
    [#378](https://github.com/libgit2/pygit2/pull/378)

# 0.20.3 (2014-04-02)

-   A number of memory issues fixed
    [#328](https://github.com/libgit2/pygit2/pull/328)
    [#348](https://github.com/libgit2/pygit2/pull/348)
    [#353](https://github.com/libgit2/pygit2/pull/353)
    [#355](https://github.com/libgit2/pygit2/pull/355)
    [#356](https://github.com/libgit2/pygit2/pull/356)
-   Compatibility fixes for PyPy
    ([#338](https://github.com/libgit2/pygit2/pull/338)), Visual Studio
    2008 ([#343](https://github.com/libgit2/pygit2/pull/343)) and Python
    3.3 ([#351](https://github.com/libgit2/pygit2/pull/351))
-   Make the sort mode parameter in `Repository.walk(...)` optional
    [#337](https://github.com/libgit2/pygit2/pull/337)
-   New `Object.peel(...)`
    [#342](https://github.com/libgit2/pygit2/pull/342)
-   New `Index.add_all(...)`
    [#344](https://github.com/libgit2/pygit2/pull/344)
-   Introduce support for libgit2 options
    [#350](https://github.com/libgit2/pygit2/pull/350)
-   More informative repr for `Repository` objects
    [#352](https://github.com/libgit2/pygit2/pull/352)
-   Introduce support for credentials
    [#354](https://github.com/libgit2/pygit2/pull/354)
-   Several documentation fixes
    [#302](https://github.com/libgit2/pygit2/issues/302)
    [#336](https://github.com/libgit2/pygit2/issues/336)
-   Tests, remove temporary files
    [#341](https://github.com/libgit2/pygit2/pull/341)

# 0.20.2 (2014-02-04)

-   Support PyPy [#209](https://github.com/libgit2/pygit2/issues/209)
    [#327](https://github.com/libgit2/pygit2/pull/327)
    [#333](https://github.com/libgit2/pygit2/pull/333)

Repository:

-   New `Repository.default_signature`
    [#310](https://github.com/libgit2/pygit2/pull/310)

Oid:

-   New `str(Oid)` deprecates `Oid.hex`
    [#322](https://github.com/libgit2/pygit2/pull/322)

Object:

-   New `Object.id` deprecates `Object.oid`
    [#322](https://github.com/libgit2/pygit2/pull/322)
-   New `TreeEntry.id` deprecates `TreeEntry.oid`
    [#322](https://github.com/libgit2/pygit2/pull/322)
-   New `Blob.diff(...)` and `Blob.diff_to_buffer(...)`
    [#307](https://github.com/libgit2/pygit2/pull/307)
-   New `Commit.tree_id` and `Commit.parent_ids`
    [#73](https://github.com/libgit2/pygit2/issues/73)
    [#311](https://github.com/libgit2/pygit2/pull/311)
-   New rich comparison between tree entries
    [#305](https://github.com/libgit2/pygit2/issues/305)
    [#313](https://github.com/libgit2/pygit2/pull/313)
-   Now `Tree.__contains__(key)` supports paths
    [#306](https://github.com/libgit2/pygit2/issues/306)
    [#316](https://github.com/libgit2/pygit2/pull/316)

Index:

-   Now possible to create `IndexEntry(...)`
    [#325](https://github.com/libgit2/pygit2/pull/325)
-   Now `IndexEntry.path`, `IndexEntry.oid` and `IndexEntry.mode` are
    writable [#325](https://github.com/libgit2/pygit2/pull/325)
-   Now `Index.add(...)` accepts an `IndexEntry` too
    [#325](https://github.com/libgit2/pygit2/pull/325)
-   Now `Index.write_tree(...)` is able to write to a different
    repository [#325](https://github.com/libgit2/pygit2/pull/325)
-   Fix memory leak in `IndexEntry.path` setter
    [#335](https://github.com/libgit2/pygit2/pull/335)

Config:

-   New `Config` iterator replaces `Config.foreach`
    [#183](https://github.com/libgit2/pygit2/issues/183)
    [#312](https://github.com/libgit2/pygit2/pull/312)

Remote:

-   New type `Refspec`
    [#314](https://github.com/libgit2/pygit2/pull/314)
-   New `Remote.push_url`
    [#315](https://github.com/libgit2/pygit2/pull/314)
-   New `Remote.add_push` and `Remote.add_fetch`
    [#255](https://github.com/libgit2/pygit2/issues/255)
    [#318](https://github.com/libgit2/pygit2/pull/318)
-   New `Remote.fetch_refspecs` replaces `Remote.get_fetch_refspecs()`
    and `Remote.set_fetch_refspecs(...)`
    [#319](https://github.com/libgit2/pygit2/pull/319)
-   New `Remote.push_refspecs` replaces `Remote.get_push_refspecs()` and
    `Remote.set_push_refspecs(...)`
    [#319](https://github.com/libgit2/pygit2/pull/319)
-   New `Remote.progress`, `Remote.transfer_progress` and
    `Remote.update_tips`
    [#274](https://github.com/libgit2/pygit2/issues/274)
    [#324](https://github.com/libgit2/pygit2/pull/324)
-   New type `TransferProgress`
    [#274](https://github.com/libgit2/pygit2/issues/274)
    [#324](https://github.com/libgit2/pygit2/pull/324)
-   Fix refcount leak in `Repository.remotes`
    [#321](https://github.com/libgit2/pygit2/issues/321)
    [#332](https://github.com/libgit2/pygit2/pull/332)

Other: [#331](https://github.com/libgit2/pygit2/pull/331)

# 0.20.1 (2013-12-24)

-   New remote ref-specs API:
    [#290](https://github.com/libgit2/pygit2/pull/290)
-   New `Repository.reset(...)`:
    [#292](https://github.com/libgit2/pygit2/pull/292),
    [#294](https://github.com/libgit2/pygit2/pull/294)
-   Export `GIT_DIFF_MINIMAL`:
    [#293](https://github.com/libgit2/pygit2/pull/293)
-   New `Repository.merge(...)`:
    [#295](https://github.com/libgit2/pygit2/pull/295)
-   Fix `Repository.blame` argument handling:
    [#297](https://github.com/libgit2/pygit2/pull/297)
-   Fix build error on Windows:
    [#298](https://github.com/libgit2/pygit2/pull/298)
-   Fix typo in the README file, Blog → Blob:
    [#301](https://github.com/libgit2/pygit2/pull/301)
-   Now `Diff.patch` returns `None` if no patch:
    [#232](https://github.com/libgit2/pygit2/pull/232),
    [#303](https://github.com/libgit2/pygit2/pull/303)
-   New `Walker.simplify_first_parent()`:
    [#304](https://github.com/libgit2/pygit2/pull/304)

# 0.20.0 (2013-11-24)

-   Upgrade to libgit2 v0.20.0:
    [#288](https://github.com/libgit2/pygit2/pull/288)
-   New `Repository.head_is_unborn` replaces
    `Repository.head_is_orphaned`
-   Changed `pygit2.clone_repository(...)`. Drop `push_url`,
    `fetch_spec` and `push_spec` parameters. Add `ignore_cert_errors`.
-   New `Patch.additions` and `Patch.deletions`:
    [#275](https://github.com/libgit2/pygit2/pull/275)
-   New `Patch.is_binary`:
    [#276](https://github.com/libgit2/pygit2/pull/276)
-   New `Reference.log_append(...)`:
    [#277](https://github.com/libgit2/pygit2/pull/277)
-   New `Blob.is_binary`:
    [#278](https://github.com/libgit2/pygit2/pull/278)
-   New `len(Diff)` shows the number of patches:
    [#281](https://github.com/libgit2/pygit2/pull/281)
-   Rewrite `Repository.status()`:
    [#283](https://github.com/libgit2/pygit2/pull/283)
-   New `Reference.shorthand`:
    [#284](https://github.com/libgit2/pygit2/pull/284)
-   New `Repository.blame(...)`:
    [#285](https://github.com/libgit2/pygit2/pull/285)
-   Now `Repository.listall_references()` and
    `Repository.listall_branches()` return a list, not a tuple:
    [#289](https://github.com/libgit2/pygit2/pull/289)
