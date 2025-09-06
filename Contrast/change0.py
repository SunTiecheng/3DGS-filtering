import os
import argparse

# Function to replace the normal vector values (nx, ny, nz) with zeros in a PLY file
def replace_normal_with_zero(ply_file, output_ply_file):
    """
    Replace the normal vector (nx, ny, nz) with zeros in the PLY file.
    
    :param ply_file: Path to the input PLY file
    :param output_ply_file: Path to save the output PLY file
    """
    # Check if the input file exists
    if not os.path.exists(ply_file):
        print(f"Error: The input file {ply_file} does not exist!")
        return

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

    # Replace the normal vector data (nx, ny, nz) with zero
    modified_data = []
    for line in data_lines:
        parts = line.strip().split()
        if len(parts) >= 5:
            parts[3] = '0'  # nx
            parts[4] = '0'  # ny
            parts[5] = '0'  # nz
        modified_data.append(' '.join(parts) + '\n')

    # Update vertex count and data part in the header
    for i, line in enumerate(header):
        if line.startswith('element vertex'):
            header[i] = f"element vertex {len(modified_data)}\n"
            break

    # Ensure the output directory exists
    output_dir = os.path.dirname(output_ply_file)
    if not os.path.exists(output_dir):
        print(f"Error: The output directory {output_dir} does not exist!")
        return

    # Save the new PLY file
    with open(output_ply_file, 'w') as f:
        f.writelines(header)
        f.writelines(modified_data)

    print(f"Normal vector data has been replaced, and the result is saved as: {output_ply_file}")


# Set up command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Replace normal vector data with zeros in a PLY file.")
    parser.add_argument('--ply_file', type=str, required=True, help="Path to the input PLY file")
    parser.add_argument('--output_ply_file', type=str, required=True, help="Path to save the output PLY file")
    return parser.parse_args()

# Main function
def main():
    # Parse command line arguments
    args = parse_args()

    # Call the function to replace normal vector with zero
    replace_normal_with_zero(args.ply_file, args.output_ply_file)

if __name__ == "__main__":
    main()
