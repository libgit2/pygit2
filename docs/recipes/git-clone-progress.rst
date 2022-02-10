**********************************************************************
git-clone with progress monitor
**********************************************************************

Example for cloning a git repository with progress monitoring:

.. code-block:: bash

   $ git clone https://github.com/libgit2/pygit2

.. code-block:: python

    class MyRemoteCallbacks(pygit2.RemoteCallbacks):

        def transfer_progress(self, stats):
            print(f'{stats.indexed_objects}/{stats.total_objects}')

    print("Cloning pygit2")
    pygit2.clone_repository("https://github.com/libgit2/pygit2", "pygit2.git",
                            callbacks=MyRemoteCallbacks())
