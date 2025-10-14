"""Parse the latest release notes from CHANGELOG.md.

If running in GitHub Actions, set the `release_title` output
variable for use in subsequent step(s).

If running in CI, write the release notes to ReleaseNotes.md
for upload as an artifact.

Otherwise, print the release title and notes to stdout.
"""

import re
import subprocess
from os import environ
from pathlib import Path


class ChangesEntry:
    def __init__(self, version: str, notes: str) -> None:
        self.version = version
        title = notes.splitlines()[0]
        self.title = f'{version} {title}'
        self.notes = notes[len(title) :].strip()


H1 = re.compile(r'^# (\d+\.\d+\.\d+)', re.MULTILINE)


def parse_changelog() -> list[ChangesEntry]:
    changelog = Path('CHANGELOG.md').read_text(encoding='utf-8')
    parsed = H1.split(changelog)  # may result in a blank line at index 0
    if not parsed[0]:  # leading entry is a blank line due to re.split() implementation
        parsed = parsed[1:]
    assert len(parsed) % 2 == 0, (
        'Malformed CHANGELOG.md; Entries expected to start with "# x.y.x"'
    )

    changes: list[ChangesEntry] = []
    for i in range(0, len(parsed), 2):
        version = parsed[i]
        notes = parsed[i + 1].strip()
        changes.append(ChangesEntry(version, notes))
    return changes


def get_version_tag() -> str | None:
    if 'GITHUB_REF' in environ:  # for use in GitHub Actions
        git_ref = environ['GITHUB_REF']
    else:  # for local use
        git_out = subprocess.run(
            ['git', 'rev-parse', '--symbolic-full-name', 'HEAD'],
            capture_output=True,
            text=True,
            check=True,
        )
        git_ref = git_out.stdout.strip()
    version: str | None = None
    if git_ref and git_ref.startswith('refs/tags/'):
        version = git_ref[len('refs/tags/') :].lstrip('v')
    else:
        print(
            f"Using latest CHANGELOG.md entry because the git ref '{git_ref}' is not a tag."
        )
    return version


def get_entry(changes: list[ChangesEntry], version: str | None) -> ChangesEntry:
    latest = changes[0]
    if version is not None:
        for entry in changes:
            if entry.version == version:
                latest = entry
                break
        else:
            raise ValueError(f'No changelog entry found for version {version}')
    return latest


def main() -> None:
    changes = parse_changelog()
    version = get_version_tag()
    latest = get_entry(changes=changes, version=version)
    if 'GITHUB_OUTPUT' in environ:
        with Path(environ['GITHUB_OUTPUT']).open('a') as gh_out:
            print(f'release_title={latest.title}', file=gh_out)
    if environ.get('CI', 'false') == 'true':
        Path('ReleaseNotes.md').write_text(latest.notes, encoding='utf-8')
    else:
        print('Release notes:')
        print(f'# {latest.title}\n{latest.notes}')


if __name__ == '__main__':
    main()
