
import os
import numpy as pil
import matplotlib.pyplot as plt

from pydicom import dcmread

username = 'home'
path = os.path.join('/Users', username, 'Desktop', '10.dcm')
# path = 'Users/home/Desktop/xxxx.DCM'
# ให้เอา file (.dcm) ไปไว้ที่หน้า desktop 


try:
    x = dcmread(path)
    print(dir(x))
    # print(x.PixelSpacing)
    # print(x.pixel_array)
    print("Pixel array shape:", x.pixel_array.shape)

    # Create a figure for displaying images
    plt.figure(figsize=(10, 10))  # Optional: set figure size

    # plot the image using matplotlib
    for i in range(x.pixel_array.shape[0]):
        plt.imshow(x.pixel_array[i], cmap='grey')
        plt.title(f'Slice {i + 1}')
        plt.axis('off')  # Turn off axis numbers and ticks

        plt.pause(0.5)  # Pause for 0.5 seconds (adjust as needed)
    plt.show()

except FileNotFoundError:
    print(f"No such file or directory: {path}")
except Exception as e:
    print(f"An error occurred: {e}")