# punny-phylo
Python Utilities for Newick and Nexus Yare Phylogenetic tree editing

# Dependencies
- [treeswift](https://github.com/niemasd/TreeSwift?tab=readme-ov-file)


# Usage
## Newick:
### rename_tips
Rename **Newick** taxa labels in tree [-t] based on tab-delimited file [-r] with headers where the first column contains the original taxa labels and column two contains the new labels.
```
python rename_tips.py \
    -t "/path/to/tree/file" \
    -r "/path/to/tsv/rename/file" \
    -d "/path/to/output/directory/" \
    -o "output_filename_prefix"
```
Output </path/to/output/directory>/<output_filename_prefix>.nwk

## Nexus
### merge_nexus_annot
Merges annotations from two **Nexus** files.
```
python merge_nexus_annot.py \
    -t "/path/to/file1" "/path/to/file2" ... \
    -d "/path/to/output/directory/" \
    -o "output_filename.nexus.tree"
```
