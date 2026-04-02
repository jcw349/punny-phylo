# punny-phylo
Python Utilities for Newick and Nexus Yare Phylogenetic tree editing

# Dependencies
Install dependencies first before running punny-phylo tools.
- [treeswift](https://github.com/niemasd/TreeSwift?tab=readme-ov-file)
- [pandas](https://pandas.pydata.org/)

# Usage
## Newick:
### rename_tips
Rename **Newick** taxa labels in tree [-t] based on tab-delimited file [-r] with headers where the first column contains the original taxa labels and column two contains the new labels.
Input: <tree_file>.nwk
Output: <path_to_output_directory>/<output_filename_prefix>.nwk
```
python rename_tips.py \
    -t "/path/to/tree/file" \
    -r "/path/to/tsv/rename/file" \
    -d "/path/to/output/directory/" \
    -o "output_filename_prefix"
```

### rescale_branches
Rescale the **Newick** branch length by the clock rate (`branch_length`/`clock_rate`)
Input: <tree_file>.nwk
Output: <path_to_output_directory>/<output_filename_prefix>.nwk
```
python rescale_branches.py \
    -t "/path/to/tree/file" \
    -r [clock_rate, default=6E-5] \
    -d "/path/to/output/directory/" \
    -o "output_filename_prefix"
```

### reshape_tree
Reshape **Newick** tree by collapsing or resolving polytomies
Input: <tree_file>.nwk
Param: -c [float] or -p [bool] -- collapse nodes below [float] value OR resolve polytomies
Output: <path_to_output_directory>/<output_filename_prefix>.nwk
```
python reshape_tree.py \
    -t "/path/to/tree/file" \
    [-c [max_branch_length_to_collapse]] OR [-p [True]] \
    -d "/path/to/output/directory/" \
    -o "output_filename_prefix"
```

## Nexus
### merge_nexus_annot
Merges annotations from two **Nexus** files.
```
python merge_nexus_annot.py \
    -t "/path/to/file1" "/path/to/file2" ... \
    -d "/path/to/output/directory/" \
    -o "output_filename.nexus.tree"
```
