import os
from PIL import Image
import numpy as np
import argparse

# Function to process images and replace black pixels with the specified color
def process_images(input_folder, output_folder, replacement_color):
    """Process images to replace black pixels with the specified color."""
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Process each image in the input folder
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):  # Check for image files
            img_path = os.path.join(input_folder, filename)
            img = Image.open(img_path).convert('RGB')

            # Convert image to numpy array for processing
            img_array = np.array(img)
            mask = np.all(img_array == [0, 0, 0], axis=-1)  # Find black pixels
            img_array[mask] = replacement_color  # Replace black pixels with the specified color

            # Convert back to image and save it
            new_img = Image.fromarray(img_array)
            new_img.save(os.path.join(output_folder, filename))

    print("All images processed successfully ")

# Set up command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Replace black pixels in images with a specified color.")
    parser.add_argument('--input_folder', type=str, required=True, help="Input folder containing images")
    parser.add_argument('--output_folder', type=str, required=True, help="Output folder to save processed images")
    parser.add_argument('--replacement_color', type=str, default='204,204,204', help="Color to replace black pixels, in RGB format (e.g., '204,204,204')")
    return parser.parse_args()

# Main function
def main():
    args = parse_args()

    # Parse the replacement color
    replacement_color = tuple(map(int, args.replacement_color.split(',')))

    # Process the images
    process_images(args.input_folder, args.output_folder, replacement_color)

if __name__ == "__main__":
    main()
