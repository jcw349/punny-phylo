# punny
Python Utilities for Newick and Nexus Yare Phylogenetic tree editing

# Dependencies
- [treeswift](https://github.com/niemasd/TreeSwift?tab=readme-ov-file)


# Usage
## merge_nexus_annot
Merges annotations from two Nexus files.
```
python merge_nexus_annot.py \
    -t "/path/to/file1" "/path/to/file2" ... \
    -d "/path/to/output/directory/" \
    -o "output_filename.nexus.tree"
```
