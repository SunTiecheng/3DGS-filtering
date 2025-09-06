import os
import numpy as np
import pandas as pd
from tqdm import tqdm  # Import progress bar library
import argparse

# Function to read the PLY file and separate the header and data
def read_ply(file_path):
    """Read the PLY file and separate the header and data parts"""
    with open(file_path, 'r') as f:
        header = []
        data_start = 0
        for i, line in enumerate(f):
            header.append(line)
            if line.strip() == "end_header":
                data_start = i + 1
                break
        data = pd.read_csv(file_path, skiprows=data_start, sep=' ', header=None)
    return header, data

# Function to add a unique ID to each row of the data
def add_unique_id(data):
    """
    Add a unique ID to each row.
    :param data: Input DataFrame
    :return: DataFrame with added ID
    """
    data['ID'] = range(len(data))  # Add ID column starting from 0
    return data

# Function to filter the columns and update the header
def filter_ply_columns(header, data, columns_to_keep):
    """
    Filter specified columns and update the header information.
    :param header: Original header
    :param data: Data part
    :param columns_to_keep: List of columns to keep
    :return: Updated header and filtered data
    """
    # Add the unique ID column, ensuring ID is the last column
    data = add_unique_id(data)
    columns_to_keep = columns_to_keep + [-1]  # Include ID column index
    filtered_data = data.iloc[:, columns_to_keep]

    # Update the header
    updated_header = []
    property_lines = []
    keep_index = 0
    for line in header:
        if line.startswith("property"):
            if keep_index in columns_to_keep:
                property_lines.append(line)
            keep_index += 1
        elif line.startswith("element vertex"):
            element_vertex_line = f"element vertex {len(filtered_data)}\n"
            updated_header.append(element_vertex_line)
        elif line.startswith("format") or line.startswith("ply") or line.startswith("end_header"):
            updated_header.append(line)
        else:
            updated_header.append(line)

    # Add ID column description to header
    property_lines.append("property int ID\n")
    updated_header = updated_header[:3] + property_lines + ["end_header\n"]

    return updated_header, filtered_data

# Function to write the filtered data to a PLY file
def write_ply(output_path, header, filtered_data):
    """Save the filtered data to a PLY file"""
    with open(output_path, 'w') as f:
        for line in header:
            f.write(line)
        for row in filtered_data.itertuples(index=False):
            f.write(' '.join(map(str, row)) + '\n')

# Set up command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Process PLY files and filter columns.")
    parser.add_argument('--input', type=str, required=True, help="Input PLY file path")
    parser.add_argument('--output_dir', type=str, required=True, help="Output directory path")
    return parser.parse_args()

# Main function
def main():
    # Get command line arguments
    args = parse_args()

    # Define the columns to keep and their corresponding output file names
    columns_to_keep_list = [
        ([0, 1, 2], "xyz_ascii"),  # x, y, z
        ([3, 4, 5], "nxyz_ascii"),  # nxyz
        ([6, 7, 8], "fdc012_ascii"),  # fdc012
        ([9, 10, 11], "fre012_ascii"), # fre012~
        ([12, 13, 14], "fre345_ascii"),
        ([15, 16, 17], "fre678_ascii"),
        ([18, 19, 20], "fre91011_ascii"),
        ([21, 22, 23], "fre121314_ascii"),
        ([24, 25, 26], "fre151617_ascii"),
        ([27, 28, 29], "fre181920_ascii"),
        ([30, 31, 32], "fre212223_ascii"),
        ([33, 34, 35], "fre242526_ascii"),
        ([36, 37, 38], "fre272829_ascii"),
        ([39, 40, 41], "fre303132_ascii"),
        ([42, 43, 44], "fre333435_ascii"),
        ([45, 46, 47], "fre363738_ascii"),
        ([48, 49, 50], "fre394041_ascii"),
        ([51, 52, 53], "fre424344_ascii"),  # ~fre424344
        ([52, 53, 54], "fre4344op_ascii"),  # fre4344opacity
        ([55, 56, 57], "scale012_ascii"), # scale012
        ([58, 59, 60], "rot012_ascii"),   # rot012
        ([59, 60, 61], "rot123_ascii")    # rot123
    ]

    # Read input PLY file
    header, data = read_ply(args.input)

    # Process and filter columns, then save them to the output directory
    for columns_to_keep, name_suffix in tqdm(columns_to_keep_list, desc="Processing columns", ncols=100):
        updated_header, filtered_data = filter_ply_columns(header, data, columns_to_keep)
        output_ply = os.path.join(args.output_dir, f"{name_suffix}.ply")  # Output file path with custom name
        write_ply(output_ply, updated_header, filtered_data)
        print(f"PLY file with ID added saved to: {output_ply}")

if __name__ == '__main__':
    main()
