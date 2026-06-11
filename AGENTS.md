# pygit2 Agent Guide

## Project Overview

**pygit2** is a Python library providing bindings to [libgit2](https://libgit2.org/), the shared C library that implements Git plumbing operations. It exposes both a low-level API (direct libgit2 wrappers) and a high-level Pythonic API for repository manipulation.

- **Version**: 1.19.2
- **License**: GPLv2 with linking exception
- **Maintainer**: J. David Ibáñez
- **Python Support**: 3.11 – 3.14 and PyPy3 7.3+
- **libgit2 Version**: 1.9.4
- **Homepage**: <https://www.pygit2.org/>
- **Repository**: <https://github.com/libgit2/pygit2>

## Architecture

The project uses a **hybrid C/Python** architecture with two compiled extension modules:

- **`src/`** — C11 source files that compile into the `_pygit2` C extension module. Each file generally maps to a libgit2 concept:
  - Core objects: `blob.c`, `commit.c`, `object.c`, `tag.c`, `tree.c`
  - Repository and refs: `repository.c`, `branch.c`, `reference.c`, `refdb.c`, `refdb_backend.c`, `revspec.c`
  - Diff and patch: `diff.c`, `patch.c`
  - ODB and backend: `odb.c`, `odb_backend.c`
  - Filters and mailmap: `filter.c`, `mailmap.c`
  - Notes and signatures: `note.c`, `signature.c`
  - Main module init: `pygit2.c`

- **`pygit2/`** — The main Python package.
  - **`_pygit2*.so`** — Compiled C extension (built from `src/`).
  - **`_libgit2.abi3.so`** — CFFI-generated ABI module built from `pygit2/_run.py`.
  - **`decl/`** — C header stub files used by CFFI to define the libgit2 API surface (e.g., `types.h`, `repository.h`, `callbacks.h`, `diff.h`, `remote.h`).
  - **`_build.py`** — Build-time helpers and the canonical `__version__` string. Also used at runtime to locate libgit2. Must remain importable without the rest of the package being built because `setup.py` imports it.
  - **`_run.py`** — CFFI build script that aggregates `decl/*.h` and compiles `pygit2._libgit2`.
  - **`ffi.py`** — Runtime import of the CFFI `ffi` and `lib` (`C`) objects.
  - **`_pygit2.pyi`** — Type stubs for the C extension. Keep it in sync when adding or changing low-level APIs.
  - **`py.typed`** — PEP 561 marker indicating the package is typed.
  - **High-level modules** — Pure-Python wrappers that sit on top of the C extension:
    `repository.py`, `callbacks.py`, `config.py`, `index.py`, `remotes.py`, `settings.py`, `submodules.py`, `transaction.py`, `filter.py`, `blob.py`, `blame.py`, `credentials.py`, `errors.py`, `options.py`, `packbuilder.py`, `references.py`, `refspec.py`, `utils.py`, `enums.py`, `legacyenums.py`.

- **`test/`** — pytest suite with fixture-based repository handling.
- **`docs/`** — Sphinx documentation (RTD theme).

## Key Configuration Files

- **`setup.py`** — setuptools entry point. Builds both the C extension (`src/*.c`) and the CFFI extension (`pygit2/_run.py:ffi`).
- **`pyproject.toml`** — Build system requirements, `cibuildwheel` configuration, `ruff` settings, and `codespell` settings.
- **`setup.cfg`** — Legacy pycodestyle configuration.
- **`pytest.ini`** — pytest configuration (`--capture=no -ra --verbose`, `testpaths = test/`).
- **`mypy.ini`** — mypy configuration with strict settings.
- **`mypy-stubtest.ini`** — mypy configuration for `stubtest` against `_pygit2.pyi`.
- **`requirements.txt`** — Runtime/build requirements (`cffi>=2.0`, `setuptools` for Python >= 3.12).
- **`requirements-test.txt`** — Test requirements (`pytest`, `pytest-cov`).
- **`requirements-typing.txt`** — Typing requirements (`mypy`, `types-cffi`).
- **`Makefile`** — Convenience targets: `make` builds deps + extension inplace; `make html` builds docs.

## Build and Test Commands

### Quick Development Build (inplace)

Requires libgit2 development headers and library to be installed on the system or pointed to via the `LIBGIT2` environment variable.

```bash
python setup.py build_ext --inplace
pytest
```

### Full Build with Dependencies

The `build.sh` script can download, compile, and bundle libgit2 (and optionally libssh2 and OpenSSL) into a local prefix. On Windows, `build.ps1` handles libgit2 compilation via CMake.

```bash
# Build inplace with bundled libgit2/libssh2/OpenSSL
make

# Or manually:
LIBSSH2_VERSION=1.11.1 LIBGIT2_VERSION=1.9.4 sh build.sh

# Build inplace + run tests
sh build.sh test

# Build a wheel, install it, and run tests
sh build.sh wheel

# Run tests with coverage
sh build.sh test   # (build.sh already adds --cov=pygit2)

# Run mypy type checking
sh build.sh mypy

# Run stubtest against the .pyi file
sh build.sh stubtest
```

### Environment Variables

- `LIBGIT2` — Base path where libgit2 is installed (default: `/usr/local` or `%ProgramFiles%\libgit2` on Windows).
- `LIBGIT2_LIB` — Override the library directory specifically.
- `LIBGIT2_VERSION` — If set, `build.sh` downloads and builds this libgit2 version.
- `LIBSSH2_VERSION` — If set, `build.sh` downloads and builds libssh2 with SSH support.
- `OPENSSL_VERSION` — If set, `build.sh` downloads and builds OpenSSL (mainly used for macOS universal builds on CI).

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

### C

- Standard: C11
- All C source files must include the standard GPLv2 copyright header.
- The `.vimrc` at repo root configures ALE with `-std=c11 -Wall` and includes the Python headers and `/usr/local/include`.

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
- **Fixtures**: Defined in `test/conftest.py`. They yield `pygit2.Repository` instances extracted from zipped sample repos in `test/data/` (e.g., `testrepo.zip`, `barerepo.zip`).
- **Test utilities**: `test/utils.py` provides helpers such as `TemporaryRepository`, network/proxy/SSH skip markers, and `diff_safeiter`.
- **Isolation**: The session-scoped `global_git_config` fixture clears `GLOBAL`, `XDG`, and `SYSTEM` config search paths to ensure reproducibility.
- **Coverage**: `pytest-cov` is used; run via `sh build.sh test`.

## CI / Deployment

GitHub Actions workflows live in `.github/workflows/`:

- **`tests.yml`** — Runs on s390x via QEMU (allowed to fail; see issue #812).
- **`lint.yml`** — Runs `ruff format --diff`, `ruff check`, and `sh build.sh mypy`.
- **`wheels.yml`** — Uses `cibuildwheel` to build wheels for Linux (amd64, arm64, ppc64le, musl), macOS (intel, arm64, PyPy), and Windows (x64, x86, arm64). Publishes to PyPI and creates GitHub Releases on version tags (`v*`).
- **`codespell.yml`** — Spell checking.

## Security Considerations

- The project links against OpenSSL and libssh2. CI pins specific versions of these libraries when building wheels.
- Wheel repair commands (`auditwheel`, `delocate-wheel`) bundle shared libraries so wheels are self-contained.
- Credentials callbacks (`RemoteCallbacks`, `get_credentials`) are the primary interface for supplying secrets; never hardcode credentials in tests.
- Valgrind support: see `docs/development.rst` and `misc/valgrind-python.supp` for memory-leak debugging instructions.

## Useful Notes for Agents

- **Do not assume libgit2 is installed globally.** Check for `LIBGIT2` or use `build.sh`.
- **`pygit2/_build.py`** is imported by `setup.py`; it must remain importable without the rest of the package being built.
- **CFFI and setuptools extensions are both built from `setup.py`.** `ext_modules` builds the C extension from `src/*.c`; `cffi_modules` triggers the CFFI build via `pygit2/_run.py:ffi`.
- **`.pyi` stub file**: `pygit2/_pygit2.pyi` provides type stubs for the C extension. Keep it in sync when adding or changing low-level APIs.
- **`pygit2/__init__.py`** is large because it re-exports a vast surface of constants and classes. Follow existing patterns when adding new public symbols.
