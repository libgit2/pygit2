project('pygit2', 'c', version: '1.13.2')

py = import('python').find_installation(pure: false)

#includes = include_directories('src')

# If some files (such as .py files) need to be copied to site-packages,
# this is where they get specified. Files get copied to
# <python directory>/site-packages/<subdir>
sources = [
  'pygit2/__init__.py',
  'pygit2/_build.py',
  'pygit2/_run.py',
  'pygit2/blame.py',
  'pygit2/blob.py',
  'pygit2/callbacks.py',
  'pygit2/config.py',
  'pygit2/credentials.py',
  'pygit2/errors.py',
  'pygit2/ffi.py',
  'pygit2/filter.py',
  'pygit2/index.py',
  'pygit2/packbuilder.py',
  'pygit2/refspec.py',
  'pygit2/remote.py',
  'pygit2/repository.py',
  'pygit2/settings.py',
  'pygit2/submodule.py',
  'pygit2/utils.py',
]
py.install_sources(sources, subdir: 'pygit2', pure: false)

sources = [
  'src/blob.c',
  'src/branch.c',
  'src/commit.c',
  'src/diff.c',
  'src/error.c',
  'src/filter.c',
  'src/mailmap.c',
  'src/note.c',
  'src/object.c',
  'src/odb_backend.c',
  'src/odb.c',
  'src/oid.c',
  'src/options.c',
  'src/patch.c',
  'src/pygit2.c',
  'src/refdb_backend.c',
  'src/refdb.c',
  'src/reference.c',
  'src/repository.c',
  'src/revspec.c',
  'src/signature.c',
  'src/stash.c',
  'src/tag.c',
  'src/treebuilder.c',
  'src/tree.c',
  'src/utils.c',
  'src/walker.c',
  'src/wildmatch.c',
  'src/worktree.c',
]

py.extension_module('_pygit2', sources, install: true)
