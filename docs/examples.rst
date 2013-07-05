**********************************************************************
Quick examples
**********************************************************************

A list of some common command-line operations and their pygit2 equivalents.

Creating a new repository with ``git init``

    >>> pygit2.init_repository('repo_name', False)
    <pygit2.repository.Repository object at 0x10f08b680>

Viewing a commit with ``git show d370f56``

    >>> repo = pygit2.Repository('/path/to/repository')
    >>> commit = repo['d370f56']

Viewing the last commit message

    >>> repo[repo.head.oid].message
    'commit message'

Traversing the commit history with ``git log``

    >>> last = repo[repo.head.oid]
    >>> for commit in repo.walk(last.oid, pygit2.GIT_SORT_TIME):
    >>>     print(commit.message) # or some other operation

Listing all branches with ``git branch``

    >>> regex = re.compile('^refs/heads/')
    >>> filter(lambda r: regex.match(r), repo.listall_references())

Similarly, listing all tags with ``git tag``

    >>> regex = re.compile('^refs/tags')
    >>> filter(lambda r: regex.match(r), repo.listall_references())

Listing all files in the last commit

    >>> for e in repo[repo.head.oid].tree:
    >>>     print(e.name)
