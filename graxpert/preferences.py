import json
import logging
import os
import shutil
from dataclasses import asdict, dataclass, field, fields
from datetime import datetime
from typing import AnyStr, List

import numpy as np

from graxpert.app_state import AppState
from graxpert.version import version as graxpert_version


@dataclass
class Prefs:
    working_dir: AnyStr = os.getcwd()
    width: int = None
    height: int = None
    background_points: List = field(default_factory=list)
    bg_flood_selection_option: bool = False
    bg_pts_option: int = 15
    stretch_option: AnyStr = "No Stretch"
    saturation: float = 1.0
    channels_linked_option: bool = False
    images_linked_option: bool = False
    display_pts: bool = True
    bg_tol_option: float = 1.0
    interpol_type_option: AnyStr = "RBF"
    smoothing_option: float = 0.0
    saveas_option: AnyStr = "32 bit Tiff"
    saveas_stretched: bool = False
    sample_size: int = 25
    sample_color: int = 55
    RBF_kernel: AnyStr = "thin_plate"
    spline_order: int = 3
    lang: AnyStr = None
    corr_type: AnyStr = "Subtraction"
    scaling: float = 1.0
    bge_ai_version: AnyStr = None
    deconvolution_type_option: AnyStr = "Object-only"
    deconvolution_object_ai_version: AnyStr = None
    deconvolution_stars_ai_version: AnyStr = None
    denoise_ai_version: AnyStr = None
    graxpert_version: AnyStr = graxpert_version
    deconvolution_strength: float = 0.5
    deconvolution_psfsize: float = 5.0
    denoise_strength: float = 0.5
    ai_batch_size: int = 4
    ai_gpu_acceleration: bool = True


def app_state_2_prefs(prefs: Prefs, app_state: AppState) -> Prefs:
    prefs.background_points = [p.tolist() for p in app_state.background_points]
    return prefs


def prefs_2_app_state(prefs: Prefs, app_state: AppState) -> AppState:
    app_state.background_points = [np.array(p) for p in prefs.background_points]
    return app_state


def merge_json(prefs: Prefs, json) -> Prefs:
    for f in fields(prefs):
        if f.name in json:
            setattr(prefs, f.name, json[f.name])
    return prefs


def load_preferences(prefs_filename) -> Prefs:
    prefs = Prefs()
    try:
        if os.path.isfile(prefs_filename):
            with open(prefs_filename) as f:
                json_prefs = json.load(f)

                if "ai_version" in json_prefs:
                    logging.warning(f"Obsolete key 'ai_version' found in {prefs_filename}. Renaming it to 'bge_ai_version.")
                    json_prefs = {"bge_ai_version" if k == "ai_version" else k: v for k, v in json_prefs.items()}

                prefs = merge_json(prefs, json_prefs)

                if not "graxpert_version" in json_prefs:  # reset scaling in case we start from GraXpert < 2.1.0
                    prefs.scaling = 1.0
        else:
            logging.info("{} appears to be missing. it will be created after program shutdown".format(prefs_filename))
    except:
        logging.exception("could not load preferences.json from {}".format(prefs_filename))
        if os.path.isfile(prefs_filename):
            # make a backup of the old preferences file so we don't loose it
            backup_filename = os.path.join(os.path.dirname(prefs_filename), datetime.now().strftime("%m-%d-%Y_%H-%M-%S_{}".format(os.path.basename(prefs_filename))))
            shutil.copyfile(prefs_filename, backup_filename)
    return prefs


def save_preferences(prefs_filename, prefs):
    try:
        os.makedirs(os.path.dirname(prefs_filename), exist_ok=True)
        with open(prefs_filename, "w") as f:
            json.dump(asdict(prefs), f)
    except OSError as err:
        logging.exception("error serializing preferences")


def app_state_2_fitsheader(prefs: Prefs, app_state: AppState, fits_header):
    fits_header["INTP-OPT"] = prefs.interpol_type_option
    fits_header["SMOOTH"] = prefs.smoothing_option
    fits_header["CORRTYPE"] = prefs.corr_type

    if prefs.interpol_type_option == "AI":
        fits_header["BGAI_VER"] = prefs.bge_ai_version

    if prefs.interpol_type_option != "AI":
        fits_header["SAMPSIZE"] = prefs.sample_size
        fits_header["RBFKRNL"] = prefs.RBF_kernel
        fits_header["SPLNORDR"] = prefs.spline_order
        fits_header["BG-PTS"] = str(list(map(lambda e: e.tolist(), app_state.background_points)))

    return fits_header


def fitsheader_2_app_state(prefs: Prefs, app_state: AppState, fits_header):
    if "BG-PTS" in fits_header.keys():
        try:
            app_state.background_points = [np.array(p) for p in json.loads(fits_header["BG-PTS"])]
        except:
            logging.warning("Could not transfer background points from fits header to application state", stack_info=True)

    if "INTP-OPT" in fits_header.keys():
        prefs.interpol_type_option = fits_header["INTP-OPT"]
        prefs.smoothing_option = fits_header["SMOOTH"]
        prefs.corr_type = fits_header["CORRTYPE"]

        if fits_header["INTP-OPT"] != "AI":
            prefs.sample_size = fits_header["SAMPSIZE"]
            prefs.RBF_kernel = fits_header["RBFKRNL"]
            prefs.spline_order = fits_header["SPLNORDR"]

    return app_state
