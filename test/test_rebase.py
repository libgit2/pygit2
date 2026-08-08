# Copyright 2010-2026 The pygit2 contributors
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

"""Tests for rebasing.

Two flavors are covered here:

1. "Manual rebase": rebasing implemented from first principles out of
   merge_base(), walk(), merge_trees(), create_commit() and checkout, the
   way applications had to before pygit2 wrapped libgit2's rebase API.
   These tests are kept as a behavioral baseline to compare edge cases
   against.

2. The native rebase API: Repository.rebase_init() / rebase_open() and the
   Rebase object, wrapping libgit2's git_rebase_* functions.
"""

from itertools import count
from pathlib import Path

import pytest

import pygit2
from pygit2 import (
    Blob,
    Commit,
    Index,
    IndexEntry,
    Oid,
    Reference,
    Repository,
    Signature,
)
from pygit2.enums import (
    CheckoutStrategy,
    FileMode,
    RebaseOperationType,
    RepositoryState,
    SortMode,
)

# Fixed base timestamp (like libgit2's examples/rebase.c) so that commit ids
# do not depend on the clock.
_timestamps = count(1_700_000_000)

FileSpec = tuple[str, str, str]  # path, content, commit message


def _signature() -> Signature:
    return Signature('Test User', 'test@example.com', time=next(_timestamps), offset=0)


def _tip(ref: Reference) -> Oid:
    target = ref.target
    assert isinstance(target, Oid), 'symbolic reference where a commit was expected'
    return target


def _commit_index(repo: Repository, message: str) -> Oid:
    index = repo.index
    index.write()
    tree = index.write_tree()
    signature = _signature()
    parents = [] if repo.head_is_unborn else [repo.head.target]
    return repo.create_commit('HEAD', signature, signature, message, tree, parents)


def _commit_file(repo: Repository, name: str, content: str, message: str) -> Oid:
    (Path(repo.workdir) / name).write_text(content)
    repo.index.add(name)
    return _commit_index(repo, message)


def _commit_removal(repo: Repository, name: str, message: str) -> Oid:
    (Path(repo.workdir) / name).unlink()
    repo.index.remove(name)
    return _commit_index(repo, message)


def _diverge(
    repo: Repository, upstream: list[FileSpec], local: list[FileSpec]
) -> tuple[Oid, list[Oid]]:
    """Grow an 'upstream' branch and the current branch from the current HEAD.

    Returns the tip of the upstream branch and the local commit ids, and
    leaves the repository back on the original branch.
    """
    main = repo.head.shorthand
    repo.branches.local.create('upstream', repo.head.peel(Commit))
    repo.checkout(repo.branches['upstream'])
    for name, content, message in upstream:
        _commit_file(repo, name, content, message)
    upstream_target = _tip(repo.branches['upstream'])
    repo.checkout(repo.branches[main])
    local_oids = [
        _commit_file(repo, name, content, message) for name, content, message in local
    ]
    return upstream_target, local_oids


def _entry_text(repo: Repository, entry: IndexEntry | None) -> str:
    """One side of a conflict: '' for a deleted side, newline-terminated text
    otherwise."""
    if entry is None:
        return ''
    blob = repo[entry.id]
    assert isinstance(blob, Blob)
    text = blob.data.decode('utf-8', errors='replace')
    if text and not text.endswith('\n'):
        text += '\n'
    return text


def _resolve_with_markers(repo: Repository, merge_index: Index, commit: Commit) -> None:
    """Resolve every conflict by embedding both sides of the file in git-style
    conflict markers, then stage the marked-up file, the way `git rebase`
    leaves conflicting files in the working tree for the user to edit."""
    conflicts = merge_index.conflicts
    assert conflicts is not None
    resolutions = []
    for ancestor_entry, our_entry, their_entry in conflicts:
        some_entry = their_entry or our_entry or ancestor_entry
        assert some_entry is not None
        content = (
            '<<<<<<< HEAD (rebased)\n'
            + _entry_text(repo, our_entry)
            + '=======\n'
            + _entry_text(repo, their_entry)
            + f'>>>>>>> {commit.short_id} ({commit.message.strip()})\n'
        )
        blob_oid = repo.create_blob(content.encode('utf-8'))
        resolutions.append(IndexEntry(some_entry.path, blob_oid, FileMode.BLOB))
    for entry in resolutions:
        del merge_index.conflicts[entry.path]
        merge_index.add(entry)


def _replay_commit(repo: Repository, commit: Commit, onto: Oid) -> Oid:
    """Replay one commit on top of `onto` with a three-way merge of trees."""
    merge_index = repo.merge_trees(
        commit.parents[0].tree,  # ancestor: state the commit was made against
        repo[onto].peel(Commit).tree,  # ours: state rebuilt so far
        commit.tree,  # theirs: the commit being replayed
    )
    message = commit.message
    if merge_index.conflicts is not None:
        _resolve_with_markers(repo, merge_index, commit)
        message = (
            f'{message.rstrip()}\n\n[Rebased with conflicts - manual resolution needed]'
        )
    tree_oid = merge_index.write_tree(repo)
    signature = _signature()
    return repo.create_commit(None, signature, signature, message, tree_oid, [onto])


def _fast_forward(repo: Repository, upstream_target: Oid) -> None:
    repo.checkout_tree(repo[upstream_target])  # type: ignore[no-untyped-call]
    repo.references[repo.head.name].set_target(upstream_target)


def _rebase_onto(repo: Repository, upstream_target: Oid) -> None:
    """Rebase the current branch onto `upstream_target` from first principles.

    This is the second half of a hand-rolled `git pull --rebase` (the first
    half being a fetch): fast-forward when possible, otherwise replay the
    diverged local commits one by one on top of the upstream tip.
    """
    merge_base = repo.merge_base(repo.head.target, upstream_target)
    if merge_base == upstream_target:
        # Upstream did not move, there is nothing to rebase onto.
        return
    if merge_base == repo.head.target:
        _fast_forward(repo, upstream_target)
        return

    walker = repo.walk(repo.head.target, SortMode.TOPOLOGICAL)
    walker.hide(merge_base)
    commits_to_replay = list(walker)
    commits_to_replay.reverse()  # replay oldest first

    repo.checkout_tree(repo[upstream_target])  # type: ignore[no-untyped-call]
    current_parent = upstream_target
    for commit in commits_to_replay:
        current_parent = _replay_commit(repo, commit, current_parent)

    repo.references[repo.head.name].set_target(current_parent)
    repo.checkout('HEAD', strategy=CheckoutStrategy.FORCE)


def _linear_history(repo: Repository) -> list[str]:
    """Commit messages from HEAD down to the root, asserting that the history
    contains no merge commits."""
    messages = []
    for commit in repo.walk(repo.head.target, SortMode.TOPOLOGICAL):
        assert len(commit.parents) <= 1
        messages.append(commit.message)
    return messages


@pytest.fixture
def rebaserepo(tmp_path: Path) -> Repository:
    repo = pygit2.init_repository(tmp_path / 'rebaserepo')
    _commit_file(repo, 'README.md', '# Test Repository\n', 'Initial commit')
    _commit_file(
        repo, 'file1.txt', 'Content of file 1\nLine 2\nLine 3\n', 'Add file1.txt'
    )
    _commit_file(
        repo, 'file2.txt', 'Content of file 2\nOriginal content\n', 'Add file2.txt'
    )
    return repo


def test_rebase_noop_when_up_to_date(rebaserepo: Repository) -> None:
    head_before = _tip(rebaserepo.head)
    _rebase_onto(rebaserepo, head_before)
    assert rebaserepo.head.target == head_before
    assert rebaserepo.status() == {}


def test_rebase_noop_when_upstream_is_behind(rebaserepo: Repository) -> None:
    upstream_target, local_oids = _diverge(
        rebaserepo,
        upstream=[],
        local=[('file4.txt', 'New file 4\n', 'Add file4.txt')],
    )
    _rebase_onto(rebaserepo, upstream_target)
    assert rebaserepo.head.target == local_oids[0]
    assert rebaserepo.status() == {}


def test_rebase_fast_forwards_when_local_did_not_diverge(
    rebaserepo: Repository,
) -> None:
    upstream_target, _ = _diverge(
        rebaserepo,
        upstream=[
            ('file3.txt', 'New file 3\n', 'Add file3.txt'),
            ('file1.txt', 'Content of file 1\nLine 2 changed\n', 'Change file1.txt'),
        ],
        local=[],
    )
    _rebase_onto(rebaserepo, upstream_target)
    assert rebaserepo.head.target == upstream_target
    workdir = Path(rebaserepo.workdir)
    assert (workdir / 'file3.txt').read_text() == 'New file 3\n'
    assert (workdir / 'file1.txt').read_text() == 'Content of file 1\nLine 2 changed\n'
    assert rebaserepo.status() == {}


def test_rebase_replays_diverged_commit_cleanly(rebaserepo: Repository) -> None:
    upstream_target, local_oids = _diverge(
        rebaserepo,
        upstream=[('file3.txt', 'New file 3 from upstream\n', 'Add file3.txt')],
        local=[('file4.txt', 'New file 4 from local\n', 'Add file4.txt')],
    )
    _rebase_onto(rebaserepo, upstream_target)

    head = rebaserepo.head.peel(Commit)
    assert head.message == 'Add file4.txt'
    # The replayed commit is a new object with the upstream tip as its parent.
    assert head.id != local_oids[0]
    assert [parent.id for parent in head.parents] == [upstream_target]
    workdir = Path(rebaserepo.workdir)
    assert (workdir / 'file3.txt').read_text() == 'New file 3 from upstream\n'
    assert (workdir / 'file4.txt').read_text() == 'New file 4 from local\n'
    assert rebaserepo.status() == {}
    # The pre-rebase commit is still in the object database.
    assert rebaserepo.get(local_oids[0]) is not None


def test_rebase_replays_multiple_commits_oldest_first(rebaserepo: Repository) -> None:
    upstream_target, _ = _diverge(
        rebaserepo,
        upstream=[('file3.txt', 'upstream\n', 'Upstream commit')],
        local=[
            ('a.txt', 'a\n', 'Add a.txt'),
            ('b.txt', 'b\n', 'Add b.txt'),
            ('c.txt', 'c\n', 'Add c.txt'),
        ],
    )
    _rebase_onto(rebaserepo, upstream_target)
    assert _linear_history(rebaserepo) == [
        'Add c.txt',
        'Add b.txt',
        'Add a.txt',
        'Upstream commit',
        'Add file2.txt',
        'Add file1.txt',
        'Initial commit',
    ]
    workdir = Path(rebaserepo.workdir)
    for name in ('a.txt', 'b.txt', 'c.txt', 'file3.txt'):
        assert (workdir / name).exists()
    assert rebaserepo.status() == {}


def test_rebase_conflicting_commit_gets_markers(rebaserepo: Repository) -> None:
    upstream_target, local_oids = _diverge(
        rebaserepo,
        upstream=[
            (
                'file1.txt',
                'Content of file 1\nLine 2 changed upstream\nLine 3\n',
                'Change line 2 upstream',
            )
        ],
        local=[
            (
                'file1.txt',
                'Content of file 1\nLine 2 changed locally\nLine 3\n',
                'Change line 2 locally',
            )
        ],
    )
    original = rebaserepo[local_oids[0]].peel(Commit)
    _rebase_onto(rebaserepo, upstream_target)

    head = rebaserepo.head.peel(Commit)
    assert head.message == (
        'Change line 2 locally\n\n[Rebased with conflicts - manual resolution needed]'
    )
    assert [parent.id for parent in head.parents] == [upstream_target]
    expected = (
        '<<<<<<< HEAD (rebased)\n'
        'Content of file 1\n'
        'Line 2 changed upstream\n'
        'Line 3\n'
        '=======\n'
        'Content of file 1\n'
        'Line 2 changed locally\n'
        'Line 3\n'
        f'>>>>>>> {original.short_id} (Change line 2 locally)\n'
    )
    assert (Path(rebaserepo.workdir) / 'file1.txt').read_text() == expected
    assert rebaserepo.index.conflicts is None
    assert rebaserepo.status() == {}


def test_rebase_conflict_when_local_deleted_a_modified_file(
    rebaserepo: Repository,
) -> None:
    main = rebaserepo.head.shorthand
    rebaserepo.branches.local.create('upstream', rebaserepo.head.peel(Commit))
    rebaserepo.checkout(rebaserepo.branches['upstream'])
    _commit_file(
        rebaserepo,
        'file2.txt',
        'Content of file 2\nModified upstream\n',
        'Modify file2.txt upstream',
    )
    upstream_target = _tip(rebaserepo.branches['upstream'])
    rebaserepo.checkout(rebaserepo.branches[main])
    removal_oid = _commit_removal(rebaserepo, 'file2.txt', 'Delete file2.txt')
    original = rebaserepo[removal_oid].peel(Commit)

    _rebase_onto(rebaserepo, upstream_target)

    head = rebaserepo.head.peel(Commit)
    assert head.message == (
        'Delete file2.txt\n\n[Rebased with conflicts - manual resolution needed]'
    )
    # The deleted side is left empty between the conflict markers.
    expected = (
        '<<<<<<< HEAD (rebased)\n'
        'Content of file 2\n'
        'Modified upstream\n'
        '=======\n'
        f'>>>>>>> {original.short_id} (Delete file2.txt)\n'
    )
    assert (Path(rebaserepo.workdir) / 'file2.txt').read_text() == expected
    assert rebaserepo.status() == {}


def test_rebase_mixed_clean_and_conflicting_commits(rebaserepo: Repository) -> None:
    upstream_target, local_oids = _diverge(
        rebaserepo,
        upstream=[
            (
                'file1.txt',
                'Content of file 1\nLine 2 changed upstream\nLine 3\n',
                'Change line 2 upstream',
            )
        ],
        local=[
            ('file4.txt', 'New file 4\n', 'Add file4.txt'),
            (
                'file1.txt',
                'Content of file 1\nLine 2 changed locally\nLine 3\n',
                'Change line 2 locally',
            ),
        ],
    )
    original = rebaserepo[local_oids[1]].peel(Commit)
    _rebase_onto(rebaserepo, upstream_target)

    # The clean commit is replayed verbatim, only the conflicting one is
    # annotated.
    assert _linear_history(rebaserepo) == [
        'Change line 2 locally\n\n[Rebased with conflicts - manual resolution needed]',
        'Add file4.txt',
        'Change line 2 upstream',
        'Add file2.txt',
        'Add file1.txt',
        'Initial commit',
    ]
    workdir = Path(rebaserepo.workdir)
    assert (workdir / 'file4.txt').read_text() == 'New file 4\n'
    expected = (
        '<<<<<<< HEAD (rebased)\n'
        'Content of file 1\n'
        'Line 2 changed upstream\n'
        'Line 3\n'
        '=======\n'
        'Content of file 1\n'
        'Line 2 changed locally\n'
        'Line 3\n'
        f'>>>>>>> {original.short_id} (Change line 2 locally)\n'
    )
    assert (workdir / 'file1.txt').read_text() == expected
    assert rebaserepo.status() == {}


def test_pull_rebase_after_fetch_from_remote(tmp_path: Path) -> None:
    """The full `git pull --rebase` flow against a local "remote"."""
    origin_path = tmp_path / 'origin'
    origin = pygit2.init_repository(origin_path)
    _commit_file(origin, 'README.md', '# Test Repository\n', 'Initial commit')
    _commit_file(origin, 'file1.txt', 'Content of file 1\n', 'Add file1.txt')

    local = pygit2.clone_repository(str(origin_path), str(tmp_path / 'local'))

    _commit_file(origin, 'file3.txt', 'From origin\n', 'Add file3.txt in origin')
    local_oid = _commit_file(local, 'file4.txt', 'From local\n', 'Add file4.txt local')

    for remote in local.remotes:
        remote.fetch()

    branch = local.branches[local.head.shorthand]
    upstream = branch.upstream
    assert upstream is not None
    _rebase_onto(local, _tip(upstream))

    assert _linear_history(local) == [
        'Add file4.txt local',
        'Add file3.txt in origin',
        'Add file1.txt',
        'Initial commit',
    ]
    assert local.head.target != local_oid
    workdir = Path(local.workdir)
    assert (workdir / 'file3.txt').read_text() == 'From origin\n'
    assert (workdir / 'file4.txt').read_text() == 'From local\n'
    assert local.status() == {}


# ---------------------------------------------------------------------------
# The native rebase API: Repository.rebase_init() / rebase_open() and Rebase
# ---------------------------------------------------------------------------

CONFLICT_SCENARIO = dict(
    upstream=[
        (
            'file1.txt',
            'Content of file 1\nLine 2 changed upstream\nLine 3\n',
            'Change line 2 upstream',
        )
    ],
    local=[
        (
            'file1.txt',
            'Content of file 1\nLine 2 changed locally\nLine 3\n',
            'Change line 2 locally',
        )
    ],
)


def test_rebase_api_clean(rebaserepo: Repository) -> None:
    main = rebaserepo.head.shorthand
    upstream_target, local_oids = _diverge(
        rebaserepo,
        upstream=[('file3.txt', 'New file 3 from upstream\n', 'Add file3.txt')],
        local=[
            ('a.txt', 'a\n', 'Add a.txt'),
            ('b.txt', 'b\n', 'Add b.txt'),
        ],
    )
    rebase = rebaserepo.rebase_init(upstream=rebaserepo.branches['upstream'])

    assert len(rebase) == 2
    assert rebase.current_index is None
    assert rebase.onto_id == upstream_target
    assert rebase.onto_name == 'upstream'
    assert rebase.orig_head_name == f'refs/heads/{main}'
    assert rebase.orig_head_id == local_oids[-1]
    # Operations replay the diverged commits oldest first.
    assert [rebase[i].id for i in range(len(rebase))] == local_oids
    assert rebase[-1].id == local_oids[-1]
    with pytest.raises(IndexError):
        rebase[2]

    replayed: list[Oid] = []
    for i, operation in enumerate(rebase):
        assert operation.type == RebaseOperationType.PICK
        assert operation.id == local_oids[i]
        assert operation.exec is None
        assert rebase.current_index == i
        assert rebaserepo.state() == RepositoryState.REBASE_MERGE
        new_id = rebase.commit(committer=_signature())
        assert new_id is not None
        replayed.append(new_id)
    rebase.finish(_signature())

    assert rebaserepo.state() == RepositoryState.NONE
    assert replayed[0] != local_oids[0]
    head = rebaserepo.head.peel(Commit)
    assert head.id == replayed[-1]
    assert rebaserepo.head.name == f'refs/heads/{main}'
    assert _linear_history(rebaserepo)[:4] == [
        'Add b.txt',
        'Add a.txt',
        'Add file3.txt',
        'Add file2.txt',
    ]
    workdir = Path(rebaserepo.workdir)
    for name in ('a.txt', 'b.txt', 'file3.txt'):
        assert (workdir / name).exists()
    assert rebaserepo.status() == {}


def test_rebase_api_conflict_has_hunk_level_markers(rebaserepo: Repository) -> None:
    _, local_oids = _diverge(rebaserepo, **CONFLICT_SCENARIO)
    rebase = rebaserepo.rebase_init(upstream=rebaserepo.branches['upstream'])

    next(rebase)
    conflicts = rebaserepo.index.conflicts
    assert conflicts is not None
    ancestor, ours, theirs = conflicts['file1.txt']
    assert ancestor is not None and ours is not None and theirs is not None

    # Unlike the manual whole-file markers, libgit2 wrote hunk-level
    # markers into the working directory: common lines stay outside, and
    # the sides are labeled with the onto name and the commit summary.
    expected = (
        'Content of file 1\n'
        '<<<<<<< upstream\n'
        'Line 2 changed upstream\n'
        '=======\n'
        'Line 2 changed locally\n'
        '>>>>>>> Change line 2 locally\n'
        'Line 3\n'
    )
    assert (Path(rebaserepo.workdir) / 'file1.txt').read_text() == expected

    # Keep the markers as the resolution, the autocommit way: staging the
    # file marks the conflict as resolved.
    rebaserepo.index.add('file1.txt')
    rebaserepo.index.write()
    assert rebaserepo.index.conflicts is None
    rebase.commit(
        committer=_signature(),
        message='Change line 2 locally\n\n[Rebased with conflicts]',
    )
    with pytest.raises(StopIteration):
        next(rebase)
    rebase.finish(_signature())

    head = rebaserepo.head.peel(Commit)
    assert head.message == 'Change line 2 locally\n\n[Rebased with conflicts]'
    assert (Path(rebaserepo.workdir) / 'file1.txt').read_text() == expected
    assert rebaserepo.status() == {}


def test_rebase_api_unresolved_conflict_blocks_commit(rebaserepo: Repository) -> None:
    _diverge(rebaserepo, **CONFLICT_SCENARIO)
    rebase = rebaserepo.rebase_init(upstream=rebaserepo.branches['upstream'])
    next(rebase)
    with pytest.raises(pygit2.GitError):
        rebase.commit(committer=_signature())
    rebase.abort()


def test_rebase_api_custom_labels(rebaserepo: Repository) -> None:
    _diverge(rebaserepo, **CONFLICT_SCENARIO)
    rebase = rebaserepo.rebase_init(
        upstream=rebaserepo.branches['upstream'],
        our_label='HEAD (rebased)',
        their_label='incoming',
    )
    next(rebase)
    content = (Path(rebaserepo.workdir) / 'file1.txt').read_text()
    assert '<<<<<<< HEAD (rebased)\n' in content
    assert '>>>>>>> incoming\n' in content
    rebase.abort()


def test_rebase_api_diff3_conflict_style(rebaserepo: Repository) -> None:
    _diverge(rebaserepo, **CONFLICT_SCENARIO)
    rebase = rebaserepo.rebase_init(
        upstream=rebaserepo.branches['upstream'],
        checkout_strategy=CheckoutStrategy.SAFE
        | CheckoutStrategy.RECREATE_MISSING
        | CheckoutStrategy.CONFLICT_STYLE_DIFF3,
    )
    next(rebase)
    content = (Path(rebaserepo.workdir) / 'file1.txt').read_text()
    # diff3 style includes the common ancestor version of the hunk.
    assert '||||||| ancestor\nLine 2\n=======\n' in content
    rebase.abort()


def test_rebase_api_abort(rebaserepo: Repository) -> None:
    main = rebaserepo.head.shorthand
    upstream_target, local_oids = _diverge(
        rebaserepo,
        upstream=[('file3.txt', 'upstream\n', 'Upstream commit')],
        local=[
            ('a.txt', 'a\n', 'Add a.txt'),
            ('b.txt', 'b\n', 'Add b.txt'),
        ],
    )
    head_before = _tip(rebaserepo.head)

    rebase = rebaserepo.rebase_init(upstream=rebaserepo.branches['upstream'])
    operation = next(rebase)
    rebase.commit(committer=_signature())
    operation = next(rebase)
    assert operation.id == local_oids[1]
    assert rebaserepo.state() == RepositoryState.REBASE_MERGE

    rebase.abort()

    assert rebaserepo.state() == RepositoryState.NONE
    assert rebaserepo.head.name == f'refs/heads/{main}'
    assert rebaserepo.head.target == head_before
    workdir = Path(rebaserepo.workdir)
    assert (workdir / 'a.txt').exists()
    assert (workdir / 'b.txt').exists()
    assert not (workdir / 'file3.txt').exists()
    assert rebaserepo.status() == {}


def test_rebase_api_inmemory(rebaserepo: Repository) -> None:
    main = rebaserepo.head.shorthand
    upstream_target, local_oids = _diverge(
        rebaserepo,
        upstream=[('file3.txt', 'upstream\n', 'Upstream commit')],
        local=[('file4.txt', 'local\n', 'Add file4.txt')],
    )
    head_before = _tip(rebaserepo.head)

    rebase = rebaserepo.rebase_init(
        upstream=rebaserepo.branches['upstream'], inmemory=True
    )
    operation = next(rebase)
    assert operation.id == local_oids[0]
    # The repository is not put into a rebasing state, and the working
    # directory is not touched.
    assert rebaserepo.state() == RepositoryState.NONE
    assert not (Path(rebaserepo.workdir) / 'file3.txt').exists()

    merged = rebase.inmemory_index
    assert merged.conflicts is None
    assert 'file4.txt' in merged

    new_oid = rebase.commit(committer=_signature())
    assert new_oid is not None
    rebase.finish(_signature())

    # HEAD and the branch were left alone; putting the result in place is
    # the caller's job, like the manual _fast_forward() epilogue.
    assert rebaserepo.head.target == head_before
    new_commit = rebaserepo[new_oid].peel(Commit)
    assert [parent.id for parent in new_commit.parents] == [upstream_target]
    assert new_commit.message == 'Add file4.txt'

    rebaserepo.references[f'refs/heads/{main}'].set_target(new_oid)
    rebaserepo.checkout('HEAD', strategy=CheckoutStrategy.FORCE)
    assert _linear_history(rebaserepo)[:2] == ['Add file4.txt', 'Upstream commit']
    assert rebaserepo.status() == {}


def test_rebase_api_finish_moves_branch_when_local_did_not_diverge(
    rebaserepo: Repository,
) -> None:
    upstream_target, _ = _diverge(
        rebaserepo,
        upstream=[('file3.txt', 'New file 3\n', 'Add file3.txt')],
        local=[],
    )
    rebase = rebaserepo.rebase_init(upstream=rebaserepo.branches['upstream'])
    # Local did not diverge: there is nothing to replay, and finishing
    # fast-forwards the branch to the upstream tip.
    assert len(rebase) == 0
    with pytest.raises(StopIteration):
        next(rebase)
    rebase.finish(_signature())
    assert rebaserepo.head.target == upstream_target
    assert (Path(rebaserepo.workdir) / 'file3.txt').exists()
    assert rebaserepo.status() == {}


def test_rebase_api_replays_even_when_upstream_is_behind(
    rebaserepo: Repository,
) -> None:
    """Unlike `git pull --rebase` porcelain (and the manual no-op check),
    the plumbing does not detect that the upstream is simply behind: it
    replays the local commits, rewriting their ids."""
    upstream_target, local_oids = _diverge(
        rebaserepo,
        upstream=[],
        local=[('file4.txt', 'New file 4\n', 'Add file4.txt')],
    )
    rebase = rebaserepo.rebase_init(upstream=rebaserepo.branches['upstream'])
    assert len(rebase) == 1
    for _operation in rebase:
        rebase.commit(committer=_signature())
    rebase.finish(_signature())
    assert _linear_history(rebaserepo)[:2] == ['Add file4.txt', 'Add file2.txt']
    assert rebaserepo.head.target != local_oids[0]
    assert rebaserepo.status() == {}


def test_rebase_api_already_applied_commit(rebaserepo: Repository) -> None:
    """A local commit whose changes are already present upstream has
    nothing left to commit; commit() reports that by returning None and
    the caller simply moves on to the next operation."""
    _diverge(
        rebaserepo,
        upstream=[('file3.txt', 'identical\n', 'Add file3.txt upstream')],
        local=[('file3.txt', 'identical\n', 'Add file3.txt locally')],
    )
    rebase = rebaserepo.rebase_init(upstream=rebaserepo.branches['upstream'])
    next(rebase)
    assert rebase.commit(committer=_signature()) is None
    with pytest.raises(StopIteration):
        next(rebase)
    rebase.finish(_signature())
    assert rebaserepo.head.target == _tip(rebaserepo.branches['upstream'])
    assert rebaserepo.status() == {}


def test_rebase_open_resumes_rebase(rebaserepo: Repository) -> None:
    upstream_target, local_oids = _diverge(
        rebaserepo,
        upstream=[('file3.txt', 'upstream\n', 'Upstream commit')],
        local=[
            ('a.txt', 'a\n', 'Add a.txt'),
            ('b.txt', 'b\n', 'Add b.txt'),
        ],
    )
    rebase = rebaserepo.rebase_init(upstream=rebaserepo.branches['upstream'])
    next(rebase)
    rebase.commit(committer=_signature())
    del rebase

    # Another client (or a later process) picks the rebase up from disk.
    resumed = rebaserepo.rebase_open()
    assert len(resumed) == 2
    assert resumed.current_index == 0
    assert resumed.onto_id == upstream_target
    operation = next(resumed)
    assert operation.id == local_oids[1]
    resumed.commit(committer=_signature())
    resumed.finish(_signature())

    assert rebaserepo.state() == RepositoryState.NONE
    assert _linear_history(rebaserepo)[:3] == [
        'Add b.txt',
        'Add a.txt',
        'Upstream commit',
    ]
    assert rebaserepo.status() == {}
