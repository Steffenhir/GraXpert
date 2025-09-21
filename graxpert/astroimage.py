import json
import logging
import os

import numpy as np
from astropy.io import fits
from PIL import Image, ImageEnhance
from skimage import exposure, img_as_float32, io
from skimage.util import img_as_uint
from xisf import XISF

from graxpert.app_state import AppState
from graxpert.preferences import Prefs, app_state_2_fitsheader
from graxpert.stretch import stretch, StretchParameters


class AstroImage:
    def __init__(self, do_update_display=True):
        self.img_array = None
        self.img_display = None
        self.img_display_saturated = None
        self.img_format = None
        self.fits_header = None
        self.xisf_metadata = {}
        self.image_metadata = {"FITSKeywords": {}}
        self.do_update_display = do_update_display
        self.width = 0
        self.height = 0
        self.roworder = "BOTTOM-UP"

    def set_from_file(self, directory: str, stretch_params: StretchParameters, saturation: float):
        self.img_format = os.path.splitext(directory)[1].lower()

        img_array = None
        if self.img_format == ".fits" or self.img_format == ".fit" or self.img_format == ".fts":
            hdul = fits.open(directory)
            img_array = np.copy(hdul[0].data)
            self.fits_header = hdul[0].header
            hdul.close()

            if len(img_array.shape) == 3:
                img_array = np.moveaxis(img_array, 0, -1)

            if "ROWORDER" in self.fits_header:
                self.roworder = self.fits_header["ROWORDER"]

        elif self.img_format == ".xisf":
            xisf = XISF(directory)
            self.xisf_metadata = xisf.get_file_metadata()
            self.image_metadata = xisf.get_images_metadata()[0]
            self.fits_header = fits.Header()
            self.xisf_imagedata_2_fitsheader()
            img_array = np.copy(xisf.read_image(0))

            entry = {"id": "GraXpert:ProcessingHistory", "type": "String", "value": "BackgroundExtraction"}
            self.image_metadata["XISFProperties"]["GraXpert:ProcessingHistory"] = entry

        else:
            img_array = np.copy(io.imread(directory))
            self.fits_header = fits.Header()

        # Reshape greyscale picture to shape (y,x,1)
        if len(img_array.shape) == 2:
            img_array = np.array([img_array])
            img_array = np.moveaxis(img_array, 0, -1)

        # Use 32 bit float with range (0,1) for internal calculations
        img_array = img_as_float32(img_array)

        if np.min(img_array) < 0 or np.max(img_array > 1):
            img_array = exposure.rescale_intensity(img_array, out_range=(0, 1))

        self.img_array = img_array
        self.width = self.img_array.shape[1]
        self.height = self.img_array.shape[0]

        if self.do_update_display:
            self.update_display(stretch_params, saturation)

        return

    def set_from_array(self, array):
        self.img_array = array
        self.width = self.img_array.shape[1]
        self.height = self.img_array.shape[0]
        return

    def update_display(self, stretch_params: StretchParameters, saturation: float):
        img_display = self.stretch(stretch_params)
        img_display = img_display * 255

        # if self.roworder == "TOP-DOWN":
        #    img_display = np.flip(img_display, axis=0)

        if img_display.shape[2] == 1:
            self.img_display = Image.fromarray(img_display[:, :, 0].astype(np.uint8))
        else:
            self.img_display = Image.fromarray(img_display.astype(np.uint8))

        self.update_saturation(saturation)

        return

    def update_display_from_array(self, img_display, saturation):
        img_display = img_display * 255

        # if self.roworder == "TOP-DOWN":
        #    img_display = np.flip(img_display, axis=0)

        if img_display.shape[2] == 1:
            self.img_display = Image.fromarray(img_display[:, :, 0].astype(np.uint8))
        else:
            self.img_display = Image.fromarray(img_display.astype(np.uint8))

        self.update_saturation(saturation)

        return

    def stretch(self, stretch_params: StretchParameters):
        if stretch_params.do_stretch:
            return np.clip(stretch(self.img_array, stretch_params), 0.0, 1.0)
        else:
            return np.clip(self.img_array, 0.0, 1.0)

    def crop(self, startx, endx, starty, endy):
        self.img_array = self.img_array[starty:endy, startx:endx, :]
        self.img_display = self.img_display.crop((startx, starty, endx, endy))
        self.img_display_saturated = self.img_display_saturated.crop((startx, starty, endx, endy))
        self.width = self.img_array.shape[1]
        self.height = self.img_array.shape[0]
        return

    def update_fits_header(self, original_header, background_mean, prefs: Prefs, app_state: AppState):
        if original_header is None:
            self.fits_header = fits.Header()
        else:
            self.fits_header = original_header

        self.fits_header["BG-EXTR"] = "GraXpert"
        self.fits_header["CBG-1"] = background_mean
        self.fits_header["CBG-2"] = background_mean
        self.fits_header["CBG-3"] = background_mean
        self.fits_header = app_state_2_fitsheader(prefs, app_state, self.fits_header)

        if "ROWORDER" in self.fits_header:
            self.roworder = self.fits_header["ROWORDER"]

    def save(self, dir, saveas_type):
        if self.img_array is None:
            return

        if saveas_type == "16 bit Tiff" or saveas_type == "16 bit Fits" or saveas_type == "16 bit XISF":
            image_converted = img_as_uint(self.img_array)
        else:
            image_converted = self.img_array.astype(np.float32)

        if saveas_type != "16 bit XISF" and saveas_type != "32 bit XISF":
            if image_converted.shape[-1] == 3:
                if saveas_type == "16 bit Fits" or saveas_type == "32 bit Fits":
                    image_converted = np.moveaxis(image_converted, -1, 0)
            else:
                image_converted = image_converted[:, :, 0]

        if saveas_type == "16 bit Tiff" or saveas_type == "32 bit Tiff":
            io.imsave(dir, image_converted)

        elif saveas_type == "16 bit XISF" or saveas_type == "32 bit XISF":
            self.update_xisf_imagedata()
            XISF.write(dir, image_converted, creator_app="GraXpert", image_metadata=self.image_metadata, xisf_metadata=self.xisf_metadata)
        else:
            hdu = fits.PrimaryHDU(data=image_converted, header=self.fits_header)
            hdul = fits.HDUList([hdu])
            hdul.writeto(dir, output_verify="warn", overwrite=True)
            hdul.close()

        return

    def save_stretched(self, dir, saveas_type, stretch_params):
        if self.img_array is None:
            return

        if self.fits_header is not None:
            self.fits_header["STRETCH"] = stretch_params.stretch_option

        stretched_img = self.stretch(stretch_params)

        if saveas_type == "16 bit Tiff" or saveas_type == "16 bit Fits" or saveas_type == "16 bit XISF":
            image_converted = img_as_uint(stretched_img)
        else:
            image_converted = stretched_img.astype(np.float32)

        if saveas_type != "16 bit XISF" and saveas_type != "32 bit XISF":
            if image_converted.shape[-1] == 3:
                if saveas_type == "16 bit Fits" or saveas_type == "32 bit Fits":
                    image_converted = np.moveaxis(image_converted, -1, 0)
            else:
                image_converted = image_converted[:, :, 0]

        if saveas_type == "16 bit Tiff" or saveas_type == "32 bit Tiff":
            io.imsave(dir, image_converted)

        elif saveas_type == "16 bit XISF" or saveas_type == "32 bit XISF":
            self.update_xisf_imagedata()
            XISF.write(dir, image_converted, creator_app="GraXpert", image_metadata=self.image_metadata, xisf_metadata=self.xisf_metadata)
        else:
            hdu = fits.PrimaryHDU(data=image_converted, header=self.fits_header)
            hdul = fits.HDUList([hdu])
            hdul.writeto(dir, output_verify="warn", overwrite=True)
            hdul.close()

        return

    def get_local_median(self, img_point):
        sample_radius = 2
        y1 = int(np.amax([img_point[1] - sample_radius, 0]))
        y2 = int(np.amin([img_point[1] + sample_radius, self.height]))
        x1 = int(np.amax([img_point[0] - sample_radius, 0]))
        x2 = int(np.amin([img_point[0] + sample_radius, self.width]))

        if self.img_array.shape[-1] == 3:
            R = np.median(self.img_array[y1:y2, x1:x2, 0])
            G = np.median(self.img_array[y1:y2, x1:x2, 1])
            B = np.median(self.img_array[y1:y2, x1:x2, 2])

            return [R, G, B]

        if self.img_array.shape[-1] == 1:
            L = np.median(self.img_array[x1:x2, y1:y2, 0])

            return L

    def copy_metadata(self, source_img):
        self.xisf_metadata = source_img.xisf_metadata
        self.image_metadata = source_img.image_metadata

    def update_saturation(self, saturation):
        self.img_display_saturated = self.img_display

        if self.img_array.shape[-1] == 3:
            self.img_display_saturated = ImageEnhance.Color(self.img_display)
            self.img_display_saturated = self.img_display_saturated.enhance(saturation)

        return

    def update_xisf_imagedata(self):
        unique_keys = list(dict.fromkeys(self.fits_header.keys()))

        for key in unique_keys:
            if key == "BG-PTS":
                try:
                    bg_pts = json.loads(self.fits_header["BG-PTS"])

                    for i in range(len(bg_pts)):
                        self.image_metadata["FITSKeywords"]["BG-PTS" + str(i)] = [{"value": bg_pts[i], "comment": ""}]
                except:
                    logging.warning("Could not transfer background points from fits header to xisf image metadata", stack_info=True)
            else:
                value = str(self.fits_header[key]).splitlines()
                comment = str(self.fits_header.comments[key]).splitlines()

                entry = []

                for i in range(max(len(comment), len(value))):
                    value_i = ""
                    comment_i = ""

                    if i < len(comment):
                        comment_i = comment[i]
                    if i < len(value):
                        value_i = value[i]

                    entry.append({"value": value_i, "comment": comment_i})

                if len(entry) == 0:
                    entry = [{"value": "", "comment": ""}]

                self.image_metadata["FITSKeywords"][key] = entry

    def xisf_imagedata_2_fitsheader(self):
        commentary_keys = ["HISTORY", "COMMENT", ""]

        bg_pts = []
        for key in self.image_metadata["FITSKeywords"].keys():
            if key.startswith("BG-PTS"):
                try:
                    bg_pts.append(json.loads(self.image_metadata["FITSKeywords"][key][0]["value"]))
                except:
                    logging.warning(f"Could not load background points from xisf image metadata. Affected entry: {self.image_metadata['FITSKeywords'][key]}", stack_info=True)

            else:
                for i in range(len(self.image_metadata["FITSKeywords"][key])):
                    value = self.image_metadata["FITSKeywords"][key][i]["value"]
                    comment = self.image_metadata["FITSKeywords"][key][i]["comment"]

                    # Commentary cards have to comments in Fits standard
                    if key in commentary_keys:
                        if value == "":
                            value = comment

                    if value.isdigit():
                        value = int(value)
                    elif value.isdecimal():
                        value = float(value)

                    self.fits_header[key] = (value, comment)

        if len(bg_pts) > 0:
            self.fits_header["BG-PTS"] = str(bg_pts)
