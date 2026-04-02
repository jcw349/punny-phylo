import argparse
import treeswift as ts
import os
import pathlib as p
from os.path import isfile
import pandas as pd


def rename_tips(tree, rename_dict):
    for node in tree.traverse_preorder():
        if node.is_leaf():
            if node.label in rename_dict:
                node.label = rename_dict[node.label]
    return tree


def args():
    parser = argparse.ArgumentParser(description="Read a Newick tree using treeswift to rescale tree by clock rate.")
    parser.add_argument("-t","--treefile", help="Path to the Newick tree file")
    parser.add_argument('-r', '--rename', required=True, type=str, help="Comma separated list of names to rename (csv)")
    parser.add_argument("-d","--output_dir", type=str, default=".", help="Output directory (default: current directory)")
    parser.add_argument("-o","--output_prefix", type=str, default="scaled_tree", help="Output file prefix (default: 'scaled_tree')")
    args = parser.parse_args()

    tree = ts.read_tree_newick(args.treefile)

    if isfile(args.rename):
        print("\nRenaming tips")
        renameDict = pd.read_csv(args.rename, sep=',', header=0, names=["old","new"]).set_index("old").squeeze().to_dict()
        tree = rename_tips(tree, renameDict)

    # create output directory if it doesn't exist
    try:
        os.makedirs(args.output_dir, exist_ok=True)
    except IsADirectoryError:
        print("Unable to create output directory: "+ args.output_dir, args.output_pref)
                
    # Save the updated tree (replace 'updated_tree.nwk' with your desired output file)
    tree.write_tree_newick(args.output_dir + "/"+ args.output_prefix + ".nwk")

if __name__ == "__main__":
    args()