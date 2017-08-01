**********************************************************************
git-clone ssh://git@example.com
**********************************************************************

Example for cloning a git repository over ssh.

.. code-block:: bash

   $> git clone git@example.com

.. code-block:: python

    class MyRemoteCallbacks(pygit2.RemoteCallbacks):

        def credentials(self, url, username_from_url, allowed_types):
            if allowed_types & pygit2.credentials.GIT_CREDTYPE_USERNAME:
                return pygit2.Username("git")
            elif allowed_types & pygit2.credentials.GIT_CREDTYPE_SSH_KEY:
                return pygit2.Keypair("git", "id_rsa.pub", "id_rsa", "")
            else:
                return None

    print("Cloning pygit2 over ssh")
    pygit2.clone_repository("ssh://github.com/libgit2/pygit2", "pygit2.git",
                            callbacks=MyRemoteCallbacks())

    print("Cloning pygit2 over ssh with the username in the URL")
    keypair = pygit2.Keypair("git", "id_rsa.pub", "id_rsa", "")
    callbacks = pygit2.RemoteCallbacks(credentials=keypair)
    pygit2.clone_repository("ssh://git@github.com/libgit2/pygit2", "pygit2.git",
                            callbacks=callbacks)
