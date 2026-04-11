import argparse
import os
import treeswift as ts
import pandas as pd
import json

def get_tree_file(input_file):
    trees = []
    types = []
    for file in input_file:
        if os.path.isfile(file):
            print(f"Reading file: {file}")
            try:
                f = ts.read_tree_newick(file)
                t = 'newick'
            except:
                f = ts.read_tree_nexus(file)
                t = 'nexus'
            #tf = ts.read_tree(file, schema=file_type)
            trees.append(f)
            types.append(t)
        else:
            print(f"Warning: {file} is not a valid filepath and will be skipped.")
    return trees, types
    

def read_table_as_dict(table_path, has_header=True):
    try:
        if os.path.isfile(table_path):
            print("\n Reading table file: " + table_path)
            
            h=0 if has_header else None
            rename_dict = pd.read_csv(table_path, sep='\t',
                                     header=h,
                                     names=["old","new"]).set_index("old").squeeze().to_dict()
            return rename_dict
    except FileNotFoundError:
        print("Error: The tree file does not exist.")
    except IOError:
        print("Error: Could not read the file")


def read_table(table_path, skip_rows=0):
    if os.path.exists(table_path):
        df = pd.read_csv(table_path, sep="\t", skiprows=skip_rows)
        df.columns = ['NODE_ID']+ list(df.columns)[1:]
        return df
    

def write_tree_file(tree, output_dir, output_filename, file_type):
    #oPath = os.makedirs(output_dir, exist_ok=True)
    if not os.path.exists(output_dir):
        print(f"Output directory {output_dir} does not exist. Creating directory.")
        os.makedirs(output_dir, exist_ok=True)
    try:
        if isinstance(tree, dict):
            t = tree['tree1']
        else:
            t = tree
        try:
            if file_type.lower() == "nexus":
                t.write_tree_nexus(output_dir + "/"+ output_filename)
                print(f"Tree successfully written to {output_dir}/{output_filename}")
            elif file_type.lower() == "newick":
                t.write_tree_newick(output_dir + "/"+ output_filename)
                print(f"Tree successfully written to {output_dir}/{output_filename}")
        except Exception as e:
            print(f"Error writing tree to {output_dir}/{output_filename}: {e}")
    except Exception as e:
        print(f"Error writing tree to {output_dir}/{output_filename}: {e}")


def export_file(data, output_dir, output_filename):
    if not os.path.exists(output_dir):
        print(f"Output directory {output_dir} does not exist. Creating directory.")
        os.makedirs(output_dir, exist_ok=True)
    try:
        filepath = os.path.join(output_dir,output_filename)
        if isinstance(data, dict):
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
                print(f"Successfully written json to {filepath}")
        elif isinstance(data, pd.DataFrame):
            data.to_csv(filepath, sep='\t', index=False)
            print(f"Successfully written table to {filepath}")
        else:
            print(f"Warning, unrecognized filetype: {data}")
    except Exception as e:
        print(f"Error writing output file to {filepath}: {e}")