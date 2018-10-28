# -*- coding: UTF-8 -*-
#
# Copyright 2010-2017 The pygit2 contributors
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

from __future__ import absolute_import
from __future__ import unicode_literals

import pytest

from pygit2 import GIT_REF_OID, GIT_REF_SYMBOLIC, Signature
from pygit2 import Commit, Tree, reference_is_valid_name
from pygit2 import AlreadyExistsError, GitError, InvalidSpecError
from . import utils

LAST_COMMIT = '2be5719152d4f82c7302b1c0932d8e5f0a4a0e98'


class ReferencesObjectTest(utils.RepoTestCase):
    def test_list_all_reference_objects(self):
        repo = self.repo

        refs = [(ref.name, ref.target.hex)
                for ref in repo.references.objects]
        assert sorted(refs) == [
            ('refs/heads/i18n', '5470a671a80ac3789f1a6a8cefbcf43ce7af0563'),
            ('refs/heads/master', '2be5719152d4f82c7302b1c0932d8e5f0a4a0e98')]

    def test_list_all_references(self):
        repo = self.repo

        # Without argument
        assert sorted(repo.references) == ['refs/heads/i18n',
                                           'refs/heads/master']

        # We add a symbolic reference
        repo.create_reference('refs/tags/version1', 'refs/heads/master')
        assert sorted(repo.references) == ['refs/heads/i18n',
                                           'refs/heads/master',
                                           'refs/tags/version1']

    def test_head(self):
        head = self.repo.head
        assert LAST_COMMIT == self.repo[head.target].hex

    def test_lookup_reference(self):
        repo = self.repo

        refname = 'refs/foo'
        # Raise KeyError ?
        with pytest.raises(KeyError): self.repo.references[refname]

        # Return None ?
        assert self.repo.references.get(refname) is None

        # Test a lookup
        reference = repo.references.get('refs/heads/master')
        assert reference.name == 'refs/heads/master'

    def test_reference_get_sha(self):
        reference = self.repo.references['refs/heads/master']
        assert reference.target.hex == LAST_COMMIT

    def test_reference_set_sha(self):
        NEW_COMMIT = '5ebeeebb320790caf276b9fc8b24546d63316533'
        reference = self.repo.references.get('refs/heads/master')
        reference.set_target(NEW_COMMIT)
        assert reference.target.hex == NEW_COMMIT

    def test_reference_set_sha_prefix(self):
        NEW_COMMIT = '5ebeeebb320790caf276b9fc8b24546d63316533'
        reference = self.repo.references.get('refs/heads/master')
        reference.set_target(NEW_COMMIT[0:6])
        assert reference.target.hex == NEW_COMMIT

    def test_reference_get_type(self):
        reference = self.repo.references.get('refs/heads/master')
        assert reference.type == GIT_REF_OID

    def test_get_target(self):
        reference = self.repo.references.get('HEAD')
        assert reference.target == 'refs/heads/master'

    def test_set_target(self):
        reference = self.repo.references.get('HEAD')
        assert reference.target == 'refs/heads/master'
        reference.set_target('refs/heads/i18n')
        assert reference.target == 'refs/heads/i18n'

    def test_get_shorthand(self):
        reference = self.repo.references.get('refs/heads/master')
        assert reference.shorthand == 'master'
        reference = self.repo.references.create('refs/remotes/origin/master', LAST_COMMIT)
        assert reference.shorthand == 'origin/master'

    def test_set_target_with_message(self):
        reference = self.repo.references.get('HEAD')
        assert reference.target == 'refs/heads/master'
        sig = Signature('foo', 'bar')
        self.repo.set_ident('foo', 'bar')
        msg = 'Hello log'
        reference.set_target('refs/heads/i18n', message=msg)
        assert reference.target == 'refs/heads/i18n'
        first = list(reference.log())[0]
        assert first.message == msg
        assert first.committer == sig

    def test_delete(self):
        repo = self.repo

        # We add a tag as a new reference that points to "origin/master"
        reference = repo.references.create('refs/tags/version1', LAST_COMMIT)
        assert 'refs/tags/version1' in repo.references

        # And we delete it
        reference.delete()
        assert 'refs/tags/version1' not in repo.references

        # Access the deleted reference
        with pytest.raises(GitError): getattr(reference, 'name')
        with pytest.raises(GitError): getattr(reference, 'type')
        with pytest.raises(GitError): getattr(reference, 'target')
        with pytest.raises(GitError): reference.delete()
        with pytest.raises(GitError): reference.resolve()
        with pytest.raises(GitError): reference.rename("refs/tags/version2")

    def test_rename(self):
        # We add a tag as a new reference that points to "origin/master"
        reference = self.repo.references.create('refs/tags/version1',
                                                LAST_COMMIT)
        assert reference.name == 'refs/tags/version1'
        reference.rename('refs/tags/version2')
        assert reference.name == 'refs/tags/version2'

    #   def test_reload(self):
    #       name = 'refs/tags/version1'

    #       repo = self.repo
    #       ref = repo.create_reference(name, "refs/heads/master", symbolic=True)
    #       ref2 = repo.lookup_reference(name)
    #       ref.delete()
    #       assert ref2.name == name
    #       with pytest.raises(KeyError): ref2.reload()
    #       with pytest.raises(GitError): getattr(ref2, 'name')


    def test_reference_resolve(self):
        reference = self.repo.references.get('HEAD')
        assert reference.type == GIT_REF_SYMBOLIC
        reference = reference.resolve()
        assert reference.type == GIT_REF_OID
        assert reference.target.hex == LAST_COMMIT

    def test_reference_resolve_identity(self):
        head = self.repo.references.get('HEAD')
        ref = head.resolve()
        assert ref.resolve() is ref

    def test_create_reference(self):
        # We add a tag as a new reference that points to "origin/master"
        reference = self.repo.references.create('refs/tags/version1',
                                                LAST_COMMIT)
        refs = self.repo.references
        assert 'refs/tags/version1' in refs
        reference = self.repo.references.get('refs/tags/version1')
        assert reference.target.hex == LAST_COMMIT

        # try to create existing reference
        with pytest.raises(ValueError):
            self.repo.references.create('refs/tags/version1', LAST_COMMIT)

        # try to create existing reference with force
        reference = self.repo.references.create('refs/tags/version1',
                                                LAST_COMMIT, force=True)
        assert reference.target.hex == LAST_COMMIT

    def test_create_symbolic_reference(self):
        repo = self.repo
        # We add a tag as a new symbolic reference that always points to
        # "refs/heads/master"
        reference = repo.references.create('refs/tags/beta',
                                           'refs/heads/master')
        assert reference.type == GIT_REF_SYMBOLIC
        assert reference.target == 'refs/heads/master'

        # try to create existing symbolic reference
        with pytest.raises(ValueError):
            repo.references.create('refs/tags/beta', 'refs/heads/master')

        # try to create existing symbolic reference with force
        reference = repo.references.create('refs/tags/beta',
                                           'refs/heads/master', force=True)
        assert reference.type == GIT_REF_SYMBOLIC
        assert reference.target == 'refs/heads/master'

    #   def test_packall_references(self):
    #       self.repo.packall_references()


    def test_get_object(self):
        repo = self.repo
        ref = repo.references.get('refs/heads/master')
        assert repo[ref.target].id == ref.get_object().id

    def test_peel(self):
        ref = self.repo.references.get('refs/heads/master')
        commit = ref.peel(Commit)
        assert commit.tree.id == ref.peel(Tree).id


class ReferencesTest(utils.RepoTestCase):
    def test_list_all_reference_objects(self):
        repo = self.repo
        refs = [(ref.name, ref.target.hex)
                for ref in repo.listall_reference_objects()]

        assert sorted(refs) == [
            ('refs/heads/i18n', '5470a671a80ac3789f1a6a8cefbcf43ce7af0563'),
            ('refs/heads/master', '2be5719152d4f82c7302b1c0932d8e5f0a4a0e98')]

    def test_list_all_references(self):
        repo = self.repo

        # Without argument
        assert sorted(repo.listall_references()) == ['refs/heads/i18n', 'refs/heads/master']

        # We add a symbolic reference
        repo.create_reference('refs/tags/version1', 'refs/heads/master')
        assert sorted(repo.listall_references()) == ['refs/heads/i18n',
                                                     'refs/heads/master',
                                                     'refs/tags/version1']

    def test_head(self):
        head = self.repo.head
        assert LAST_COMMIT == self.repo[head.target].hex

    def test_lookup_reference(self):
        repo = self.repo

        # Raise KeyError ?
        with pytest.raises(KeyError): repo.lookup_reference('refs/foo')

        # Test a lookup
        reference = repo.lookup_reference('refs/heads/master')
        assert reference.name == 'refs/heads/master'

    def test_reference_get_sha(self):
        reference = self.repo.lookup_reference('refs/heads/master')
        assert reference.target.hex == LAST_COMMIT

    def test_reference_set_sha(self):
        NEW_COMMIT = '5ebeeebb320790caf276b9fc8b24546d63316533'
        reference = self.repo.lookup_reference('refs/heads/master')
        reference.set_target(NEW_COMMIT)
        assert reference.target.hex == NEW_COMMIT

    def test_reference_set_sha_prefix(self):
        NEW_COMMIT = '5ebeeebb320790caf276b9fc8b24546d63316533'
        reference = self.repo.lookup_reference('refs/heads/master')
        reference.set_target(NEW_COMMIT[0:6])
        assert reference.target.hex == NEW_COMMIT

    def test_reference_get_type(self):
        reference = self.repo.lookup_reference('refs/heads/master')
        assert reference.type == GIT_REF_OID

    def test_get_target(self):
        reference = self.repo.lookup_reference('HEAD')
        assert reference.target == 'refs/heads/master'

    def test_set_target(self):
        reference = self.repo.lookup_reference('HEAD')
        assert reference.target == 'refs/heads/master'
        reference.set_target('refs/heads/i18n')
        assert reference.target == 'refs/heads/i18n'

    def test_get_shorthand(self):
        reference = self.repo.lookup_reference('refs/heads/master')
        assert reference.shorthand == 'master'
        reference = self.repo.create_reference('refs/remotes/origin/master', LAST_COMMIT)
        assert reference.shorthand == 'origin/master'

    def test_set_target_with_message(self):
        reference = self.repo.lookup_reference('HEAD')
        assert reference.target == 'refs/heads/master'
        sig = Signature('foo', 'bar')
        self.repo.set_ident('foo', 'bar')
        msg = 'Hello log'
        reference.set_target('refs/heads/i18n', message=msg)
        assert reference.target == 'refs/heads/i18n'
        first = list(reference.log())[0]
        assert first.message == msg
        assert first.committer == sig

    def test_delete(self):
        repo = self.repo

        # We add a tag as a new reference that points to "origin/master"
        reference = repo.create_reference('refs/tags/version1', LAST_COMMIT)
        assert 'refs/tags/version1' in repo.listall_references()

        # And we delete it
        reference.delete()
        assert 'refs/tags/version1' not in repo.listall_references()

        # Access the deleted reference
        with pytest.raises(GitError): getattr(reference, 'name')
        with pytest.raises(GitError): getattr(reference, 'type')
        with pytest.raises(GitError): getattr(reference, 'target')
        with pytest.raises(GitError): reference.delete()
        with pytest.raises(GitError): reference.resolve()
        with pytest.raises(GitError): reference.rename("refs/tags/version2")

    def test_rename(self):
        # We add a tag as a new reference that points to "origin/master"
        reference = self.repo.create_reference('refs/tags/version1',
                                               LAST_COMMIT)
        assert reference.name == 'refs/tags/version1'
        reference.rename('refs/tags/version2')
        assert reference.name == 'refs/tags/version2'

    #   def test_reload(self):
    #       name = 'refs/tags/version1'

    #       repo = self.repo
    #       ref = repo.create_reference(name, "refs/heads/master", symbolic=True)
    #       ref2 = repo.lookup_reference(name)
    #       ref.delete()
    #       assert ref2.name == name
    #       with pytest.raises(KeyError): ref2.reload()
    #       with pytest.raises(GitError): getattr(ref2, 'name')


    def test_reference_resolve(self):
        reference = self.repo.lookup_reference('HEAD')
        assert reference.type == GIT_REF_SYMBOLIC
        reference = reference.resolve()
        assert reference.type == GIT_REF_OID
        assert reference.target.hex == LAST_COMMIT

    def test_reference_resolve_identity(self):
        head = self.repo.lookup_reference('HEAD')
        ref = head.resolve()
        assert ref.resolve() is ref

    def test_create_reference(self):
        # We add a tag as a new reference that points to "origin/master"
        reference = self.repo.create_reference('refs/tags/version1',
                                               LAST_COMMIT)
        refs = self.repo.listall_references()
        assert 'refs/tags/version1' in refs
        reference = self.repo.lookup_reference('refs/tags/version1')
        assert reference.target.hex == LAST_COMMIT

        # try to create existing reference
        with pytest.raises(AlreadyExistsError) as error:
            self.repo.create_reference('refs/tags/version1', LAST_COMMIT)
        assert isinstance(error.value, ValueError)
        
        # Clear error
        del error

        # try to create existing reference with force
        reference = self.repo.create_reference('refs/tags/version1',
                                               LAST_COMMIT, force=True)
        assert reference.target.hex == LAST_COMMIT

    def test_create_symbolic_reference(self):
        repo = self.repo
        # We add a tag as a new symbolic reference that always points to
        # "refs/heads/master"
        reference = repo.create_reference('refs/tags/beta',
                                          'refs/heads/master')
        assert reference.type == GIT_REF_SYMBOLIC
        assert reference.target == 'refs/heads/master'

        # try to create existing symbolic reference
        with pytest.raises(AlreadyExistsError) as error:
            repo.create_reference('refs/tags/beta', 'refs/heads/master')
        assert isinstance(error.value, ValueError)

        # try to create existing symbolic reference with force
        reference = repo.create_reference('refs/tags/beta',
                                          'refs/heads/master', force=True)
        assert reference.type == GIT_REF_SYMBOLIC
        assert reference.target == 'refs/heads/master'

    def test_create_invalid_reference(self):
        repo = self.repo

        # try to create a reference with an invalid name
        with pytest.raises(InvalidSpecError) as error:
            repo.create_reference('refs/tags/in..valid', 'refs/heads/master')
        assert isinstance(error.value, ValueError)

    #   def test_packall_references(self):
    #       self.repo.packall_references()


    def test_get_object(self):
        repo = self.repo
        ref = repo.lookup_reference('refs/heads/master')
        assert repo[ref.target].id == ref.get_object().id

    def test_peel(self):
        ref = self.repo.lookup_reference('refs/heads/master')
        commit = ref.peel(Commit)
        assert commit.tree.id == ref.peel(Tree).id


class ReferenceIsValidNameTest(utils.NoRepoTestCase):

    def test_valid_reference_names_ascii(self):
        assert reference_is_valid_name('HEAD')
        assert reference_is_valid_name('refs/heads/master')
        assert reference_is_valid_name('refs/heads/perfectly/valid')
        assert reference_is_valid_name('refs/tags/v1')
        assert reference_is_valid_name('refs/special/ref')

    def test_valid_reference_names_unicode(self):
        assert reference_is_valid_name('refs/heads/ünicöde')
        assert reference_is_valid_name('refs/tags/😀')

    def test_invalid_reference_names(self):
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

    def test_invalid_arguments(self):
        with pytest.raises(TypeError):
            reference_is_valid_name()
        with pytest.raises(TypeError):
            reference_is_valid_name(None)
        with pytest.raises(TypeError):
            reference_is_valid_name(1)
        with pytest.raises(TypeError):
            reference_is_valid_name('too', 'many')
