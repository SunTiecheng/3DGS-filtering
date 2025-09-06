import open3d as o3d
import numpy as np
import os
import argparse

# Function to read the PLY file and extract x, y, z coordinates, and add IDs
def read_ply(ply_file):
    """
    Read an ASCII-encoded PLY file, extract x, y, z coordinates, and add IDs.
    
    :param ply_file: Path to the input PLY file
    :return: Points and their corresponding IDs
    """
    pcd = o3d.io.read_point_cloud(ply_file, format='ply')
    points = np.asarray(pcd.points)
    ids = np.arange(1, len(points) + 1)
    return points, ids

# Function to denoise the point cloud using Statistical Outlier Removal (SOR) and return inliers and outliers with their IDs
def denoise_and_sort(points, ids, nb_neighbors=20, std_ratio=2.0):
    """
    Denoise the point cloud using Statistical Outlier Removal (SOR) and return the inlier and outlier IDs.
    
    :param points: The points in the point cloud
    :param ids: The IDs corresponding to the points
    :param nb_neighbors: The number of neighbors for the SOR filter (default is 20)
    :param std_ratio: The standard deviation ratio for the SOR filter (default is 2.0)
    :return: Filtered points, filtered IDs, and outlier IDs
    """
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)

    # Apply Statistical Outlier Removal filter
    sor = pcd.remove_statistical_outlier(nb_neighbors=nb_neighbors, std_ratio=std_ratio)
    inlier_indices = sor[1]  # Indices of inliers (points retained)

    # Get the filtered points and their IDs
    filtered_points = points[inlier_indices]
    filtered_ids = ids[inlier_indices]

    # Get the outliers and their IDs
    outlier_indices = np.setdiff1d(np.arange(len(points)), inlier_indices)
    outlier_ids = ids[outlier_indices]

    return filtered_points, filtered_ids, outlier_ids

# Function to save the denoised point cloud and the removed IDs to separate files
def save_denoised_point_cloud(filtered_points, filtered_ids, output_ply_file, outlier_ids):
    """
    Save the denoised point cloud, sorted by IDs, and save the removed IDs to a text file.
    
    :param filtered_points: The filtered points after SOR
    :param filtered_ids: The filtered IDs after SOR
    :param outlier_ids: The IDs of the removed (outlier) points
    :param output_ply_file: Path to save the denoised PLY file
    :param removed_ids_file: Path to save the removed IDs text file
    """
    sorted_indices = np.argsort(filtered_ids)
    sorted_points = filtered_points[sorted_indices]
    sorted_ids = filtered_ids[sorted_indices]

    # Save the PLY file (only x, y, z)
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(sorted_points)
    o3d.io.write_point_cloud(output_ply_file, pcd, write_ascii=True)

    # Save the removed IDs to a text file
    output_dir = os.path.dirname(output_ply_file)
    removed_ids_file = os.path.join(output_dir, 'removed_ids.txt')
    with open(removed_ids_file, 'w') as f:
        for id in outlier_ids:
            f.write(f"{id}\n")

    print(f"Denoised point cloud saved to {output_ply_file}")
    print(f"Removed IDs saved to {removed_ids_file}")

# Set up command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Denoise point cloud using Statistical Outlier Removal (SOR) and save the results.")
    parser.add_argument('--ply_file', type=str, required=True, help="Path to the input PLY file")
    parser.add_argument('--output_ply_file', type=str, required=True, help="Path to save the denoised PLY file")
    parser.add_argument('--nb_neighbors', type=int, default=20, help="Number of neighbors for SOR filter (default is 20)")
    parser.add_argument('--std_ratio', type=float, default=2.0, help="Standard deviation ratio for SOR filter (default is 2.0)")
    return parser.parse_args()

# Main function
def main():
    # Parse command line arguments
    args = parse_args()

    # Read the point cloud
    points, ids = read_ply(args.ply_file)

    # Denoise using Statistical Outlier Removal (SOR)
    filtered_points, filtered_ids, outlier_ids = denoise_and_sort(points, ids, args.nb_neighbors, args.std_ratio)

    # Save the results
    save_denoised_point_cloud(filtered_points, filtered_ids, args.output_ply_file, outlier_ids)

if __name__ == "__main__":
    main()
