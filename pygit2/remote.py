# -*- coding: utf-8 -*-
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

# Import from the future
from __future__ import absolute_import

from _pygit2 import Oid

from .ffi import ffi, C, to_str, strarray_to_strings, strings_to_strarray
from .errors import check_error, GitError
from .refspec import Refspec

def maybe_string(ptr):
    if not ptr:
        return None

    return ffi.string(ptr).decode()


class TransferProgress(object):
    """Progress downloading and indexing data during a fetch"""

    def __init__(self, tp):
        self.total_objects = tp.total_objects
        self.indexed_objects = tp.indexed_objects
        self.received_objects = tp.received_objects
        self.local_objects = tp.local_objects
        self.total_deltas = tp.total_deltas
        self.indexed_deltas = tp.indexed_deltas
        self.received_bytes = tp.received_bytes

class Remote(object):
    def __init__(self, repo, ptr):
        """The constructor is for internal use only"""

        self._repo = repo
        self._remote = ptr
        self._stored_exception = None

        # Build the callback structure
        callbacks = ffi.new('git_remote_callbacks *')
        callbacks.version = 1
        callbacks.progress = self._progress_cb
        callbacks.transfer_progress = self._transfer_progress_cb
        callbacks.update_tips = self._update_tips_cb
        callbacks.credentials = self._credentials_cb
        # We need to make sure that this handle stays alive
        self._self_handle = ffi.new_handle(self)
        callbacks.payload = self._self_handle

        err = C.git_remote_set_callbacks(self._remote, callbacks)
        check_error(err)

    def __del__(self):
        C.git_remote_free(self._remote)

    @property
    def name(self):
        return maybe_string(C.git_remote_name(self._remote))

    @name.setter
    def name(self, value):
        err = C.git_remote_rename(self._remote, to_str(value), ffi.NULL, ffi.NULL)
        check_error(err)

    @property
    def url(self):
        return maybe_string(C.git_remote_url(self._remote))

    @url.setter
    def url(self, value):
        err = C.git_remote_set_url(self._remote, to_str(value))

    @property
    def push_url(self):
        return maybe_string(C.git_remote_pushurl(self._remote))

    @push_url.setter
    def push_url(self, value):
        err = C.git_remote_set_pushurl(self._remote, to_str(value))
        check_error(err)

    def save(self):
        err = C.git_remote_save(self._remote)
        check_error(err)

    def fetch(self):
        self._stored_exception = None
        err = C.git_remote_fetch(self._remote)
        if self._stored_exception:
            raise self._stored_exception

        check_error(err)

        return TransferProgress(C.git_remote_stats(self._remote))

    @property
    def refspec_count(self):
        return C.git_remote_refspec_count(self._remote)

    def get_refspec(self, n):
        spec = C.git_remote_get_refspec(self._remote, n)
        return Refspec(self, spec)

    @property
    def fetch_refspecs(self):
        specs = ffi.new('git_strarray *')
        err = C.git_remote_get_fetch_refspecs(specs, self._remote)
        check_error(err)

        return strarray_to_strings(specs)

    @fetch_refspecs.setter
    def fetch_refspecs(self, l):
        arr, refs = strings_to_strarray(l)
        err = C.git_remote_set_fetch_refspecs(self._remote, arr)
        check_error(err)

    @property
    def push_refspecs(self):
        specs = ffi.new('git_strarray *')
        err = C.git_remote_get_push_refspecs(specs, self._remote)
        check_error(err)

        return strarray_to_strings(specs)

    @push_refspecs.setter
    def push_refspecs(self, l):
        arr, refs = strings_to_strarray(l)
        err = C.git_remote_set_push_refspecs(self._remote, arr)
        check_error(err)

    def add_fetch(self, spec):
        err = C.git_remote_add_fetch(self._remote, to_str(spec))

    def add_push(self, spec):
        err = C.git_remote_add_push(self._remote, to_str(spec))

    @ffi.callback("int (*cb)(const char *ref, const char *msg, void *data)")
    def _push_cb(ref, msg, data):
        self = ffi.from_handle(data)
        if msg:
            self._bad_message = ffi.string(msg).decode()
        return 0

    def push(self, spec):
        cpush = ffi.new('git_push **')
        err = C.git_push_new(cpush, self._remote)
        check_error(err)

        push = cpush[0]

        try:
            err = C.git_push_add_refspec(push, to_str(spec))
            check_error(err)

            err = C.git_push_finish(push)
            check_error(err)

            if not C.git_push_unpack_ok(push):
                raise GitError("remote failed to unpack objects")

            err = C.git_push_status_foreach(push, self._push_cb, ffi.new_handle(self))
            check_error(err)

            if hasattr(self, '_bad_message'):
                raise GitError(self._bad_message)

            err = C.git_push_update_tips(push)
            check_error(err)

        finally:
            C.git_push_free(push)

    # These functions exist to be called by the git_remote as
    # callbacks. They proxy the call to whatever the user set

    @ffi.callback('int (*transfer_progress)(const git_transfer_progress *stats, void *data)')
    def _transfer_progress_cb(stats_ptr, data):
        self = ffi.from_handle(data)
        if not hasattr(self, 'transfer_progress'):
            return 0

        try:
            self.transfer_progress(TransferProgress(stats_ptr))
        except Exception, e:
            self._stored_exception = e
            return C.GIT_EUSER

        return 0

    @ffi.callback('int (*progress)(const char *str, int len, void *data)')
    def _progress_cb(string, length, data):
        self = ffi.from_handle(data)

        if not hasattr(self, 'progress'):
            return 0

        try:
            s = ffi.string(string, length).decode()
            self.progress(s)
        except Exception, e:
            self._stored_exception = e
            return C.GIT_EUSER

        return 0

    @ffi.callback('int (*update_tips)(const char *refname, const git_oid *a, const git_oid *b, void *data)')
    def _update_tips_cb(refname, a, b, data):
        self = ffi.from_handle(data)

        if not hasattr(self, 'update_tips'):
            return 0

        try:
            s = maybe_string(refname)
            a = Oid(raw=bytes(ffi.buffer(a)))
            b = Oid(raw=bytes(ffi.buffer(b)))

            self.update_tips(s, a, b)
        except Exception, e:
            self._stored_exception = e
            return C.GIT_EUSER

        return 0

    @ffi.callback('int (*credentials)(git_cred **cred, const char *url, const char *username_from_url, unsigned int allowed_types,	void *data)')
    def _credentials_cb(cred_out, url, username, allowed, data):
        self = ffi.from_handle(data)

        if not hasattr(self, 'credentials'):
            return 0

        try:
            url_str = maybe_string(url)
            username_str = maybe_string(username)

            creds = self.credentials(url_str, username_str, allowed)

            if not hasattr(creds, 'credential_type') or not hasattr(creds, 'credential_tuple'):
                raise TypeError("credential does not implement interface")

            cred_type = creds.credential_type

            if not (allowed & cred_type):
                raise TypeError("invalid credential type")

            ccred = ffi.new('git_cred **')
            if cred_type == C.GIT_CREDTYPE_USERPASS_PLAINTEXT:
                name, passwd = creds.credential_tuple
                err = C.git_cred_userpass_plaintext_new(ccred, to_str(name), to_str(passwd))

            elif cred_type == C.GIT_CREDTYPE_SSH_KEY:
                name, pubkey, privkey, passphrase = creds.credential_tuple
                err = C.git_cred_ssh_key_new(ccred, to_str(name),to_str(pubkey),
                                             to_str(privkey), to_str(passphrase))

            else:
                raise TypeError("unsupported credential type")

            check_error(err)
            cred_out[0] = ccred[0]

        except Exception, e:
            self._stored_exception = e
            return C.GIT_EUSER

        return 0
