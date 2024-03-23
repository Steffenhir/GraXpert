from graxpert.astroimage import AstroImage
from graxpert.stretch import StretchParameters, stretch_all
from typing import Dict

class AstroImageRepository:
    images: Dict = {"Original": None, "Gradient-Corrected": None, "Background": None, "Denoised": None}
    
    def set(self, type:str, image:AstroImage):
        self.images[type] = image
    
    def get(self, type:str):
        return self.images[type]
    
    def stretch_all(self, stretch_params:StretchParameters, saturation:float):
        all_image_arrays = []
        
        for key, value in self.images.items():
            if (value is not None):
                all_image_arrays.append(value.img_array)
                
                
        stretches = stretch_all(all_image_arrays, stretch_params)
        
        i = 0
        for key, value in self.images.items():
            if (value is not None):
                value.update_display_from_array(stretches[i], saturation)
                i = i + 1
                
    def crop_all(self, start_x:float, end_x:float, start_y:float, end_y:float):
        for key, astroimg in self.images.items():
            if astroimg is not None:
                astroimg.crop(start_x, end_x, start_y, end_y)
                
    def update_saturation(self, saturation):
        for key, value in self.images.items():
            if (value is not None):
                value.update_saturation(saturation)
    
    def reset(self):
        for key, value in self.images.items():
            self.images[key] = None
    
    def display_options(self):
        display_options = []
        
        for key, value in self.images.items():
            if (self.images[key] is not None):
                display_options.append(key)
            
        return display_options
    
    
    