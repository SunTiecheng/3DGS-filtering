import os
import pandas as pd
from functools import reduce
import argparse

# Function to read PLY file and separate header and data
def read_ply(file_path):
    """Read the PLY file and separate the header and data parts."""
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

# Function to write the data back to a PLY file, keeping ASCII format
def write_ply(file_path, header, data):
    """Write the data back to a PLY file, keeping ASCII format."""
    with open(file_path, 'w') as f:
        for line in header:
            f.write(line)
        for row in data.itertuples(index=False):
            f.write(' '.join(map(str, row)) + '\n')

# Set up command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Merge point cloud files based on ID.")
    parser.add_argument('--input_dir', type=str, required=True, help="Input directory path containing the PLY files")
    parser.add_argument('--output_path', type=str, required=True, help="Output file path to save the merged point cloud")
    return parser.parse_args()

# Main function
def main():
    # Get command line arguments
    args = parse_args()

    # Common input directory prefix
    input_prefix = args.input_dir

    # List of file suffixes for original PLY files
    file_suffixes = [
        'xyz_ascii_voxeltopc.ply', 'fdc012_ascii_voxeltopc.ply', 'fre012_ascii_voxeltopc.ply', 
        'fre345_ascii_voxeltopc.ply', 'fre678_ascii_voxeltopc.ply', 'fre91011_ascii_voxeltopc.ply',
        'fre121314_ascii_voxeltopc.ply', 'fre151617_ascii_voxeltopc.ply', 'fre181920_ascii_voxeltopc.ply',
        'fre212223_ascii_voxeltopc.ply', 'fre242526_ascii_voxeltopc.ply', 'fre272829_ascii_voxeltopc.ply',
        'fre303132_ascii_voxeltopc.ply', 'fre333435_ascii_voxeltopc.ply', 'fre363738_ascii_voxeltopc.ply',
        'fre394041_ascii_voxeltopc.ply', 'fre424344_ascii_voxeltopc.ply', 'opacity_ascii_voxeltopc.ply',
        'scale012_ascii_voxeltopc.ply', 'rot012_ascii_voxeltopc.ply', 'rot3_ascii_voxeltopc.ply'
    ]
    
    # Columns for each file, corresponding to the files in `file_suffixes`
    columns_list = [
        ['x', 'y', 'z', 'ID'], ['f_dc_0', 'f_dc_1', 'f_dc_2', 'ID'], ['f_rest_0', 'f_rest_1', 'f_rest_2', 'ID'],
        ['f_rest_3', 'f_rest_4', 'f_rest_5', 'ID'], ['f_rest_6', 'f_rest_7', 'f_rest_8', 'ID'], 
        ['f_rest_9', 'f_rest_10', 'f_rest_11', 'ID'], ['f_rest_12', 'f_rest_13', 'f_rest_14', 'ID'],
        ['f_rest_15', 'f_rest_16', 'f_rest_17', 'ID'], ['f_rest_18', 'f_rest_19', 'f_rest_20', 'ID'],
        ['f_rest_21', 'f_rest_22', 'f_rest_23', 'ID'], ['f_rest_24', 'f_rest_25', 'f_rest_26', 'ID'],
        ['f_rest_27', 'f_rest_28', 'f_rest_29', 'ID'], ['f_rest_30', 'f_rest_31', 'f_rest_32', 'ID'],
        ['f_rest_33', 'f_rest_34', 'f_rest_35', 'ID'], ['f_rest_36', 'f_rest_37', 'f_rest_38', 'ID'],
        ['f_rest_39', 'f_rest_40', 'f_rest_41', 'ID'], ['f_rest_42', 'f_rest_43', 'f_rest_44', 'ID'],
        ['opacity', 'ID'], ['scale_0', 'scale_1', 'scale_2', 'ID'], ['rot_0', 'rot_1', 'rot_2', 'ID'],
        ['rot_3', 'ID']
    ]

    # Read all files and set column names
    dataframes = []
    for file_suffix, columns in zip(file_suffixes, columns_list):
        file_path = os.path.join(input_prefix, file_suffix)
        _, data = read_ply(file_path)
        data.columns = columns
        dataframes.append(data)

    # Merge all dataframes based on 'ID'
    merged_data = reduce(lambda left, right: pd.merge(left, right, on='ID', how='inner'), dataframes)

    # Drop the 'ID' column
    merged_data = merged_data.drop(columns=['ID'])

    # Update header information
    updated_header = [
        "ply\n", "format ascii 1.0\n", f"element vertex {len(merged_data)}\n"
    ] + [f"property float {col}\n" for col in merged_data.columns] + ["end_header\n"]

    # Write the merged data to the output file
    write_ply(args.output_path, updated_header, merged_data)

    print(f"Merged point cloud saved to: {args.output_path}")

if __name__ == "__main__":
    main()
