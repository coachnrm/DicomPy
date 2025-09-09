import os
import numpy as np
import matplotlib.pyplot as plt
from pydicom import dcmread
from PIL import Image
import cv2

def process_image_file(file_path):
    """
    Process either DICOM or JPG image file and return pixel array
    """
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == '.dcm':
        # Process DICOM file
        try:
            x = dcmread(file_path)
            if hasattr(x, 'pixel_array'):
                pixel_array = x.pixel_array
                print(f"DICOM file - Pixel array shape: {pixel_array.shape}")
                return pixel_array
            else:
                print("No pixel data found in DICOM file")
                return None
        except Exception as e:
            print(f"Error reading DICOM file: {e}")
            return None
    
    elif file_extension in ['.jpg', '.jpeg']:
        # Process JPG file
        try:
            # Method 1: Using PIL/Pillow
            img = Image.open(file_path)
            pixel_array = np.array(img)
            print(f"JPG file - Pixel array shape: {pixel_array.shape}")
            return pixel_array
            
            # Alternative method using OpenCV (uncomment if preferred)
            # pixel_array = cv2.imread(file_path)
            # pixel_array = cv2.cvtColor(pixel_array, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
            # print(f"JPG file - Pixel array shape: {pixel_array.shape}")
            # return pixel_array
            
        except Exception as e:
            print(f"Error reading JPG file: {e}")
            return None
    
    else:
        print(f"Unsupported file format: {file_extension}")
        return None

# Example usage
username = 'home'
# For DICOM file
dicom_path = os.path.join('/Users', username, 'Desktop', 'converted_image.dcm')
# For JPG file
jpg_path = os.path.join('/Users', username, 'Desktop', '10.jpg')

# Process the file (change the path as needed)
file_path = dicom_path  # or dicom_path

pixel_array = process_image_file(file_path)

if pixel_array is not None:
    # Create a figure for displaying images
    plt.figure(figsize=(10, 10))
    
    # Check if it's a multi-frame image (3D) or single frame (2D)
    if len(pixel_array.shape) == 3:
        if pixel_array.shape[2] == 3:  # Color image (RGB)
            plt.imshow(pixel_array)
            plt.title('Color Image')
        else:  # Multi-frame image (multiple slices)
            for i in range(pixel_array.shape[0]):
                plt.imshow(pixel_array[i], cmap='gray')
                plt.title(f'Slice {i + 1}')
                plt.axis('off')
                plt.pause(0.5)  # Pause for 0.5 seconds between slices
    else:
        # Single frame grayscale image
        plt.imshow(pixel_array, cmap='gray')
        plt.title('Grayscale Image')
    
    plt.axis('off')
    plt.show()
    
    # Additional information
    print(f"Data type: {pixel_array.dtype}")
    print(f"Value range: {pixel_array.min()} to {pixel_array.max()}")