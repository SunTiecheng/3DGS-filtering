import torch
import MinkowskiEngine as ME
from pcc_model import PCCModel
from scipy.spatial import cKDTree
import numpy as np
import os
import argparse

# Function to read PLY file with ID, extracting coordinates and IDs
def read_ply_with_id(file_path):
    """Read PLY file with ID and extract coordinates and IDs."""
    coords = []
    ids = []
    with open(file_path, 'r') as f:
        header_ended = False
        for line in f:
            if header_ended:
                values = line.strip().split()
                if len(values) >= 4:
                    coords.append(list(map(float, values[:3])))  # Extract XYZ coordinates
                    ids.append(int(float(values[3])))  # Extract ID
            elif line.startswith("end_header"):
                header_ended = True
    coords = torch.tensor(coords).float()
    ids = torch.tensor(ids).int()
    return coords, ids

# Function to write PLY file with coordinates and IDs, keeping the header consistent
def write_ply_with_id(output_path, coords, ids, input_ply_path):
    """Write point cloud coordinates and IDs to a PLY file, keeping the header consistent."""
    with open(input_ply_path, 'r') as f:
        head_lines = []
        header_ended = False

        for line in f:
            if header_ended:
                break
            head_lines.append(line)
            if line.startswith("end_header"):
                header_ended = True

    with open(output_path, 'w') as f:
        # Write header
        for line in head_lines:
            if line.startswith("element vertex"):
                f.write(f"element vertex {coords.shape[0]}\n")  # Update vertex count
            else:
                f.write(line)

        # Write point cloud data
        for i in range(coords.shape[0]):
            x, y, z = coords[i].tolist()
            f.write(f"{x} {y} {z} {ids[i].item()}\n")

# Function to save compressed data (sparse tensor and related info)
def save_compressed_data(filename, sparse_tensor, num_points):
    """Save compressed data including coordinates, features, and point count info."""
    np.save(f"{filename}_coords.npy", sparse_tensor.C.cpu().numpy())  # Save coordinates
    np.save(f"{filename}_feats.npy", sparse_tensor.F.cpu().numpy())  # Save features
    np.save(f"{filename}_num_points.npy", np.array(num_points))  # Save point counts
    np.save(f"{filename}_tensor_stride.npy", sparse_tensor.tensor_stride)  # Save tensor stride

    print(f"Compressed data saved to {filename}_*.npy")

# Function to load compressed data (coordinates, features, and point count info)
def load_compressed_data(filename, device):
    """Load compressed data including coordinates, features, and point count info."""
    coords = torch.tensor(np.load(f"{filename}_coords.npy")).to(device)  # Load coordinates
    feats = torch.tensor(np.load(f"{filename}_feats.npy")).to(device)  # Load features
    num_points = np.load(f"{filename}_num_points.npy").tolist()  # Load point counts
    tensor_stride = np.load(f"{filename}_tensor_stride.npy").tolist()  # Load tensor stride

    sparse_tensor = ME.SparseTensor(
        features=feats,
        coordinates=coords,
        tensor_stride=tensor_stride,
        device=device
    )

    return sparse_tensor, num_points

# Function for encoding process
def encoder_process(model_path, input_ply_path, output_dir):
    """Encoder process to compress point cloud data."""
    os.makedirs(output_dir, exist_ok=True)  # Ensure output directory exists

    filename_base = os.path.join(output_dir, os.path.basename(input_ply_path).split('.')[0])
    encoder_output_ply_path = f"{filename_base}_encoder.ply"

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = PCCModel().to(device)
    checkpoint = torch.load(model_path, map_location=device)
    model.load_state_dict(checkpoint['model'])
    model.eval()

    coords, ids = read_ply_with_id(input_ply_path)
    features = torch.ones((coords.shape[0], 1)).to(device)
    batch_id = torch.zeros(coords.shape[0], dtype=torch.int32).unsqueeze(1)
    coords_with_batch = torch.cat([batch_id, coords.int()], dim=1)
    sparse_input = ME.SparseTensor(features=features, coordinates=coords_with_batch, device=device)

    with torch.no_grad():
        encoder_outputs = model.encoder(sparse_input)
        out2 = encoder_outputs[0]
        num_points = [len(gt) for gt in encoder_outputs[1:] + [sparse_input]]

    save_compressed_data(filename_base, out2, num_points)

    out2_coords = out2.C.cpu().numpy()[:, 1:]  # Remove batch_id
    input_coords = coords.numpy()
    kdtree = cKDTree(input_coords)

    k = 10
    used_ids = set()
    id_mapping = []

    for out_coord in out2_coords:
        assigned = False
        while not assigned:
            distances, indices = kdtree.query(out_coord, k=k)
            for neighbor_index in indices:
                candidate_id = ids[neighbor_index].item()
                if candidate_id not in used_ids:
                    id_mapping.append(candidate_id)
                    used_ids.add(candidate_id)
                    assigned = True
                    break
            if not assigned:
                k += 1

    sorted_indices = np.argsort(id_mapping)
    sorted_coords = out2_coords[sorted_indices]
    sorted_ids = np.array(id_mapping)[sorted_indices]

    write_ply_with_id(encoder_output_ply_path, torch.tensor(sorted_coords),
                      torch.tensor(sorted_ids, dtype=torch.int32), input_ply_path)
    print(f"Encoder output saved to: {encoder_output_ply_path}")

    return filename_base

# Function for decoding process
def decoder_process(model_path, compressed_data_prefix, input_ply_path, output_ply_path, rho=1.0):
    """Decoder process to reconstruct point cloud from compressed data."""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = PCCModel().to(device)
    checkpoint = torch.load(model_path, map_location=device)
    model.load_state_dict(checkpoint['model'])
    model.eval()

    coords, ids = read_ply_with_id(input_ply_path)

    y, num_points = load_compressed_data(compressed_data_prefix, device)

    num_points[-1] = int(rho * num_points[-1])
    nums_list = [[num] for num in num_points]

    with torch.no_grad():
        y_q, _ = model.get_likelihood(y, quantize_mode="symbols")
        out_cls_list, out = model.decoder(y_q, nums_list, ground_truth_list=[None] * 3, training=False)

    reconstructed_coords = out.C.cpu().numpy()[:, 1:]

    input_coords = coords.numpy()
    kdtree = cKDTree(reconstructed_coords)
    distances, indices = kdtree.query(input_coords, k=1)

    matched_coords = reconstructed_coords[indices]
    matched_ids = ids

    write_ply_with_id(output_ply_path, torch.tensor(matched_coords), matched_ids, input_ply_path)
    print(f"Reconstructed point cloud saved to: {output_ply_path}")

# Set up command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Point Cloud Compression and Reconstruction")
    parser.add_argument('--model_path', type=str, required=True, help="Path to the trained model file")
    parser.add_argument('--input_dir', type=str, required=True, help="Directory containing the input PLY files")
    parser.add_argument('--output_dir', type=str, required=True, help="Directory to save the processed files")
    return parser.parse_args()

# Main function
def main():
    args = parse_args()

    input_prefix = args.input_dir
    output_dir = args.output_dir
    model_path = args.model_path

    file_suffixes = [
        'xyz_ascii_voxeltopc.ply', 'fdc012_ascii_voxeltopc.ply', 'fre012_ascii_voxeltopc.ply', 
        'fre345_ascii_voxeltopc.ply', 'fre678_ascii_voxeltopc.ply', 'fre91011_ascii_voxeltopc.ply',
        'fre121314_ascii_voxeltopc.ply', 'fre151617_ascii_voxeltopc.ply', 'fre181920_ascii_voxeltopc.ply',
        'fre212223_ascii_voxeltopc.ply', 'fre242526_ascii_voxeltopc.ply', 'fre272829_ascii_voxeltopc.ply',
        'fre303132_ascii_voxeltopc.ply', 'fre333435_ascii_voxeltopc.ply', 'fre363738_ascii_voxeltopc.ply',
        'fre394041_ascii_voxeltopc.ply', 'fre424344_ascii_voxeltopc.ply', 'opacity_ascii_voxeltopc.ply',
        'scale012_ascii_voxeltopc.ply', 'rot012_ascii_voxeltopc.ply', 'rot3_ascii_voxeltopc.ply'
    ]

    for file_suffix in file_suffixes:
        input_ply_path = os.path.join(input_prefix, file_suffix)
        compressed_data_prefix = encoder_process(model_path, input_ply_path, output_dir)

        output_ply_path = os.path.join(output_dir, f"{file_suffix.replace('.ply', '_reconstructed.ply')}")
        decoder_process(model_path, compressed_data_prefix, input_ply_path, output_ply_path, rho=1.0)

if __name__ == "__main__":
    main()
