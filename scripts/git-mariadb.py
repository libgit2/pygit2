#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import configparser
import os
import sys

import pygit2


class Config(configparser.ConfigParser):
    PATH = os.path.join(os.path.expanduser("~"), ".git-mariadb")

    def __init__(self):
        super(Config, self).__init__()
        self.read(self.PATH)

    def write(self):
        with open(self.PATH, 'w') as file_descriptor:
            super(Config, self).write(file_descriptor)


def make_config(args):
    config = Config()

    config['db'] = {}
    config['user'] = {}

    for (section, var, question, default) in [
                ("user", "name", "User name", "Jerome Flesch"),
                ("user", "email", "User email", "jflesch@gmail.com"),
                ("db", "host", "Database host", "localhost"),
                ("db", "port", "Database port", "3306"),
                ("db", "user", "Database login", "pygit2"),
                ("db", "passwd", "Database password", "pygit2"),
                ("db", "db", "Database name", "pygit2"),
                ("db", "table_prefix", "Table prefix", "pygit2"),
            ]:
        print (("%s ? [%s]" % (question, default)))
        value = input().strip()
        if value == "":
            value = default
        config[section][var] = value

    print ("Testing config ...")
    repo = pygit2.Repository(
        config["db"]["host"], int(config["db"]["port"]),
        config["db"]["user"], config["db"]["passwd"],
        None, config["db"]["db"],
        config["db"]["table_prefix"], 0)
    repo.close()

    print ("Writing config ...")
    config.write()
    print ("Done")


def _make_blob(repo, filepath):
    with open(filepath, "rb") as file_descriptor:
        file_content = file_descriptor.read()
    return repo.create_blob(file_content)


def _make_tree(repo, trees, filedir):
    if filedir == ".":
        return trees
    (filedir_parent, filedir_name) = os.path.split(filedir)
    (tree_builder, tree_children) = _make_tree(repo, trees, filedir_parent)
    if not filedir_name in tree_children:
        tree_children[filedir_name] = (repo.TreeBuilder(), {})
    return tree_children[filedir_name]


def _insert_blob_in_trees(repo, trees, filedir, filename, blob_oid):
    (tree_builder, _) = _make_tree(repo, trees, filedir)
    tree_builder.insert(filename, blob_oid, pygit2.GIT_FILEMODE_BLOB)


def _insert_trees(trees, tree_path):
    (tree_builder, tree_children) = trees
    for (tree_name, tree_child) in list(tree_children.items()):
        tree_oid = _insert_trees(tree_child, os.path.join(tree_path, tree_name))
        tree_builder.insert(tree_name, tree_oid, pygit2.GIT_FILEMODE_TREE)
    oid = tree_builder.write()
    return oid


def make_repo(args):
    workdir = args.workdir
    repo_id = args.repository_id
    print (("=== Loading workdir '%s' in DB, as repository %d ==="
        % (workdir, repo_id)))

    os.chdir(workdir)

    config = Config()
    repo = pygit2.Repository(
        config["db"]["host"], int(config["db"]["port"]),
        config["db"]["user"], config["db"]["passwd"],
        None, config["db"]["db"],
        config["db"]["table_prefix"], repo_id)
    try:
        blob_oids = []

        for (dirpath, _, filenames) in os.walk("."):
            if "/." in dirpath or "/__" in dirpath:
                continue
            for filename in filenames:
                if filename[0] == ".":
                    continue
                filepath = os.path.join(dirpath, filename)
                sys.stdout.write("%s --> " % filepath)
                sys.stdout.flush()
                blob_oid = _make_blob(repo, filepath)
                sys.stdout.write("%s\n" % blob_oid.hex)
                sys.stdout.flush()
                blob_oids.append((filepath, blob_oid))

        # create the tree and insert the blob in them
        trees = (
                # root
                repo.TreeBuilder(),  # corresponding tree builder
                {}  # children nodes
            )
        for (filepath, blob_oid) in blob_oids:
            (filedir, filename) = os.path.split(filepath)
            _insert_blob_in_trees(repo, trees, filedir, filename, blob_oid)

        # insert the trees, starting from the children, and end with the parents
        tree_oid = _insert_trees(trees, ".")

        print ("Looking for HEAD ...")
        parents = []
        try:
            parent = repo.head.target
            if parent is not None:
                print ("HEAD: %s" % parent.hex)
                if parent != pygit2.Oid(hex='0'):
                    parents = [parent]
        except pygit2.GitError:
            pass
        if parents == []:
            print ("HEAD not found")

        print ("Commiting ...")
        author = pygit2.Signature(config['user']['name'],
            config['user']['email'])
        committer = pygit2.Signature(config['user']['name'],
            config['user']['email'])
        repo.create_commit(
               'refs/heads/master',
                author, committer, args.msg,
                tree_oid,
                parents
            )

        if parents == []:
            # make sure head points to the new branch
            repo.set_head("refs/heads/master")

        print ("Done")
    except:
        repo.rollback()
        raise
    finally:
        repo.close()


def _checkout_tree(repo, parent_path, tree):
    for node in tree:
        path = os.path.join(parent_path, node.name)
        print (("Checking out %s (%d) ..." % (str(path), node.filemode)))

        if (node.filemode == pygit2.GIT_FILEMODE_BLOB
                or node.filemode == pygit2.GIT_FILEMODE_BLOB_EXECUTABLE):
            blob = repo.get(node.id)
            data = blob.data
            with open(path, 'wb') as file_descriptor:
                file_descriptor.write(data)
        elif node.filemode == pygit2.GIT_FILEMODE_TREE:
            try:
                os.mkdir(path)
            except FileExistsError:
                pass
            node_id = node.id
            tree = repo.get(node_id)
            _checkout_tree(repo, path, tree)
            print ("<--")
        else:
            print (("WARNING: Unmanaged tree element type: %d, %s"
                    % (node.filemode, node.id.hex)))


def checkout(args):
    workdir = args.workdir
    repo_id = args.repository_id
    revision = args.revision

    print (("=== Checking out revision '%s' to '%s'" % (revision, workdir)))

    os.chdir(workdir)
    config = Config()
    repo = pygit2.Repository(
        config["db"]["host"], int(config["db"]["port"]),
        config["db"]["user"], config["db"]["passwd"],
        None, config["db"]["db"],
        config["db"]["table_prefix"], repo_id)
    try:
        commit = repo[repo.head.target]
        tree = commit.tree
        _checkout_tree(repo, ".", tree)
    finally:
        repo.close()

CMDS = {
    'make-config': (make_config, "Create a git-mariadb config file"),
    'commit-all': (make_repo, "Build/update a repository containing the whole"
        " work directory)"),
    'checkout': (checkout, "Checkout repository content"),
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd",
        help="Command (possible values: %s)" % ", ".join(list(CMDS.keys())))
    parser.add_argument("-R", "--repository-id",
        help="Repository id (default: 0)", type=int, default=0)
    parser.add_argument("-w", "--workdir",
        help="Workdir path (default: \".\")",
        default=".")
    parser.add_argument("-m", "--msg", help="Commit message",
        default="maintenance")
    parser.add_argument("-r", "--revision", help="Revision/ref to checkout",
        default="HEAD")
    args = parser.parse_args()

    if not args.cmd in CMDS:
        parser.print_help()
        return os.EX_USAGE

    CMDS[args.cmd][0](args)
    return os.EX_OK


if __name__ == "__main__":
    sys.exit(main())