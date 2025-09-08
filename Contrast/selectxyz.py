import os
import argparse

# Function to extract xyz coordinates and add an ID to a PLY file
def extract_xyz_with_id(input_ply, output_ply):
    """
    Extract XYZ coordinates and add an ID to a PLY file.

    :param input_ply: Path to the input PLY file
    :param output_ply: Path to save the output PLY file with added ID
    """
    with open(input_ply, 'r') as f:
        lines = f.readlines()

    header = []
    data_start_idx = 0
    xyz_props = ['property float x', 'property float y', 'property float z']

    # Process header: keep necessary structure + x, y, z declaration
    for i, line in enumerate(lines):
        header.append(line)
        if line.strip() == 'end_header':
            data_start_idx = i + 1
            break

    # Construct new header, keeping only x, y, z and adding id field
    new_header = []
    for line in header:
        if line.startswith('property'):
            if line.strip() in xyz_props:
                new_header.append(line)
        elif line.startswith('element vertex'):
            point_count = int(line.strip().split()[-1])
            new_header.append(line)
        elif line.strip() == 'end_header':
            new_header.append('property int id\n')  # Add id field
            new_header.append('end_header\n')
        else:
            new_header.append(line)

    # Process data: extract xyz and add id
    data_lines = lines[data_start_idx:]
    output_data = []
    for idx, line in enumerate(data_lines):
        cols = line.strip().split()
        x, y, z = cols[:3]
        id_val = idx + 1  # Start numbering from 1
        output_data.append(f"{x} {y} {z} {id_val}\n")

    # Write to the new file
    with open(output_ply, 'w') as f:
        f.writelines(new_header)
        f.writelines(output_data)

    print(f"Processing complete, saved to {output_ply}")

# Set up command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Extract XYZ coordinates and add ID to a PLY file.")
    parser.add_argument('--input_ply', type=str, required=True, help="Path to the input PLY file")
    parser.add_argument('--output_ply', type=str, required=True, help="Path to save the output PLY file")
    return parser.parse_args()

# Main function
def main():
    # Parse command line arguments
    args = parse_args()

    # Extract XYZ and add ID to the PLY file
    extract_xyz_with_id(args.input_ply, args.output_ply)

if __name__ == "__main__":
    main()
