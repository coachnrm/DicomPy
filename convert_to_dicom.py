import os
import numpy as np
import matplotlib.pyplot as plt
from pydicom import dcmread
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import generate_uid, ExplicitVRLittleEndian
from pydicom.data import get_testdata_files
from datetime import datetime
from PIL import Image
import cv2

def process_image_file(file_path):
    """
    Process either DICOM or JPG image file and return pixel array and metadata
    """
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == '.dcm':
        # Process DICOM file
        try:
            x = dcmread(file_path)
            if hasattr(x, 'pixel_array'):
                pixel_array = x.pixel_array
                print(f"DICOM file - Pixel array shape: {pixel_array.shape}")
                return pixel_array, x, file_extension
            else:
                print("No pixel data found in DICOM file")
                return None, None, None
        except Exception as e:
            print(f"Error reading DICOM file: {e}")
            return None, None, None
    
    elif file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
        # Process image file
        try:
            img = Image.open(file_path)
            pixel_array = np.array(img)
            print(f"Image file - Pixel array shape: {pixel_array.shape}")
            return pixel_array, None, file_extension
            
        except Exception as e:
            print(f"Error reading image file: {e}")
            return None, None, None
    
    else:
        print(f"Unsupported file format: {file_extension}")
        return None, None, None

def convert_to_dicom(pixel_array, output_path, original_dicom=None, file_extension=None):
    """
    Convert numpy array to DICOM format
    """
    try:
        # Create file meta dataset
        file_meta = Dataset()
        file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.2'  # CT Image Storage
        file_meta.MediaStorageSOPInstanceUID = generate_uid()
        file_meta.ImplementationClassUID = generate_uid()
        file_meta.TransferSyntaxUID = ExplicitVRLittleEndian  # Set transfer syntax
        
        # Create main dataset
        if original_dicom:
            # Use metadata from original DICOM if available
            ds = original_dicom
            ds.file_meta = file_meta
            ds.is_little_endian = True
            ds.is_implicit_VR = False
        else:
            # Create new DICOM dataset with file meta
            ds = FileDataset(output_path, {}, file_meta=file_meta, preamble=b"\0" * 128)
            ds.is_little_endian = True
            ds.is_implicit_VR = False
            
            # Populate required DICOM fields
            ds.SOPClassUID = file_meta.MediaStorageSOPClassUID
            ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
            
            # Patient information
            ds.PatientName = "Unknown^Patient"
            ds.PatientID = "123456"
            ds.PatientSex = "O"  # Other
            ds.PatientBirthDate = ""
            
            # Study information
            ds.StudyInstanceUID = generate_uid()
            ds.SeriesInstanceUID = generate_uid()
            ds.StudyID = "1"
            ds.SeriesNumber = "1"
            
            # Image information
            ds.Modality = "CT"
            ds.InstanceNumber = "1"
            ds.ImageType = ['ORIGINAL', 'PRIMARY', 'AXIAL']
            
            # Set current date and time
            current_date = datetime.now().strftime('%Y%m%d')
            current_time = datetime.now().strftime('%H%M%S')
            ds.StudyDate = current_date
            ds.SeriesDate = current_date
            ds.ContentDate = current_date
            ds.StudyTime = current_time
            ds.SeriesTime = current_time
            ds.ContentTime = current_time
        
        # Set image dimensions
        if len(pixel_array.shape) == 3:
            ds.Rows = pixel_array.shape[0]
            ds.Columns = pixel_array.shape[1]
            ds.SamplesPerPixel = pixel_array.shape[2]
            ds.PhotometricInterpretation = "RGB" if pixel_array.shape[2] == 3 else "MONOCHROME2"
            ds.PlanarConfiguration = 0  # 0 = color-by-pixel, 1 = color-by-plane
        else:
            ds.Rows = pixel_array.shape[0]
            ds.Columns = pixel_array.shape[1]
            ds.SamplesPerPixel = 1
            ds.PhotometricInterpretation = "MONOCHROME2"
        
        # Set pixel data properties
        ds.BitsAllocated = 8
        ds.BitsStored = 8
        ds.HighBit = 7
        ds.PixelRepresentation = 0  # unsigned integer
        
        # Convert pixel array to appropriate format
        if pixel_array.dtype != np.uint8:
            if pixel_array.max() > 255:
                # Normalize to 0-255 range
                pixel_array = (pixel_array - pixel_array.min()) / (pixel_array.max() - pixel_array.min()) * 255
            pixel_array = pixel_array.astype(np.uint8)
        
        # Set pixel data
        ds.PixelData = pixel_array.tobytes()
        
        # Set windowing parameters for better display (for grayscale images)
        if len(pixel_array.shape) == 2:  # Grayscale
            ds.WindowCenter = int(np.median(pixel_array))
            ds.WindowWidth = int(pixel_array.max() - pixel_array.min())
            if ds.WindowWidth == 0:
                ds.WindowWidth = 1
        
        # Add some optional but commonly used tags
        ds.LossyImageCompression = '00'
        ds.LossyImageCompressionRatio = 1.0
        
        # Only set compression method if we know the original file type
        if file_extension and file_extension in ['.jpg', '.jpeg']:
            ds.LossyImageCompressionMethod = 'ISO_10918_1'
        else:
            ds.LossyImageCompressionMethod = ''
        
        # Save as DICOM with explicit parameters
        ds.save_as(output_path, write_like_original=False)
        print(f"DICOM file saved successfully: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error converting to DICOM: {e}")
        import traceback
        traceback.print_exc()
        return False

# Example usage
username = 'home'
# Input file paths
dicom_path = os.path.join('/Users', username, 'Desktop', '10.dcm')
jpg_path = os.path.join('/Users', username, 'Desktop', '10.jpg')

# Output DICOM path
output_dicom_path = os.path.join('/Users', username, 'Desktop', 'converted_image.dcm')

# Process the input file (change the path as needed)
input_file_path = jpg_path  # or dicom_path

pixel_array, dicom_metadata, file_extension = process_image_file(input_file_path)

if pixel_array is not None:
    # Display the image
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    if len(pixel_array.shape) == 3:
        if pixel_array.shape[2] == 3:  # Color image (RGB)
            plt.imshow(pixel_array)
            plt.title('Original Image (Color)')
        else:  # Multi-frame image
            plt.imshow(pixel_array[0], cmap='gray')
            plt.title('First Slice')
    else:
        plt.imshow(pixel_array, cmap='gray')
        plt.title('Original Image (Grayscale)')
    plt.axis('off')
    
    # Additional information
    print(f"Data type: {pixel_array.dtype}")
    print(f"Value range: {pixel_array.min()} to {pixel_array.max()}")
    print(f"Shape: {pixel_array.shape}")
    
    # Convert to DICOM
    success = convert_to_dicom(pixel_array, output_dicom_path, dicom_metadata, file_extension)
    
    if success:
        # Verify the converted DICOM file
        try:
            converted_ds = dcmread(output_dicom_path)
            print(f"\nConverted DICOM verification:")
            print(f"  Rows: {converted_ds.Rows}")
            print(f"  Columns: {converted_ds.Columns}")
            print(f"  Samples per pixel: {converted_ds.SamplesPerPixel}")
            print(f"  Photometric interpretation: {converted_ds.PhotometricInterpretation}")
            print(f"  Transfer Syntax: {converted_ds.file_meta.TransferSyntaxUID}")
            
            # Display converted DICOM image
            plt.subplot(1, 2, 2)
            if hasattr(converted_ds, 'pixel_array'):
                if converted_ds.SamplesPerPixel == 1:
                    plt.imshow(converted_ds.pixel_array, cmap='gray')
                else:
                    plt.imshow(converted_ds.pixel_array)
                plt.title('Converted DICOM Image')
                plt.axis('off')
            
            plt.tight_layout()
            plt.show()
            
            print(f"\nDICOM conversion successful! File saved at: {output_dicom_path}")
                
        except Exception as e:
            print(f"Error verifying converted DICOM: {e}")
            import traceback
            traceback.print_exc()