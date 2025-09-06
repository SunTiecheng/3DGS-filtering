import numpy as np
import pandas as pd
import os
import argparse

# Function to read PLY file and separate header and data
def read_ply(file_path):
    """Read PLY file and separate header and data."""
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

# Function to normalize coordinates and voxelize the data while keeping the IDs
def normalize_and_voxelize(data, voxel_resolution):
    """Normalize coordinates and voxelize the data while retaining IDs."""
    # Extract XYZ coordinates and ID column
    xyz = data.iloc[:, :3].values
    attributes = data.iloc[:, 3:-1].values  # Other attributes
    ids = data.iloc[:, -1].values.astype(int)  # Ensure IDs are integers

    # Normalize to [0, 1] range
    xyz_min = xyz.min(axis=0)
    xyz_max = xyz.max(axis=0)
    xyz_normalized = (xyz - xyz_min) / (xyz_max - xyz_min)

    # Scale to voxel grid
    voxel_grid_coords = (xyz_normalized * voxel_resolution).astype(int)

    # Concatenate voxel coordinates, attributes, and IDs
    voxelized_data = np.hstack((voxel_grid_coords, attributes, ids.reshape(-1, 1)))
    return voxelized_data

# Function to write the processed voxelized data to a PLY file
def write_ply(output_path, header, voxelized_data):
    """Write processed voxelized data to a PLY file."""
    with open(output_path, 'w') as f:
        for line in header:
            f.write(line)
        for row in voxelized_data:
            # Write each column of data, ensuring IDs are integers
            row = list(row)
            row[:-1] = map(str, row[:-1])  # Convert other columns to string
            row[-1] = str(int(row[-1]))   # Ensure ID is integer
            f.write(' '.join(row) + '\n')

# Set up command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Voxelize point cloud data and save to a new PLY file.")
    parser.add_argument('--input_dir', type=str, required=True, help="Directory containing input PLY files")
    parser.add_argument('--output_dir', type=str, required=True, help="Directory to save voxelized PLY files")
    parser.add_argument('--voxel_resolution', type=int, default=7168, help="Resolution of the voxel grid")
    return parser.parse_args()

# Main function
def main():
    args = parse_args()

    # Common input directory prefix
    input_prefix = args.input_dir
    output_dir = args.output_dir
    voxel_resolution = args.voxel_resolution

    # List of input PLY file suffixes
    file_suffixes = [
        'xyz_ascii.ply', 'nxyz_ascii.ply', 'fdc012_ascii.ply', 'fre012_ascii.ply', 'fre345_ascii.ply',
        'fre678_ascii.ply', 'fre91011_ascii.ply', 'fre121314_ascii.ply', 'fre151617_ascii.ply', 'fre181920_ascii.ply',
        'fre212223_ascii.ply', 'fre242526_ascii.ply', 'fre272829_ascii.ply', 'fre303132_ascii.ply', 'fre333435_ascii.ply',
        'fre363738_ascii.ply', 'fre394041_ascii.ply', 'fre424344_ascii.ply', 'fre4344op_ascii.ply', 'scale012_ascii.ply',
        'rot012_ascii.ply', 'rot123_ascii.ply'
    ]

    # Process each file
    for file_suffix in file_suffixes:
        input_ply_path = os.path.join(input_prefix, file_suffix)
        output_ply_path = os.path.join(output_dir, file_suffix.replace('.ply', '_voxel.ply'))

        # Read, voxelize, and write output
        header, data = read_ply(input_ply_path)
        voxelized_data = normalize_and_voxelize(data, voxel_resolution)
        write_ply(output_ply_path, header, voxelized_data)

        print(f"Voxelized point cloud saved to: {output_ply_path}")

if __name__ == "__main__":
    main()
