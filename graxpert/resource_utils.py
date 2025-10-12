# from appdirs import
import os

from tempfile import TemporaryDirectory
from importlib import resources

temp_resource_dir = TemporaryDirectory()

def temp_cleanup():
    temp_resource_dir.cleanup()

def resource_path(relative_path):
    base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(base_path, relative_path)


def temp_resource_path(relative_path):
    return os.path.join(temp_resource_dir.name, relative_path)


def resource_bytestream(name, dir = 'img'):
    return resources.files(f'graxpert.{dir}').joinpath(name).open('rb')


def resource_image(name):
    from PIL import Image
    with resources.as_file(resources.files('graxpert.img').joinpath(name)) as file_path:
        return Image.open(file_path)


# Unfortunately tk.PhotoImage doesn't accept file-like objects, so we need to use a temporary file
def resource_photoimage(resource_name):
    import tkinter as tk
    with resources.as_file(resources.files('graxpert.img').joinpath(resource_name)) as file_path:
        return tk.PhotoImage(file=file_path)