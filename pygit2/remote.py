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

# Import from pygit2
from _pygit2 import Oid
from .errors import check_error, GitError
from .ffi import ffi, C
from .credentials import KeypairFromAgent
from .refspec import Refspec
from .utils import to_bytes, strarray_to_strings, StrArray


def maybe_string(ptr):
    if not ptr:
        return None

    return ffi.string(ptr).decode()


class TransferProgress(object):
    """Progress downloading and indexing data during a fetch"""

    def __init__(self, tp):

        self.total_objects = tp.total_objects
        """Total number of objects to download"""

        self.indexed_objects = tp.indexed_objects
        """Objects which have been indexed"""

        self.received_objects = tp.received_objects
        """Objects which have been received up to now"""

        self.local_objects = tp.local_objects
        """Local objects which were used to fix the thin pack"""

        self.total_deltas = tp.total_deltas
        """Total number of deltas in the pack"""

        self.indexed_deltas = tp.indexed_deltas
        """Deltas which have been indexed"""

        self.received_bytes = tp.received_bytes
        """"Number of bytes received up to now"""


class Remote(object):

    def sideband_progress(self, string):
        """Progress output callback

        Override this function with your own progress reporting function

        :param str string: Progress output from the remote
        """
        pass

    def credentials(self, url, username_from_url, allowed_types):
        """Credentials callback

        If the remote server requires authentication, this function will
        be called and its return value used for authentication. Override
        it if you want to be able to perform authentication.

        Parameters:

        - url (str) -- The url of the remote.

        - username_from_url (str or None) -- Username extracted from the url,
          if any.

        - allowed_types (int) -- Credential types supported by the remote.

        Return value: credential
        """
        pass

    def transfer_progress(self, stats):
        """Transfer progress callback

        Override with your own function to report transfer progress.

        :param TransferProgress stats: The progress up to now
        """
        pass

    def update_tips(self, refname, old, new):
        """Update tips callabck

        Override with your own function to report reference updates

        :param str refname: the name of the reference that's being updated
        :param Oid old: the reference's old value
        :param Oid new: the reference's new value
        """

    def push_update_reference(self, refname, message):
        """Push update reference callback

        Override with your own function to report the remote's
        acceptace or rejection of reference updates.

        :param str refname: the name of the reference (on the remote)
        :param str messsage: rejection message from the remote. If None, the update was accepted.
        """

    def __init__(self, repo, ptr):
        """The constructor is for internal use only"""

        self._repo = repo
        self._remote = ptr
        self._stored_exception = None

    def __del__(self):
        C.git_remote_free(self._remote)

    @property
    def name(self):
        """Name of the remote"""

        return maybe_string(C.git_remote_name(self._remote))

    @property
    def url(self):
        """Url of the remote"""

        return maybe_string(C.git_remote_url(self._remote))

    @property
    def push_url(self):
        """Push url of the remote"""

        return maybe_string(C.git_remote_pushurl(self._remote))

    def save(self):
        """Save a remote to its repository's configuration."""

        err = C.git_remote_save(self._remote)
        check_error(err)

    def fetch(self, refspecs=None, message=None):
        """Perform a fetch against this remote. Returns a <TransferProgress>
        object.
        """

        fetch_opts = ffi.new('git_fetch_options *')
        err = C.git_fetch_init_options(fetch_opts, C.GIT_FETCH_OPTIONS_VERSION)

        fetch_opts.callbacks.sideband_progress = self._sideband_progress_cb
        fetch_opts.callbacks.transfer_progress = self._transfer_progress_cb
        fetch_opts.callbacks.update_tips = self._update_tips_cb
        fetch_opts.callbacks.credentials = self._credentials_cb
        # We need to make sure that this handle stays alive
        self._self_handle = ffi.new_handle(self)
        fetch_opts.callbacks.payload = self._self_handle

        self._stored_exception = None

        try:
            with StrArray(refspecs) as arr:
                err = C.git_remote_fetch(self._remote, arr, fetch_opts, to_bytes(message))
                if self._stored_exception:
                    raise self._stored_exception
                check_error(err)
        finally:
            self._self_handle = None

        return TransferProgress(C.git_remote_stats(self._remote))

    @property
    def refspec_count(self):
        """Total number of refspecs in this remote"""

        return C.git_remote_refspec_count(self._remote)

    def get_refspec(self, n):
        """Return the <Refspec> object at the given position."""
        spec = C.git_remote_get_refspec(self._remote, n)
        return Refspec(self, spec)

    @property
    def fetch_refspecs(self):
        """Refspecs that will be used for fetching"""

        specs = ffi.new('git_strarray *')
        err = C.git_remote_get_fetch_refspecs(specs, self._remote)
        check_error(err)

        return strarray_to_strings(specs)

    @property
    def push_refspecs(self):
        """Refspecs that will be used for pushing"""

        specs = ffi.new('git_strarray *')
        err = C.git_remote_get_push_refspecs(specs, self._remote)
        check_error(err)

        return strarray_to_strings(specs)

    def push(self, specs):
        """Push the given refspec to the remote. Raises ``GitError`` on
        protocol error or unpack failure.

        :param [str] specs: push refspecs to use
        """
        push_opts = ffi.new('git_push_options *')
        err = C.git_push_init_options(push_opts, C.GIT_PUSH_OPTIONS_VERSION)

        # Build custom callback structure
        push_opts.callbacks.sideband_progress = self._sideband_progress_cb
        push_opts.callbacks.transfer_progress = self._transfer_progress_cb
        push_opts.callbacks.update_tips = self._update_tips_cb
        push_opts.callbacks.credentials = self._credentials_cb
        push_opts.callbacks.push_update_reference = self._push_update_reference_cb
        # We need to make sure that this handle stays alive
        self._self_handle = ffi.new_handle(self)
        push_opts.callbacks.payload = self._self_handle

        try:
            with StrArray(specs) as refspecs:
                err = C.git_remote_push(self._remote, refspecs, push_opts)
                check_error(err)
        finally:
            self._self_handle = None

    # These functions exist to be called by the git_remote as
    # callbacks. They proxy the call to whatever the user set

    @ffi.callback('git_transfer_progress_cb')
    def _transfer_progress_cb(stats_ptr, data):
        self = ffi.from_handle(data)

        if not hasattr(self, 'transfer_progress') \
           or not self.transfer_progress:
            return 0

        try:
            self.transfer_progress(TransferProgress(stats_ptr))
        except Exception as e:
            self._stored_exception = e
            return C.GIT_EUSER

        return 0

    @ffi.callback('git_transport_message_cb')
    def _sideband_progress_cb(string, length, data):
        self = ffi.from_handle(data)

        if not hasattr(self, 'progress') or not self.progress:
            return 0

        try:
            s = ffi.string(string, length).decode()
            self.progress(s)
        except Exception as e:
            self._stored_exception = e
            return C.GIT_EUSER

        return 0

    @ffi.callback('int (*update_tips)(const char *refname, const git_oid *a,'
                  'const git_oid *b, void *data)')
    def _update_tips_cb(refname, a, b, data):
        self = ffi.from_handle(data)

        if not hasattr(self, 'update_tips') or not self.update_tips:
            return 0

        try:
            s = maybe_string(refname)
            a = Oid(raw=bytes(ffi.buffer(a)[:]))
            b = Oid(raw=bytes(ffi.buffer(b)[:]))

            self.update_tips(s, a, b)
        except Exception as e:
            self._stored_exception = e
            return C.GIT_EUSER

        return 0

    @ffi.callback("int (*push_update_reference)(const char *ref, const char *msg, void *data)")
    def _push_update_reference_cb(ref, msg, data):
        self = ffi.from_handle(data)

        if not hasattr(self, 'push_update_reference') or not self.push_update_reference:
            return 0

        try:
            refname = ffi.string(ref)
            message = maybe_string(msg)
            self.push_update_reference(refname, message)
        except Exception as e:
            self._stored_exception = e
            return C.GIT_EUSER

        return 0

    @ffi.callback('int (*credentials)(git_cred **cred, const char *url,'
                  'const char *username_from_url, unsigned int allowed_types,'
                  'void *data)')
    def _credentials_cb(cred_out, url, username, allowed, data):
        self = ffi.from_handle(data)

        if not hasattr(self, 'credentials') or not self.credentials:
            return 0

        try:
            ccred = get_credentials(self.credentials, url, username, allowed)
            cred_out[0] = ccred[0]

        except Exception as e:
            self._stored_exception = e
            return C.GIT_EUSER

        return 0


def get_credentials(fn, url, username, allowed):
    """Call fn and return the credentials object"""

    url_str = maybe_string(url)
    username_str = maybe_string(username)

    creds = fn(url_str, username_str, allowed)

    if not hasattr(creds, 'credential_type') \
       or not hasattr(creds, 'credential_tuple'):
        raise TypeError("credential does not implement interface")

    cred_type = creds.credential_type

    if not (allowed & cred_type):
        raise TypeError("invalid credential type")

    ccred = ffi.new('git_cred **')
    if cred_type == C.GIT_CREDTYPE_USERPASS_PLAINTEXT:
        name, passwd = creds.credential_tuple
        err = C.git_cred_userpass_plaintext_new(ccred, to_bytes(name),
                                                to_bytes(passwd))

    elif cred_type == C.GIT_CREDTYPE_SSH_KEY:
        name, pubkey, privkey, passphrase = creds.credential_tuple
        if pubkey is None and privkey is None:
            err = C.git_cred_ssh_key_from_agent(ccred, to_bytes(name))
        else:
            err = C.git_cred_ssh_key_new(ccred, to_bytes(name),
                                         to_bytes(pubkey), to_bytes(privkey),
                                         to_bytes(passphrase))
    else:
        raise TypeError("unsupported credential type")

    check_error(err)

    return ccred

class RemoteCollection(object):
    """Collection of configured remotes

    You can use this class to look up and manage the remotes configured
    in a repository.  You can access repositories using index
    access. E.g. to look up the "origin" remote, you can use

    >>> repo.remotes["origin"]
    """

    def __init__(self, repo):
        self._repo = repo;

    def __len__(self):
        names = ffi.new('git_strarray *')

        try:
            err = C.git_remote_list(names, self._repo._repo)
            check_error(err)

            return names.count
        finally:
            C.git_strarray_free(names)

    def __iter__(self):
        names = ffi.new('git_strarray *')

        try:
            err = C.git_remote_list(names, self._repo._repo)
            check_error(err)

            cremote = ffi.new('git_remote **')
            for i in range(names.count):
                err = C.git_remote_lookup(cremote, self._repo._repo, names.strings[i])
                check_error(err)

                yield Remote(self._repo, cremote[0])
        finally:
            C.git_strarray_free(names)

    def __getitem__(self, name):
        if isinstance(name, int):
            return list(self)[name]

        cremote = ffi.new('git_remote **')
        err = C.git_remote_lookup(cremote, self._repo._repo, to_bytes(name))
        check_error(err)

        return Remote(self._repo, cremote[0])

    def create(self, name, url, fetch=None):
        """Create a new remote with the given name and url. Returns a <Remote>
        object.

        If 'fetch' is provided, this fetch refspec will be used instead of the default
        """

        cremote = ffi.new('git_remote **')

        if fetch:
            err = C.git_remote_create_with_fetchspec(cremote, self._repo._repo, to_bytes(name), to_bytes(url), to_bytes(fetch))
        else:
            err = C.git_remote_create(cremote, self._repo._repo, to_bytes(name), to_bytes(url))

        check_error(err)

        return Remote(self._repo, cremote[0])

    def rename(self, name, new_name):
        """Rename a remote in the configuration. The refspecs in standard
        format will be renamed.

        Returns a list of fetch refspecs (list of strings) which were not in
        the standard format and thus could not be remapped.
        """

        if not new_name:
            raise ValueError("Current remote name must be a non-empty string")

        if not new_name:
            raise ValueError("New remote name must be a non-empty string")

        problems = ffi.new('git_strarray *')
        err = C.git_remote_rename(problems, self._repo._repo, to_bytes(name), to_bytes(new_name))
        check_error(err)

        ret = strarray_to_strings(problems)
        C.git_strarray_free(problems)

        return ret

    def delete(self, name):
        """Remove a remote from the configuration

        All remote-tracking branches and configuration settings for the remote will be removed.
        """
        err = C.git_remote_delete(self._repo._repo, to_bytes(name))
        check_error(err)

    def set_url(self, name, url):
        """ Set the URL for a remote
        """
        err = C.git_remote_set_url(self._repo._repo, to_bytes(name), to_bytes(url))
        check_error(err)

    def set_push_url(self, name, url):
        """Set the push-URL for a remote
        """
        err = C.git_remote_set_pushurl(self._repo._repo, to_bytes(name), to_bytes(url))
        check_error(err)

    def add_fetch(self, name, refspec):
        """Add a fetch refspec (str) to the remote
        """

        err = C.git_remote_add_fetch(self._repo._repo, to_bytes(name), to_bytes(refspec))
        check_error(err)

    def add_push(self, name, refspec):
        """Add a push refspec (str) to the remote
        """

        err = C.git_remote_add_push(self._repo._repo, to_bytes(name), to_bytes(refspec))
        check_error(err)
