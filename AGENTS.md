# pygit2 Agent Guide

## Project Overview

**pygit2** is a Python library that provides bindings to
[libgit2](https://libgit2.org/), the shared C library that implements Git
plumbing operations. It exposes both a low-level API (direct libgit2 wrappers)
and a high-level, Pythonic API for repository manipulation.

- **Version**: 1.19.3 (canonical version is defined in `pygit2/_build.py`)
- **License**: GPLv2 with linking exception (see `COPYING`)
- **Maintainer**: J. David Ibáñez
- **Python Support**: 3.11 – 3.14 and PyPy3 7.3+
- **libgit2 Version**: 1.9.4
- **Homepage**: <https://www.pygit2.org/>
- **Repository**: <https://github.com/libgit2/pygit2>

## Architecture

The project uses a **hybrid C/Python** architecture with two compiled extension
modules:

- **`src/`** — C11 source and header files that compile into the `_pygit2` C
  extension module. Each file generally maps to a libgit2 concept:
  - Core objects: `blob.c`, `commit.c`, `object.c`, `tag.c`, `tree.c`
  - Repository, refs and branches: `repository.c`, `branch.c`, `reference.c`,
    `refdb.c`, `refdb_backend.c`, `revspec.c`, `worktree.c`
  - Diff and patch: `diff.c`, `patch.c`
  - ODB and backends: `odb.c`, `odb_backend.c`
  - Index, walking and helpers: `treebuilder.c`, `walker.c`, `oid.c`,
    `note.c`, `signature.c`, `mailmap.c`, `stash.c`
  - Filters: `filter.c`
  - Module infrastructure: `pygit2.c`, `error.c`, `utils.c`, `wildmatch.c`
  - Headers: `*.h` files mirroring the C sources (e.g. `repository.h`,
    `diff.h`, `types.h`, `error.h`)

- **`pygit2/`** — The main Python package.
  - **`_pygit2*.so`** — Compiled C extension built from `src/`.
  - **`_libgit2.abi3.so`** — CFFI-generated ABI module built from
    `pygit2/_run.py`.
  - **`decl/`** — C header stub files used by CFFI to define the libgit2 API
    surface (e.g. `types.h`, `repository.h`, `callbacks.h`, `diff.h`,
    `remote.h`). `pygit2/_run.py` concatenates these stubs in a specific order
    before passing them to CFFI.
  - **`_build.py`** — Build-time helpers and the canonical `__version__`
    string. Also used at runtime to locate libgit2. It must remain importable
    without the rest of the package being built because `setup.py` imports it.
  - **`_run.py`** — CFFI build script that aggregates `decl/*.h` and compiles
    `pygit2._libgit2`.
  - **`ffi.py`** — Runtime import of the CFFI `ffi` and `lib` (`C`) objects.
  - **`_pygit2.pyi`** — Type stubs for the C extension. Keep it in sync when
    adding or changing low-level APIs.
  - **`py.typed`** — PEP 561 marker indicating the package is typed.
  - **High-level modules** — Pure-Python wrappers that sit on top of the C
    extension:
    `repository.py`, `callbacks.py`, `config.py`, `index.py`, `remotes.py`,
    `settings.py`, `submodules.py`, `transaction.py`, `filter.py`, `blob.py`,
    `blame.py`, `branches.py`, `credentials.py`, `errors.py`, `options.py`,
    `packbuilder.py`, `references.py`, `refspec.py`, `utils.py`, `enums.py`,
    `legacyenums.py`.

- **`test/`** — pytest suite with fixture-based repository handling.
- **`docs/`** — Sphinx documentation (RTD theme).

## Key Configuration Files

- **`setup.py`** — setuptools entry point. Builds both the C extension
  (`src/*.c`) and the CFFI extension (`pygit2/_run.py:ffi`).
- **`pyproject.toml`** — Build-system requirements, `cibuildwheel`
  configuration, `ruff` settings, and `codespell` settings.
- **`setup.cfg`** — Legacy pycodestyle configuration.
- **`pytest.ini`** — pytest configuration (`--capture=no -ra --verbose`,
  `testpaths = test/`).
- **`mypy.ini`** — mypy configuration with strict settings.
- **`mypy-stubtest.ini`** — mypy configuration for `stubtest` against
  `_pygit2.pyi`.
- **`requirements.txt`** — Runtime/build requirements (`cffi>=2.0`,
  `setuptools` for Python >= 3.12).
- **`requirements-test.txt`** — Test requirements (`pytest`, `pytest-cov`).
- **`requirements-typing.txt`** — Typing requirements (`mypy`, `types-cffi`).
- **`Makefile`** — Convenience targets: `make` builds dependencies + extension
  inplace; `make html` builds docs.
- **`.vimrc`** — Local editor configuration for C development with ALE
  (`-std=c11 -Wall`, Python include path, `/usr/local/include`).

## Build and Test Commands

### Quick Development Build (inplace)

Requires libgit2 development headers and library to be installed on the system
or pointed to via the `LIBGIT2` environment variable.

```bash
python setup.py build_ext --inplace
pytest
```

### Full Build with Dependencies

The `build.sh` script can download, compile, and bundle libgit2 (and optionally
libssh2, OpenSSL, and zlib) into a local prefix. On Windows, `build.ps1`
handles libgit2 compilation via CMake.

```bash
# Build inplace with bundled libgit2/libssh2/OpenSSL
make

# Or manually:
LIBSSH2_VERSION=1.11.1 LIBGIT2_VERSION=1.9.4 sh build.sh

# Build inplace and run the tests
sh build.sh test

# Build a wheel, install it, and run the tests
sh build.sh wheel

# Run tests with coverage
sh build.sh test   # build.sh adds --cov=pygit2

# Run mypy type checking
sh build.sh mypy

# Run stubtest against the .pyi file
sh build.sh stubtest
```

`build.sh` creates a virtual environment under `ci/<python_tag>/` by default,
where `<python_tag>` is computed by `build_tag.py`. Use the `PYTHON`
environment variable to select a different interpreter (default: `python3`).

### Environment Variables

Variables consumed by `setup.py` / `pygit2/_build.py`:

- `LIBGIT2` — Base path where libgit2 is installed (default: `/usr/local` or
  `%ProgramFiles%\libgit2` on Windows).
- `LIBGIT2_LIB` — Override the library directory specifically.

Variables consumed by `build.sh`:

- `LIBGIT2_VERSION` — If set, download and build this libgit2 version.
- `LIBSSH2_VERSION` — If set, download and build libssh2 with SSH support.
- `OPENSSL_VERSION` — If set, download and build OpenSSL (mainly used for
  macOS universal builds on CI).
- `ZLIB_VERSION` — If set, download and build zlib.
- `BUILD_TYPE` — CMake build type (default: `Debug`).
- `PYTHON` — Python interpreter to use (default: `python3`).
- `PREFIX` — Installation prefix (default: `$(pwd)/ci/$PYTHON_TAG`).
- `CIBUILDWHEEL` — Set to `1` when invoked by cibuildwheel; changes package
  manager and directory layout.
- `AUDITWHEEL_PLAT` — Linux platform for auditwheel repair.
- `LIBSSH2_OPENSSL` — Where to find OpenSSL when building libssh2.

### Documentation Build

```bash
# Build the extension first, then docs
make                # builds deps + extension
make -C docs html   # requires sphinx-rtd-theme
```

## Code Style Guidelines

### Python

- **Formatter / Linter**: [ruff](https://docs.astral.sh/ruff/)
  - Target Python: 3.11+
  - Quote style: single quotes
  - Selected rules: `E4`, `E7`, `E9`, `F`, `I`, `UP035`, `UP007`
- **Type checker**: mypy (strict settings enabled; see `mypy.ini`)
- All Python source files must include the standard GPLv2 copyright header.
- `pygit2/__init__.py` is large because it re-exports a large surface of
  constants and classes; follow existing patterns when adding new public
  symbols.

### C

- Standard: C11
- All C source files must include the standard GPLv2 copyright header.
- The `.vimrc` at repo root configures ALE with `-std=c11 -Wall` and includes
  the Python headers and `/usr/local/include`.

### Docstrings

Use the following style (from `docs/development.rst`):

```python
def f(a, b):
    """
    The general description goes here.

    Returns: bla bla.

    Parameters:

    a : <type>
        Bla bla.

    b : <type>
        Bla bla.

    Examples::

        >>> f(...)
    """
```

## Testing Instructions

- **Runner**: pytest
- **Configuration**: `pytest.ini`
  ```ini
  [pytest]
  addopts = --capture=no -ra --verbose
  testpaths = test/
  ```
- **Fixtures**: Defined in `test/conftest.py`. They yield `pygit2.Repository`
  instances extracted from zipped sample repos in `test/data/` (e.g.
  `testrepo.zip`, `barerepo.zip`). Named fixtures include `testrepo`,
  `testrepo_path`, `barerepo`, `barerepo_path`, `emptyrepo`, `dirtyrepo`,
  `mergerepo`, `encodingrepo`, `testrepopacked`, `gpgsigned`, `blameflagsrepo`,
  and `pygit2_empty_key`.
- **Test utilities**: `test/utils.py` provides helpers such as
  `TemporaryRepository`, `gen_blob_sha1`, `rmtree`, `diff_safeiter`, and
  markers like `requires_network`, `requires_proxy`, `requires_ssh`,
  `requires_refcount`, `fails_in_macos`, and `requires_future_libgit2`.
- **Isolation**: The session-scoped `global_git_config` fixture clears
  `GLOBAL`, `XDG`, and `SYSTEM` config search paths to ensure reproducibility.
- **Coverage**: `pytest-cov` is used; run via `sh build.sh test`.

## CI / Deployment

GitHub Actions workflows live in `.github/workflows/`:

- **`tests.yml`** — Runs on s390x via QEMU (`uraimo/run-on-arch-action`).
  Allowed to fail; see issue #812.
- **`lint.yml`** — Runs `ruff format --diff`, `ruff check`, and
  `sh build.sh mypy`.
- **`wheels.yml`** — Uses `cibuildwheel` to build wheels for Linux (amd64,
  arm64, ppc64le, musl), macOS (intel, arm64, PyPy), and Windows (x64, x86,
  arm64). It also builds an sdist, runs a `twine check`, publishes to PyPI,
  and creates a GitHub Release on version tags (`v*`).
- **`codespell.yml`** — Spell checking with the codespell action.

The `cibuildwheel` configuration in `pyproject.toml` pins:

- `LIBGIT2_VERSION="1.9.4"`
- `LIBSSH2_VERSION="1.11.1"`
- `OPENSSL_VERSION="3.5.4"`

and skips `*musllinux_ppc64le` plus testing on `*-*linux_ppc64le` and
`pp*-macosx_arm64`.

## Security Considerations

- The project links against OpenSSL and libssh2. CI pins specific versions of
  these libraries when building wheels.
- Wheel repair commands (`auditwheel`, `delocate-wheel`) bundle shared
  libraries so wheels are self-contained.
- Credentials callbacks (`RemoteCallbacks`, `get_credentials`) are the primary
  interface for supplying secrets; never hardcode credentials in tests.
- Valgrind support: see `docs/development.rst` and
  `misc/valgrind-python.supp` for memory-leak debugging instructions.

## Useful Notes for Agents

- **Do not assume libgit2 is installed globally.** Check for `LIBGIT2` or use
  `build.sh` / `make`.
- **`pygit2/_build.py`** is imported by `setup.py`; it must remain importable
  without the rest of the package being built.
- **CFFI and setuptools extensions are both built from `setup.py`.**
  `ext_modules` builds the C extension from `src/*.c`; `cffi_modules` triggers
  the CFFI build via `pygit2/_run.py:ffi`.
- **`.pyi` stub file**: `pygit2/_pygit2.pyi` provides type stubs for the C
  extension. Keep it in sync when adding or changing low-level APIs.
- **Header stub order matters**: `pygit2/_run.py` concatenates `decl/*.h` in a
  fixed list; add new stubs in the correct position if dependencies require it.
- Run the full test suite and type checks before considering a change complete:
  `sh build.sh test` and `sh build.sh mypy`.
