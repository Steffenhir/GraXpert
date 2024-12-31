import json
import logging
import os
import sys
from textwrap import dedent

import numpy as np
from appdirs import user_config_dir

from graxpert.ai_model_handling import (
    ai_model_path_from_version,
    bge_ai_models_dir,
    denoise_ai_models_dir,
    deconvolution_object_ai_models_dir,
    deconvolution_stars_ai_models_dir,
    download_version,
    latest_version,
    list_local_versions,
)
from graxpert.astroimage import AstroImage
from graxpert.background_extraction import extract_background
from graxpert.denoising import denoise
from graxpert.deconvolution import deconvolve
from graxpert.preferences import Prefs, load_preferences, save_preferences
from graxpert.s3_secrets import bge_bucket_name, denoise_bucket_name, deconvolution_object_bucket_name, deconvolution_stars_bucket_name

user_preferences_filename = os.path.join(user_config_dir(appname="GraXpert"), "preferences.json")


class CmdlineToolBase:
    def __init__(self, args):
        self.args = args

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


class BGECmdlineTool(CmdlineToolBase):
    def __init__(self, args):
        super().__init__(args)

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
                        if "ai_gpu_acceleration" in json_prefs:
                            preferences.ai_gpu_acceleration = json_prefs["ai_gpu_acceleration"]

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

        if self.args.gpu_acceleration is not None:
            preferences.ai_gpu_acceleration = True if self.args.gpu_acceleration == "true" else False
            logging.info(f"Using user-supplied gpu acceleration setting {preferences.ai_gpu_acceleration}.")
        else:
            logging.info(f"Using stored gpu acceleration setting {preferences.ai_gpu_acceleration}.")

        if preferences.interpol_type_option == "AI":
            ai_model_path = ai_model_path_from_version(bge_ai_models_dir, self.get_ai_version(preferences))
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
                ai_gpu_acceleration=preferences.ai_gpu_acceleration,
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
            ai_version = prefs.bge_ai_version

        if ai_version is None:
            ai_version = latest_version(bge_ai_models_dir, bge_bucket_name)
            logging.info(f"Using AI version {ai_version}. You can overwrite this by providing the argument '-ai_version'")

        if not ai_version in [v["version"] for v in list_local_versions(bge_ai_models_dir)]:
            try:
                logging.info(f"AI version {ai_version} not found locally, downloading...")
                download_version(bge_ai_models_dir, bge_bucket_name, ai_version)
                logging.info("download successful")
            except Exception as e:
                logging.exception(e)
                logging.shutdown()
                sys.exit(1)

        user_preferences.ai_version = ai_version
        save_preferences(user_preferences_filename, user_preferences)

        return ai_version

    def get_background_save_path(self):
        save_path = self.get_save_path()
        return os.path.splitext(save_path)[0] + "_background" + self.get_output_file_ending()


class DenoiseCmdlineTool(CmdlineToolBase):
    def __init__(self, args):
        super().__init__(args)
        self.args = args

    def execute(self):
        astro_Image = AstroImage(do_update_display=False)
        astro_Image.set_from_file(self.args.filename, None, None)

        processed_Astro_Image = AstroImage(do_update_display=False)

        processed_Astro_Image.fits_header = astro_Image.fits_header

        if self.args.preferences_file is not None:
            preferences = Prefs()
            try:
                preferences_file = os.path.abspath(self.args.preferences_file)
                if os.path.isfile(preferences_file):
                    with open(preferences_file, "r") as f:
                        json_prefs = json.load(f)
                        if "ai_version" in json_prefs:
                            preferences.ai_version = json_prefs["ai_version"]
                        if "denoise_strength" in json_prefs:
                            preferences.denoise_strength = json_prefs["denoise_strength"]
                        if "ai_batch_size" in json_prefs:
                            preferences.ai_batch_size = json_prefs["ai_batch_size"]
                        if "ai_gpu_acceleration" in json_prefs:
                            preferences.ai_gpu_acceleration = json_prefs["ai_gpu_acceleration"]

            except Exception as e:
                logging.exception(e)
                logging.shutdown()
                sys.exit(1)
        else:
            preferences = Prefs()

        if self.args.denoise_strength is not None:
            preferences.denoise_strength = self.args.denoise_strength
            logging.info(f"Using user-supplied denoise strength value {preferences.denoise_strength}.")
        else:
            logging.info(f"Using stored denoise strength value {preferences.denoise_strength}.")

        if self.args.ai_batch_size is not None:
            preferences.ai_batch_size = self.args.ai_batch_size
            logging.info(f"Using user-supplied batch size value {preferences.ai_batch_size}.")
        else:
            logging.info(f"Using stored batch size value {preferences.ai_batch_size}.")

        if self.args.gpu_acceleration is not None:
            preferences.ai_gpu_acceleration = True if self.args.gpu_acceleration == "true" else False
            logging.info(f"Using user-supplied gpu acceleration setting {preferences.ai_gpu_acceleration}.")
        else:
            logging.info(f"Using stored gpu acceleration setting {preferences.ai_gpu_acceleration}.")

        ai_model_path = ai_model_path_from_version(denoise_ai_models_dir, self.get_ai_version(preferences))

        logging.info(
            dedent(
                f"""\
                    Excecuting denoising with the following parameters:
                    AI model path - {ai_model_path}
                    denoise strength - {preferences.denoise_strength}"""
            )
        )

        processed_Astro_Image.set_from_array(
            denoise(astro_Image.img_array, ai_model_path, preferences.denoise_strength, batch_size=preferences.ai_batch_size, ai_gpu_acceleration=preferences.ai_gpu_acceleration)
        )
        processed_Astro_Image.save(self.get_save_path(), self.get_output_file_format())

    def get_ai_version(self, prefs):
        user_preferences = load_preferences(user_preferences_filename)

        ai_version = None
        if self.args.ai_version:
            ai_version = self.args.ai_version
            logging.info(f"Using user-supplied AI version {ai_version}.")
        else:
            ai_version = prefs.denoise_ai_version

        if ai_version is None:
            ai_version = latest_version(denoise_ai_models_dir, denoise_bucket_name)
            logging.info(f"Using AI version {ai_version}. You can overwrite this by providing the argument '-ai_version'")

        if not ai_version in [v["version"] for v in list_local_versions(denoise_ai_models_dir)]:
            try:
                logging.info(f"AI version {ai_version} not found locally, downloading...")
                download_version(denoise_ai_models_dir, denoise_bucket_name, ai_version)
                logging.info("download successful")
            except Exception as e:
                logging.exception(e)
                logging.shutdown()
                sys.exit(1)

        user_preferences.ai_version = ai_version
        save_preferences(user_preferences_filename, user_preferences)

        return ai_version


class DeconvObjCmdlineTool(CmdlineToolBase):
    def __init__(self, args):
        super().__init__(args)
        self.args = args

    def execute(self):
        astro_Image = AstroImage(do_update_display=False)
        astro_Image.set_from_file(self.args.filename, None, None)

        processed_Astro_Image = AstroImage(do_update_display=False)

        processed_Astro_Image.fits_header = astro_Image.fits_header

        if self.args.preferences_file is not None:
            preferences = Prefs()
            try:
                preferences_file = os.path.abspath(self.args.preferences_file)
                if os.path.isfile(preferences_file):
                    with open(preferences_file, "r") as f:
                        json_prefs = json.load(f)
                        if "ai_version" in json_prefs:
                            preferences.ai_version = json_prefs["ai_version"]
                        if "deconvolution_strength" in json_prefs:
                            preferences.deconvolution_strength = json_prefs["deconvolution_strength"]
                        if "deconvolution_psfsize" in json_prefs:
                            preferences.deconvolution_psfsize = json_prefs["deconvolution_psfsize"]
                        if "ai_batch_size" in json_prefs:
                            preferences.ai_batch_size = json_prefs["ai_batch_size"]
                        if "ai_gpu_acceleration" in json_prefs:
                            preferences.ai_gpu_acceleration = json_prefs["ai_gpu_acceleration"]

            except Exception as e:
                logging.exception(e)
                logging.shutdown()
                sys.exit(1)
        else:
            preferences = Prefs()

        if self.args.deconvolution_strength is not None:
            preferences.deconvolution_strength = self.args.deconvolution_strength
            logging.info(f"Using user-supplied deconvolution strength value {preferences.deconvolution_strength}.")
        else:
            logging.info(f"Using stored deconvolution strength value {preferences.deconvolution_strength}.")

        if self.args.deconvolution_psfsize is not None:
            preferences.deconvolution_psfsize = self.args.deconvolution_psfsize
            logging.info(f"Using user-supplied deconvolution psfsize value {preferences.deconvolution_psfsize}.")
        else:
            logging.info(f"Using stored deconvolution psfsize value {preferences.deconvolution_psfsize}.")

        if self.args.ai_batch_size is not None:
            preferences.ai_batch_size = self.args.ai_batch_size
            logging.info(f"Using user-supplied batch size value {preferences.ai_batch_size}.")
        else:
            logging.info(f"Using stored batch size value {preferences.ai_batch_size}.")

        if self.args.gpu_acceleration is not None:
            preferences.ai_gpu_acceleration = True if self.args.gpu_acceleration == "true" else False
            logging.info(f"Using user-supplied gpu acceleration setting {preferences.ai_gpu_acceleration}.")
        else:
            logging.info(f"Using stored gpu acceleration setting {preferences.ai_gpu_acceleration}.")

        ai_model_path = ai_model_path_from_version(deconvolution_object_ai_models_dir, self.get_ai_version(preferences))

        logging.info(
            dedent(
                f"""\
                    Excecuting deconvolution on objects with the following parameters:
                    AI model path - {ai_model_path}
                    deconvolution strength - {preferences.deconvolution_strength}
                    deconvolution psfsize - {preferences.deconvolution_psfsize}"""
            )
        )

        processed_Astro_Image.set_from_array(
            deconvolve(
                astro_Image.img_array,
                ai_model_path,
                preferences.deconvolution_strength,
                preferences.deconvolution_psfsize,
                batch_size=preferences.ai_batch_size,
                ai_gpu_acceleration=preferences.ai_gpu_acceleration,
            )
        )
        processed_Astro_Image.save(self.get_save_path(), self.get_output_file_format())

    def get_ai_version(self, prefs):
        user_preferences = load_preferences(user_preferences_filename)

        ai_version = None
        if self.args.ai_version:
            ai_version = self.args.ai_version
            logging.info(f"Using user-supplied AI version {ai_version}.")
        else:
            ai_version = prefs.deconvolution_object_ai_version

        if ai_version is None:
            ai_version = latest_version(deconvolution_object_ai_models_dir, deconvolution_object_bucket_name)
            logging.info(f"Using AI version {ai_version}. You can overwrite this by providing the argument '-ai_version'")

        if not ai_version in [v["version"] for v in list_local_versions(deconvolution_object_ai_models_dir)]:
            try:
                logging.info(f"AI version {ai_version} not found locally, downloading...")
                download_version(deconvolution_object_ai_models_dir, deconvolution_object_bucket_name, ai_version)
                logging.info("download successful")
            except Exception as e:
                logging.exception(e)
                logging.shutdown()
                sys.exit(1)

        user_preferences.ai_version = ai_version
        save_preferences(user_preferences_filename, user_preferences)

        return ai_version


class DeconvStellarCmdlineTool(CmdlineToolBase):
    def __init__(self, args):
        super().__init__(args)
        self.args = args

    def execute(self):
        astro_Image = AstroImage(do_update_display=False)
        astro_Image.set_from_file(self.args.filename, None, None)

        processed_Astro_Image = AstroImage(do_update_display=False)

        processed_Astro_Image.fits_header = astro_Image.fits_header

        if self.args.preferences_file is not None:
            preferences = Prefs()
            try:
                preferences_file = os.path.abspath(self.args.preferences_file)
                if os.path.isfile(preferences_file):
                    with open(preferences_file, "r") as f:
                        json_prefs = json.load(f)
                        if "ai_version" in json_prefs:
                            preferences.ai_version = json_prefs["ai_version"]
                        if "deconvolution_strength" in json_prefs:
                            preferences.deconvolution_strength = json_prefs["deconvolution_strength"]
                        if "deconvolution_psfsize" in json_prefs:
                            preferences.deconvolution_psfsize = json_prefs["deconvolution_psfsize"]
                        if "ai_batch_size" in json_prefs:
                            preferences.ai_batch_size = json_prefs["ai_batch_size"]
                        if "ai_gpu_acceleration" in json_prefs:
                            preferences.ai_gpu_acceleration = json_prefs["ai_gpu_acceleration"]

            except Exception as e:
                logging.exception(e)
                logging.shutdown()
                sys.exit(1)
        else:
            preferences = Prefs()

        if self.args.deconvolution_strength is not None:
            preferences.deconvolution_strength = self.args.deconvolution_strength
            logging.info(f"Using user-supplied deconvolution strength value {preferences.deconvolution_strength}.")
        else:
            logging.info(f"Using stored deconvolution strength value {preferences.deconvolution_strength}.")

        if self.args.deconvolution_psfsize is not None:
            preferences.deconvolution_psfsize = self.args.deconvolution_psfsize
            logging.info(f"Using user-supplied deconvolution psfsize value {preferences.deconvolution_psfsize}.")
        else:
            logging.info(f"Using stored deconvolution psfsize value {preferences.deconvolution_psfsize}.")

        if self.args.ai_batch_size is not None:
            preferences.ai_batch_size = self.args.ai_batch_size
            logging.info(f"Using user-supplied batch size value {preferences.ai_batch_size}.")
        else:
            logging.info(f"Using stored batch size value {preferences.ai_batch_size}.")

        if self.args.gpu_acceleration is not None:
            preferences.ai_gpu_acceleration = True if self.args.gpu_acceleration == "true" else False
            logging.info(f"Using user-supplied gpu acceleration setting {preferences.ai_gpu_acceleration}.")
        else:
            logging.info(f"Using stored gpu acceleration setting {preferences.ai_gpu_acceleration}.")

        ai_model_path = ai_model_path_from_version(deconvolution_stars_ai_models_dir, self.get_ai_version(preferences))

        logging.info(
            dedent(
                f"""\
                    Excecuting deconvolution on stellar with the following parameters:
                    AI model path - {ai_model_path}
                    deconvolution strength - {preferences.deconvolution_strength}
                    deconvolution psfsize - {preferences.deconvolution_psfsize}"""
            )
        )

        processed_Astro_Image.set_from_array(
            deconvolve(
                astro_Image.img_array,
                ai_model_path,
                preferences.deconvolution_strength,
                preferences.deconvolution_psfsize,
                batch_size=preferences.ai_batch_size,
                ai_gpu_acceleration=preferences.ai_gpu_acceleration,
            )
        )
        processed_Astro_Image.save(self.get_save_path(), self.get_output_file_format())

    def get_ai_version(self, prefs):
        user_preferences = load_preferences(user_preferences_filename)

        ai_version = None
        if self.args.ai_version:
            ai_version = self.args.ai_version
            logging.info(f"Using user-supplied AI version {ai_version}.")
        else:
            ai_version = prefs.deconvolution_stars_ai_version

        if ai_version is None:
            ai_version = latest_version(deconvolution_stars_ai_models_dir, deconvolution_stars_bucket_name)
            logging.info(f"Using AI version {ai_version}. You can overwrite this by providing the argument '-ai_version'")

        if not ai_version in [v["version"] for v in list_local_versions(deconvolution_stars_ai_models_dir)]:
            try:
                logging.info(f"AI version {ai_version} not found locally, downloading...")
                download_version(deconvolution_stars_ai_models_dir, deconvolution_stars_bucket_name, ai_version)
                logging.info("download successful")
            except Exception as e:
                logging.exception(e)
                logging.shutdown()
                sys.exit(1)

        user_preferences.ai_version = ai_version
        save_preferences(user_preferences_filename, user_preferences)

        return ai_version
