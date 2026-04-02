import argparse
import treeswift as ts

def args():
    parser = argparse.ArgumentParser(description="Read a Newick tree using treeswift to rescale tree by clock rate.")
    parser.add_argument("-t","--treefile", help="Path to the Newick tree file")
    parser.add_argument("-r","--clock_rate", type=float, default=6E-5, help="Clock rate to scale branch lengths (default: 6E-5)")
    parser.add_argument("-d","--output_dir", type=str, default=".", help="Output directory (default: current directory)")
    parser.add_argument("-o","--output_prefix", type=str, default="scaled_tree", help="Output file prefix (default: 'scaled_tree')")
    args = parser.parse_args()

    tree = ts.read_tree_newick(args.treefile)
    for node in tree.traverse_preorder():
        if node.edge_length is not None:
            node.edge_length /= args.clock_rate
            
    # Save the updated tree (replace 'updated_tree.nwk' with your desired output file)
    tree.write_tree_newick(args.output_dir + "/"+ args.output_prefix + ".nwk")

if __name__ == "__main__":
    args()