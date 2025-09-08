import argparse

def remove_points_by_id(ply_file, id_txt_file, output_ply_file):
    """
    Remove points from a PLY file based on a list of IDs provided in a text file.
    
    :param ply_file: Path to the input PLY file
    :param id_txt_file: Path to the text file containing the IDs of points to be removed
    :param output_ply_file: Path to save the output PLY file with the points removed
    """
    # Read the IDs to be removed
    with open(id_txt_file, 'r') as f:
        remove_ids = set(int(line.strip()) for line in f if line.strip())

    with open(ply_file, 'r') as f:
        lines = f.readlines()

    # Separate header and data part
    header = []
    data_start_index = 0
    for i, line in enumerate(lines):
        header.append(line)
        if line.strip() == 'end_header':
            data_start_index = i + 1
            break

    data_lines = lines[data_start_index:]

    # Process data: remove lines where the ID matches
    retained_data = []
    for line in data_lines:
        parts = line.strip().split()
        if len(parts) < 4:
            continue  # Skip empty lines or incorrectly formatted ones
        point_id = int(parts[-1])  # ID is in the last column
        if point_id not in remove_ids:
            retained_data.append(line)

    # Update vertex count in the header
    for i, line in enumerate(header):
        if line.startswith('element vertex'):
            header[i] = f"element vertex {len(retained_data)}\n"
            break

    # Save the new PLY file with filtered data
    with open(output_ply_file, 'w') as f:
        f.writelines(header)
        f.writelines(retained_data)

    print(f"Processing complete, {len(remove_ids)} points removed. Result saved to: {output_ply_file}")


# Set up command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Remove points from PLY file based on IDs.")
    parser.add_argument('--ply_file', type=str, required=True, help="Path to the input PLY file")
    parser.add_argument('--id_txt_file', type=str, required=True, help="Path to the text file containing IDs to remove")
    parser.add_argument('--output_ply_file', type=str, required=True, help="Path to save the output PLY file")
    return parser.parse_args()

# Main function
def main():
    # Parse command line arguments
    args = parse_args()

    # Call the function to remove points by ID
    remove_points_by_id(args.ply_file, args.id_txt_file, args.output_ply_file)

if __name__ == "__main__":
    main()
