# -*- coding: utf-8 -*-
#
# Copyright 2012 Nico von Geyso
#
# This file is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License, version 2,
# as published by the Free Software Foundation.
#
# In addition to the permissions in the GNU General Public License,
# the authors give you unlimited permission to link the compiled
# version of this file into combinations with other programs,
# and to distribute those combinations without any restriction
# coming from the use of this file.  (The General Public License
# restrictions do apply in other respects; for example, they cover
# modification of the file, and distribution when not linked into
# a combined executable.)
#
# This file is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING.  If not, write to
# the Free Software Foundation, 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301, USA.

import os

def tree_insert_node(repo, root_oid, node_oid, path):
    """
      Creates a new tree with a given node and path in an existing tree

      @param repo : instance of pygit2.Repository
      @param root_oid  : oid of root tree
      @param node_oid : oid of node to insert
      @param path : path where to store the node
    """

    root = repo.TreeBuilder(root_oid)
    current_node = repo[root_oid]

    entries = path.split('/')[:-1]
    entries.reverse()

# search for existing nodes in path
    tree_path = [('/', root)]
    while len(entries) > 0:
        if entries[-1] not in current_node:
            break

        entry = entries.pop()
        current_node = repo[current_node[entry].oid]
        tree_path.append((
          entry, repo.TreeBuilder(current_node.oid)
        ))

# create node
    if len(entries) > 0:
        tmp = repo.TreeBuilder()
    else:
        tmp = tree_path[-1][1]

    filename = os.path.basename(path)
    tmp.insert(filename, node_oid, 0o100644)
    current = tmp.write()

# create new nodes bottom-up for our node
    size = len(entries)
    for i, entry in enumerate(entries):
        if i < (size - 1):
            tmp = repo.TreeBuilder()
            tmp.insert(entry, current, 0o40000)
            current = tmp.write()
        else:
            tree_path.append((entry, None))

# connect existing nodes with created nodes
    pre = tree_path.pop()[0]
    tree_path.reverse()
    for name, builder in tree_path:
        builder.insert(pre, current, 0o40000)
        current = builder.write()
        pre = name 

    return current
