import json
import logging
import os
import shutil
from datetime import datetime
from typing import AnyStr, List, TypedDict

import numpy as np

from app_state import AppState


class Prefs(TypedDict):
    working_dir: AnyStr
    width: int
    height: int
    background_points: List
    bg_flood_selection_option: bool
    bg_pts_option: int
    stretch_option: AnyStr
    saturation: float
    bg_tol_option: float
    interpol_type_option: AnyStr
    smoothing_option: float
    saveas_option: AnyStr
    sample_size: int
    sample_color: int
    RBF_kernel: AnyStr
    lang: AnyStr
    corr_type: AnyStr

DEFAULT_PREFS: Prefs = {
    "working_dir": os.getcwd(),
    "width": None,
    "height": None,
    "background_points": [],
    "bg_flood_selection_option": False,
    "bg_pts_option": 15,
    "stretch_option": "No Stretch",
    "saturation": 1.0,
    "bg_tol_option": 1.0,
    "interpol_type_option": "RBF",
    "smoothing_option": 1.0,
    "saveas_option": "32 bit Tiff",
    "sample_size": 25,
    "sample_color": 55,
    "RBF_kernel": "thin_plate",
    "spline_order": 3,
    "lang": None,
    "corr_type": "Subtraction"
}


def app_state_2_prefs(prefs: Prefs, app_state: AppState, app) -> Prefs:
    if "background_points" in app_state:
        prefs["background_points"] = [p.tolist() for p in app_state["background_points"]]
        prefs["bg_pts_option"] = app.bg_pts.get()
        prefs["stretch_option"] = app.stretch_option_current.get()
        prefs["saturation"] = app.saturation.get()
        prefs["bg_tol_option"] = app.bg_tol.get()
        prefs["interpol_type_option"] = app.interpol_type.get()
        prefs["smoothing_option"] = app.smoothing.get()
        prefs["saveas_option"] = app.saveas_type.get()
        prefs["sample_size"] = app.sample_size.get()
        prefs["sample_color"] = app.sample_color.get()
        prefs["RBF_kernel"] = app.RBF_kernel.get()
        prefs["spline_order"] = app.spline_order.get()
        prefs["lang"] = app.lang.get()
        prefs["corr_type"] = app.corr_type.get()
        prefs["bg_flood_selection_option"] = app.flood_select_pts.get()
    return prefs


def prefs_2_app_state(prefs: Prefs, app_state: AppState) -> AppState:
    if "background_points" in prefs:
        app_state["background_points"] = [np.array(p) for p in prefs["background_points"]]
    return app_state


def merge_json(prefs: Prefs, json) -> Prefs:
    if "working_dir" in json:
        prefs["working_dir"] = json["working_dir"]
    if "width" in json:
        prefs["width"] = json["width"]
    if "height" in json:
        prefs["height"] = json["height"]
    if "background_points" in json:
        prefs["background_points"] = json["background_points"]
    if "bg_flood_selection_option" in json:
        prefs["bg_flood_selection_option"] = json["bg_flood_selection_option"]
    if "bg_pts_option" in json:
        prefs["bg_pts_option"] = json["bg_pts_option"]
    if "stretch_option" in json:
        prefs["stretch_option"] = json["stretch_option"]
    if "saturation" in json:
        prefs["saturation"] = json["saturation"]
    if "bg_tol_option" in json:
        prefs["bg_tol_option"] = json["bg_tol_option"]
    if "interpol_type_option" in json:
        prefs["interpol_type_option"] = json["interpol_type_option"]
    if "smoothing_option" in json:
        prefs["smoothing_option"] = json["smoothing_option"]
    if "saveas_option" in json:
        prefs["saveas_option"] = json["saveas_option"]
    if "sample_size" in json:
        prefs["sample_size"] = json["sample_size"]
    if "sample_color" in json:
        prefs["sample_color"] = json["sample_color"]
    if "RBF_kernel" in json:
        prefs["RBF_kernel"] = json["RBF_kernel"]
    if "spline_order" in json:
        prefs["spline_order"] = json["spline_order"]
    if "lang" in json:
        prefs["lang"] = json["lang"]
    if "corr_type" in json:
        prefs["corr_type"] = json["corr_type"]
    return prefs


def load_preferences(prefs_filename) -> Prefs:
    prefs = DEFAULT_PREFS
    try:
        if os.path.isfile(prefs_filename):
            with open(prefs_filename) as f:
                    json_prefs: Prefs = json.load(f)
                    prefs = merge_json(prefs, json_prefs)
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
            json.dump(prefs, f)
    except OSError as err:
        logging.exception("error serializing preferences")


def app_state_2_fitsheader(app, app_state, fits_header):
    prefs = Prefs()
    prefs = app_state_2_prefs(prefs, app_state, app)
    fits_header["INTP-OPT"] = prefs["interpol_type_option"]
    fits_header["SMOOTHING"] = prefs["smoothing_option"]
    fits_header["SAMPLE-SIZE"] = prefs["sample_size"]
    fits_header["RBF-KERNEL"] = prefs["RBF_kernel"]
    fits_header["SPLINE-ORDER"] = prefs["spline_order"]
    fits_header["CORR-TYPE"] = prefs["corr_type"]
    fits_header["BG-PTS"] = str(prefs["background_points"])
    
    return fits_header


def fitsheader_2_app_state(app, app_state, fits_header):
    if "BG-PTS" in fits_header.keys():
        app_state["background_points"] = [np.array(p) for p in json.loads(fits_header["BG-PTS"])]
    
    if "INTP-OPT" in fits_header.keys():
        app.interpol_type.set(fits_header["INTP-OPT"])
        app.smoothing_slider.set(fits_header["SMOOTHING"])
        app.help_panel.sample_size_slider.set(fits_header["SAMPLE-SIZE"])
        app.RBF_kernel.set(fits_header["RBF-KERNEL"])
        app.spline_order.set(fits_header["SPLINE-ORDER"])
        app.corr_type.set(fits_header["CORR-TYPE"])
    
    return app_state
    
