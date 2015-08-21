#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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


def help():
    print ("%s <command> [opt]" % sys.argv[0])
    print ("")
    print ("Available commands:")
    for (cmd, (_, desc)) in CMDS.items():
        print ("\t%s : %s" % (cmd, desc))


def make_config():
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
        print ("%s ? [%s]" % (question, default))
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

def make_repo():
    print ("Let's make a repo !")


CMDS = {
    'help': (help, "Help"),
    'make-config': (make_config, "Create a git-mariadb config file"),
    'make-repo': (make_repo, "Build a repository containing the whole"
        " current repository"),
}


def main():
    if len(sys.argv) <= 1 or sys.argv[1] not in CMDS:
        help()
        return os.EX_USAGE
    CMDS[sys.argv[1]][0]()
    return os.EX_OK


if __name__ == "__main__":
    sys.exit(main())