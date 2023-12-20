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


def scale_img(relative_path, scaling, shape):
    os.makedirs(os.path.dirname(temp_resource_path(relative_path)), exist_ok=True)
    
    img = io.imread(resource_path(relative_path))
    img = resize(img, (int(shape[0] * scaling), int(shape[1] * scaling)))
    img = img * 255
    img = img.astype(dtype=np.uint8)
    io.imsave(
        temp_resource_path(relative_path.replace(".png", "-scaled.png")),
        img,
        check_contrast=False,
    )
