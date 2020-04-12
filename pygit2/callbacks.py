# Copyright 2010-2020 The pygit2 contributors
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

"""
This is a utility module, it's here to support calls from libgit2 to written in
Python.
"""

# Standard Library
from contextlib import contextmanager
from functools import wraps

# pygit2
from ._pygit2 import Oid
from .errors import check_error, Passthrough
from .ffi import ffi, C
from .utils import maybe_string, to_bytes


#
# The context managers below wrap calls to libgit2 functions, which them in
# turn call to user defined functions written in Python.
#
# pygit2 api:
# -> wrapper (context manager)
#    -> libgit2 function
#       -> cffi function (proxy)
#          -> user defined function (Python callback)
#          <- returns or raises exception
#       <- returns error code or success to libgit2
#    <- returns error code or success
# <- returns object on success, or reraises exception from user defined
#    function, or raises exception from libgit2 error
#

class Payload:

    def __init__(self, **kw):
        for key, value in kw.items():
            setattr(self, key, value)
        self._stored_exception = None

    def check_error(self):
        if self._stored_exception is not None:
            raise self._stored_exception


@contextmanager
def git_clone_options(payload, opts=None):
    if opts is None:
        opts = ffi.new('git_clone_options *')
        C.git_clone_options_init(opts, C.GIT_CLONE_OPTIONS_VERSION)

    handle = ffi.new_handle(payload)

    # Plug callbacks
    if payload.repository:
        opts.repository_cb = C._repository_create_cb
        opts.repository_cb_payload = handle
    if payload.remote:
        opts.remote_cb = C._remote_create_cb
        opts.remote_cb_payload = handle

    # Give back control
    yield opts, payload


@contextmanager
def git_fetch_options(callbacks, opts=None):
    if callbacks is None:
        callbacks = RemoteCallbacks()

    if opts is None:
        opts = ffi.new('git_fetch_options *')
        C.git_fetch_init_options(opts, C.GIT_FETCH_OPTIONS_VERSION)

    # Plug callbacks
    opts.callbacks.sideband_progress = C._sideband_progress_cb
    opts.callbacks.transfer_progress = C._transfer_progress_cb
    opts.callbacks.update_tips = C._update_tips_cb
    opts.callbacks.credentials = C._credentials_cb
    opts.callbacks.certificate_check = C._certificate_cb
    # Payload
    callbacks._stored_exception = None
    handle = ffi.new_handle(callbacks)
    opts.callbacks.payload = handle

    # Give back control
    yield opts, callbacks


@contextmanager
def git_push_options(callbacks, opts=None):
    if callbacks is None:
        callbacks = RemoteCallbacks()

    if opts is None:
        opts = ffi.new('git_push_options *')
        C.git_push_init_options(opts, C.GIT_PUSH_OPTIONS_VERSION)

    # Plug callbacks
    opts.callbacks.sideband_progress = C._sideband_progress_cb
    opts.callbacks.transfer_progress = C._transfer_progress_cb
    opts.callbacks.update_tips = C._update_tips_cb
    opts.callbacks.credentials = C._credentials_cb
    opts.callbacks.certificate_check = C._certificate_cb
    opts.callbacks.push_update_reference = C._push_update_reference_cb
    # Payload
    callbacks._stored_exception = None
    handle = ffi.new_handle(callbacks)
    opts.callbacks.payload = handle

    # Give back control
    yield opts, callbacks


@contextmanager
def git_remote_callbacks(callbacks):
    if callbacks is None:
        callbacks = RemoteCallbacks()

    cdata = ffi.new('git_remote_callbacks *')
    C.git_remote_init_callbacks(cdata, C.GIT_REMOTE_CALLBACKS_VERSION)

    # Plug callbacks
    cdata.credentials = C._credentials_cb
    cdata.update_tips = C._update_tips_cb
    # Payload
    callbacks._stored_exception = None
    handle = ffi.new_handle(callbacks)
    cdata.payload = handle

    # Give back control
    yield cdata, callbacks



#
# C callbacks
#
# These functions are translated to C by cffi. They are called by libgit2, and
# proxy to the user defined callbacks written in Python, then back to libgit2.
#
# When an exception happens in the Python callback, they return GIT_EUSER and
# and keep the exception, to be re-raised later.
#

def callback_proxy(f):
    @wraps(f)
    def wrapper(*args):
        data = ffi.from_handle(args[-1])
        args = args[:-1] + (data,)
        try:
            return f(*args)
        except Passthrough:
            # A user defined callback can raise Passthrough to decline to act;
            # then libgit2 will behave as if there was no callback set in the
            # first place.
            return C.GIT_PASSTHROUGH
        except Exception as e:
            # Keep the exception to be re-raised later, and inform libgit2 that
            # the user defined callback has failed.
            data._stored_exception = e
            return C.GIT_EUSER

    return ffi.def_extern()(wrapper)


@callback_proxy
def _certificate_cb(cert_i, valid, host, data):
    # We want to simulate what should happen if libgit2 supported pass-through
    # for this callback. For SSH, 'valid' is always False, because it doesn't
    # look at known_hosts, but we do want to let it through in order to do what
    # libgit2 would if the callback were not set.
    try:
        is_ssh = cert_i.cert_type == C.GIT_CERT_HOSTKEY_LIBSSH2

        certificate_check = getattr(data, 'certificate_check', None)
        if not certificate_check:
            raise Passthrough

        # python's parsing is deep in the libraries and assumes an OpenSSL-owned cert
        val = certificate_check(None, bool(valid), ffi.string(host))
        if not val:
            return C.GIT_ECERTIFICATE
    except Passthrough:
        if is_ssh:
            return 0
        elif valid:
            return 0
        else:
            return C.GIT_ECERTIFICATE

    return 0


@callback_proxy
def _credentials_cb(cred_out, url, username, allowed, data):
    credentials = getattr(data, 'credentials', None)
    if not credentials:
        return 0

    ccred = get_credentials(credentials, url, username, allowed)
    cred_out[0] = ccred[0]
    return 0


@callback_proxy
def _push_update_reference_cb(ref, msg, data):
    push_update_reference = getattr(data, 'push_update_reference', None)
    if not push_update_reference:
        return 0

    refname = ffi.string(ref)
    message = maybe_string(msg)
    push_update_reference(refname, message)
    return 0


@callback_proxy
def _remote_create_cb(remote_out, repo, name, url, data):
    from .repository import Repository

    remote = data.remote(Repository._from_c(repo, False), ffi.string(name), ffi.string(url))
    remote_out[0] = remote._remote
    # we no longer own the C object
    remote._remote = ffi.NULL

    return 0


@callback_proxy
def _repository_create_cb(repo_out, path, bare, data):
    repository = data.repository(ffi.string(path), bare != 0)
    # we no longer own the C object
    repository._disown()
    repo_out[0] = repository._repo

    return 0


@callback_proxy
def _sideband_progress_cb(string, length, data):
    progress = getattr(data, 'progress', None)
    if not progress:
        return 0

    s = ffi.string(string, length).decode('utf-8')
    progress(s)
    return 0


@callback_proxy
def _transfer_progress_cb(stats_ptr, data):
    from .remote import TransferProgress

    transfer_progress = getattr(data, 'transfer_progress', None)
    if not transfer_progress:
        return 0

    transfer_progress(TransferProgress(stats_ptr))
    return 0


@callback_proxy
def _update_tips_cb(refname, a, b, data):
    update_tips = getattr(data, 'update_tips', None)
    if not update_tips:
        return 0

    s = maybe_string(refname)
    a = Oid(raw=bytes(ffi.buffer(a)[:]))
    b = Oid(raw=bytes(ffi.buffer(b)[:]))
    update_tips(s, a, b)
    return 0


#
# Public interface
# These functions are used within this module, but may also be used from the
# outside.
#

class RemoteCallbacks(object):
    """Base class for pygit2 remote callbacks.

    Inherit from this class and override the callbacks which you want to use
    in your class, which you can then pass to the network operations.
    """

    def __init__(self, credentials=None, certificate=None):
        """Initialize some callbacks in-line

        Use this constructor to provide credentials and certificate
        callbacks in-line, instead of defining your own class for these ones.

        You can e.g. also pass in one of the credential objects as 'credentials'
        instead of creating a function which returns a hard-coded object.
        """

        if credentials is not None:
            self.credentials = credentials
        if certificate is not None:
            self.certificate = certificate

    def sideband_progress(self, string):
        """
        Progress output callback.  Override this function with your own
        progress reporting function

        Parameters:

        string : str
            Progress output from the remote.
        """

    def credentials(self, url, username_from_url, allowed_types):
        """
        Credentials callback.  If the remote server requires authentication,
        this function will be called and its return value used for
        authentication. Override it if you want to be able to perform
        authentication.

        Returns: credential

        Parameters:

        url : str
            The url of the remote.

        username_from_url : str or None
            Username extracted from the url, if any.

        allowed_types : int
            Credential types supported by the remote.
        """
        raise Passthrough

    def certificate_check(self, certificate, valid, host):
        """
        Certificate callback. Override with your own function to determine
        whether to accept the server's certificate.

        Returns: True to connect, False to abort.

        Parameters:

        certificate : None
            The certificate. It is currently always None while we figure out
            how to represent it cross-platform.

        valid : bool
            Whether the TLS/SSH library thinks the certificate is valid.

        host : str
            The hostname we want to connect to.
        """

        raise Passthrough

    def transfer_progress(self, stats):
        """
        Transfer progress callback. Override with your own function to report
        transfer progress.

        Parameters:

        stats : TransferProgress
            The progress up to now.
        """

    def update_tips(self, refname, old, new):
        """
        Update tips callabck. Override with your own function to report
        reference updates.

        Parameters:

        refname : str
            The name of the reference that's being updated.

        old : Oid
            The reference's old value.

        new : Oid
            The reference's new value.
        """

    def push_update_reference(self, refname, message):
        """
        Push update reference callback. Override with your own function to
        report the remote's acceptance or rejection of reference updates.

        refname : str
            The name of the reference (on the remote).

        message : str
            Rejection message from the remote. If None, the update was accepted.
        """


def get_credentials(fn, url, username, allowed):
    """Call fn and return the credentials object.
    """
    url_str = maybe_string(url)
    username_str = maybe_string(username)

    creds = fn(url_str, username_str, allowed)

    credential_type = getattr(creds, 'credential_type', None)
    credential_tuple = getattr(creds, 'credential_tuple', None)
    if not credential_type or not credential_tuple:
        raise TypeError("credential does not implement interface")

    cred_type = credential_type

    if not (allowed & cred_type):
        raise TypeError("invalid credential type")

    ccred = ffi.new('git_cred **')
    if cred_type == C.GIT_CREDTYPE_USERPASS_PLAINTEXT:
        name, passwd = credential_tuple
        err = C.git_cred_userpass_plaintext_new(ccred, to_bytes(name),
                                                to_bytes(passwd))

    elif cred_type == C.GIT_CREDTYPE_SSH_KEY:
        name, pubkey, privkey, passphrase = credential_tuple
        name = to_bytes(name)
        if pubkey is None and privkey is None:
            err = C.git_cred_ssh_key_from_agent(ccred, name)
        else:
            err = C.git_cred_ssh_key_new(ccred, name, to_bytes(pubkey),
                                         to_bytes(privkey),
                                         to_bytes(passphrase))

    elif cred_type == C.GIT_CREDTYPE_USERNAME:
        name, = credential_tuple
        err = C.git_cred_username_new(ccred, to_bytes(name))

    elif cred_type == C.GIT_CREDTYPE_SSH_MEMORY:
        name, pubkey, privkey, passphrase = credential_tuple
        if pubkey is None and privkey is None:
            raise TypeError("SSH keys from memory are empty")
        err = C.git_cred_ssh_key_memory_new(ccred, to_bytes(name),
                                            to_bytes(pubkey), to_bytes(privkey),
                                            to_bytes(passphrase))
    else:
        raise TypeError("unsupported credential type")

    check_error(err)

    return ccred
