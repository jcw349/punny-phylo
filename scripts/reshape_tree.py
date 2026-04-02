import argparse
import os
import treeswift as ts

def args():
    parser = argparse.ArgumentParser(description="Read a Newick tree using treeswift to collapse or resolve polytomies.")
    parser.add_argument("-t","--treefile", help="Path to the Newick tree file")
    parser.add_argument("-c","--collapse_polytomies", type=float, default=None, help="Collapse internal branches (not terminal branches) with length less than or equal to threshold. A branch length of None will not be performed [default=False]")
    parser.add_argument("-p","--resolve_polytomies", type=bool, default=False, help="Resolve internal branches with 0 dist into polytomies with length less than or equal to threshold. [default=False]")
    parser.add_argument("-d","--output_dir", type=str, default=".", help="Output directory (default: current directory)")
    parser.add_argument("-o","--output_prefix", type=str, default="reshaped_tree", help="Output file prefix (default: 'reshaped_tree')")
    args = parser.parse_args()
    
    oPath = os.makedirs(args.output_dir, exist_ok=True)
    if not args.output_dir:
        os.mkdir(oPath, parents=True, exist_ok=True)
    
    tree = ts.read_tree_newick(args.treefile)

    if args.collapse_polytomies:
        tree.collapse_short_branches(threshold=args.collapse_polytomies)

    if args.resolve_polytomies:
        tree.resolve_polytomies()
    # Save the updated tree (replace 'updated_tree.nwk' with your desired output file)
    tree.write_tree_newick(args.output_dir + "/"+ args.output_prefix + ".nwk")

if __name__ == "__main__":
    args()
