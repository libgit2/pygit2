import codecs
import gc
from collections.abc import Callable, Generator
from io import BytesIO

import pytest

import pygit2
from pygit2 import Blob, Filter, FilterSource, Repository
from pygit2.enums import BlobFilter
from pygit2.errors import Passthrough


def _rot13(data: bytes) -> bytes:
    return codecs.encode(data.decode('utf-8'), 'rot_13').encode('utf-8')


class _Rot13Filter(pygit2.Filter):
    attributes = 'text'

    def write(
        self,
        data: bytes,
        src: FilterSource,
        write_next: Callable[[bytes], None],
    ) -> None:
        return super().write(_rot13(data), src, write_next)


class _BufferedFilter(pygit2.Filter):
    attributes = 'text'

    def __init__(self) -> None:
        super().__init__()
        self.buf = BytesIO()

    def write(
        self,
        data: bytes,
        src: FilterSource,
        write_next: Callable[[bytes], None],
    ) -> None:
        self.buf.write(data)

    def close(self, write_next: Callable[[bytes], None]) -> None:
        write_next(_rot13(self.buf.getvalue()))


class _PassthroughFilter(_Rot13Filter):
    def check(self, src: FilterSource, attr_values: list[str | None]) -> None:
        assert attr_values == [None]
        assert src.repo
        raise Passthrough


class _UnmatchedFilter(_Rot13Filter):
    attributes = 'filter=rot13'


def _filter_fixture(name: str, filter: type[Filter]) -> Generator[None, None, None]:
    pygit2.filter_register(name, filter)
    yield

    # Collect any FilterLists that may use this filter before unregistering it
    gc.collect()

    pygit2.filter_unregister(name)


@pytest.fixture
def rot13_filter() -> Generator[None, None, None]:
    yield from _filter_fixture('rot13', _Rot13Filter)


@pytest.fixture
def passthrough_filter() -> Generator[None, None, None]:
    yield from _filter_fixture('passthrough-rot13', _PassthroughFilter)


@pytest.fixture
def buffered_filter() -> Generator[None, None, None]:
    yield from _filter_fixture('buffered-rot13', _BufferedFilter)


@pytest.fixture
def unmatched_filter() -> Generator[None, None, None]:
    yield from _filter_fixture('unmatched-rot13', _UnmatchedFilter)


def test_filter(testrepo: Repository, rot13_filter: Filter) -> None:
    blob_oid = testrepo.create_blob_fromworkdir('bye.txt')
    blob = testrepo[blob_oid]
    assert isinstance(blob, Blob)
    flags = BlobFilter.CHECK_FOR_BINARY | BlobFilter.ATTRIBUTES_FROM_HEAD
    assert b'olr jbeyq\n' == blob.data
    with pygit2.BlobIO(blob) as reader:
        assert b'olr jbeyq\n' == reader.read()
    with pygit2.BlobIO(blob, as_path='bye.txt', flags=flags) as reader:
        assert b'bye world\n' == reader.read()


def test_filter_buffered(testrepo: Repository, buffered_filter: Filter) -> None:
    blob_oid = testrepo.create_blob_fromworkdir('bye.txt')
    blob = testrepo[blob_oid]
    assert isinstance(blob, Blob)
    flags = BlobFilter.CHECK_FOR_BINARY | BlobFilter.ATTRIBUTES_FROM_HEAD
    assert b'olr jbeyq\n' == blob.data
    with pygit2.BlobIO(blob) as reader:
        assert b'olr jbeyq\n' == reader.read()
    with pygit2.BlobIO(blob, 'bye.txt', flags=flags) as reader:
        assert b'bye world\n' == reader.read()


def test_filter_passthrough(testrepo: Repository, passthrough_filter: Filter) -> None:
    blob_oid = testrepo.create_blob_fromworkdir('bye.txt')
    blob = testrepo[blob_oid]
    assert isinstance(blob, Blob)
    flags = BlobFilter.CHECK_FOR_BINARY | BlobFilter.ATTRIBUTES_FROM_HEAD
    assert b'bye world\n' == blob.data
    with pygit2.BlobIO(blob) as reader:
        assert b'bye world\n' == reader.read()
    with pygit2.BlobIO(blob, 'bye.txt', flags=flags) as reader:
        assert b'bye world\n' == reader.read()


def test_filter_unmatched(testrepo: Repository, unmatched_filter: Filter) -> None:
    blob_oid = testrepo.create_blob_fromworkdir('bye.txt')
    blob = testrepo[blob_oid]
    assert isinstance(blob, Blob)
    flags = BlobFilter.CHECK_FOR_BINARY | BlobFilter.ATTRIBUTES_FROM_HEAD
    assert b'bye world\n' == blob.data
    with pygit2.BlobIO(blob) as reader:
        assert b'bye world\n' == reader.read()
    with pygit2.BlobIO(blob, as_path='bye.txt', flags=flags) as reader:
        assert b'bye world\n' == reader.read()


def test_filter_cleanup(dirtyrepo: Repository, rot13_filter: Filter) -> None:
    # Indirectly test that pygit2_filter_cleanup has the GIL
    # before calling pygit2_filter_payload_free.
    dirtyrepo.diff()


def test_filterlist_none(testrepo: Repository) -> None:
    fl = testrepo.load_filter_list('hello.txt')
    assert fl is None


def test_filterlist_crlf(testrepo: Repository) -> None:
    testrepo.config['core.autocrlf'] = True

    fl = testrepo.load_filter_list('hello.txt')
    assert fl is not None
    assert len(fl) == 1
    assert 'crlf' in fl

    with pytest.raises(TypeError):
        1234 in fl  # type: ignore


def test_filterlist_rot13(testrepo: Repository, rot13_filter: Filter) -> None:
    fl = testrepo.load_filter_list('hello.txt')
    assert fl is not None
    assert 'rot13' in fl


def test_filterlist_dangerous_unregister(testrepo: Repository) -> None:
    pygit2.filter_register('rot13', _Rot13Filter)

    fl = testrepo.load_filter_list('hello.txt')
    assert fl is not None
    assert len(fl) == 1
    assert 'rot13' in fl

    # Unregistering a filter that's still in use in a FilterList is dangerous!
    # Our built-in check (that raises RuntimeError) may avert a segfault.
    with pytest.raises(RuntimeError):
        pygit2.filter_unregister('rot13')

    # Delete any FilterLists that use the filter, and only then is it safe
    # to unregister the filter.
    del fl
    gc.collect()
    pygit2.filter_unregister('rot13')
