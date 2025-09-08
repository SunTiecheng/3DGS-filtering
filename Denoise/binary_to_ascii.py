import struct
import os
import argparse

# Function to convert a binary-encoded PLY file to ASCII format
def convert_binary_ply_to_ascii(binary_ply_path, ascii_ply_path):
    """
    Convert a binary-encoded PLY file to ASCII format.

    Parameters:
        binary_ply_path (str): Path to the binary PLY file.
        ascii_ply_path (str): Path to save the converted ASCII PLY file.
    """
    with open(binary_ply_path, 'rb') as f:
        # Read the header
        header = []
        while True:
            line = f.readline().decode('utf-8', errors='ignore')
            header.append(line)
            if line.startswith("end_header"):
                break

        # Parse header to determine the structure
        is_binary = False
        num_vertices = 0
        properties = []
        for line in header:
            if "format binary" in line:
                is_binary = True
            if line.startswith("element vertex"):
                num_vertices = int(line.split()[-1])
            if line.startswith("property"):
                properties.append(line.split()[1])  # e.g., float, uchar

        if not is_binary:
            raise ValueError("The input file is not in binary format.")

        # Write the ASCII header
        with open(ascii_ply_path, 'w') as ascii_file:
            for line in header:
                ascii_file.write(line.replace("binary_little_endian", "ascii"))

        # Read binary data and convert to ASCII
        with open(ascii_ply_path, 'a') as ascii_file:
            for _ in range(num_vertices):
                data = []
                for prop in properties:
                    if prop == "float":
                        data.append(struct.unpack('<f', f.read(4))[0])
                    elif prop == "uchar":
                        data.append(struct.unpack('<B', f.read(1))[0])
                    elif prop == "int":
                        data.append(struct.unpack('<i', f.read(4))[0])
                    # Add other property types if necessary
                ascii_file.write(" ".join(map(str, data)) + "\n")

    print(f"Conversion complete. ASCII PLY file saved at: {ascii_ply_path}")

# Set up command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Convert a binary PLY file to ASCII format.")
    parser.add_argument('--input', type=str, required=True, help="Input binary PLY file path")
    parser.add_argument('--output', type=str, required=True, help="Output ASCII PLY file path")
    return parser.parse_args()

# Main function
def main():
    # Get command line arguments
    args = parse_args()

    # Convert binary PLY to ASCII
    convert_binary_ply_to_ascii(args.input, args.output)

if __name__ == '__main__':
    main()
