**********************************************************************
Recipes
**********************************************************************

A list of some standard git commands and their pygit2 equivalents. This
document is a work in progress, and is organized according to the `git man
page`_.

----------------------------------------------------------------------
High Level Commands
----------------------------------------------------------------------

======================================================================
Main porcelain commands
======================================================================

.. toctree::
   :maxdepth: 1

   git-cherry-pick (Apply the changes introduced by some existing commits.) <recipes/git-cherry-pick>
   git-init (Create an empty git repository or reinitialize an existing one.) <recipes/git-init>
   git-log (Show commit logs.) <recipes/git-log>
   git-show (Show various types of objects.) <recipes/git-show>
   git-tag (Create, list, delete or verify a tag object signed with GPG.) <recipes/git-tag>
   git clone (Clone with progress monitor) <recipes/git-clone-progress>
   git clone --mirror (Clone with a mirroring configuration) <recipes/git-clone-mirror>
   git clone username@hostname (Clone over ssh) <recipes/git-clone-ssh>
   git-add / git-reset HEAD (Add file contents to the index / Unstage) <recipes/git-add-reset>
   git commit (Make an initial commit, and a subsequent commit) <recipes/git-commit>

.. _git man page: https://www.kernel.org/pub/software/scm/git/docs/git.html
