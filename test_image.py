import os
import numpy as np
import matplotlib.pyplot as plt
from pydicom import dcmread

username = 'home'
path = os.path.join('/Users', username, 'Desktop', '10.dcm')

try:
    x = dcmread(path)
    print("Available attributes:", [attr for attr in dir(x) if not attr.startswith('_')])
    
    # Check if pixel data exists
    if hasattr(x, 'pixel_array'):
        print("Pixel array shape:", x.pixel_array.shape)
        
        # Create a figure for displaying images
        plt.figure(figsize=(10, 10))
        
        # Check if it's a multi-frame image (3D) or single frame (2D)
        if len(x.pixel_array.shape) == 3:
            # Multi-frame image (multiple slices)
            for i in range(x.pixel_array.shape[0]):
                plt.imshow(x.pixel_array[i], cmap='gray')
                plt.title(f'Slice {i + 1}')
                plt.axis('off')
                plt.pause(0.5)  # Pause for 0.5 seconds between slices
        else:
            # Single frame image
            plt.imshow(x.pixel_array, cmap='gray')
            plt.title('DICOM Image')
            plt.axis('off')
        
        plt.show()
    else:
        print("No pixel data found in DICOM file")
        
except FileNotFoundError:
    print(f"No such file or directory: {path}")
except Exception as e:
    print(f"An error occurred: {e}")