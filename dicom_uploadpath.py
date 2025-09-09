import os
import numpy as np
import matplotlib.pyplot as plt
from pydicom import dcmread
from PIL import Image
import cv2
from matplotlib.widgets import Button, TextBox

class ImageViewer:
    def __init__(self, pixel_array=None):
        self.pixel_array = pixel_array
        if pixel_array is not None:
            self.current_array = pixel_array.copy()
        else:
            self.current_array = None
        self.zoom_level = 1.0
        self.brightness_level = 1.0
        
        # Create figure and axes
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        plt.subplots_adjust(bottom=0.25)
        
        # Display the image if available
        self.update_display()
        
        # Create buttons
        self.create_buttons()
        
        # Connect events
        self.fig.canvas.mpl_connect('scroll_event', self.on_scroll)
        
    def create_buttons(self):
        # File path input
        ax_textbox = plt.axes([0.1, 0.12, 0.6, 0.04])
        self.text_box = TextBox(ax_textbox, 'DICOM Path:', initial='')
        self.text_box.on_submit(self.load_from_path)
        
        # Upload button
        ax_upload = plt.axes([0.72, 0.12, 0.18, 0.04])
        self.btn_upload = Button(ax_upload, 'Load DICOM')
        self.btn_upload.on_clicked(self.load_from_path_click)
        
        # Zoom buttons
        ax_zoom_in = plt.axes([0.1, 0.05, 0.1, 0.04])
        ax_zoom_out = plt.axes([0.21, 0.05, 0.1, 0.04])
        
        self.btn_zoom_in = Button(ax_zoom_in, 'Zoom In')
        self.btn_zoom_out = Button(ax_zoom_out, 'Zoom Out')
        
        self.btn_zoom_in.on_clicked(self.zoom_in)
        self.btn_zoom_out.on_clicked(self.zoom_out)
        
        # Brightness buttons
        ax_bright = plt.axes([0.45, 0.05, 0.1, 0.04])
        ax_dark = plt.axes([0.56, 0.05, 0.1, 0.04])
        ax_reset = plt.axes([0.67, 0.05, 0.1, 0.04])
        
        self.btn_bright = Button(ax_bright, 'Brighter')
        self.btn_dark = Button(ax_dark, 'Darker')
        self.btn_reset = Button(ax_reset, 'Reset')
        
        self.btn_bright.on_clicked(self.increase_brightness)
        self.btn_dark.on_clicked(self.decrease_brightness)
        self.btn_reset.on_clicked(self.reset_image)
        
        # Disable buttons if no image is loaded
        if self.current_array is None:
            self.set_buttons_state(False)
        
    def set_buttons_state(self, state):
        """Enable or disable control buttons"""
        self.btn_zoom_in.set_active(state)
        self.btn_zoom_out.set_active(state)
        self.btn_bright.set_active(state)
        self.btn_dark.set_active(state)
        self.btn_reset.set_active(state)
        
    def load_from_path(self, text):
        """Load image from the path entered in the text box"""
        if text and os.path.exists(text):
            self.load_image(text)
        
    def load_from_path_click(self, event):
        """Load image from the current path in the text box when button is clicked"""
        current_path = self.text_box.text
        if current_path and os.path.exists(current_path):
            self.load_image(current_path)
        else:
            print("Please enter a valid file path")
            
    def load_image(self, file_path):
        """Load and process the image file"""
        print(f"Loading file: {file_path}")
        pixel_array = process_image_file(file_path)
        
        if pixel_array is not None:
            # Normalize the pixel array to 0-255 if needed
            if pixel_array.dtype != np.uint8:
                pixel_array = ((pixel_array - pixel_array.min()) / 
                              (pixel_array.max() - pixel_array.min()) * 255).astype(np.uint8)
            
            self.pixel_array = pixel_array
            self.current_array = pixel_array.copy()
            self.zoom_level = 1.0
            self.brightness_level = 1.0
            
            # Enable control buttons
            self.set_buttons_state(True)
            
            # Update display
            self.update_display()
            
            # Print image information
            print(f"Data type: {pixel_array.dtype}")
            print(f"Value range: {pixel_array.min()} to {pixel_array.max()}")
            print(f"Image shape: {pixel_array.shape}")
        else:
            print(f"Failed to load image from: {file_path}")
        
    def zoom_in(self, event):
        if self.current_array is not None:
            self.zoom_level *= 1.2
            self.update_display()
        
    def zoom_out(self, event):
        if self.current_array is not None:
            self.zoom_level /= 1.2
            self.update_display()
        
    def on_scroll(self, event):
        if self.current_array is not None and event.inaxes == self.ax:
            if event.button == 'up':
                self.zoom_in(event)
            elif event.button == 'down':
                self.zoom_out(event)
            
    def increase_brightness(self, event):
        if self.current_array is not None:
            self.brightness_level *= 1.2
            self.update_brightness()
        
    def decrease_brightness(self, event):
        if self.current_array is not None:
            self.brightness_level /= 1.2
            self.update_brightness()
        
    def reset_image(self, event):
        if self.current_array is not None:
            self.zoom_level = 1.0
            self.brightness_level = 1.0
            self.current_array = self.pixel_array.copy()
            self.update_display()
        
    def update_brightness(self):
        if self.current_array is not None:
            # Apply brightness adjustment
            self.current_array = np.clip(self.pixel_array.astype(np.float32) * self.brightness_level, 
                                         self.pixel_array.min(), self.pixel_array.max()).astype(self.pixel_array.dtype)
            self.update_display()
        
    def update_display(self):
        # Clear the axis
        self.ax.clear()
        
        if self.current_array is not None:
            # Display the image with current settings
            if len(self.current_array.shape) == 3 and self.current_array.shape[2] == 3:
                self.img = self.ax.imshow(self.current_array)
            else:
                self.img = self.ax.imshow(self.current_array, cmap='gray')
                
            # Set title with current settings
            self.ax.set_title(f'DICOM Viewer - Zoom: {self.zoom_level:.2f}x, Brightness: {self.brightness_level:.2f}x')
            
            # Apply zoom by changing axis limits
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            
            x_center = (xlim[0] + xlim[1]) / 2
            y_center = (ylim[0] + ylim[1]) / 2
            
            x_width = (xlim[1] - xlim[0]) / 2 / self.zoom_level
            y_height = (ylim[1] - ylim[0]) / 2 / self.zoom_level
            
            self.ax.set_xlim(x_center - x_width, x_center + x_width)
            self.ax.set_ylim(y_center - y_height, y_center + y_height)
        else:
            self.ax.text(0.5, 0.5, 'No DICOM image loaded\n\nEnter DICOM file path below and click "Load DICOM"\n\nExample: /Users/username/Desktop/image.dcm', 
                        horizontalalignment='center', verticalalignment='center', 
                        transform=self.ax.transAxes, fontsize=12)
            self.ax.set_title('DICOM Image Viewer')
        
        self.ax.axis('off')
        
        # Redraw the figure
        self.fig.canvas.draw()

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
            
        except Exception as e:
            print(f"Error reading JPG file: {e}")
            return None
    
    else:
        print(f"Unsupported file format: {file_extension}")
        return None

# Main execution
if __name__ == "__main__":
    # Create the interactive viewer without an initial image
    viewer = ImageViewer()
    
    # Add some usage instructions
    print("=" * 60)
    print("DICOM IMAGE VIEWER INSTRUCTIONS:")
    print("1. Enter the full path to your DICOM file in the text box")
    print("2. Click 'Load DICOM' or press Enter to load the image")
    print("3. Use the Zoom and Brightness controls to adjust the view")
    print("4. Use mouse scroll wheel to zoom in/out")
    print("=" * 60)
    print("Example path: /Users/yourusername/Desktop/image.dcm")
    print("=" * 60)
    
    plt.show()