import open3d as o3d
import numpy as np
import argparse

# Function to read the PLY file and extract x, y, z coordinates, and add IDs
def read_ply(ply_file):
    """
    Read an ASCII-encoded PLY file, extract x, y, z, and add IDs.
    
    :param ply_file: Path to the input PLY file
    :return: Point cloud object, points, and their corresponding IDs
    """
    pcd = o3d.io.read_point_cloud(ply_file, format='ply')
    points = np.asarray(pcd.points)
    ids = np.arange(1, len(points) + 1)
    return pcd, points, ids

# Function to denoise the point cloud using DBSCAN and return inliers and outliers with their IDs
def denoise_and_sort_with_dbscan(pcd, points, ids, eps=0.05, min_points=10):
    """
    Denoise the point cloud using DBSCAN and return the inlier and outlier IDs.
    
    :param pcd: Point cloud object
    :param points: The points in the point cloud
    :param ids: The IDs corresponding to the points
    :param eps: DBSCAN epsilon parameter controlling the neighborhood size
    :param min_points: Minimum number of points for a neighborhood
    :return: Filtered points, filtered IDs, and outlier IDs
    """
    labels = np.array(pcd.cluster_dbscan(eps=eps, min_points=min_points, print_progress=True))

    # Inlier indices (non-noise points)
    inlier_indices = np.where(labels != -1)[0]
    filtered_points = points[inlier_indices]
    filtered_ids = ids[inlier_indices]

    # Outlier indices (noise points)
    outlier_indices = np.where(labels == -1)[0]
    outlier_ids = ids[outlier_indices]

    return filtered_points, filtered_ids, outlier_ids

# Function to save the denoised point cloud and the removed IDs to separate files
def save_denoised_point_cloud(filtered_points, filtered_ids, outlier_ids, output_ply_file, txt_file_path):
    """
    Save the denoised point cloud, sorted by IDs, and save the removed IDs to a text file.
    
    :param filtered_points: The filtered points after DBSCAN
    :param filtered_ids: The filtered IDs after DBSCAN
    :param outlier_ids: The IDs of the removed (outlier) points
    :param output_ply_file: Path to save the denoised point cloud
    :param txt_file_path: Path to save the removed IDs
    """
    sorted_indices = np.argsort(filtered_ids)
    sorted_points = filtered_points[sorted_indices]
    sorted_ids = filtered_ids[sorted_indices]

    # Set colors to zero for visualization (all black)
    colors = np.zeros_like(sorted_points)
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(sorted_points)
    pcd.colors = o3d.utility.Vector3dVector(colors)

    o3d.io.write_point_cloud(output_ply_file, pcd, write_ascii=True)

    with open(txt_file_path, "w") as f:
        for id in outlier_ids:
            f.write(f"{id}\n")

    print(f"Denoised point cloud saved to {output_ply_file}")
    print(f"Removed IDs saved to {txt_file_path}")

# Set up command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Denoise point cloud using DBSCAN and save the results.")
    parser.add_argument('--ply_file', type=str, required=True, help="Path to the input PLY file")
    parser.add_argument('--output_ply_file', type=str, required=True, help="Path to save the denoised PLY file")
    parser.add_argument('--txt_file_path', type=str, required=True, help="Path to save the removed IDs text file")
    parser.add_argument('--eps', type=float, default=0.05, help="DBSCAN epsilon parameter (neighborhood size)")
    parser.add_argument('--min_points', type=int, default=10, help="DBSCAN minimum points parameter (density)")
    return parser.parse_args()

# Main function
def main():
    # Parse command line arguments
    args = parse_args()

    # Read the point cloud
    pcd, points, ids = read_ply(args.ply_file)

    # Denoise using DBSCAN
    filtered_points, filtered_ids, outlier_ids = denoise_and_sort_with_dbscan(pcd, points, ids, args.eps, args.min_points)

    # Save the results
    save_denoised_point_cloud(filtered_points, filtered_ids, outlier_ids, args.output_ply_file, args.txt_file_path)

if __name__ == "__main__":
    main()
