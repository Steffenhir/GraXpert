import os
import numpy as np
from astropy.io import fits
from skimage import io, img_as_float32, exposure
from skimage.util import img_as_ubyte, img_as_uint
from PIL import Image
from stretch import stretch

class AstroImage:
    def __init__(self, stretch_option):
        self.img_array = None
        self.img_display = None
        self.img_format = None
        self.fits_header = None
        self.stretch_option = stretch_option
        
    def set_from_file(self, directory):
        self.img_format = os.path.splitext(directory)[1]
        
        img_array = None
        if(self.img_format == ".fits" or self.img_format == ".fit"):
            hdul = fits.open(directory)
            img_array = hdul[0].data
            self.fits_header = hdul[0].header
            hdul.close()
            
            if(len(img_array.shape) == 3):
               img_array = np.moveaxis(img_array,0,-1)

        else:
            img_array = io.imread(directory)
        
        # Reshape greyscale picture to shape (y,x,1)
        if(len(img_array.shape) == 2):            
            img_array = np.array([img_array])
            img_array = np.moveaxis(img_array,0,-1)
       
        # Use 32 bit float with range (0,1) for internal calculations
        img_array = img_as_float32(img_array)
        
        
        if(np.min(img_array) < 0 or np.max(img_array > 1)):
            img_array = exposure.rescale_intensity(img_array, out_range=(0,1))
        
        self.img_array = img_array
        self.update_display()
        return
    
    def set_from_array(self, array):
        self.img_array = array
        self.update_display()
        return
    
    def update_display(self):
        img_display = self.stretch()
        img_display = img_display*255
        if(img_display.shape[2] == 1):
            self.img_display = Image.fromarray(img_display[:,:,0].astype(np.uint8))
        else:
            self.img_display = Image.fromarray(img_display.astype(np.uint8))
        
        return
    
    def stretch(self):
        bg, sigma = (0.2, 3)
        if(self.stretch_option.get() == "No Stretch"):
            return self.img_array
        
        elif(self.stretch_option.get() == "10% Bg, 3 sigma"):
                bg, sigma = (0.1,3)
               
        elif(self.stretch_option.get() == "15% Bg, 3 sigma"):
                bg, sigma = (0.15,3)
                
        elif(self.stretch_option.get() == "20% Bg, 3 sigma"):
                bg, sigma = (0.2,3)
                
        elif(self.stretch_option.get() == "25% Bg, 1.25 sigma"):
                bg, sigma = (0.25,1.25)
            
        
        return stretch(self.img_array, bg, sigma)
    
    def save(self, dir, saveas_type, fits_header=None):
        if(self.img_array is None):
            return
        
        if(saveas_type == "16 bit Tiff" or saveas_type == "16 bit Fits"):
            image_converted = img_as_uint(self.img_array)
        else:
            image_converted = self.img_array
         
        if(saveas_type == "16 bit Tiff" or saveas_type == "32 bit Tiff"):
            io.imsave(dir, image_converted)
        else:
            if(len(image_converted.shape) == 3):
               image_converted = np.moveaxis(image_converted,-1,0)
 
            hdu = fits.PrimaryHDU(data=image_converted, header=fits_header)
            hdul = fits.HDUList([hdu])
            hdul.writeto(dir, output_verify="warn", overwrite=True)
            hdul.close()
            
        return
        