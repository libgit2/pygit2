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

"""Tests for reference objects."""

from pathlib import Path

import pytest

from pygit2 import Commit, Signature, Tree, reference_is_valid_name
from pygit2 import AlreadyExistsError, GitError, InvalidSpecError
from pygit2.enums import ReferenceType


LAST_COMMIT = '2be5719152d4f82c7302b1c0932d8e5f0a4a0e98'


def test_refs_list_objects(testrepo):
    refs = [(ref.name, ref.target) for ref in testrepo.references.objects]
    assert sorted(refs) == [
        ('refs/heads/i18n', '5470a671a80ac3789f1a6a8cefbcf43ce7af0563'),
        ('refs/heads/master', '2be5719152d4f82c7302b1c0932d8e5f0a4a0e98'),
    ]


def test_refs_list(testrepo):
    # Without argument
    assert sorted(testrepo.references) == ['refs/heads/i18n', 'refs/heads/master']

    # We add a symbolic reference
    testrepo.create_reference('refs/tags/version1', 'refs/heads/master')
    assert sorted(testrepo.references) == [
        'refs/heads/i18n',
        'refs/heads/master',
        'refs/tags/version1',
    ]


def test_head(testrepo):
    head = testrepo.head
    assert LAST_COMMIT == testrepo[head.target].id
    assert LAST_COMMIT == testrepo[head.raw_target].id


def test_refs_getitem(testrepo):
    refname = 'refs/foo'
    # Raise KeyError ?
    with pytest.raises(KeyError):
        testrepo.references[refname]

    # Return None ?
    assert testrepo.references.get(refname) is None

    # Test a lookup
    reference = testrepo.references.get('refs/heads/master')
    assert reference.name == 'refs/heads/master'


def test_refs_get_sha(testrepo):
    reference = testrepo.references['refs/heads/master']
    assert reference.target == LAST_COMMIT


def test_refs_set_sha(testrepo):
    NEW_COMMIT = '5ebeeebb320790caf276b9fc8b24546d63316533'
    reference = testrepo.references.get('refs/heads/master')
    reference.set_target(NEW_COMMIT)
    assert reference.target == NEW_COMMIT


def test_refs_set_sha_prefix(testrepo):
    NEW_COMMIT = '5ebeeebb320790caf276b9fc8b24546d63316533'
    reference = testrepo.references.get('refs/heads/master')
    reference.set_target(NEW_COMMIT[0:6])
    assert reference.target == NEW_COMMIT


def test_refs_get_type(testrepo):
    reference = testrepo.references.get('refs/heads/master')
    assert reference.type == ReferenceType.DIRECT


def test_refs_get_target(testrepo):
    reference = testrepo.references.get('HEAD')
    assert reference.target == 'refs/heads/master'
    assert reference.raw_target == b'refs/heads/master'


def test_refs_set_target(testrepo):
    reference = testrepo.references.get('HEAD')
    assert reference.target == 'refs/heads/master'
    assert reference.raw_target == b'refs/heads/master'
    reference.set_target('refs/heads/i18n')
    assert reference.target == 'refs/heads/i18n'
    assert reference.raw_target == b'refs/heads/i18n'


def test_refs_get_shorthand(testrepo):
    reference = testrepo.references.get('refs/heads/master')
    assert reference.shorthand == 'master'
    reference = testrepo.references.create('refs/remotes/origin/master', LAST_COMMIT)
    assert reference.shorthand == 'origin/master'


def test_refs_set_target_with_message(testrepo):
    reference = testrepo.references.get('HEAD')
    assert reference.target == 'refs/heads/master'
    assert reference.raw_target == b'refs/heads/master'
    sig = Signature('foo', 'bar')
    testrepo.set_ident('foo', 'bar')
    msg = 'Hello log'
    reference.set_target('refs/heads/i18n', message=msg)
    assert reference.target == 'refs/heads/i18n'
    assert reference.raw_target == b'refs/heads/i18n'
    first = list(reference.log())[0]
    assert first.message == msg
    assert first.committer == sig


def test_refs_delete(testrepo):
    # We add a tag as a new reference that points to "origin/master"
    reference = testrepo.references.create('refs/tags/version1', LAST_COMMIT)
    assert 'refs/tags/version1' in testrepo.references

    # And we delete it
    reference.delete()
    assert 'refs/tags/version1' not in testrepo.references

    # Access the deleted reference
    with pytest.raises(GitError):
        getattr(reference, 'name')
    with pytest.raises(GitError):
        getattr(reference, 'type')
    with pytest.raises(GitError):
        getattr(reference, 'target')
    with pytest.raises(GitError):
        reference.delete()
    with pytest.raises(GitError):
        reference.resolve()
    with pytest.raises(GitError):
        reference.rename('refs/tags/version2')


def test_refs_rename(testrepo):
    # We add a tag as a new reference that points to "origin/master"
    reference = testrepo.references.create('refs/tags/version1', LAST_COMMIT)
    assert reference.name == 'refs/tags/version1'
    reference.rename('refs/tags/version2')
    assert reference.name == 'refs/tags/version2'

    with pytest.raises(AlreadyExistsError):
        reference.rename('refs/tags/version2')

    with pytest.raises(InvalidSpecError):
        reference.rename('b1')


# def test_reload(testrepo):
#    name = 'refs/tags/version1'
#    ref = testrepo.create_reference(name, "refs/heads/master", symbolic=True)
#    ref2 = testrepo.lookup_reference(name)
#    ref.delete()
#    assert ref2.name == name
#    with pytest.raises(KeyError): ref2.reload()
#    with pytest.raises(GitError): getattr(ref2, 'name')


def test_refs_resolve(testrepo):
    reference = testrepo.references.get('HEAD')
    assert reference.type == ReferenceType.SYMBOLIC
    reference = reference.resolve()
    assert reference.type == ReferenceType.DIRECT
    assert reference.target == LAST_COMMIT


def test_refs_resolve_identity(testrepo):
    head = testrepo.references.get('HEAD')
    ref = head.resolve()
    assert ref.resolve() is ref


def test_refs_create(testrepo):
    # We add a tag as a new reference that points to "origin/master"
    reference = testrepo.references.create('refs/tags/version1', LAST_COMMIT)
    refs = testrepo.references
    assert 'refs/tags/version1' in refs
    reference = testrepo.references.get('refs/tags/version1')
    assert reference.target == LAST_COMMIT

    # try to create existing reference
    with pytest.raises(ValueError):
        testrepo.references.create('refs/tags/version1', LAST_COMMIT)

    # try to create existing reference with force
    reference = testrepo.references.create(
        'refs/tags/version1', LAST_COMMIT, force=True
    )
    assert reference.target == LAST_COMMIT


def test_refs_create_symbolic(testrepo):
    # We add a tag as a new symbolic reference that always points to
    # "refs/heads/master"
    reference = testrepo.references.create('refs/tags/beta', 'refs/heads/master')
    assert reference.type == ReferenceType.SYMBOLIC
    assert reference.target == 'refs/heads/master'
    assert reference.raw_target == b'refs/heads/master'

    # try to create existing symbolic reference
    with pytest.raises(ValueError):
        testrepo.references.create('refs/tags/beta', 'refs/heads/master')

    # try to create existing symbolic reference with force
    reference = testrepo.references.create(
        'refs/tags/beta', 'refs/heads/master', force=True
    )
    assert reference.type == ReferenceType.SYMBOLIC
    assert reference.target == 'refs/heads/master'
    assert reference.raw_target == b'refs/heads/master'


# def test_packall_references(testrepo):
#    testrepo.packall_references()


def test_refs_peel(testrepo):
    ref = testrepo.references.get('refs/heads/master')
    assert testrepo[ref.target].id == ref.peel().id
    assert testrepo[ref.raw_target].id == ref.peel().id

    commit = ref.peel(Commit)
    assert commit.tree.id == ref.peel(Tree).id


def test_refs_equality(testrepo):
    ref1 = testrepo.references.get('refs/heads/master')
    ref2 = testrepo.references.get('refs/heads/master')
    ref3 = testrepo.references.get('refs/heads/i18n')

    assert ref1 is not ref2
    assert ref1 == ref2
    assert not ref1 != ref2

    assert ref1 != ref3
    assert not ref1 == ref3


def test_refs_compress(testrepo):
    packed_refs_file = Path(testrepo.path) / 'packed-refs'
    assert not packed_refs_file.exists()
    old_refs = [(ref.name, ref.target) for ref in testrepo.references.objects]

    testrepo.references.compress()
    assert packed_refs_file.exists()
    new_refs = [(x.name, x.target) for x in testrepo.references.objects]
    assert old_refs == new_refs


#
# Low level API written in C, repo.references call these.
#


def test_list_all_reference_objects(testrepo):
    repo = testrepo
    refs = [(ref.name, ref.target) for ref in repo.listall_reference_objects()]

    assert sorted(refs) == [
        ('refs/heads/i18n', '5470a671a80ac3789f1a6a8cefbcf43ce7af0563'),
        ('refs/heads/master', '2be5719152d4f82c7302b1c0932d8e5f0a4a0e98'),
    ]


def test_list_all_references(testrepo):
    repo = testrepo

    # Without argument
    assert sorted(repo.listall_references()) == ['refs/heads/i18n', 'refs/heads/master']
    assert sorted(repo.raw_listall_references()) == [
        b'refs/heads/i18n',
        b'refs/heads/master',
    ]

    # We add a symbolic reference
    repo.create_reference('refs/tags/version1', 'refs/heads/master')
    assert sorted(repo.listall_references()) == [
        'refs/heads/i18n',
        'refs/heads/master',
        'refs/tags/version1',
    ]
    assert sorted(repo.raw_listall_references()) == [
        b'refs/heads/i18n',
        b'refs/heads/master',
        b'refs/tags/version1',
    ]


def test_references_iterator_init(testrepo):
    repo = testrepo
    iter = repo.references_iterator_init()

    assert iter.__class__.__name__ == 'RefsIterator'


def test_references_iterator_next(testrepo):
    repo = testrepo
    repo.create_reference(
        'refs/tags/version1', '2be5719152d4f82c7302b1c0932d8e5f0a4a0e98'
    )
    repo.create_reference(
        'refs/tags/version2', '2be5719152d4f82c7302b1c0932d8e5f0a4a0e98'
    )

    iter_all = repo.references_iterator_init()
    all_refs = []
    for _ in range(4):
        curr_ref = repo.references_iterator_next(iter_all)
        if curr_ref:
            all_refs.append((curr_ref.name, curr_ref.target))

    assert sorted(all_refs) == [
        ('refs/heads/i18n', '5470a671a80ac3789f1a6a8cefbcf43ce7af0563'),
        ('refs/heads/master', '2be5719152d4f82c7302b1c0932d8e5f0a4a0e98'),
        ('refs/tags/version1', '2be5719152d4f82c7302b1c0932d8e5f0a4a0e98'),
        ('refs/tags/version2', '2be5719152d4f82c7302b1c0932d8e5f0a4a0e98'),
    ]

    iter_branches = repo.references_iterator_init()
    all_branches = []
    for _ in range(4):
        curr_ref = repo.references_iterator_next(iter_branches, 1)
        if curr_ref:
            all_branches.append((curr_ref.name, curr_ref.target))

    assert sorted(all_branches) == [
        ('refs/heads/i18n', '5470a671a80ac3789f1a6a8cefbcf43ce7af0563'),
        ('refs/heads/master', '2be5719152d4f82c7302b1c0932d8e5f0a4a0e98'),
    ]

    iter_tags = repo.references_iterator_init()
    all_tags = []
    for _ in range(4):
        curr_ref = repo.references_iterator_next(iter_tags, 2)
        if curr_ref:
            all_tags.append((curr_ref.name, curr_ref.target))

    assert sorted(all_tags) == [
        ('refs/tags/version1', '2be5719152d4f82c7302b1c0932d8e5f0a4a0e98'),
        ('refs/tags/version2', '2be5719152d4f82c7302b1c0932d8e5f0a4a0e98'),
    ]


def test_references_iterator_next_python(testrepo):
    repo = testrepo
    repo.create_reference(
        'refs/tags/version1', '2be5719152d4f82c7302b1c0932d8e5f0a4a0e98'
    )
    repo.create_reference(
        'refs/tags/version2', '2be5719152d4f82c7302b1c0932d8e5f0a4a0e98'
    )

    refs = [(x.name, x.target) for x in repo.references.iterator()]
    assert sorted(refs) == [
        ('refs/heads/i18n', '5470a671a80ac3789f1a6a8cefbcf43ce7af0563'),
        ('refs/heads/master', '2be5719152d4f82c7302b1c0932d8e5f0a4a0e98'),
        ('refs/tags/version1', '2be5719152d4f82c7302b1c0932d8e5f0a4a0e98'),
        ('refs/tags/version2', '2be5719152d4f82c7302b1c0932d8e5f0a4a0e98'),
    ]

    branches = [(x.name, x.target) for x in repo.references.iterator(1)]
    assert sorted(branches) == [
        ('refs/heads/i18n', '5470a671a80ac3789f1a6a8cefbcf43ce7af0563'),
        ('refs/heads/master', '2be5719152d4f82c7302b1c0932d8e5f0a4a0e98'),
    ]

    tags = [(x.name, x.target) for x in repo.references.iterator(2)]
    assert sorted(tags) == [
        ('refs/tags/version1', '2be5719152d4f82c7302b1c0932d8e5f0a4a0e98'),
        ('refs/tags/version2', '2be5719152d4f82c7302b1c0932d8e5f0a4a0e98'),
    ]


def test_references_iterator_invalid_filter(testrepo):
    repo = testrepo
    iter_all = repo.references_iterator_init()

    all_refs = []
    for _ in range(4):
        curr_ref = repo.references_iterator_next(iter_all, 5)
        if curr_ref:
            all_refs.append((curr_ref.name, curr_ref.target))

    assert all_refs == []


def test_references_iterator_invalid_filter_python(testrepo):
    repo = testrepo
    refs = []
    with pytest.raises(ValueError):
        for ref in repo.references.iterator(5):
            refs.append((ref.name, ref.target))


def test_lookup_reference(testrepo):
    repo = testrepo

    # Raise KeyError ?
    with pytest.raises(KeyError):
        repo.lookup_reference('refs/foo')

    # Test a lookup
    reference = repo.lookup_reference('refs/heads/master')
    assert reference.name == 'refs/heads/master'


def test_lookup_reference_dwim(testrepo):
    repo = testrepo

    # remote ref
    reference = testrepo.create_reference('refs/remotes/origin/master', LAST_COMMIT)
    assert reference.shorthand == 'origin/master'
    # tag
    repo.create_reference('refs/tags/version1', LAST_COMMIT)

    # Test dwim lookups

    # Raise KeyError ?
    with pytest.raises(KeyError):
        repo.lookup_reference_dwim('foo')
    with pytest.raises(KeyError):
        repo.lookup_reference_dwim('refs/foo')

    reference = repo.lookup_reference_dwim('refs/heads/master')
    assert reference.name == 'refs/heads/master'

    reference = repo.lookup_reference_dwim('master')
    assert reference.name == 'refs/heads/master'

    reference = repo.lookup_reference_dwim('origin/master')
    assert reference.name == 'refs/remotes/origin/master'

    reference = repo.lookup_reference_dwim('version1')
    assert reference.name == 'refs/tags/version1'


def test_resolve_refish(testrepo):
    repo = testrepo

    # remote ref
    reference = testrepo.create_reference('refs/remotes/origin/master', LAST_COMMIT)
    assert reference.shorthand == 'origin/master'
    # tag
    repo.create_reference('refs/tags/version1', LAST_COMMIT)

    # Test dwim lookups

    # Raise KeyError ?
    with pytest.raises(KeyError):
        repo.resolve_refish('foo')
    with pytest.raises(KeyError):
        repo.resolve_refish('refs/foo')

    commit, ref = repo.resolve_refish('refs/heads/i18n')
    assert ref.name == 'refs/heads/i18n'
    assert commit.id == '5470a671a80ac3789f1a6a8cefbcf43ce7af0563'

    commit, ref = repo.resolve_refish('master')
    assert ref.name == 'refs/heads/master'
    assert commit.id == LAST_COMMIT

    commit, ref = repo.resolve_refish('origin/master')
    assert ref.name == 'refs/remotes/origin/master'
    assert commit.id == LAST_COMMIT

    commit, ref = repo.resolve_refish('version1')
    assert ref.name == 'refs/tags/version1'
    assert commit.id == LAST_COMMIT

    commit, ref = repo.resolve_refish(LAST_COMMIT)
    assert ref is None
    assert commit.id == LAST_COMMIT

    commit, ref = repo.resolve_refish('HEAD~1')
    assert ref is None
    assert commit.id == '5ebeeebb320790caf276b9fc8b24546d63316533'


def test_reference_get_sha(testrepo):
    reference = testrepo.lookup_reference('refs/heads/master')
    assert reference.target == LAST_COMMIT


def test_reference_set_sha(testrepo):
    NEW_COMMIT = '5ebeeebb320790caf276b9fc8b24546d63316533'
    reference = testrepo.lookup_reference('refs/heads/master')
    reference.set_target(NEW_COMMIT)
    assert reference.target == NEW_COMMIT


def test_reference_set_sha_prefix(testrepo):
    NEW_COMMIT = '5ebeeebb320790caf276b9fc8b24546d63316533'
    reference = testrepo.lookup_reference('refs/heads/master')
    reference.set_target(NEW_COMMIT[0:6])
    assert reference.target == NEW_COMMIT


def test_reference_get_type(testrepo):
    reference = testrepo.lookup_reference('refs/heads/master')
    assert reference.type == ReferenceType.DIRECT


def test_get_target(testrepo):
    reference = testrepo.lookup_reference('HEAD')
    assert reference.target == 'refs/heads/master'
    assert reference.raw_target == b'refs/heads/master'


def test_set_target(testrepo):
    reference = testrepo.lookup_reference('HEAD')
    assert reference.target == 'refs/heads/master'
    assert reference.raw_target == b'refs/heads/master'
    reference.set_target('refs/heads/i18n')
    assert reference.target == 'refs/heads/i18n'
    assert reference.raw_target == b'refs/heads/i18n'


def test_get_shorthand(testrepo):
    reference = testrepo.lookup_reference('refs/heads/master')
    assert reference.shorthand == 'master'
    reference = testrepo.create_reference('refs/remotes/origin/master', LAST_COMMIT)
    assert reference.shorthand == 'origin/master'


def test_set_target_with_message(testrepo):
    reference = testrepo.lookup_reference('HEAD')
    assert reference.target == 'refs/heads/master'
    assert reference.raw_target == b'refs/heads/master'
    sig = Signature('foo', 'bar')
    testrepo.set_ident('foo', 'bar')
    msg = 'Hello log'
    reference.set_target('refs/heads/i18n', message=msg)
    assert reference.target == 'refs/heads/i18n'
    assert reference.raw_target == b'refs/heads/i18n'
    first = list(reference.log())[0]
    assert first.message == msg
    assert first.committer == sig


def test_delete(testrepo):
    repo = testrepo

    # We add a tag as a new reference that points to "origin/master"
    reference = repo.create_reference('refs/tags/version1', LAST_COMMIT)
    assert 'refs/tags/version1' in repo.listall_references()
    assert b'refs/tags/version1' in repo.raw_listall_references()

    # And we delete it
    reference.delete()
    assert 'refs/tags/version1' not in repo.listall_references()
    assert b'refs/tags/version1' not in repo.raw_listall_references()

    # Access the deleted reference
    with pytest.raises(GitError):
        getattr(reference, 'name')
    with pytest.raises(GitError):
        getattr(reference, 'type')
    with pytest.raises(GitError):
        getattr(reference, 'target')
    with pytest.raises(GitError):
        reference.delete()
    with pytest.raises(GitError):
        reference.resolve()
    with pytest.raises(GitError):
        reference.rename('refs/tags/version2')


def test_rename(testrepo):
    # We add a tag as a new reference that points to "origin/master"
    reference = testrepo.create_reference('refs/tags/version1', LAST_COMMIT)
    assert reference.name == 'refs/tags/version1'
    reference.rename('refs/tags/version2')
    assert reference.name == 'refs/tags/version2'


#   def test_reload(testrepo):
#       name = 'refs/tags/version1'

#       repo = testrepo
#       ref = repo.create_reference(name, "refs/heads/master", symbolic=True)
#       ref2 = repo.lookup_reference(name)
#       ref.delete()
#       assert ref2.name == name
#       with pytest.raises(KeyError): ref2.reload()
#       with pytest.raises(GitError): getattr(ref2, 'name')


def test_reference_resolve(testrepo):
    reference = testrepo.lookup_reference('HEAD')
    assert reference.type == ReferenceType.SYMBOLIC
    reference = reference.resolve()
    assert reference.type == ReferenceType.DIRECT
    assert reference.target == LAST_COMMIT


def test_reference_resolve_identity(testrepo):
    head = testrepo.lookup_reference('HEAD')
    ref = head.resolve()
    assert ref.resolve() is ref


def test_create_reference(testrepo):
    # We add a tag as a new reference that points to "origin/master"
    reference = testrepo.create_reference('refs/tags/version1', LAST_COMMIT)
    assert 'refs/tags/version1' in testrepo.listall_references()
    assert b'refs/tags/version1' in testrepo.raw_listall_references()
    reference = testrepo.lookup_reference('refs/tags/version1')
    assert reference.target == LAST_COMMIT

    # try to create existing reference
    with pytest.raises(AlreadyExistsError) as error:
        testrepo.create_reference('refs/tags/version1', LAST_COMMIT)
    assert isinstance(error.value, ValueError)

    # Clear error
    del error

    # try to create existing reference with force
    reference = testrepo.create_reference('refs/tags/version1', LAST_COMMIT, force=True)
    assert reference.target == LAST_COMMIT


def test_create_reference_with_message(testrepo):
    sig = Signature('foo', 'bar')
    testrepo.set_ident('foo', 'bar')
    msg = 'Hello log'
    reference = testrepo.create_reference(
        'refs/heads/feature', LAST_COMMIT, message=msg
    )
    first = list(reference.log())[0]
    assert first.message == msg
    assert first.committer == sig


def test_create_symbolic_reference(testrepo):
    repo = testrepo
    # We add a tag as a new symbolic reference that always points to
    # "refs/heads/master"
    reference = repo.create_reference('refs/tags/beta', 'refs/heads/master')
    assert reference.type == ReferenceType.SYMBOLIC
    assert reference.target == 'refs/heads/master'
    assert reference.raw_target == b'refs/heads/master'

    # try to create existing symbolic reference
    with pytest.raises(AlreadyExistsError) as error:
        repo.create_reference('refs/tags/beta', 'refs/heads/master')
    assert isinstance(error.value, ValueError)

    # try to create existing symbolic reference with force
    reference = repo.create_reference('refs/tags/beta', 'refs/heads/master', force=True)
    assert reference.type == ReferenceType.SYMBOLIC
    assert reference.target == 'refs/heads/master'
    assert reference.raw_target == b'refs/heads/master'


def test_create_symbolic_reference_with_message(testrepo):
    sig = Signature('foo', 'bar')
    testrepo.set_ident('foo', 'bar')
    msg = 'Hello log'
    reference = testrepo.create_reference(
        'HEAD', 'refs/heads/i18n', force=True, message=msg
    )
    first = list(reference.log())[0]
    assert first.message == msg
    assert first.committer == sig


def test_create_invalid_reference(testrepo):
    repo = testrepo

    # try to create a reference with an invalid name
    with pytest.raises(InvalidSpecError) as error:
        repo.create_reference('refs/tags/in..valid', 'refs/heads/master')
    assert isinstance(error.value, ValueError)


#   def test_packall_references(testrepo):
#       testrepo.packall_references()


def test_peel(testrepo):
    repo = testrepo
    ref = repo.lookup_reference('refs/heads/master')
    assert repo[ref.target].id == ref.peel().id
    assert repo[ref.raw_target].id == ref.peel().id

    commit = ref.peel(Commit)
    assert commit.tree.id == ref.peel(Tree).id


def test_valid_reference_names_ascii():
    assert reference_is_valid_name('HEAD')
    assert reference_is_valid_name('refs/heads/master')
    assert reference_is_valid_name('refs/heads/perfectly/valid')
    assert reference_is_valid_name('refs/tags/v1')
    assert reference_is_valid_name('refs/special/ref')


def test_valid_reference_names_unicode():
    assert reference_is_valid_name('refs/heads/ünicöde')
    assert reference_is_valid_name('refs/tags/😀')


def test_invalid_reference_names():
    assert not reference_is_valid_name('')
    assert not reference_is_valid_name(' refs/heads/master')
    assert not reference_is_valid_name('refs/heads/in..valid')
    assert not reference_is_valid_name('refs/heads/invalid~')
    assert not reference_is_valid_name('refs/heads/invalid^')
    assert not reference_is_valid_name('refs/heads/invalid:')
    assert not reference_is_valid_name('refs/heads/invalid\\')
    assert not reference_is_valid_name('refs/heads/invalid?')
    assert not reference_is_valid_name('refs/heads/invalid[')
    assert not reference_is_valid_name('refs/heads/invalid*')
    assert not reference_is_valid_name('refs/heads/@{no}')
    assert not reference_is_valid_name('refs/heads/foo//bar')


def test_invalid_arguments():
    with pytest.raises(TypeError):
        reference_is_valid_name()
    with pytest.raises(TypeError):
        reference_is_valid_name(None)
    with pytest.raises(TypeError):
        reference_is_valid_name(1)
    with pytest.raises(TypeError):
        reference_is_valid_name('too', 'many')
