# from appdirs import
import os
from tempfile import TemporaryDirectory

temp_resource_dir = TemporaryDirectory()


def resource_path(relative_path):
    base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(base_path, relative_path)


def temp_resource_path(relative_path):
    return os.path.join(temp_resource_dir.name, relative_path)
