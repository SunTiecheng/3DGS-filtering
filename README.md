# 3DGS-filtering
Article：A Background Noise Removal Method for 3D Gaussian Point Clouds

Abstract：Recently, the 3D Gaussian Splatting method has demonstrated outstanding visual performance in rendering tasks. Many object dataset for 3D reconstruction have black background. However, due to overfitting, background noise may appear after training 3D Gaussian with such images. To address this problem, we propose an encoder-decoder architecture to filter this kind of noise. In our method, we split the multiple attributes of 3D Gaussian into several groups. These groups are individually fed into the proposed encoder-decoder filter. Since the noise points are outliers of the 3D Gaussian point cloud, they are filtered out during the down-sampling process. Through this filtering principle, we filtered these attribute groups and obtained the 3D Gaussian primitives through attribute fusion. The proposed method can effectively remove the background noise, which significantly improves the overall visual quality of 3D Gaussian rendering. The code is available at: https://github.com/SunTiecheng/3DGS-filtering

Reference project：[PCGv2](https://github.com/NJUVISION/PCGCv2)

The pre-trained model used is: r7_0.4bpp.pth

## 1.Data Acquisition

### 1.1 Dataset

Baidu Cloud: https://pan.baidu.com/s/1copPs-zVf-t5QIR68dexKQ?pwd=2526

Google Cloud: https://drive.google.com/file/d/1Yw_ANfpAfNGokGLs_7YlDZgVny_q5gVO/view?usp=sharing

### 1.2 Point Cloud Data

3DGS method : [gaussian-splatting](https://github.com/graphdeco-inria/gaussian-splatting)

Steps：

1. After deploying the environment, create a new folder in the project list, name it "data", and then create an input folder in the internal subfolders interface. Then, store the images (for a single dataset, such as an airplane) under this folder.
2. Run ``` python convert.py -s data```
   Attention: If you find that there are fewer images (which do not match the number of images in the original dataset), then delete the 0 in the distorted section, change the 1 to 0, and then run:
   ```python conver.py -s data --skip_matching ```
3. ```
   python train.py -s data（Your data path） --eval
   ```
4. After completing the training, you can open the output file in the output folder, find pointcloud, and then open file 1 from 30000 steps to obtain the point cloud.

## 2.The sequence of denoising process

After deploying [PCGv2](https://github.com/NJUVISION/PCGCv2) , please create multiple folders according to personal habits to store files output by different scripts.  It is recommended to create 6 folders for each dataset, which should be used to store split, aligned, voxelized, and deduplicated files after voxelization encoder, the point cloud file after denoising.
Please run the following script after deploying PCGv2:

1. Convert noisy point clouds from binary encoding to ASCII encoding.
   
   ```
   python binary_to_ascii.py --input /path/to/input.ply --output /path/to/output.ply
   ```
2. Point cloud splitting and adding IDs.
   
   ```
   python attributes_spilt.py --input /path/to/input.ply --output /path/to/output
   ```
3. Point cloud voxelization.
   
   ```
   python voxelization.py --input_dir /path/to/input --output_dir /path/to/output --voxel_resolution 7168
   ```
4. Delete duplicate voxels.
   
   ```
   python delete_repeat_voxel.py --input_dir /home/user/project/input --output_dir /home/user/project/output
   ```
5. Use pretrained models to reconstruct each split point cloud (repc5 and repc4 need to be placed in the PCGv2 directory).
   
   ```
   python repc5.py --model_path /path/to/model.pth --input_dir /path/to/input --output_dir /path/to/output
   ```
6. If a memory overflow is encountered in the fifth step, this script can be used for separate reconstruction.
   
   ```
   python repc4.py --model_path /path/to/model.pth --input_dir /path/to/input --output_dir /path/to/output
   ```
7. Devoxelization.
   
   ```
   python devoxelization.py --input_dir /path/to/input --voxelized_dir /path/to/voxelized --output_dir /path/to/output
   ```
8. Execute twice, delete the first two columns of data for fre4344op and rot123 groups respectively. (Note: This script is incomplete, and the two output files need to be manually opened to remove the fre43, fre44, and rot1, rot2 declarations in the header file.)
   
   ```
   python delete_row.py --input ~/rot123_ascii_voxeltopc.ply --output ~/rot3_ascii_voxeltopc.ply
   ```
   
   ```
   python delete_row.py --input ~/fre4344op_ascii_voxeltopc.ply --output ~/opacity_ascii_voxeltopc.ply
   ```
9. Merge the reconstructed point cloud.
   
   ```
   python fusion.py --input_dir /path/to/input --output_path /path/to/output/merged.ply
   ```
10. Because the nxyz normal vector has always been 0 and has not been processed before, this step is to directly add the normal vector to the processed point cloud.
    
    ```
    python addnxyz.py --input /path/to/input.ply --output /path/to/output.ply
    ```
11. Convert point cloud back to binary encoding.
    
    ```
    python ascii_to_binary.py --input /path/to/input.ply --output /path/to/output.ply
    ```

## Evaluation Metric

Use the built-in evaluation indicator code in the [gaussian-splatting](https://github.com/graphdeco-inria/gaussian-splatting) project for evaluation.

Step: (Taking 3dgs as an example, other methods can replace the point cloud in the point_cloud file with the processed point cloud.):

1. Modify the 'bg_comor=[1,1,1] if dataset. white_mackground else [0,0,0]' in render.exe of the 3dgs project to 'bg_comor=bg_comor=[0.8,0.8,0.8]'
   
   The purpose of this step is to display the rendered noise. If not modified, the noise and background will be the same color.
2. Run
   
   ```
   python render.py -m (The path of the subfile output in your output)
   ```
3. Implement changes in the background of GT.
   
   ```
   python rgbtransfer.py --input_folder /path/to/input/folder --output_folder /path/to/output/folder --replacement_color "204,204,204"
   ```
4. To obtain evaluation metric data, all other methods only need to replace the point cloud, with the same steps.
   
   ```
   python metrics.py -m (The path of the subfile output in your output)
   ```

## Comparative Experiment

Input the noisy point cloud of 3dgs
Steps:

1. Transcoding.
   
   ```
   python 012ascii.py --binary_ply_path /path/to/input/binary.ply --ascii_ply_path /path/to/output/converted_ascii.ply
   ```
2. Add IDs.
   
   ```
   python addIDtoascii.py --input_dir /path/to/input/folder --output_dir /path/to/output/folder
   ```
3. Choose coordinates.
   
   ```
   python selectxyz.py --input_ply /path/to/your/input/point_cloud.ply --output_ply /path/to/your/output/point_cloud_with_id.ply
   ```
4. Different traditional denoising algorithm.
   
   ```
   python SORdenoise.py --ply_file /path/to/your/input/point_cloud.ply --output_ply_file /path/to/your/output/denoised_point_cloud.ply --nb_neighbors 20 --std_ratio 2.0
   ```
   
   ```
   python RORdenoise.py --ply_file /path/to/your/input/point_cloud.ply --output_ply_file /path/to/your/output/denoised_point_cloud.ply --radius 0.05 --min_neighbors 10
   ```
   
   ```
   python DBSCANdenoise.py --ply_file /path/to/your/input/point_cloud.ply --output_ply_file /path/to/your/output/denoised_point_cloud.ply --txt_file_path /path/to/your/output/removed_ids.txt --eps 0.05 --min_points 10
   ```
5. Delete points from Gaussian point cloud
   
   ```
   python 3dgsdeletepoint.py --ply_file /path/to/your/input/point_cloud.ply --id_txt_file /path/to/your/ids_to_remove.txt --output_ply_file /path/to/your/output/filtered_output.ply
   ```
6. Delete IDs.
   
   ```
   python deleteid.py --input_file /path/to/your/input/point_cloud.ply --output_file /path/to/your/output/filtered_point_cloud.ply
   ```
7. Add normal vector.
   
   ```
   python change0.py --ply_file /path/to/your/input/point_cloud.ply --output_ply_file /path/to/your/output/filtered_point_cloud.ply
   ```
8. Transcoding.
   
   ```
   python ascii201.py --binary_ply_path /path/to/input/binary.ply --ascii_ply_path /path/to/output/converted_ascii.ply
   ```

## Pseudo color projection

Used to test the correlation between data of the same type of attribute.
The script is：pseudo_color_projection.py

## Other

The code before modifying the path is in a folder named 'unmodified'.
