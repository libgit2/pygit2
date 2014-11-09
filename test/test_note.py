# -*- coding: UTF-8 -*-
#
# Copyright 2010-2014 The pygit2 contributors
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

"""Tests for note objects."""

from __future__ import absolute_import
from __future__ import unicode_literals
import unittest

from pygit2 import Signature
from . import utils

NOTE = ('6c8980ba963cad8b25a9bcaf68d4023ee57370d8', 'note message')

NOTES = [
    ('ab533997b80705767be3dae8cbb06a0740809f79', 'First Note - HEAD\n',
     '784855caf26449a1914d2cf62d12b9374d76ae78'),
    ('d879714d880671ed84f8aaed8b27fca23ba01f27', 'Second Note - HEAD~1\n',
     'f5e5aa4e36ab0fe62ee1ccc6eb8f79b866863b87')]


class NotesTest(utils.BareRepoTestCase):

    def test_create_note(self):
        annotated_id = self.repo.revparse_single('HEAD~3').hex
        author = committer = Signature('Foo bar', 'foo@bar.com', 12346, 0)
        note_id = self.repo.create_note(NOTE[1], author, committer,
                                        annotated_id)
        self.assertEqual(NOTE[0], note_id.hex)

        # check the note blob
        self.assertEqual(NOTE[1].encode(), self.repo[note_id].data)

    def test_lookup_note(self):
        annotated_id = self.repo.head.target.hex
        note = self.repo.lookup_note(annotated_id)
        self.assertEqual(NOTES[0][0], note.id.hex)
        self.assertEqual(NOTES[0][1], note.message)

    def test_remove_note(self):
        head = self.repo.head
        note = self.repo.lookup_note(head.target.hex)
        author = committer = Signature('Foo bar', 'foo@bar.com', 12346, 0)
        note.remove(author, committer)
        self.assertRaises(KeyError, self.repo.lookup_note, head.target.hex)

    def test_iterate_notes(self):
        for i, note in enumerate(self.repo.notes()):
            entry = (note.id.hex, note.message, note.annotated_id.hex)
            self.assertEqual(NOTES[i], entry)

    def test_iterate_non_existing_ref(self):
        self.assertRaises(KeyError, self.repo.notes, "refs/notes/bad_ref")


if __name__ == '__main__':
    unittest.main()
