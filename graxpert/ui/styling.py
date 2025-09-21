import os
import shutil

import customtkinter

from graxpert.resource_utils import resource_path, temp_resource_path
from graxpert.ui_scaling import get_scaling_factor


def style():
    theme_file = "graxpert-dark-blue.json"
    os.makedirs(os.path.dirname(temp_resource_path(theme_file)), exist_ok=True)
    shutil.copy(resource_path(theme_file), temp_resource_path(theme_file))
    customtkinter.set_default_color_theme(temp_resource_path(theme_file))
    customtkinter.set_appearance_mode("dark")
    scaling = get_scaling_factor()
    customtkinter.set_widget_scaling(scaling)
