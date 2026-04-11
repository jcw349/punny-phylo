import argparse
import scripts.punny_io as pio

def arguments():
    parser = argparse.ArgumentParser(description="Read a tree file using treeswift to merge trees with annotations.")
    parser.add_argument("-t","--treefiles", nargs="+", type=str, help="Paths to the tree files")
    parser.add_argument("-d","--output_dir", type=str, default=".", help="Output directory (default: current directory)")
    parser.add_argument("-o","--output_filename", type=str, default="merged_tree.nexus.tree", help="Output filenames (default: 'merged_tree.nexus.tree')")
    parser.add_argument("-O","--output_type", choices=["nexus", "newick"], default=None, help="Indicate the output file type of the tree file. [default: same as input file type]")       
    # merge parser
    mrg = parser.add_argument_group(title="Merge options for annotated trees", description="Options for merging NEXUS annotated trees")
    mrg.add_argument("-m","--merge_annot", action="store_true", help="Merge NEXUS trees with annotations. Requires multiple tree files as input. [example: --treefiles tree1.nexus tree2.nexus]")
    mrg.add_argument('-N',"--node_label", type=str, default="label", help="Provide node ID label (Default=label)")
    #mrg.add_argument('-D',"--get_dates", nargs="+", type=bool, default=[False], help="Provide node ID label (Default=[False])")
    mrg.add_argument('-a',"--add_annotations", type=str, default=None, help="Comma separated filepaths to tab delimited tables of annotations to add to the merged tree, where the first column is [Node_ID] and all other columns will be added, index of table matches the index of the trees. [default: None]")
    mrg.add_argument('-A',"--annotation_table", action="store_true", default=False, help="Export tab delimited table of nodes and their annotations")
    
    
    # rename parser
    rn = parser.add_argument_group(title="Rename options", description="Options for renaming taxa labels in tree file(s). Required if --rename is selected.")
    #rn.add_argument("--rename_tips", action="store_true", help="Rename taxa labels in the tree file. Requires rename TSV file as input.")
    rn.add_argument("-r","--rename_table", type=str, default=None, help="Path to the TSV rename table file. Required if --rename is selected.")
    rn.add_argument("-H","--has_header", type=bool, default=True, help="Indicate whether input rename table has a header. [default: True]")
    
    # rescale branches
    
    rs = parser.add_argument_group(title="Rescale branch length options")
    comp = rs.add_mutually_exclusive_group()
    comp.add_argument("--dist_to_time", action="store_true", help="Rescale branch lengths distance to divergence time by a given clock rate (branch_length / clock_rate). Cannot use it with --time_to_dist.")
    comp.add_argument("--time_to_dist", action="store_true", help="Rescale divergence time to branch length distance by given clock rate (divergence_time * clock_rate). Cannot use it with --dist_to_time.")
    rs.add_argument("-c","--clock_rate", type=float, default=6E-5, help="Rescale branch length to divergence time. Cannot use with (default: 6E-5)")
    
    rsh = parser.add_argument_group(title="Reshape tree options", description="Options for reshaping tree.")
    pt = rsh.add_mutually_exclusive_group()
    pt.add_argument('-C', '--collapse_polytomies', type=float, default=None, help="Collapse internal branches (not terminal branches) with length less than or equal to threshold. A branch length of None will not be performed. Cannot use it with --resolve_polytomies [default=None]")
    pt.add_argument('-p', '--resolve_polytomies', type=bool, default=False, help="Resolve internal branches with 0 dist into polytomies with length less than or equal to threshold. Cannot use it with --collapse_polytomies [default=False]")
    rsh.add_argument("-R", "--reroot_tree", type=str, default=None, help="Reroot tree with specified outgroup.")
    rsh.add_argument("-R_l", "--root_length", type=float, default=None, help="The distance up the specified edge at which to reroot this Tree. If 0 or None, reroot at the node (not on the incident edge)")
    rsh.add_argument("-R_s", "--root_support", type=bool, default=False, help="True if internal node labels represent branch support values, otherwise False. [default: False]")
    args = parser.parse_args()

    return args


def run_add_annotations(trees, annotations, tree_node_labels='label'):
    from scripts.punny_utils import set_annotations

    annots = [ pio.read_table(fp, skip_rows=1) for fp in annotations.split(",") ]
    trees = [ set_annotations(trees[tid], annot) if annot is not None else trees[tid] for tid, annot in enumerate(annots) ]
    return trees


def run_merge(trees, tree_type):
    # if there are less than 2 input tree files, print an error message and exit
    if len(trees) < 2:
        print("Error: Attempting to merge trees, but less than 2 tree files were provided.")
        exit(10)
    if len(set(tree_type)) > 1:
        print("Warning: Attempting to merge trees of different file types. Multiple input file types are not recommended, but will proceed.")
    
    from scripts.punny_utils import merge_trees
    merged_tree = merge_trees(trees)
    return merged_tree


def run_rename(trees, rename_dict, has_header):
    # check for rename table file, print error message and exit if not provided
    if not rename_dict:
        print("Error: Attempting to rename tips, but no rename table file provided.")
        exit(1)
    rename_dict = pio.read_table_as_dict(rename_dict, has_header)
    
    from scripts.punny_utils import rename_tips
    logs = dict({"function": [],
                 "log": []})
    for idx, tree in enumerate(trees):
        trees[idx], log = rename_tips(tree, rename_dict)
        logs['function'].append(f"rename_tree_{idx+1}")
        logs['log'].append(log)
    return trees, logs


def run_branch_rescale(trees, clock_rate, oper="dist_to_time"):
    if not clock_rate:
        print("Error: Attempting to rescale branches, but no clock rate provided.")
        exit(20)
    from scripts.punny_utils import rescale_branches
    op = True if oper == "dist_to_time" else False
    for idx, tree in enumerate(trees):
        trees[idx] = rescale_branches(tree, clock_rate, to_time=op)
    return trees


def run_collapse(trees, threshold):
    if not threshold:
        print("Error: Attempting to collapse branches, but no threshold provided.")
        exit(30)
    from scripts.punny_utils import collapse_polytomies
    
    for idx, tree in enumerate(trees):
        trees[idx] = collapse_polytomies(tree, threshold)
    return trees


def run_resolve(trees):
    from scripts.punny_utils import resolve_polytomies
    for idx, tree in enumerate(trees):
        trees[idx] = resolve_polytomies(tree)
    return trees


def run_reroot(trees, root, length, support):
    if not isinstance(root):
        print("Error: must provide the root node or leaf node to root the tree.")
        exit(32)
    from scripts.punny_utils import reroot_tree
    for idx, tree in enumerate(trees):
        tree[idx] = reroot_tree(tree, root, length, support)


def get_node_annotations(trees, node_id_key='label'):
    from scripts.punny_utils import get_annotations
    tree_annot =  [ get_annotations(tree, node_key=node_id_key) for tree in trees]
    return tree_annot

def write_output(trees, output_dir, output_filename, output_type, table_list):
    # write output tree file(s)
    if len(trees) > 1:
        output_filenames = ["".join(args.output_filename.rsplit(".", 1)[:-1])+"_{i+1}.tree" for i in range(len(trees))]
        for i, tree in enumerate(trees):
            pio.write_tree_file(tree, output_dir, output_filenames, output_type[i])
    else:
        pio.write_tree_file(trees[0], output_dir, output_filename, output_type)

    if table_list:
        for ext, t in table_list:
            output_filename = "_".join(["".join(args.output_filename.rsplit(".", 1)[:-1]),ext]) if "." in args.output_filename else "_".join([args.output_filename,ext])
            pio.export_file(t, output_dir, output_filename)


def run_functions(args):
    tree_files, input_types = pio.get_tree_file(args.treefiles)
    logs = dict()


    if args.add_annotations:
        tree_files = run_add_annotations(tree_files, args.add_annotations, args.node_label)


    if args.merge_annot:
        # merge function is selected, return type is a single tree
        tree_files = [run_merge(tree_files, input_types)]


    if args.rename_table:
        # rename function is selected
        tree_files, log = run_rename(tree_files, args.rename_table, args.has_header)
        logs.update(log)

    # one of the rescaling functions are selected
    if args.dist_to_time:
        tree_files = run_branch_rescale(tree_files, args.clock_rate, oper='dist_to_time')
    elif args.time_to_dist:
        tree_files = run_branch_rescale(tree_files, args.clock_rate, oper='time_to_dist')

    # one of the reshaping function is selected
    if args.collapse_polytomies:
        tree_files = run_collapse(tree_files, args.collapse_polytomies)
    elif args.resolve_polytomies:
        tree_files = run_resolve(tree_files)

    if args.reroot_tree:
        tree_files = run_reroot(tree_files, args.reroot_tree, args.root_length, args.root_support)

    if args.annotation_table:
        import pandas as pd
        annot_df = get_node_annotations(tree_files, node_id_key=args.node_label)
        exp_tables = [('annotation.txt',annot_df[0])]

    # check output file type
    if args.output_type is None:
        if len(tree_files)==1 and (len(tree_files) == len(set(input_types))):
            output_types = list(set(input_types))[0]
        elif len(tree_files) == len(input_types):
            output_types = input_types
        elif len(set(input_types)) > 1:
            print("Warning: Multiple input file types detected and no output file type specified. Attempting to write different number of trees. Output file type will be set to the first input file type.")
            output_types = input_types[0] * len(tree_files)
        elif len(tree_files)==1:
            print("Warning: Only writing 1 tree file with multiple input file types and no output file type specified. Output file type will be set to the first input file type.")
            output_types = input_types[0]
    else:
        output_types = args.output_type
    
    if len(logs)>0:
        exp_tables.append(('logs',logs))

    # write output
    write_output(tree_files, args.output_dir, args.output_filename, output_types, exp_tables)


if __name__ == "__main__":
    args = arguments()
    run_functions(args)
    
    