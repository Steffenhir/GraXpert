import os
import sys

import astropy
from cx_Freeze import Executable, setup

from graxpert.version import release, version

astropy_path = os.path.dirname(os.path.abspath(astropy.__file__))

directory_table = [("ProgramMenuFolder", "TARGETDIR", "."), ("GraXpert", "ProgramMenuFolder", "GraXpert")]

msi_data = {
    "Directory": directory_table,
    "ProgId": [("Prog.Id", None, None, "GraXpert is an astronomical image processing program for extracting and removing gradients in the background of your astrophotos", "IconId", None)],
    "Icon": [("IconId", "./img/Icon.ico")],
}

msi_summary_data = {"author": "GraXpert Development Team", "comments": "<info@graxpert.com>"}

bdist_msi_options = {
    "add_to_path": True,
    "data": msi_data,
    "summary_data": msi_summary_data,
    "upgrade_code": "{8887032b-9211-4752-8f88-6d29833bb001}",
    "target_name": "GraXpert",
    "install_icon": "./img/Icon.ico",
}

bidst_rpm_options = {"release": release, "vendor": "GraXpert Development Team <info@graxpert.com>", "group": "Unspecified"}

build_options = {
    "includes": ["astropy.constants.codata2018", "astropy.constants.iau2015", "imageio.plugins.pillow", "skimage.draw.draw", "skimage.exposure.exposure", "skimage.filters._gaussian"],
    "include_files": [
        ["./img", "./lib/img"],
        ["./graxpert-dark-blue.json", "./lib/graxpert-dark-blue.json"],
        ["./locales/", "./lib/locales/"],
        [os.path.join(astropy_path, "units", "format", "generic_parsetab.py"), "./lib/astropy/units/format/generic_parsetab.py"],
        [os.path.join(astropy_path, "units", "format", "generic_lextab.py"), "./lib/astropy/units/format/generic_lextab.py"],
    ],
    "excludes": [],
    "include_msvcr": True,
}

base = "Win32GUI" if sys.platform == "win32" else None

executables = [Executable("./graxpert/main.py", base=base, icon="./img/Icon.ico", target_name="GraXpert", shortcut_name="GraXpert {}".format(version), shortcut_dir="GraXpert")]

setup(
    name="GraXpert",
    version=version,
    description="GraXpert is an astronomical image processing program for extracting and removing gradients in the background of your astrophotos",
    executables=executables,
    options={"build_exe": build_options, "bdist_msi": bdist_msi_options, "bdist_rpm": bidst_rpm_options},
    license="GLP-3.0",
)
