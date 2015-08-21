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

    for (section, var, question, default) in [
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


def make_repo(args):
    print ("Let's make a repo !")


CMDS = {
    'make-config': (make_config, "Create a git-mariadb config file"),
    'make-repo': (make_repo, "Build a repository containing the whole"
        " current repository"),
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd",
        help="Command (possible values: %s)" % ", ".join(list(CMDS.keys())))
    parser.add_argument("-r", help="Repository id (default: 0)", type=int,
        default=0)
    args = parser.parse_args()
    if not args.cmd in CMDS:
        parser.print_help()
        return os.EX_USAGE

    CMDS[args.cmd][0](args)
    return os.EX_OK


if __name__ == "__main__":
    sys.exit(main())