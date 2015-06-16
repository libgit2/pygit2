**********************************************************************
git-clone --mirror
**********************************************************************

git provides an argument to set up the repository as a mirror, which
involves setting the refspec to one which copies all refs and a mirror
option for push in the remote.

.. code-block:: bash

   $> git clone --mirror https://github.com/libgit2/pygit2

.. code-block:: python

    def init_remote(repo, name, url):
        # Create the remote with a mirroring url
        remote = repo.remotes.create(name, url, "+refs/*:refs/*")
        # And set the configuration option to true for the push command
        mirror_var = "remote.{}.mirror".format(name)
        repo.config[mirror_var] = True
        # Return the remote, which pygit2 will use to perform the clone
        return remote
    
    print("Cloning pygit2 as mirror")
    pygit2.clone_repository("https://github.com/libgit2/pygit2", "pygit2.git", bare=True,
                            remote=init_remote)
