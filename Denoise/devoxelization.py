import os
import numpy as np
import pandas as pd
import argparse

# Function to get the min and max coordinates from the point cloud file
def get_min_max_coordinates(file_path):
    """Get the minimum and maximum coordinates from the point cloud file."""
    with open(file_path, 'r') as f:
        data_start = 0
        for i, line in enumerate(f):
            if line.strip() == "end_header":
                data_start = i + 1
                break
    data = pd.read_csv(file_path, skiprows=data_start, sep=' ', header=None)
    xyz = data.iloc[:, :3].values
    xyz_min = xyz.min(axis=0)
    xyz_max = xyz.max(axis=0)
    return xyz_min, xyz_max

# Function to read the voxelized PLY file and separate the header and data parts
def read_voxelized_ply(file_path):
    """Read the voxelized PLY file and separate the header and data parts."""
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

# Function to perform devoxelization, converting voxel grid coordinates back to approximate original coordinates
def devoxelize(data, voxel_resolution, original_min, original_max):
    """Devoxelize the data by converting voxel grid coordinates back to the original coordinate range."""
    voxel_coords = data.iloc[:, :3].values
    attributes = data.iloc[:, 3:-1].values  # Other attributes
    ids = data.iloc[:, -1].values          # Point IDs

    # Normalize the coordinates to the range [0, 1]
    normalized_coords = voxel_coords / voxel_resolution

    # Convert back to the original coordinate range
    original_coords = normalized_coords * (original_max - original_min) + original_min

    # Concatenate the restored coordinates, attributes, and IDs
    restored_data = np.hstack((original_coords, attributes, ids.reshape(-1, 1)))
    return restored_data

# Function to save the devoxelized data back to a PLY file
def write_devoxelized_ply(output_path, header, restored_data):
    """Save the devoxelized data back to a PLY file, keeping the same header as the input file."""
    with open(output_path, 'w') as f:
        for line in header:
            f.write(line)
        for row in restored_data:
            row = list(row)
            row[:-1] = map(str, row[:-1])  # Keep coordinates and attributes as strings
            row[-1] = str(int(row[-1]))   # Force the ID to be an integer
            f.write(' '.join(row) + '\n')

# Function to process each pair of file paths, executing the devoxelization
def process_files(original_ply_path, voxelized_ply_path, output_ply_path, voxel_resolution):
    """Process each pair of file paths and perform devoxelization."""
    # Get the min and max coordinates from the original point cloud
    xyz_min, xyz_max = get_min_max_coordinates(original_ply_path)
    print(f"Processing: {original_ply_path} -> {voxelized_ply_path} -> {output_ply_path}")
    print("Min coordinates (xyz_min):", xyz_min)
    print("Max coordinates (xyz_max):", xyz_max)

    # Read the voxelized point cloud file
    header, voxel_data = read_voxelized_ply(voxelized_ply_path)

    # Perform the devoxelization operation
    restored_data = devoxelize(voxel_data, voxel_resolution, xyz_min, xyz_max)

    # Save the devoxelized point cloud file
    write_devoxelized_ply(output_ply_path, header, restored_data)
    print(f"Devoxelized point cloud data saved to: {output_ply_path}")

# Set up command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Devoxelize point cloud files after voxelization.")
    parser.add_argument('--input_dir', type=str, required=True, help="Input directory path containing the original point cloud files")
    parser.add_argument('--voxelized_dir', type=str, required=True, help="Input directory path containing the voxelized point cloud files")
    parser.add_argument('--output_dir', type=str, required=True, help="Output directory path to save the devoxelized point cloud files")
    return parser.parse_args()

# Main function
def main():
    # Get command line arguments
    args = parse_args()

    # Common input directory prefix
    input_prefix = args.input_dir
    voxelized_prefix = args.voxelized_dir
    output_prefix = args.output_dir

    # List of file suffixes for original, voxelized, and output files
    file_suffixes = [
        'xyz_ascii.ply', 'fdc012_ascii.ply', 'fre012_ascii.ply', 'fre345_ascii.ply', 'fre678_ascii.ply',
        'fre91011_ascii.ply', 'fre121314_ascii.ply', 'fre151617_ascii.ply', 'fre181920_ascii.ply', 'fre212223_ascii.ply',
        'fre242526_ascii.ply', 'fre272829_ascii.ply', 'fre303132_ascii.ply', 'fre333435_ascii.ply', 'fre363738_ascii.ply',
        'fre394041_ascii.ply', 'fre424344_ascii.ply', 'fre4344op_ascii.ply', 'rot012_ascii.ply', 'rot123_ascii.ply',
        'scale012_ascii.ply'
    ]

    # Voxel grid resolution
    voxel_resolution = 7168

    # Process each file pair
    for file_suffix in file_suffixes:
        original_ply_path = os.path.join(input_prefix, file_suffix)
        voxelized_ply_path = os.path.join(voxelized_prefix, file_suffix.replace('.ply', '_voxel_re.ply'))
        output_ply_path = os.path.join(output_prefix, file_suffix.replace('.ply', '_voxeltopc.ply'))

        process_files(original_ply_path, voxelized_ply_path, output_ply_path, voxel_resolution)

if __name__ == "__main__":
    main()
