import json
import logging
import os
import sys
from textwrap import dedent

import numpy as np
from appdirs import user_config_dir

from graxpert.ai_model_handling import ai_model_path_from_version, download_version, latest_version, list_local_versions
from graxpert.astroimage import AstroImage
from graxpert.background_extraction import extract_background
from graxpert.preferences import Prefs, load_preferences, save_preferences

user_preferences_filename = os.path.join(user_config_dir(appname="GraXpert"), "preferences.json")


class CommandLineTool:
    def __init__(self, args):
        self.args = args

    def execute(self):
        astro_Image = AstroImage(do_update_display=False)
        astro_Image.set_from_file(self.args.filename, None, None)

        processed_Astro_Image = AstroImage(do_update_display=False)
        background_Astro_Image = AstroImage(do_update_display=False)

        processed_Astro_Image.fits_header = astro_Image.fits_header
        background_Astro_Image.fits_header = astro_Image.fits_header

        downscale_factor = 1

        if self.args.preferences_file is not None:
            preferences = Prefs()
            preferences.interpol_type_option = "AI"
            try:
                preferences_file = os.path.abspath(self.args.preferences_file)
                if os.path.isfile(preferences_file):
                    with open(preferences_file, "r") as f:
                        json_prefs = json.load(f)
                        if "background_points" in json_prefs:
                            preferences.background_points = json_prefs["background_points"]
                        if "RBF_kernel" in json_prefs:
                            preferences.RBF_kernel = json_prefs["RBF_kernel"]
                        if "interpol_type_option" in json_prefs:
                            preferences.interpol_type_option = json_prefs["interpol_type_option"]
                        if "smoothing_option" in json_prefs:
                            preferences.smoothing_option = json_prefs["smoothing_option"]
                        if "sample_size" in json_prefs:
                            preferences.sample_size = json_prefs["sample_size"]
                        if "spline_order" in json_prefs:
                            preferences.spline_order = json_prefs["spline_order"]
                        if "corr_type" in json_prefs:
                            preferences.corr_type = json_prefs["corr_type"]
                        if "ai_version" in json_prefs:
                            preferences.ai_version = json_prefs["ai_version"]

                        if preferences.interpol_type_option == "Kriging" or preferences.interpol_type_option == "RBF":
                            downscale_factor = 4

            except Exception as e:
                logging.exception(e)
                logging.shutdown()
                sys.exit(1)
        else:
            preferences = Prefs()
            preferences.interpol_type_option = "AI"

        if self.args.smoothing is not None:
            preferences.smoothing_option = self.args.smoothing
            logging.info(f"Using user-supplied smoothing value {preferences.smoothing_option}.")
        else:
            logging.info(f"Using stored smoothing value {preferences.smoothing_option}.")

        if self.args.correction is not None:
            preferences.corr_type = self.args.correction
            logging.info(f"Using user-supplied correction type {preferences.corr_type}.")
        else:
            logging.info(f"Using stored correction type {preferences.corr_type}.")

        if preferences.interpol_type_option == "AI":
            ai_model_path = ai_model_path_from_version(self.get_ai_version(preferences))
        else:
            ai_model_path = None

        if preferences.interpol_type_option == "AI":
            logging.info(
                dedent(
                    f"""\
                        Excecuting background extraction with the following parameters:
                        interpolation type - {preferences.interpol_type_option}
                                 smoothing - {preferences.smoothing_option}
                           correction type - {preferences.corr_type}
                             AI model path - {ai_model_path}"""
                )
            )
        else:
            logging.info(
                dedent(
                    f"""\
                        Excecuting background extraction with the following parameters:
                        interpolation type - {preferences.interpol_type_option}
                         background points - {preferences.background_points}
                               sample size - {preferences.sample_size}
                                    kernel - {preferences.RBF_kernel}
                              spline order - {preferences.spline_order}
                                 smoothing - {preferences.smoothing_option}
                            orrection type - {preferences.corr_type}
                         downscale_factor  - {downscale_factor}"""
                )
            )

        background_Astro_Image.set_from_array(
            extract_background(
                astro_Image.img_array,
                np.array(preferences.background_points),
                preferences.interpol_type_option,
                preferences.smoothing_option,
                downscale_factor,
                preferences.sample_size,
                preferences.RBF_kernel,
                preferences.spline_order,
                preferences.corr_type,
                ai_model_path,
            )
        )

        processed_Astro_Image.set_from_array(astro_Image.img_array)

        processed_Astro_Image.save(self.get_save_path(), self.get_output_file_format())
        if self.args.bg:
            background_Astro_Image.save(self.get_background_save_path(), self.get_output_file_format())

    def get_ai_version(self, prefs):
        user_preferences = load_preferences(user_preferences_filename)

        ai_version = None
        if self.args.ai_version:
            ai_version = self.args.ai_version
            logging.info(f"Using user-supplied AI version {ai_version}.")
        else:
            ai_version = prefs.ai_version

        if ai_version is None:
            ai_version = latest_version()
            logging.info(f"Using AI version {ai_version}. You can overwrite this by providing the argument '-ai_version'")

        if not ai_version in [v["version"] for v in list_local_versions()]:
            try:
                logging.info(f"AI version {ai_version} not found locally, downloading...")
                download_version(ai_version)
                logging.info("download successful")
            except Exception as e:
                logging.exception(e)
                logging.shutdown()
                sys.exit(1)

        user_preferences.ai_version = ai_version
        save_preferences(user_preferences_filename, user_preferences)

        return ai_version

    def get_output_file_ending(self):
        file_ending = os.path.splitext(self.args.filename)[-1]

        if file_ending.lower() == ".xisf":
            return ".xisf"
        else:
            return ".fits"

    def get_output_file_format(self):
        output_file_ending = self.get_output_file_ending()
        if (output_file_ending) == ".xisf":
            return "32 bit XISF"
        else:
            return "32 bit Fits"

    def get_save_path(self):
        if self.args.output is not None:
            base_path = os.path.dirname(self.args.filename)
            output_file_name = self.args.output + self.get_output_file_ending()
            return os.path.join(base_path, output_file_name)

        else:
            return os.path.splitext(self.args.filename)[0] + "_GraXpert" + self.get_output_file_ending()

    def get_background_save_path(self):
        save_path = self.get_save_path()
        return os.path.splitext(save_path)[0] + "_background" + self.get_output_file_ending()
