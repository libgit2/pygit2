from io import BytesIO
import codecs
import pytest

import pygit2
from pygit2.enums import BlobFilter
from pygit2.errors import Passthrough


def _rot13(data):
    return codecs.encode(data.decode('utf-8'), 'rot_13').encode('utf-8')


class _Rot13Filter(pygit2.Filter):
    attributes = 'text'

    def write(self, data, src, write_next):
        return super().write(_rot13(data), src, write_next)


class _BufferedFilter(pygit2.Filter):
    attributes = 'text'

    def __init__(self):
        super().__init__()
        self.buf = BytesIO()

    def write(self, data, src, write_next):
        self.buf.write(data)

    def close(self, write_next):
        write_next(_rot13(self.buf.getvalue()))


class _PassthroughFilter(_Rot13Filter):
    def check(self, src, attr_values):
        assert attr_values == [None]
        assert src.repo
        raise Passthrough


class _UnmatchedFilter(_Rot13Filter):
    attributes = 'filter=rot13'


@pytest.fixture
def rot13_filter():
    pygit2.filter_register('rot13', _Rot13Filter)
    yield
    pygit2.filter_unregister('rot13')


@pytest.fixture
def passthrough_filter():
    pygit2.filter_register('passthrough-rot13', _PassthroughFilter)
    yield
    pygit2.filter_unregister('passthrough-rot13')


@pytest.fixture
def buffered_filter():
    pygit2.filter_register('buffered-rot13', _BufferedFilter)
    yield
    pygit2.filter_unregister('buffered-rot13')


@pytest.fixture
def unmatched_filter():
    pygit2.filter_register('unmatched-rot13', _UnmatchedFilter)
    yield
    pygit2.filter_unregister('unmatched-rot13')


def test_filter(testrepo, rot13_filter):
    blob_oid = testrepo.create_blob_fromworkdir('bye.txt')
    blob = testrepo[blob_oid]
    flags = BlobFilter.CHECK_FOR_BINARY | BlobFilter.ATTRIBUTES_FROM_HEAD
    assert b'olr jbeyq\n' == blob.data
    with pygit2.BlobIO(blob) as reader:
        assert b'olr jbeyq\n' == reader.read()
    with pygit2.BlobIO(blob, as_path='bye.txt', flags=flags) as reader:
        assert b'bye world\n' == reader.read()


def test_filter_buffered(testrepo, buffered_filter):
    blob_oid = testrepo.create_blob_fromworkdir('bye.txt')
    blob = testrepo[blob_oid]
    flags = BlobFilter.CHECK_FOR_BINARY | BlobFilter.ATTRIBUTES_FROM_HEAD
    assert b'olr jbeyq\n' == blob.data
    with pygit2.BlobIO(blob) as reader:
        assert b'olr jbeyq\n' == reader.read()
    with pygit2.BlobIO(blob, 'bye.txt', flags=flags) as reader:
        assert b'bye world\n' == reader.read()


def test_filter_passthrough(testrepo, passthrough_filter):
    blob_oid = testrepo.create_blob_fromworkdir('bye.txt')
    blob = testrepo[blob_oid]
    flags = BlobFilter.CHECK_FOR_BINARY | BlobFilter.ATTRIBUTES_FROM_HEAD
    assert b'bye world\n' == blob.data
    with pygit2.BlobIO(blob) as reader:
        assert b'bye world\n' == reader.read()
    with pygit2.BlobIO(blob, 'bye.txt', flags=flags) as reader:
        assert b'bye world\n' == reader.read()


def test_filter_unmatched(testrepo, unmatched_filter):
    blob_oid = testrepo.create_blob_fromworkdir('bye.txt')
    blob = testrepo[blob_oid]
    flags = BlobFilter.CHECK_FOR_BINARY | BlobFilter.ATTRIBUTES_FROM_HEAD
    assert b'bye world\n' == blob.data
    with pygit2.BlobIO(blob) as reader:
        assert b'bye world\n' == reader.read()
    with pygit2.BlobIO(blob, as_path='bye.txt', flags=flags) as reader:
        assert b'bye world\n' == reader.read()


def test_filter_cleanup(dirtyrepo, rot13_filter):
    # Indirectly test that pygit2_filter_cleanup has the GIL
    # before calling pygit2_filter_payload_free.
    dirtyrepo.diff()
