"The script is not perfect. Remember to manually remove the rot12 and fre4344 of the header in the output file."
import os
import argparse

# Function to process the file and remove the first two columns of the data
def delete_columns(file_path, output_path):
    """Process the PLY file and remove the first two columns of vertex data."""
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Find the line where the header ends
    header_end_index = lines.index('end_header\n') + 1

    # Process the data part
    processed_lines = lines[:header_end_index]  # Keep the header unchanged

    # Iterate over the vertex data and remove the first two columns
    for line in lines[header_end_index:]:
        parts = line.split()
        # Keep only the third (z) coordinate and the ID
        new_line = f"{parts[2]} {parts[3]}\n"
        processed_lines.append(new_line)

    # Save the modified data to a new file
    with open(output_path, 'w') as file:
        file.writelines(processed_lines)

    print(f"Processed file saved at: {output_path}")

# Set up command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Remove the first two columns from a PLY file after voxelization.")
    parser.add_argument('--input', type=str, required=True, help="Input PLY file path")
    parser.add_argument('--output', type=str, required=True, help="Output PLY file path")
    return parser.parse_args()

# Main function
def main():
    # Get command line arguments
    args = parse_args()

    # Process the input file and save the output
    delete_columns(args.input, args.output)

if __name__ == '__main__':
    main()

