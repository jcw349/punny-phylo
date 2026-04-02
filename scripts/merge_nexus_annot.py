import argparse
import os
import treeswift as ts

def arguments():
    parser = argparse.ArgumentParser(description="Read a Nexus tree using treeswift to merge trees with annotations.")
    parser.add_argument("-t","--treefiles", nargs="+", type=str, help="Paths to the Nexus tree files")
    parser.add_argument("-d","--output_dir", type=str, default=".", help="Output directory (default: current directory)")
    parser.add_argument("-o","--output_filename", type=str, default="merged_tree.nexus.tree", help="Output filenames (default: 'merged_tree.nexus.tree')")
    args = parser.parse_args()
    
    return args

def get_files(input_files):
    trees = []
    for file in input_files:
        if os.path.isfile(file):
            tf = ts.read_tree(file, schema="nexus")
            trees.append(tf)
        else:
            print(f"Warning: {file} is not a valid filepath and will be skipped.")
    return trees


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


def write_tree(tree, output_dir, output_filename):
    oPath = os.makedirs(output_dir, exist_ok=True)
    if not os.path.exists(output_dir):
        print(f"Output directory {output_dir} does not exist. Creating directory.")
        os.mkdir(oPath, parents=True, exist_ok=True)
    try:
        tree['tree1'].write_tree_nexus(output_dir + "/"+ output_filename)
        print(f"Tree successfully written to {output_dir}/{output_filename}")
    except Exception as e:
        print(f"Error writing tree to {output_dir}/{output_filename}: {e}")


if __name__ == "__main__":
    args = arguments()
    tree_files = get_files(args.treefiles)
    merged_tree = merge_trees(tree_files)
    write_tree(merged_tree, args.output_dir, args.output_filename)

