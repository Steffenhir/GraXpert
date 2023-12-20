import os
from tkinter import ttk

import customtkinter

from graxpert.resource_utils import resource_path
from graxpert.ui_scaling import get_scaling_factor


def style(root):
    customtkinter.set_default_color_theme(resource_path("graxpert-dark-blue.json"))
    customtkinter.set_appearance_mode("dark")
    scaling = get_scaling_factor()
    customtkinter.set_widget_scaling(scaling)
