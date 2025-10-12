import os
import shutil
from importlib import resources

import customtkinter

from graxpert.resource_utils import resource_path, temp_resource_path
from graxpert.ui_scaling import get_scaling_factor


def style():
    theme_file = "graxpert-dark-blue.json"

    # Use importlib.resources to get a reliable path to the theme file
    # This works whether the code is run from source or installed via pip/pipx
    with resources.as_file(resources.files('graxpert.theme').joinpath(theme_file)) as theme_path:
        # Now copy the file from the reliably found path
        shutil.copy(theme_path, temp_resource_path(theme_file))

    customtkinter.set_default_color_theme(temp_resource_path(theme_file))
    customtkinter.set_appearance_mode("dark")
    scaling = get_scaling_factor()
    customtkinter.set_widget_scaling(scaling)
