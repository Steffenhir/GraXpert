# from appdirs import
import os
import sys
from tempfile import TemporaryDirectory

import numpy as np
from skimage import io
from skimage.transform import resize

temp_resource_dir = TemporaryDirectory()


def resource_path(relative_path):
    if getattr(sys, "frozen", False):
        # The application is frozen
        base_path = os.path.join(os.path.dirname(sys.executable), "lib")
    else:
        # The application is not frozen
        base_path = os.path.join(os.path.dirname(__file__), "..")
    return os.path.join(base_path, relative_path)


def temp_resource_path(relative_path):
    return os.path.join(temp_resource_dir.name, relative_path)
