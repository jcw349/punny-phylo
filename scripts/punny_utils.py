import argparse
import os
import treeswift as ts
import pandas as pd


def merge_trees(trees):
    main_tree = trees[0]
    
    for n in main_tree['tree1'].traverse_internal():
        # get leaves of the current node
        leaves = [ l.get_label()for l in n.traverse_leaves()]
        
        # get corresponding node in the other trees and add their annotations
        for tree in trees[1:]:
            alt_node = tree['tree1'].mrca(leaves)
            if n.node_params == alt_node.node_params:
                continue
            else:
                n_params = n.node_params.split(",")
                alt_params = alt_node.node_params.split(",")
                for param in alt_params:
                    if param not in n_params:
                        n.node_params+=','+param
    return main_tree


def rename_tips(tree, rename_dict):
    log_dict = dict({"renamed_before":[],
                     "renamed_after":[],
                     "same_name":[],
                     "not_in_rename": [],
                     "not_in_tree": []
                     })
    leaf_names = []
    for node in tree.traverse_leaves():
        leaf_names.append(node.label)
        if node.label in rename_dict:
            if node.label == rename_dict[node.label]:
                log_dict["same_name"].append(node.label)
            else:
                node.label = rename_dict[node.label]
                log_dict["renamed_before"].append(node.label)
                log_dict["renamed_after"].append(rename_dict[node.label])
        else:
            log_dict['not_in_rename'].append(node.label)
    
    log_dict['not_in_tree'] = [ name for name in rename_dict.keys() if name not in leaf_names]
    
    return tree, log_dict


def rescale_branches(tree, clock_rate, to_time=True):
    for node in tree.traverse_preorder():
        if node.edge_length is not None:
            if to_time:
                node.edge_length /= clock_rate
            else:
                node.edge_length *= clock_rate
    return tree


def collapse_polytomies(tree, threshold):
    tree.collapse_short_branches(threshold=threshold)
    return tree


def resolve_polytomies(tree):
    tree.resolve_polytomies()
    return tree

def reroot_trees(tree, root, length, support):
    r = tree.find_node(root, leaves=True, internal=True)
    tree = tree.reroot(r, length, support)
    return tree