# punny-phylo
Python Utilities for Newick and Nexus Yare Phylogenetic tree editing

# Dependencies
Install dependencies first before running punny-phylo tools.
- [treeswift](https://github.com/niemasd/TreeSwift?tab=readme-ov-file)
- [pandas](https://pandas.pydata.org/)

# Usage
## Merge annotated trees:
Merges annotations from two or more **NEXUS** or **NEWICK** files.
```
python ./punny_phylo.py \
    -t "/path/to/file1" "/path/to/file2" ... \
    -m \                                                #--  run the merge function
    -d "/path/to/output/directory/" \
    -o "output_filename.nexus.tree" \
    -O 'nexus'                                          #--  output file in 'NEXUS" format
```

## Rename tree tips:

... Testing in Progresss ...

## Rename rescale branch length:

... Testing in Progresss ...

## Rename reshape tree topology:

... Testing in Progresss ...
