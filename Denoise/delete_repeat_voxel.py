import re
import os
import argparse
from collections import defaultdict

# Function to read the PLY file and separate the header and data parts
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

# Function to detect and remove duplicates from the PLY file
def detect_and_remove_duplicates(ply_file, output_txt, output_ply):
    # Read the points from the PLY file
    points = []  # Store point coordinates (x, y, z)
    ids = []     # Store point IDs
    header_lines = []  # Store the PLY file header

    with open(ply_file, 'r') as file:
        header_ended = False
        for line in file:
            if header_ended:
                coordinates = re.findall(r"[-+]?\d*\.\d+|\d+", line)
                if len(coordinates) >= 4:  # At least x, y, z, and ID
                    points.append(tuple(map(float, coordinates[:3])))  # Extract (x, y, z)
                    ids.append(int(float(coordinates[3])))  # Extract ID, converting to int
            else:
                header_lines.append(line)
                if line.startswith("end_header"):
                    header_ended = True

    # Remove duplicates and retain the first occurrence of each point's ID
    unique_points = {}  # Store unique points and their corresponding IDs
    for i, point in enumerate(points):
        if point not in unique_points:
            unique_points[point] = ids[i]  # Record ID for the first occurrence

    # Save the deduplicated data
    with open(output_ply, 'w') as ply_out:
        # Update PLY header with correct vertex count
        for line in header_lines:
            if line.startswith("element vertex"):
                ply_out.write(f"element vertex {len(unique_points)}\n")
            else:
                ply_out.write(line)

        # Write the deduplicated points and IDs
        for point, id_val in unique_points.items():
            ply_out.write(f"{point[0]} {point[1]} {point[2]} {id_val}\n")

    # Save the duplicate point statistics to a TXT file
    with open(output_txt, 'w') as txt_file:
        txt_file.write("Duplicate point coordinates and their occurrence counts:\n")
        duplicates = len(points) - len(unique_points)
        txt_file.write(f"Total duplicate points: {duplicates}\n")

    print(f"Deduplicated PLY file saved as {output_ply}")
    print(f"Duplicate point statistics saved to: {output_txt}")

# Set up command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Remove duplicate points from a PLY file after voxelization.")
    parser.add_argument('--input_dir', type=str, required=True, help="Input directory path containing the PLY files")
    parser.add_argument('--output_dir', type=str, required=True, help="Output directory path to save the deduplicated PLY files")
    return parser.parse_args()

# Main function
def main():
    # Get command line arguments
    args = parse_args()

    # List of file suffixes to be appended to the common input directory
    input_files = [
        'xyz_ascii_voxel.ply',
        'fdc012_ascii_voxel.ply',
        'fre012_ascii_voxel.ply',
        'fre345_ascii_voxel.ply',
        'fre678_ascii_voxel.ply',
        'fre91011_ascii_voxel.ply',
        'fre121314_ascii_voxel.ply',
        'fre151617_ascii_voxel.ply',
        'fre181920_ascii_voxel.ply',
        'fre212223_ascii_voxel.ply',
        'fre242526_ascii_voxel.ply',
        'fre272829_ascii_voxel.ply',
        'fre303132_ascii_voxel.ply',
        'fre333435_ascii_voxel.ply',
        'fre363738_ascii_voxel.ply',
        'fre394041_ascii_voxel.ply',
        'fre424344_ascii_voxel.ply',
        'fre4344op_ascii_voxel.ply',
        'scale012_ascii_voxel.ply',
        'rot012_ascii_voxel.ply',
        'rot123_ascii_voxel.ply'
    ]

    # Process the files
    for file_suffix in input_files:
        input_ply = os.path.join(args.input_dir, file_suffix)
        file_name = file_suffix.replace('.ply', '')
        output_txt_path = os.path.join(args.output_dir, f"{file_name}_rp.txt")
        output_ply_path = os.path.join(args.output_dir, f"{file_name}_norp.ply")

        detect_and_remove_duplicates(input_ply, output_txt_path, output_ply_path)

if __name__ == '__main__':
    main()
