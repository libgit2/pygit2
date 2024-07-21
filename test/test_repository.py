# Copyright 2010-2024 The pygit2 contributors
#
# This file is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License, version 2,
# as published by the Free Software Foundation.
#
# In addition to the permissions in the GNU General Public License,
# the authors give you unlimited permission to link the compiled
# version of this file into combinations with other programs,
# and to distribute those combinations without any restriction
# coming from the use of this file.  (The General Public License
# restrictions do apply in other respects; for example, they cover
# modification of the file, and distribution when not linked into
# a combined executable.)
#
# This file is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING.  If not, write to
# the Free Software Foundation, 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301, USA.

from pathlib import Path
import shutil
import tempfile

import pytest

# pygit2
import pygit2
from pygit2 import init_repository, clone_repository, discover_repository
from pygit2 import Oid
from pygit2.enums import (
    CheckoutNotify,
    CheckoutStrategy,
    FileStatus,
    ObjectType,
    RepositoryOpenFlag,
    RepositoryState,
    ResetMode,
    StashApplyProgress,
)
from . import utils


def test_is_empty(testrepo):
    assert not testrepo.is_empty


def test_is_bare(testrepo):
    assert not testrepo.is_bare


def test_get_path(testrepo_path):
    testrepo, path = testrepo_path
    assert Path(testrepo.path).resolve() == (path / '.git').resolve()


def test_get_workdir(testrepo_path):
    testrepo, path = testrepo_path
    assert Path(testrepo.workdir).resolve() == path.resolve()


def test_set_workdir(testrepo):
    directory = tempfile.mkdtemp()
    testrepo.workdir = directory
    assert Path(testrepo.workdir).resolve() == Path(directory).resolve()


def test_checkout_ref(testrepo):
    ref_i18n = testrepo.lookup_reference('refs/heads/i18n')

    # checkout i18n with conflicts and default strategy should
    # not be possible
    with pytest.raises(pygit2.GitError):
        testrepo.checkout(ref_i18n)

    # checkout i18n with GIT_CHECKOUT_FORCE
    head = testrepo.head
    head = testrepo[head.target]
    assert 'new' not in head.tree
    testrepo.checkout(ref_i18n, strategy=CheckoutStrategy.FORCE)

    head = testrepo.head
    head = testrepo[head.target]
    assert head.id == ref_i18n.target
    assert 'new' in head.tree
    assert 'bye.txt' not in testrepo.status()


def test_checkout_callbacks(testrepo):
    ref_i18n = testrepo.lookup_reference('refs/heads/i18n')

    class MyCheckoutCallbacks(pygit2.CheckoutCallbacks):
        def __init__(self):
            super().__init__()
            self.conflicting_paths = set()
            self.updated_paths = set()

        def checkout_notify_flags(self) -> CheckoutNotify:
            return CheckoutNotify.CONFLICT | CheckoutNotify.UPDATED

        def checkout_notify(self, why, path, baseline, target, workdir):
            if why == CheckoutNotify.CONFLICT:
                self.conflicting_paths.add(path)
            elif why == CheckoutNotify.UPDATED:
                self.updated_paths.add(path)

    # checkout i18n with conflicts and default strategy should not be possible
    callbacks = MyCheckoutCallbacks()
    with pytest.raises(pygit2.GitError):
        testrepo.checkout(ref_i18n, callbacks=callbacks)
    # make sure the callbacks caught that
    assert {'bye.txt'} == callbacks.conflicting_paths

    # checkout i18n with GIT_CHECKOUT_FORCE
    head = testrepo.head
    head = testrepo[head.target]
    assert 'new' not in head.tree
    callbacks = MyCheckoutCallbacks()
    testrepo.checkout(ref_i18n, strategy=CheckoutStrategy.FORCE, callbacks=callbacks)
    # make sure the callbacks caught the files affected by the checkout
    assert set() == callbacks.conflicting_paths
    assert {'bye.txt', 'new'} == callbacks.updated_paths


def test_checkout_aborted_from_callbacks(testrepo):
    ref_i18n = testrepo.lookup_reference('refs/heads/i18n')

    def read_bye_txt():
        return testrepo[testrepo.create_blob_fromworkdir('bye.txt')].data

    s = testrepo.status()
    assert s == {'bye.txt': FileStatus.WT_NEW}

    class MyCheckoutCallbacks(pygit2.CheckoutCallbacks):
        def __init__(self):
            super().__init__()
            self.invoked_times = 0

        def checkout_notify(self, why, path, baseline, target, workdir):
            self.invoked_times += 1
            # skip one file so we're certain that NO files are affected,
            # even if aborting the checkout from the second file
            if self.invoked_times == 2:
                raise InterruptedError('Stop the checkout!')

    head = testrepo.head
    head = testrepo[head.target]
    assert 'new' not in head.tree
    assert b'bye world\n' == read_bye_txt()
    callbacks = MyCheckoutCallbacks()

    # checkout i18n with GIT_CHECKOUT_FORCE - callbacks should prevent checkout from completing
    with pytest.raises(InterruptedError):
        testrepo.checkout(
            ref_i18n, strategy=CheckoutStrategy.FORCE, callbacks=callbacks
        )

    assert callbacks.invoked_times == 2
    assert 'new' not in head.tree
    assert b'bye world\n' == read_bye_txt()


def test_checkout_branch(testrepo):
    branch_i18n = testrepo.lookup_branch('i18n')

    # checkout i18n with conflicts and default strategy should
    # not be possible
    with pytest.raises(pygit2.GitError):
        testrepo.checkout(branch_i18n)

    # checkout i18n with GIT_CHECKOUT_FORCE
    head = testrepo.head
    head = testrepo[head.target]
    assert 'new' not in head.tree
    testrepo.checkout(branch_i18n, strategy=CheckoutStrategy.FORCE)

    head = testrepo.head
    head = testrepo[head.target]
    assert head.id == branch_i18n.target
    assert 'new' in head.tree
    assert 'bye.txt' not in testrepo.status()


def test_checkout_index(testrepo):
    # some changes to working dir
    with (Path(testrepo.workdir) / 'hello.txt').open('w') as f:
        f.write('new content')

    # checkout index
    assert 'hello.txt' in testrepo.status()
    testrepo.checkout(strategy=CheckoutStrategy.FORCE)
    assert 'hello.txt' not in testrepo.status()


def test_checkout_head(testrepo):
    # some changes to the index
    with (Path(testrepo.workdir) / 'bye.txt').open('w') as f:
        f.write('new content')
    testrepo.index.add('bye.txt')

    # checkout from index should not change anything
    assert 'bye.txt' in testrepo.status()
    testrepo.checkout(strategy=CheckoutStrategy.FORCE)
    assert 'bye.txt' in testrepo.status()

    # checkout from head will reset index as well
    testrepo.checkout('HEAD', strategy=CheckoutStrategy.FORCE)
    assert 'bye.txt' not in testrepo.status()


def test_checkout_alternative_dir(testrepo):
    ref_i18n = testrepo.lookup_reference('refs/heads/i18n')
    extra_dir = Path(testrepo.workdir) / 'extra-dir'
    extra_dir.mkdir()
    assert len(list(extra_dir.iterdir())) == 0
    testrepo.checkout(ref_i18n, directory=extra_dir)
    assert not len(list(extra_dir.iterdir())) == 0


def test_checkout_paths(testrepo):
    ref_i18n = testrepo.lookup_reference('refs/heads/i18n')
    ref_master = testrepo.lookup_reference('refs/heads/master')
    testrepo.checkout(ref_master)
    testrepo.checkout(ref_i18n, paths=['new'])
    status = testrepo.status()
    assert status['new'] == FileStatus.INDEX_NEW


def test_merge_base(testrepo):
    commit = testrepo.merge_base(
        '5ebeeebb320790caf276b9fc8b24546d63316533',
        '4ec4389a8068641da2d6578db0419484972284c8',
    )
    assert commit == 'acecd5ea2924a4b900e7e149496e1f4b57976e51'

    # Create a commit without any merge base to any other
    sig = pygit2.Signature('me', 'me@example.com')
    indep = testrepo.create_commit(
        None, sig, sig, 'a new root commit', testrepo[commit].peel(pygit2.Tree).id, []
    )

    assert testrepo.merge_base(indep, commit) is None


def test_descendent_of(testrepo):
    assert not testrepo.descendant_of(
        '5ebeeebb320790caf276b9fc8b24546d63316533',
        '4ec4389a8068641da2d6578db0419484972284c8',
    )
    assert not testrepo.descendant_of(
        '5ebeeebb320790caf276b9fc8b24546d63316533',
        '5ebeeebb320790caf276b9fc8b24546d63316533',
    )
    assert testrepo.descendant_of(
        '5ebeeebb320790caf276b9fc8b24546d63316533',
        'acecd5ea2924a4b900e7e149496e1f4b57976e51',
    )
    assert not testrepo.descendant_of(
        'acecd5ea2924a4b900e7e149496e1f4b57976e51',
        '5ebeeebb320790caf276b9fc8b24546d63316533',
    )

    with pytest.raises(pygit2.GitError):
        testrepo.descendant_of(
            '2' * 40,  # a valid but inexistent SHA
            '5ebeeebb320790caf276b9fc8b24546d63316533',
        )


def test_ahead_behind(testrepo):
    ahead, behind = testrepo.ahead_behind(
        '5ebeeebb320790caf276b9fc8b24546d63316533',
        '4ec4389a8068641da2d6578db0419484972284c8',
    )
    assert 1 == ahead
    assert 2 == behind

    ahead, behind = testrepo.ahead_behind(
        '4ec4389a8068641da2d6578db0419484972284c8',
        '5ebeeebb320790caf276b9fc8b24546d63316533',
    )
    assert 2 == ahead
    assert 1 == behind


def test_reset_hard(testrepo):
    ref = '5ebeeebb320790caf276b9fc8b24546d63316533'
    with (Path(testrepo.workdir) / 'hello.txt').open() as f:
        lines = f.readlines()
    assert 'hola mundo\n' in lines
    assert 'bonjour le monde\n' in lines

    testrepo.reset(ref, ResetMode.HARD)
    assert testrepo.head.target == ref

    with (Path(testrepo.workdir) / 'hello.txt').open() as f:
        lines = f.readlines()
    # Hard reset will reset the working copy too
    assert 'hola mundo\n' not in lines
    assert 'bonjour le monde\n' not in lines


def test_reset_soft(testrepo):
    ref = '5ebeeebb320790caf276b9fc8b24546d63316533'
    with (Path(testrepo.workdir) / 'hello.txt').open() as f:
        lines = f.readlines()
    assert 'hola mundo\n' in lines
    assert 'bonjour le monde\n' in lines

    testrepo.reset(ref, ResetMode.SOFT)
    assert testrepo.head.target == ref
    with (Path(testrepo.workdir) / 'hello.txt').open() as f:
        lines = f.readlines()
    # Soft reset will not reset the working copy
    assert 'hola mundo\n' in lines
    assert 'bonjour le monde\n' in lines

    # soft reset will keep changes in the index
    diff = testrepo.diff(cached=True)
    with pytest.raises(KeyError):
        diff[0]


def test_reset_mixed(testrepo):
    ref = '5ebeeebb320790caf276b9fc8b24546d63316533'
    with (Path(testrepo.workdir) / 'hello.txt').open() as f:
        lines = f.readlines()
    assert 'hola mundo\n' in lines
    assert 'bonjour le monde\n' in lines

    testrepo.reset(ref, ResetMode.MIXED)

    assert testrepo.head.target == ref

    with (Path(testrepo.workdir) / 'hello.txt').open() as f:
        lines = f.readlines()
    # mixed reset will not reset the working copy
    assert 'hola mundo\n' in lines
    assert 'bonjour le monde\n' in lines

    # mixed reset will set the index to match working copy
    diff = testrepo.diff(cached=True)
    assert 'hola mundo\n' in diff.patch
    assert 'bonjour le monde\n' in diff.patch


def test_stash(testrepo):
    stash_hash = '6aab5192f88018cb98a7ede99c242f43add5a2fd'
    stash_message = 'custom stash message'
    sig = pygit2.Signature(
        name='Stasher',
        email='stasher@example.com',
        time=1641000000,  # fixed time so the oid is stable
        offset=0,
    )

    # make sure we're starting with no stashes
    assert [] == testrepo.listall_stashes()

    # some changes to working dir
    with (Path(testrepo.workdir) / 'hello.txt').open('w') as f:
        f.write('new content')

    testrepo.stash(sig, include_untracked=True, message=stash_message)
    assert 'hello.txt' not in testrepo.status()

    repo_stashes = testrepo.listall_stashes()
    assert 1 == len(repo_stashes)
    assert repr(repo_stashes[0]) == f'<pygit2.Stash{{{stash_hash}}}>'
    assert repo_stashes[0].commit_id == stash_hash
    assert repo_stashes[0].message == 'On master: ' + stash_message

    testrepo.stash_apply()
    assert 'hello.txt' in testrepo.status()
    assert repo_stashes == testrepo.listall_stashes()  # still the same stashes

    testrepo.stash_drop()
    assert [] == testrepo.listall_stashes()

    with pytest.raises(KeyError):
        testrepo.stash_pop()


def test_stash_partial(testrepo):
    stash_message = 'custom stash message'
    sig = pygit2.Signature(
        name='Stasher', email='stasher@example.com', time=1641000000, offset=0
    )

    # make sure we're starting with no stashes
    assert [] == testrepo.listall_stashes()

    # some changes to working dir
    with (Path(testrepo.workdir) / 'hello.txt').open('w') as f:
        f.write('stash me')
    with (Path(testrepo.workdir) / 'untracked2.txt').open('w') as f:
        f.write('do not stash me')

    assert testrepo.status()['hello.txt'] == FileStatus.WT_MODIFIED
    assert testrepo.status()['bye.txt'] == FileStatus.WT_NEW
    assert testrepo.status()['untracked2.txt'] == FileStatus.WT_NEW

    def stash_pathspecs(paths):
        stash_id = testrepo.stash(
            sig, message=stash_message, keep_all=True, paths=paths
        )
        stash_commit = testrepo[stash_id].peel(pygit2.Commit)
        stash_diff = testrepo.diff(stash_commit.parents[0], stash_commit)
        stash_files = set(patch.delta.new_file.path for patch in stash_diff)
        return stash_files == set(paths)

    # Stash a modified file
    assert stash_pathspecs(['hello.txt'])

    # Stash one of several untracked files
    assert stash_pathspecs(['bye.txt'])

    # Stash a modified file and an untracked file
    assert stash_pathspecs(['hello.txt', 'bye.txt'])


def test_stash_progress_callback(testrepo):
    sig = pygit2.Signature(
        name='Stasher', email='stasher@example.com', time=1641000000, offset=0
    )

    # some changes to working dir
    with (Path(testrepo.workdir) / 'hello.txt').open('w') as f:
        f.write('new content')

    # create the stash
    testrepo.stash(sig, include_untracked=True, message='custom stash message')

    progress_sequence = []

    class MyStashApplyCallbacks(pygit2.StashApplyCallbacks):
        def stash_apply_progress(self, progress: StashApplyProgress):
            progress_sequence.append(progress)

    # apply the stash
    testrepo.stash_apply(callbacks=MyStashApplyCallbacks())

    # make sure the callbacks were notified of all the steps
    assert progress_sequence == [
        StashApplyProgress.LOADING_STASH,
        StashApplyProgress.ANALYZE_INDEX,
        StashApplyProgress.ANALYZE_MODIFIED,
        StashApplyProgress.ANALYZE_UNTRACKED,
        StashApplyProgress.CHECKOUT_UNTRACKED,
        StashApplyProgress.CHECKOUT_MODIFIED,
        StashApplyProgress.DONE,
    ]


def test_stash_aborted_from_callbacks(testrepo):
    sig = pygit2.Signature(
        name='Stasher', email='stasher@example.com', time=1641000000, offset=0
    )

    # some changes to working dir
    with (Path(testrepo.workdir) / 'hello.txt').open('w') as f:
        f.write('new content')
    with (Path(testrepo.workdir) / 'untracked.txt').open('w') as f:
        f.write('yo')

    # create the stash
    testrepo.stash(sig, include_untracked=True, message='custom stash message')

    # define callbacks that will abort the unstash process
    # just as libgit2 is ready to write the files to disk
    class MyStashApplyCallbacks(pygit2.StashApplyCallbacks):
        def stash_apply_progress(self, progress: StashApplyProgress):
            if progress == StashApplyProgress.CHECKOUT_UNTRACKED:
                raise InterruptedError('Stop applying the stash!')

    # attempt to apply and delete the stash; the callbacks will interrupt that
    with pytest.raises(InterruptedError):
        testrepo.stash_pop(callbacks=MyStashApplyCallbacks())

    # we interrupted right before the checkout part of the unstashing process,
    # so the untracked file shouldn't be here
    assert not (Path(testrepo.workdir) / 'untracked.txt').exists()

    # and hello.txt should be as it is on master
    with (Path(testrepo.workdir) / 'hello.txt').open('r') as f:
        assert f.read() == 'hello world\nhola mundo\nbonjour le monde\n'

    # and since we didn't let stash_pop run to completion, the stash itself should still be here
    repo_stashes = testrepo.listall_stashes()
    assert 1 == len(repo_stashes)
    assert repo_stashes[0].message == 'On master: custom stash message'


def test_stash_apply_checkout_options(testrepo):
    sig = pygit2.Signature(
        name='Stasher', email='stasher@example.com', time=1641000000, offset=0
    )

    hello_txt = Path(testrepo.workdir) / 'hello.txt'

    # some changes to working dir
    with hello_txt.open('w') as f:
        f.write('stashed content')

    # create the stash
    testrepo.stash(sig, include_untracked=True, message='custom stash message')

    # define callbacks that raise an InterruptedError when checkout detects a conflict
    class MyStashApplyCallbacks(pygit2.StashApplyCallbacks):
        def checkout_notify(self, why, path, baseline, target, workdir):
            if why == CheckoutNotify.CONFLICT:
                raise InterruptedError('Applying the stash would create a conflict')

    # overwrite hello.txt so that applying the stash would create a conflict
    with hello_txt.open('w') as f:
        f.write('conflicting content')

    # apply the stash with the default (safe) strategy;
    # the callbacks should detect a conflict on checkout
    with pytest.raises(InterruptedError):
        testrepo.stash_apply(
            strategy=CheckoutStrategy.SAFE, callbacks=MyStashApplyCallbacks()
        )

    # hello.txt should be intact
    with hello_txt.open('r') as f:
        assert f.read() == 'conflicting content'

    # force apply the stash; this should work
    testrepo.stash_apply(
        strategy=CheckoutStrategy.FORCE, callbacks=MyStashApplyCallbacks()
    )
    with hello_txt.open('r') as f:
        assert f.read() == 'stashed content'


def test_revert_commit(testrepo):
    master = testrepo.head.peel()
    commit_to_revert = testrepo['4ec4389a8068641da2d6578db0419484972284c8']
    parent = commit_to_revert.parents[0]
    commit_diff_stats = parent.tree.diff_to_tree(commit_to_revert.tree).stats

    revert_index = testrepo.revert_commit(commit_to_revert, master)
    revert_diff_stats = revert_index.diff_to_tree(master.tree).stats

    assert revert_diff_stats.insertions == commit_diff_stats.deletions
    assert revert_diff_stats.deletions == commit_diff_stats.insertions
    assert revert_diff_stats.files_changed == commit_diff_stats.files_changed


def test_revert(testrepo):
    hello_txt = Path(testrepo.workdir) / 'hello.txt'
    commit_to_revert = testrepo['4ec4389a8068641da2d6578db0419484972284c8']

    assert testrepo.state() == RepositoryState.NONE
    assert not testrepo.message
    assert 'bonjour le monde' in hello_txt.read_text()

    # Revert addition of French line in hello.txt
    testrepo.revert(commit_to_revert)

    assert 'bonjour le monde' not in hello_txt.read_text()
    assert testrepo.status()['hello.txt'] == FileStatus.INDEX_MODIFIED
    assert testrepo.state() == RepositoryState.REVERT
    assert (
        testrepo.message
        == f'Revert "Say hello in French"\n\nThis reverts commit {commit_to_revert.id}.\n'
    )


def test_default_signature(testrepo):
    config = testrepo.config
    config['user.name'] = 'Random J Hacker'
    config['user.email'] = 'rjh@example.com'

    sig = testrepo.default_signature
    assert 'Random J Hacker' == sig.name
    assert 'rjh@example.com' == sig.email


def test_new_repo(tmp_path):
    repo = init_repository(tmp_path, False)

    oid = repo.write(ObjectType.BLOB, 'Test')
    assert type(oid) == Oid

    assert (tmp_path / '.git').exists()


def test_no_arg(tmp_path):
    repo = init_repository(tmp_path)
    assert not repo.is_bare


def test_no_arg_aspath(tmp_path):
    repo = init_repository(Path(tmp_path))
    assert not repo.is_bare


def test_pos_arg_false(tmp_path):
    repo = init_repository(tmp_path, False)
    assert not repo.is_bare


def test_pos_arg_true(tmp_path):
    repo = init_repository(tmp_path, True)
    assert repo.is_bare


def test_keyword_arg_false(tmp_path):
    repo = init_repository(tmp_path, bare=False)
    assert not repo.is_bare


def test_keyword_arg_true(tmp_path):
    repo = init_repository(tmp_path, bare=True)
    assert repo.is_bare


def test_discover_repo(tmp_path):
    repo = init_repository(tmp_path, False)
    subdir = tmp_path / 'test1' / 'test2'
    subdir.mkdir(parents=True)
    assert repo.path == discover_repository(str(subdir))


@utils.fspath
def test_discover_repo_aspath(tmp_path):
    repo = init_repository(Path(tmp_path), False)
    subdir = Path(tmp_path) / 'test1' / 'test2'
    subdir.mkdir(parents=True)
    assert repo.path == discover_repository(subdir)


def test_discover_repo_not_found():
    assert discover_repository(tempfile.tempdir) is None


def test_repository_init(barerepo_path):
    barerepo, path = barerepo_path
    assert isinstance(path, Path)
    pygit2.Repository(path)
    pygit2.Repository(str(path))
    pygit2.Repository(bytes(path))


def test_clone_repository(barerepo, tmp_path):
    assert barerepo.is_bare
    repo = clone_repository(Path(barerepo.path), tmp_path / 'clonepath')
    assert not repo.is_empty
    assert not repo.is_bare
    repo = clone_repository(str(barerepo.path), str(tmp_path / 'clonestr'))
    assert not repo.is_empty
    assert not repo.is_bare


def test_clone_bare_repository(barerepo, tmp_path):
    repo = clone_repository(barerepo.path, tmp_path / 'clone', bare=True)
    assert not repo.is_empty
    assert repo.is_bare


@utils.requires_network
def test_clone_shallow_repository(tmp_path):
    # shallow cloning currently only works with remote repositories
    url = 'https://github.com/libgit2/TestGitRepository'
    repo = clone_repository(url, tmp_path / 'clone-shallow', depth=1)
    assert not repo.is_empty
    assert repo.is_shallow


def test_clone_repository_and_remote_callbacks(barerepo, tmp_path):
    url = Path(barerepo.path).resolve().as_uri()
    repo_path = tmp_path / 'clone-into'

    def create_repository(path, bare):
        return init_repository(path, bare)

    # here we override the name
    def create_remote(repo, name, url):
        return repo.remotes.create('custom_remote', url)

    repo = clone_repository(
        url, repo_path, repository=create_repository, remote=create_remote
    )
    assert not repo.is_empty
    assert 'refs/remotes/custom_remote/master' in repo.listall_references()
    assert b'refs/remotes/custom_remote/master' in repo.raw_listall_references()
    assert repo.remotes['custom_remote'] is not None


@utils.requires_network
def test_clone_with_credentials(tmp_path):
    url = 'https://github.com/libgit2/TestGitRepository'
    credentials = pygit2.UserPass('libgit2', 'libgit2')
    callbacks = pygit2.RemoteCallbacks(credentials=credentials)
    repo = clone_repository(url, tmp_path, callbacks=callbacks)

    assert not repo.is_empty


@utils.requires_network
def test_clone_bad_credentials(tmp_path):
    class MyCallbacks(pygit2.RemoteCallbacks):
        def credentials(self, url, username, allowed):
            raise RuntimeError('Unexpected error')

    url = 'https://github.com/github/github'
    with pytest.raises(RuntimeError) as exc:
        clone_repository(url, tmp_path, callbacks=MyCallbacks())
    assert str(exc.value) == 'Unexpected error'


def test_clone_with_checkout_branch(barerepo, tmp_path):
    # create a test case which isolates the remote
    test_repo = clone_repository(
        barerepo.path, tmp_path / 'testrepo-orig.git', bare=True
    )
    test_repo.create_branch('test', test_repo[test_repo.head.target])
    repo = clone_repository(
        test_repo.path, tmp_path / 'testrepo.git', checkout_branch='test', bare=True
    )
    assert repo.lookup_reference('HEAD').target == 'refs/heads/test'


# FIXME The tests below are commented because they are broken:
#
# - test_clone_push_url: Passes, but does nothing useful.
#
# - test_clone_fetch_spec: Segfaults because of a bug in libgit2 0.19,
#   this has been fixed already, so wait for 0.20
#
# - test_clone_push_spec: Passes, but does nothing useful.
#

# def test_clone_push_url():
#    repo_path = "./test/data/testrepo.git/"
#    repo = clone_repository(
#        repo_path, tmp_path, push_url="custom_push_url"
#    )
#    assert not repo.is_empty
#    # FIXME: When pygit2 supports retrieving the pushurl parameter,
#    # enable this test
#    # assert repo.remotes[0].pushurl == "custom_push_url"
#
# def test_clone_fetch_spec():
#    repo_path = "./test/data/testrepo.git/"
#    repo = clone_repository(repo_path, tmp_path,
#                            fetch_spec="refs/heads/test")
#    assert not repo.is_empty
#    # FIXME: When pygit2 retrieve the fetchspec we passed to git clone.
#    # fetchspec seems to be going through, but the Repository class is
#    # not getting it.
#    # assert repo.remotes[0].fetchspec == "refs/heads/test"
#
# def test_clone_push_spec():
#    repo_path = "./test/data/testrepo.git/"
#    repo = clone_repository(repo_path, tmp_path,
#                            push_spec="refs/heads/test")
#    assert not repo.is_empty
#    # FIXME: When pygit2 supports retrieving the pushspec parameter,
#    # enable this test
#    # not sure how to test this either... couldn't find pushspec
#    # assert repo.remotes[0].fetchspec == "refs/heads/test"


def test_worktree(testrepo):
    worktree_name = 'foo'
    worktree_dir = Path(tempfile.mkdtemp())
    # Delete temp path so that it's not present when we attempt to add the
    # worktree later
    worktree_dir.rmdir()

    def _check_worktree(worktree):
        # Confirm the name attribute matches the specified name
        assert worktree.name == worktree_name
        # Confirm the path attribute points to the correct path
        assert Path(worktree.path).resolve() == worktree_dir.resolve()
        # The "gitdir" in a worktree should be a file with a reference to
        # the actual gitdir. Let's make sure that the path exists and is a
        # file.
        assert (worktree_dir / '.git').is_file()

    # We should have zero worktrees
    assert testrepo.list_worktrees() == []
    # Add a worktree
    worktree = testrepo.add_worktree(worktree_name, str(worktree_dir))
    # Check that the worktree was added properly
    _check_worktree(worktree)
    # We should have one worktree now
    assert testrepo.list_worktrees() == [worktree_name]
    # We should also have a branch of the same name
    assert worktree_name in testrepo.listall_branches()
    # Test that lookup_worktree() returns a properly-instantiated
    # pygit2._Worktree object
    _check_worktree(testrepo.lookup_worktree(worktree_name))
    # Remove the worktree dir
    shutil.rmtree(worktree_dir)
    # Prune the worktree. For some reason, libgit2 treats a worktree as
    # valid unless both the worktree directory and data dir under
    # $GIT_DIR/worktrees are gone. This doesn't make much sense since the
    # normal usage involves removing the worktree directory and then
    # pruning. So, for now we have to force the prune. This may be
    # something to take up with libgit2.
    worktree.prune(True)
    assert testrepo.list_worktrees() == []


@utils.fspath
def test_worktree_aspath(testrepo):
    worktree_name = 'foo'
    worktree_dir = Path(tempfile.mkdtemp())
    # Delete temp path so that it's not present when we attempt to add the
    # worktree later
    worktree_dir.rmdir()
    testrepo.add_worktree(worktree_name, worktree_dir)
    assert testrepo.list_worktrees() == [worktree_name]


def test_worktree_custom_ref(testrepo):
    worktree_name = 'foo'
    worktree_dir = Path(tempfile.mkdtemp())
    branch_name = 'version1'

    # New branch based on head
    tip = testrepo.revparse_single('HEAD')
    worktree_ref = testrepo.branches.create(branch_name, tip)
    # Delete temp path so that it's not present when we attempt to add the
    # worktree later
    worktree_dir.rmdir()

    # Add a worktree for the given ref
    worktree = testrepo.add_worktree(worktree_name, str(worktree_dir), worktree_ref)
    # We should have one worktree now
    assert testrepo.list_worktrees() == [worktree_name]
    # We should not have a branch of the same name
    assert worktree_name not in testrepo.listall_branches()

    # The given ref is checked out in the "worktree repository"
    assert worktree_ref.is_checked_out()

    # Remove the worktree dir and prune the worktree
    shutil.rmtree(worktree_dir)
    worktree.prune(True)
    assert testrepo.list_worktrees() == []

    # The ref is no longer checked out
    assert worktree_ref.is_checked_out() is False

    # The branch still exists
    assert branch_name in testrepo.branches


def test_open_extended(tmp_path):
    with utils.TemporaryRepository('dirtyrepo.zip', tmp_path) as path:
        orig_repo = pygit2.Repository(path)
        assert not orig_repo.is_bare
        assert orig_repo.path
        assert orig_repo.workdir

        # GIT_REPOSITORY_OPEN_NO_SEARCH
        subdir_path = path / 'subdir'
        repo = pygit2.Repository(subdir_path)
        assert not repo.is_bare
        assert repo.path == orig_repo.path
        assert repo.workdir == orig_repo.workdir

        with pytest.raises(pygit2.GitError):
            repo = pygit2.Repository(subdir_path, RepositoryOpenFlag.NO_SEARCH)

        # GIT_REPOSITORY_OPEN_NO_DOTGIT
        gitdir_path = path / '.git'
        with pytest.raises(pygit2.GitError):
            repo = pygit2.Repository(path, RepositoryOpenFlag.NO_DOTGIT)

        repo = pygit2.Repository(gitdir_path, RepositoryOpenFlag.NO_DOTGIT)
        assert not repo.is_bare
        assert repo.path == orig_repo.path
        assert repo.workdir == orig_repo.workdir

        # GIT_REPOSITORY_OPEN_BARE
        repo = pygit2.Repository(gitdir_path, RepositoryOpenFlag.BARE)
        assert repo.is_bare
        assert repo.path == orig_repo.path
        assert not repo.workdir


def test_is_shallow(testrepo):
    assert not testrepo.is_shallow

    # create a dummy shallow file
    with (Path(testrepo.path) / 'shallow').open('wt') as f:
        f.write('abcdef0123456789abcdef0123456789abcdef00\n')

    assert testrepo.is_shallow


def test_repository_hashfile(testrepo):
    original_hash = testrepo.index['hello.txt'].id

    # Test simple use
    h = testrepo.hashfile('hello.txt')
    assert h == original_hash

    # Test absolute path
    # For best results on Windows, pass a pure POSIX path. (See https://github.com/libgit2/libgit2/issues/6825)
    absolute_path = Path(testrepo.workdir, 'hello.txt')
    absolute_path = absolute_path.as_posix()  # Windows compatibility
    h = testrepo.hashfile(str(absolute_path))
    assert h == original_hash

    # Test missing path
    with pytest.raises(KeyError):
        testrepo.hashfile('missing-file')

    # Test invalid object type
    with pytest.raises(pygit2.GitError):
        testrepo.hashfile('hello.txt', ObjectType.OFS_DELTA)


def test_repository_hashfile_filter(testrepo):
    original_hash = testrepo.index['hello.txt'].id

    with open(Path(testrepo.workdir, 'hello.txt'), 'rb') as f:
        original_text = f.read()

    crlf_data = original_text.replace(b'\n', b'\r\n')
    crlf_hash = utils.gen_blob_sha1(crlf_data)
    assert crlf_hash != original_hash

    # Write hellocrlf.txt as a copy of hello.txt with CRLF line endings
    with open(Path(testrepo.workdir, 'hellocrlf.txt'), 'wb') as f:
        f.write(crlf_data)

    # Set up a CRLF filter
    testrepo.config['core.autocrlf'] = True
    with open(Path(testrepo.workdir, '.gitattributes'), 'wt') as f:
        f.write('*.txt text\n*.bin binary\n\n')

    # By default, hellocrlf.txt should have the same hash as the original,
    # due to core.autocrlf=True
    h = testrepo.hashfile('hellocrlf.txt')
    assert h == original_hash

    # Treat absolute path with filters.
    # For best results on Windows, pass a pure POSIX path. (See https://github.com/libgit2/libgit2/issues/6825)
    absolute_path = Path(testrepo.workdir, 'hellocrlf.txt')
    absolute_path = absolute_path.as_posix()  # Windows compatibility
    h = testrepo.hashfile(str(absolute_path))
    assert h == original_hash

    # Bypass filters
    h = testrepo.hashfile('hellocrlf.txt', as_path='')
    assert h == crlf_hash

    # Bypass filters via .gitattributes
    h = testrepo.hashfile('hellocrlf.txt', as_path='foobar.bin')
    assert h == crlf_hash

    # If core.safecrlf=fail, hashing a non-CRLF file will fail
    testrepo.config['core.safecrlf'] = 'fail'
    with pytest.raises(pygit2.GitError):
        h = testrepo.hashfile('hello.txt')
