import numpy as np
import open3d as o3d
import matplotlib.pyplot as plt
import os
import argparse

# Function to read ASCII point cloud file and extract coordinates and attributes
def read_ascii_point_cloud(filename):
    """Read ASCII point cloud file and extract coordinates and attributes."""
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()

        # Find the end of header section
        header_end = 0
        header_lines = []
        for i, line in enumerate(lines):
            if line.startswith('#') or line.startswith('//') or line.startswith(';') or line.startswith('ply') or line.startswith('format') or line.startswith('element') or line.startswith('property') or line.startswith('end_header'):
                header_lines.append(line)
                header_end = i + 1
            elif not line.strip():  # Empty lines might be part of the header
                header_end = i + 1
            else:
                break

        header = ''.join(header_lines)
        field_names = extract_field_names(header)

        # Parse the data section
        data_lines = lines[header_end:]
        data = []
        for line in data_lines:
            if line.strip():  # Skip empty lines
                values = line.strip().split()
                if values:
                    data.append([float(v) for v in values])

        if not data:
            raise ValueError("Point cloud file contains no valid data")

        point_data = np.array(data)

        # Extract coordinates and attributes
        xyz = point_data[:, 0:3]
        attributes = {}

        if point_data.shape[1] > 3:
            if field_names and len(field_names) >= point_data.shape[1]:
                for i in range(3, point_data.shape[1]):
                    attr_name = field_names[i] if i < len(field_names) else f"attr_{i - 3}"
                    attributes[attr_name] = point_data[:, i]
            else:
                for i in range(3, point_data.shape[1]):
                    attributes[f"attr_{i - 3}"] = point_data[:, i]

        return xyz, attributes, field_names

    except Exception as e:
        print(f"Error reading point cloud file: {e}")
        return None, None, None

# Function to extract field names from the header
def extract_field_names(header):
    """Try to extract field names from the header."""
    field_names = []

    # Handle PLY format
    if "ply" in header:
        properties = []
        for line in header.split('\n'):
            if line.strip().startswith("property"):
                parts = line.strip().split()
                if len(parts) >= 3:
                    properties.append(parts[-1])
        if properties:
            return properties

    # Handle other common formats
    for line in header.split('\n'):
        line = line.strip()
        if line.startswith('#'):
            line = line[1:].strip()
        elif line.startswith('//'):
            line = line[2:].strip()
        elif line.startswith(';'):
            line = line[1:].strip()

        keywords = ['FIELDS', 'COLUMNS', 'fields', 'columns']
        found = False
        for keyword in keywords:
            if keyword in line:
                parts = line.split(keyword, 1)[1].strip().split()
                if parts:
                    field_names = parts
                    found = True
                    break

        if found:
            break

        if not field_names and len(line.split()) >= 3:
            potential_fields = line.split()
            if any(x in potential_fields[0].lower() for x in ['x', '0']):
                if any(y in potential_fields[1].lower() for y in ['y', '1']):
                    if any(z in potential_fields[2].lower() for z in ['z', '2']):
                        field_names = potential_fields

    return field_names

# Function to normalize values between 0 and 1
def normalize_values(values):
    """Normalize data to range [0,1]"""
    min_val = np.min(values)
    max_val = np.max(values)

    if max_val > min_val:
        normalized = (values - min_val) / (max_val - min_val)
    else:
        normalized = np.zeros_like(values)

    return normalized, min_val, max_val

# Function to apply the colormap to the values
def apply_colormap(values, colormap_name='viridis'):
    """Apply the specified colormap to the values"""
    cmap = plt.get_cmap(colormap_name)
    normalized_values, min_val, max_val = normalize_values(values)
    colors = cmap(normalized_values)[:, :3]  # Exclude alpha channel
    return colors, min_val, max_val

# Function to visualize the point cloud with a color map applied to the attribute
def visualize_point_cloud_with_attribute(points, values, attribute_name, colormap_name='viridis'):
    """Visualize the point cloud with an attribute mapped to colors"""
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)

    colors, min_val, max_val = apply_colormap(values, colormap_name)

    pcd.colors = o3d.utility.Vector3dVector(colors)

    # Create a coordinate frame for reference
    coordinate_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(
        size=np.max(np.ptp(points, axis=0)) * 0.1, origin=[0, 0, 0])

    print(f"\n{attribute_name} statistics:")
    print(f"  Value range: {min_val:.6f} to {max_val:.6f}")
    print(f"  Mean: {np.mean(values):.6f}")
    print(f"  Standard deviation: {np.std(values):.6f}")

    print(f"\nVisualizing {attribute_name}...")
    o3d.visualization.draw_geometries([pcd, coordinate_frame])

    return pcd, colors, min_val, max_val

# Function to create and save a colorbar image
def create_colorbar_image(colormap_name, min_val, max_val, output_path):
    """Create a colorbar image for the given colormap"""
    fig, ax = plt.subplots(figsize=(4, 1))
    cmap = plt.get_cmap(colormap_name)
    norm = plt.Normalize(min_val, max_val)

    cb = plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap),
                      cax=ax, orientation='horizontal')

    cb.set_label('Value')

    plt.tight_layout()
    plt.savefig(output_path, dpi=100, bbox_inches='tight')
    plt.close()

    print(f"Colorbar saved to {output_path}")

# Function to list all available colormaps
def list_available_colormaps():
    """List all available colormaps"""
    colormaps = plt.colormaps()
    print("\nAvailable colormaps:")
    categories = {
        "Sequential": ['viridis', 'plasma', 'inferno', 'magma', 'cividis', 'Blues', 'Greens', 'Reds', 'YlOrBr'],
        "Diverging": ['coolwarm', 'RdBu', 'RdYlBu', 'RdYlGn', 'PuOr', 'BrBG'],
        "Cyclic": ['twilight', 'twilight_shifted', 'hsv'],
        "Qualitative": ['Pastel1', 'Pastel2', 'Paired', 'Set1', 'Set2', 'tab10', 'tab20']
    }

    for category, cmaps in categories.items():
        print(f"\n  {category}:")
        valid_cmaps = [cmap for cmap in cmaps if cmap in colormaps]
        if valid_cmaps:
            print("    " + ", ".join(valid_cmaps))

    print("\n  Others:")
    other_cmaps = [cmap for cmap in colormaps if not any(cmap in cat_cmaps for cat_cmaps in categories.values())]
    for i in range(0, len(other_cmaps), 5):
        print("    " + ", ".join(other_cmaps[i:i + 5]))

# Set up command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Pseudo-color point cloud visualization tool.")
    parser.add_argument('--input', type=str, required=True, help="Input point cloud file path")
    parser.add_argument('--output', type=str, required=True, help="Output file path for the colored point cloud")
    parser.add_argument('--attribute_index', type=int, required=True, help="Index of the attribute to visualize")
    parser.add_argument('--colormap', type=str, default='viridis', help="Name of the colormap to use")
    return parser.parse_args()

# Main function
def main():
    args = parse_args()

    input_file = args.input
    output_file = args.output
    attribute_index = args.attribute_index
    colormap_name = args.colormap

    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print(f"Attribute index: {attribute_index}")
    print(f"Colormap: {colormap_name}")

    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} does not exist!")
        return

    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    points, attributes, field_names = read_ascii_point_cloud(input_file)
    if points is None or attributes is None:
        return

    print(f"Successfully read {len(points)} points.")

    print("\nAvailable attributes:")
    for i, attr_name in enumerate(attributes.keys()):
        print(f"{i}. {attr_name}")

    if not attributes:
        print("No visualizable attributes found!")
        return

    attr_name = list(attributes.keys())[attribute_index]
    attr_values = list(attributes.values())[attribute_index]

    if colormap_name not in plt.colormaps():
        print(f"Warning: Colormap '{colormap_name}' does not exist, using 'viridis' as default.")
        colormap_name = 'viridis'

    pcd, _, min_val, max_val = visualize_point_cloud_with_attribute(points, attr_values, attr_name, colormap_name)

    o3d.io.write_point_cloud(output_file, pcd)
    print(f"Colored point cloud saved to {output_file}")

    colorbar_path = os.path.splitext(output_file)[0] + "_colorbar.png"
    create_colorbar_image(colormap_name, min_val, max_val, colorbar_path)

if __name__ == "__main__":
    main()
