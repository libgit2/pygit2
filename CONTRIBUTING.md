# Contributing to pygit2

Thank you for your interest in improving pygit2! This document covers how to submit pull requests and help others in the community.

---

## Pull Requests

We welcome pull requests that fix bugs, add features, improve documentation, or clean up code. To ensure a smooth review process, please follow the steps below.

### Development Setup

See the [install documentation](https://www.pygit2.org/install.html) for instructions on building pygit2 and its libgit2 dependency.

### Making Changes

1. **Fork the repository** and create a feature branch.
2. **Follow the existing code style** (see below).
3. **Add or update tests** for any new or changed behavior. Tests live in `test/` and are run with `pytest`.
4. **Update type stubs** (`pygit2/_pygit2.pyi`) if you modify the C extension's public API.
5. **Update `pygit2/__init__.py`** if you add new public symbols that should be re-exported.
6. **Ensure the test suite passes**:
   ```bash
   pytest
   ```
7. **Run the linters and type checker**:
   ```bash
   ruff format --diff
   ruff check
   sh build.sh mypy        # or: mypy
   sh build.sh stubtest    # validate .pyi stubs
   ```
8. **Build the documentation** if you changed it (requires `sphinx-rtd-theme`):
   ```bash
   make -C docs html
   ```
9. **Write a clear commit message** explaining the *what* and *why*.

### Code Style

- **Python:** We target Python 3.11+. Use single quotes. Run `ruff format` and `ruff check` before submitting.
- **C:** We use C11. Follow `-std=c11 -Wall`. Match the style of the surrounding code in `src/`.
- **Copyright headers:** All source files must include the standard GPLv2 copyright header. Copy it from an existing file.
- **Docstrings:** Use the style shown in `docs/development.rst`:
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
      """
  ```

### Pull Request Review

- All PRs require review from a maintainer.
- CI will run tests, linting, and type checks automatically.
- Be responsive to feedback and willing to iterate.
- Keep PRs focused. A pull request that does one thing well is easier to review than a large, mixed one.

---

## Helping Others

You do not need to write code to contribute. Helping others is valuable:

- **Answer questions** in open issues and pull requests. If you know the answer, share it.
- **Review PRs.** Even if you are not a maintainer, constructive reviews from the community are welcome.
- **Improve documentation.** Doc fixes, clarifications, and typo corrections can be submitted as PRs just like code.
- **Reproduce reported issues.** Confirming a bug on your system helps maintainers prioritize fixes.

---

## Commit Messages

- Use the present tense and imperative mood (e.g., "Add support for…", not "Added support for…").
- Keep the subject line under 72 characters.
- Reference related issues with `Fixes #123` or `Closes #456` when applicable.
- If you used AI assistance while preparing the change, mention it in the commit message with a tag such as `Assisted-by: Kimi-k2.6` (or the appropriate model name).

---

Thank you for contributing!
