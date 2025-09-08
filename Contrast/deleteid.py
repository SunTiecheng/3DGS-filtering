import numpy as np
import argparse

# Function to remove the ID column from a PLY file
def remove_id_from_ply(input_file, output_file):
    """Remove the ID column from the PLY file.
    
    Args:
        input_file: The input PLY file
        output_file: The output PLY file
    """
    # Read the header and data
    header_lines = []
    data_lines = []
    vertex_count = 0

    with open(input_file, 'r') as f:
        # Read the header
        while True:
            line = f.readline().strip()
            if line == 'end_header':
                break

            # Record vertex count but do not modify it
            if line.startswith('element vertex'):
                vertex_count = int(line.split()[-1])
                header_lines.append(line)
            # Skip the ID property declaration
            elif line.startswith('property') and 'id' in line.lower():
                continue
            else:
                header_lines.append(line)

        # Read data
        data = np.loadtxt(f, dtype=np.float64)

    # Remove the last column (ID column)
    data = data[:, :-1]

    # Write the new file
    with open(output_file, 'w') as f:
        # Write the header
        for line in header_lines:
            f.write(line + '\n')
        f.write('end_header\n')

        # Write the data without the ID column
        for row in data:
            f.write(' '.join([f'{x:.16f}' for x in row]) + '\n')

# Function to check if the file contains ID information and print related details
def check_file_structure(filename):
    """Check if the file contains ID information and print relevant details."""
    has_id_property = False
    with open(filename, 'r') as f:
        # Check the header
        while True:
            line = f.readline().strip()
            if line == 'end_header':
                break
            if 'property' in line and 'id' in line.lower():
                has_id_property = True
                print(f"Found ID property declaration: {line}")

        # Check the first data line
        first_line = f.readline().strip()
        num_columns = len(first_line.split())
        print(f"Number of columns in the data: {num_columns}")

    return has_id_property

# Set up command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Remove ID column from PLY file.")
    parser.add_argument('--input_file', type=str, required=True, help="Path to the input PLY file")
    parser.add_argument('--output_file', type=str, required=True, help="Path to save the output PLY file")
    return parser.parse_args()

# Main function
def main():
    # Parse command line arguments
    args = parse_args()

    input_file = args.input_file
    output_file = args.output_file

    # First, check the file structure
    print("Checking input file structure...")
    has_id = check_file_structure(input_file)

    if has_id:
        print("Starting file processing...")
        remove_id_from_ply(input_file, output_file)
        print("Processing complete!")
        print(f"ID information removed and saved to: {output_file}")
    else:
        print("Warning: No ID property detected in the file. Please verify the file format.")

if __name__ == "__main__":
    main()
