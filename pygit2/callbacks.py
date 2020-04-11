"""
This is a utility module, it's here to support calls from libgit2 to written in
Python.
"""

# Standard Library
from contextlib import contextmanager

# pygit2
from .ffi import ffi, C


@contextmanager
def git_fetch_options(callbacks, opts=None):
    from .remote import RemoteCallbacks
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
    from .remote import RemoteCallbacks
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
    from .remote import RemoteCallbacks
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
