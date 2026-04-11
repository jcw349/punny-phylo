import argparse
import os
import treeswift as ts
import pandas as pd
import numpy as np

def get_node_params(param, field=None):
    n_params=param.strip("&").replace('"','').split(",")
    fields = [ n.split('=') for n in n_params ]
    if field:
        fields = [ (k,v) for k,v in fields if k==field]
        return fields[0]
    return fields


def set_annotations(tree, annotations, tree_node_labels='label'):
    if isinstance(tree, dict):
        t = tree['tree1']
    else:
        t = tree

    for n in t.traverse_levelorder(leaves=True, internal=True):
        
        try:
            if hasattr(n,'node_params'):
                id = get_node_params(n.node_params, field=tree_node_labels)[1] if not n.is_leaf() else n.label
                for field in list(annotations.columns)[1:]:
                    val = ''.join(annotations.loc[annotations['NODE_ID']==id][field].astype(str).values)
                    param = field+'="'+val+'"'
                    if n.node_params:
                        n.node_params+=','+param
                    else:
                        n.node_params=param
        except ValueError:
            print("Unable to match annotation node IDs to tree nodes. Make sure tree has node IDs that correspond with the input annotation file")
    return tree

def merge_trees(trees):
    
    if isinstance(trees[0], dict):
        main_tree = trees[0]['tree1']
    else:
        main_tree = trees[0]
    for n in main_tree.traverse_levelorder(leaves=True, internal=True):
        # get leaves of the current node
        leaves = [ l.get_label()for l in n.traverse_leaves()]
        # get corresponding node in the other trees and add their annotations
        for tid, tree in enumerate(trees[1:],start=1):
            alt_node = tree['tree1'].mrca(leaves) if isinstance(tree, dict) else tree.mrca(leaves)
            if n.get_edge_length() != alt_node.get_edge_length():
                if not hasattr(n,'node_params'):
                    n.node_params=""
                if "height" not in ''.join(n.node_params):
                    # if there's are no height in node params yet
                    e = 'height='+str(alt_node.get_edge_length())
                    if len(n.node_params)>0:
                        n.node_params+=','+e
                    else:
                        n.node_params=e
                else:
                    # there is already height in node params
                    n_height = get_node_params(n.node_params, 'height')[1]
                    if (n_height != str(alt_node.get_edge_length())) and (alt_node.get_edge_length() is not None) :
                        # new tree has a different height
                        e = 'height'+str(tid)+"="+str(alt_node.get_edge_length())
                        if n.node_params:
                            n.node_params+=','+e
                        else:
                            n.node_params=e
            if n.node_params == alt_node.node_params:
                continue
            else:
                n_params = n.node_params.strip("&").split(",")
                alt_params = alt_node.node_params.strip("&").split(",")
                for param in alt_params:
                    if param not in n_params:
                        if n.node_params:
                            n.node_params+=','+param
                        else:
                            n.node_params=param
            
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


def get_annotations(tree, node_key='label'):
    
    t = tree
    """
    labels = set()
    # scan for all node labels
    for n in t.traverse_levelorder(leaves=True, internal=True):
        n_params = n.node_params
        nid=n_params.strip('"').strip("&").node_params.split(",")[0].split("=")[1]
        
        labels.add(keys)
    """
    annot_dict = dict({'node_id': [],
                       'labels': [],
                       'values': []
                       })
    for n in t.traverse_levelorder(leaves=True, internal=True):
        n_params = n.node_params
        key, val = zip(*get_node_params(n_params))
        key = list(key)
        val = list(val)
        if (node_key in key):
            # internal nodes
            nid = val.pop(key.index(node_key))
            key.pop(key.index(node_key))
        elif n.is_leaf():
            # leaf nodes
            nid = n.label
        elif not n.label:
            # internal nodes
            n.set_label(nid)
        else:
            print(f"Warning: No labels found in label ({n.label}) or param ({n.node_params})")
        

        if len(key)==0:
            annot_dict['node_id'].append(nid)
            annot_dict['labels'].append("")
            annot_dict['values'].append("")
        else:
            annot_dict['node_id'].extend([nid]*(len(key)))
            annot_dict['labels'].extend(key)
            annot_dict['values'].extend(val)
    df = pd.DataFrame(annot_dict)
    nodes = np.unique(df['node_id'].values)
    df['idx']=[ int(np.where(nodes==nid)[0][0]) for nid in df['node_id']]
    df = df.drop_duplicates().reset_index()
    annot_df = pd.pivot(df,  index='node_id', columns=['labels'], values='values').reset_index()
    
    return annot_df