from graxpert.astroimage import AstroImage
from graxpert.stretch import StretchParameters, stretch_all, calculate_mtf_stretch_parameters_for_image
from typing import Dict

class AstroImageRepository:
    images: Dict = {"Original": None, "Gradient-Corrected": None, "Background": None, "Denoised": None}
    
    def set(self, type:str, image:AstroImage):
        self.images[type] = image
    
    def get(self, type:str):
        return self.images[type]
    
    def stretch_all(self, stretch_params:StretchParameters, saturation:float):
        
        if self.get("Original") is None:
            return
        
        all_image_arrays = []
        all_mtf_stretch_params = []
        
        all_image_arrays.append(self.get("Original").img_array)
        all_mtf_stretch_params.append(calculate_mtf_stretch_parameters_for_image(stretch_params, self.get("Original").img_array))
        
        if self.get("Gradient-Corrected") is not None and self.get("Background") is not None:
            all_image_arrays.append(self.get("Gradient-Corrected").img_array)
            all_mtf_stretch_params.append(calculate_mtf_stretch_parameters_for_image(stretch_params, self.get("Gradient-Corrected").img_array))
            
            all_image_arrays.append(self.get("Background").img_array)
            all_mtf_stretch_params.append(all_mtf_stretch_params[0])
            
        
        if self.get("Denoised") is not None and self.get("Gradient-Corrected") is None:
            all_image_arrays.append(self.get("Denoised").img_array)
            all_mtf_stretch_params.append(all_mtf_stretch_params[0])
            
        elif self.get("Denoised") is not None and self.get("Gradient-Corrected") is not None:
            all_image_arrays.append(self.get("Denoised").img_array)
            all_mtf_stretch_params.append(all_mtf_stretch_params[1])
            
         
        stretches = stretch_all(all_image_arrays, all_mtf_stretch_params)
        

        i = 0
        for key, image in self.images.items():
            if image is not None:
                image.update_display_from_array(stretches[i], saturation)
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
    
    
    