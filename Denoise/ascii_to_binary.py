import struct
import os
import argparse

# Function to convert an ASCII-encoded PLY file to binary format
def convert_ascii_ply_to_binary(ascii_ply_path, binary_ply_path):
    """
    Convert an ASCII-encoded PLY file to binary format.

    Parameters:
        ascii_ply_path (str): Path to the ASCII PLY file.
        binary_ply_path (str): Path to save the converted binary PLY file.
    """
    with open(ascii_ply_path, 'r') as f:
        lines = f.readlines()

    # Parse header
    header = []
    vertex_count = 0
    properties = []
    header_end_index = 0
    for i, line in enumerate(lines):
        header.append(line)
        if line.startswith("element vertex"):
            vertex_count = int(line.split()[-1])
        if line.startswith("property"):
            properties.append(line.split()[1])  # e.g., float, uchar
        if line.startswith("end_header"):
            header_end_index = i + 1
            break

    # Modify the header to binary format
    header = [line.replace("format ascii", "format binary_little_endian") for line in header]

    # Parse vertex data
    vertex_data = []
    for line in lines[header_end_index:header_end_index + vertex_count]:
        vertex_data.append([float(x) if prop == "float" else int(x) for x, prop in zip(line.split(), properties)])

    # Write binary PLY
    with open(binary_ply_path, 'wb') as f:
        # Write header
        for line in header:
            f.write(line.encode('utf-8'))

        # Write binary vertex data
        for vertex in vertex_data:
            for value, prop in zip(vertex, properties):
                if prop == "float":
                    f.write(struct.pack('<f', value))  # 4-byte float
                elif prop == "uchar":
                    f.write(struct.pack('<B', value))  # 1-byte unsigned char
                elif prop == "int":
                    f.write(struct.pack('<i', value))  # 4-byte integer
                # Add support for other types if needed

    print(f"Conversion complete. Binary PLY file saved at: {binary_ply_path}")

# Set up command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Convert an ASCII PLY file to binary format.")
    parser.add_argument('--input', type=str, required=True, help="Input ASCII PLY file path")
    parser.add_argument('--output', type=str, required=True, help="Output binary PLY file path")
    return parser.parse_args()

# Main function
def main():
    # Get command line arguments
    args = parse_args()
    
    # Convert ASCII to binary PLY
    convert_ascii_ply_to_binary(args.input, args.output)

if __name__ == '__main__':
    main()
