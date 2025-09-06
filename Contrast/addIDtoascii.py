import os
import glob
import argparse

def add_id_to_ply(input_path, output_path):
    """
    Add ID column to a PLY file
    """
    with open(input_path, 'r') as f:
        lines = f.readlines()

    # Find the position where the header ends
    header_end = 0
    vertex_count = 0
    for i, line in enumerate(lines):
        if line.startswith('element vertex'):
            vertex_count = int(line.split()[-1])
        if line.startswith('end_header'):
            header_end = i
            break

    # Build the new content for the file
    new_content = []

    # Copy header content until end_header
    new_content.extend(lines[:header_end])

    # Add the ID property declaration
    new_content.append('property int id\n')

    # Add end_header
    new_content.append('end_header\n')

    # Process data part and add IDs
    for i, line in enumerate(lines[header_end + 1:header_end + 1 + vertex_count], 1):
        new_content.append(f"{line.strip()} {i}\n")

    # Write the new content to the output file
    with open(output_path, 'w') as f:
        f.writelines(new_content)


def batch_process_ply_files(input_dir, output_dir=None):
    """
    Batch process PLY files to add ID column
    """
    # If no output directory is specified, use the input directory
    if output_dir is None:
        output_dir = input_dir

    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get all ASCII PLY files in the input directory
    ply_files = glob.glob(os.path.join(input_dir, "*.ply"))
    total_files = len(ply_files)

    print(f"Found {total_files} PLY files")

    # Process each file
    for i, ply_file in enumerate(ply_files, 1):
        filename = os.path.basename(ply_file)
        output_filename = f"{os.path.splitext(filename)[0]}_with_id.ply"
        output_path = os.path.join(output_dir, output_filename)

        print(f"[{i}/{total_files}] Processing: {filename}")

        try:
            add_id_to_ply(ply_file, output_path)
            print(f"    ID added and saved as: {output_filename}")
        except Exception as e:
            print(f"    Failed to process: {str(e)}")


# Set up command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Add ID column to PLY files")
    parser.add_argument('--input_dir', type=str, required=True, help="Directory containing input PLY files")
    parser.add_argument('--output_dir', type=str, help="Directory to save the processed PLY files")
    return parser.parse_args()

# Main function
def main():
    args = parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir if args.output_dir else input_dir

    # Execute batch processing
    batch_process_ply_files(input_dir, output_dir)

if __name__ == "__main__":
    main()
