import pandas as pd
import argparse

# Function to read the PLY file and separate header and data
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

# Function to write data back to the PLY file in ASCII format
def write_ply(file_path, header, data):
    """Write the data back to the PLY file, preserving ASCII format"""
    with open(file_path, 'w') as f:
        for line in header:
            f.write(line)
        for row in data.itertuples(index=False):
            f.write(' '.join(map(str, row)) + '\n')

# Set up command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Process PLY files.")
    parser.add_argument('--input', type=str, required=True, help="Input PLY file path")
    parser.add_argument('--output', type=str, required=True, help="Output PLY file path")
    return parser.parse_args()

# Main function
def main():
    # Get command line arguments
    args = parse_args()
    
    # Read the input file
    header, data = read_ply(args.input)

    # Add three new columns with all values set to 0, inserted at columns 4, 5, 6
    data.insert(3, 'new_col_1', 0)  # Column 4
    data.insert(4, 'new_col_2', 0)  # Column 5
    data.insert(5, 'new_col_3', 0)  # Column 6

    # Modify header to add descriptions for the new columns
    updated_header = []
    for line in header:
        if line.startswith("element vertex"):
            updated_header.append(f"element vertex {len(data)}\n")
        elif line.startswith("property") and 'z' in line:
            # Insert nx, ny, nz after the 'z' property
            updated_header.append(line)
            updated_header.append("property float nx\n")
            updated_header.append("property float ny\n")
            updated_header.append("property float nz\n")
        elif line.strip() == "end_header":
            updated_header.append("end_header\n")
        else:
            updated_header.append(line)

    # Write the processed data to the output file
    write_ply(args.output, updated_header, data)
    print(f"File processed and saved to: {args.output}")

if __name__ == '__main__':
    main()
