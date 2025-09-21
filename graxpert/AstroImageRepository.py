from enum import StrEnum
from typing import Dict

from graxpert.astroimage import AstroImage
from graxpert.stretch import StretchParameters, calculate_mtf_stretch_parameters_for_image, stretch_all


class ImageTypes(StrEnum):
    Original = "Original"
    Gradient_Corrected = "Gradient-Corrected"
    Background = "Background"
    Deconvolved_Object_only = "Deconvolved Object-only"
    Deconvolved_Stars_only = "Deconvolved Stars-only"
    Denoised = "Denoised"


class AstroImageRepository:

    images: Dict = {
        ImageTypes.Original: None,
        ImageTypes.Gradient_Corrected: None,
        ImageTypes.Background: None,
        ImageTypes.Deconvolved_Object_only: None,
        ImageTypes.Deconvolved_Stars_only: None,
        ImageTypes.Denoised: None,
    }

    def set(self, type: ImageTypes, image: AstroImage):
        self.images[type] = image

    def get(self, type: ImageTypes):
        return self.images[type]

    def stretch_all(self, stretch_params: StretchParameters, saturation: float):

        if self.get(ImageTypes.Original) is None:
            return

        stretches = []

        if not stretch_params.do_stretch:
            for key, image in self.images.items():
                if image is not None:
                    stretches.append(image.img_array)

        else:

            all_image_arrays = []
            all_mtf_stretch_params = []

            all_image_arrays.append(self.get(ImageTypes.Original).img_array)
            all_mtf_stretch_params.append(calculate_mtf_stretch_parameters_for_image(stretch_params, self.get(ImageTypes.Original).img_array))

            if self.get(ImageTypes.Gradient_Corrected) is not None and self.get(ImageTypes.Background) is not None:
                all_image_arrays.append(self.get(ImageTypes.Gradient_Corrected).img_array)
                all_mtf_stretch_params.append(calculate_mtf_stretch_parameters_for_image(stretch_params, self.get(ImageTypes.Gradient_Corrected).img_array))

                all_image_arrays.append(self.get(ImageTypes.Background).img_array)
                all_mtf_stretch_params.append(all_mtf_stretch_params[0])

            if self.get(ImageTypes.Deconvolved_Object_only) is not None and self.get(ImageTypes.Gradient_Corrected) is None:
                all_image_arrays.append(self.get(ImageTypes.Deconvolved_Object_only).img_array)
                all_mtf_stretch_params.append(all_mtf_stretch_params[0])

            elif self.get(ImageTypes.Deconvolved_Object_only) is not None and self.get(ImageTypes.Gradient_Corrected) is not None:
                all_image_arrays.append(self.get(ImageTypes.Deconvolved_Object_only).img_array)
                all_mtf_stretch_params.append(all_mtf_stretch_params[1])

            if self.get(ImageTypes.Deconvolved_Stars_only) is not None and self.get(ImageTypes.Gradient_Corrected) is None:
                all_image_arrays.append(self.get(ImageTypes.Deconvolved_Stars_only).img_array)
                all_mtf_stretch_params.append(all_mtf_stretch_params[0])

            elif self.get(ImageTypes.Deconvolved_Stars_only) is not None and self.get(ImageTypes.Gradient_Corrected) is not None:
                all_image_arrays.append(self.get(ImageTypes.Deconvolved_Stars_only).img_array)
                all_mtf_stretch_params.append(all_mtf_stretch_params[1])

            if self.get(ImageTypes.Denoised) is not None and self.get(ImageTypes.Gradient_Corrected) is None:
                all_image_arrays.append(self.get(ImageTypes.Denoised).img_array)
                all_mtf_stretch_params.append(all_mtf_stretch_params[0])

            elif self.get(ImageTypes.Denoised) is not None and self.get(ImageTypes.Gradient_Corrected) is not None:
                all_image_arrays.append(self.get(ImageTypes.Denoised).img_array)
                all_mtf_stretch_params.append(all_mtf_stretch_params[1])

            stretches = stretch_all(all_image_arrays, all_mtf_stretch_params)

        i = 0
        for key, image in self.images.items():
            if image is not None:
                image.update_display_from_array(stretches[i], saturation)
                i = i + 1

    def crop_all(self, start_x: float, end_x: float, start_y: float, end_y: float):
        for key, astroimg in self.images.items():
            if astroimg is not None:
                astroimg.crop(start_x, end_x, start_y, end_y)

    def update_saturation(self, saturation):
        for key, value in self.images.items():
            if value is not None:
                value.update_saturation(saturation)

    def reset(self):
        for key, value in self.images.items():
            self.images[key] = None

    def display_options(self):
        display_options = []

        for key, value in self.images.items():
            if self.images[key] is not None:
                display_options.append(key)

        return display_options
