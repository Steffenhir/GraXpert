import os
from typing import AnyStr, List, TypedDict

import numpy as np

from app_state import AppState


class Prefs(TypedDict):
    working_dir: AnyStr
    width: int
    height: int
    background_points: List
    bg_pts_option: int
    stretch_option: AnyStr
    bg_tol_option: float
    interpol_type_option: AnyStr
    smoothing_option: float
    saveas_option: AnyStr
    sample_size: int
    sample_color: int
    RBF_kernel: AnyStr
    lang: AnyStr

DEFAULT_PREFS: Prefs = {
    "working_dir": os.getcwd(),
    "width": None,
    "height": None,
    "background_points": [],
    "bg_pts_option": 15,
    "stretch_option": "No Stretch",
    "bg_tol_option": 1.0,
    "interpol_type_option": "RBF",
    "smoothing_option": 1.0,
    "saveas_option": "32 bit Tiff",
    "sample_size": 25,
    "sample_color": 55,
    "RBF_kernel": "thin_plate",
    "spline_order": 3,
    "lang": None
}

def app_state_2_prefs(prefs: Prefs, app_state: AppState) -> Prefs:
    if "background_points" in app_state:
        prefs["background_points"] = [p.tolist() for p in app_state["background_points"]]
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
    if "bg_pts_option" in json:
        prefs["bg_pts_option"] = json["bg_pts_option"]
    if "stretch_option" in json:
        prefs["stretch_option"] = json["stretch_option"]
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
    return prefs