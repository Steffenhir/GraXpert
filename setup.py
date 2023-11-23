from cx_Freeze import Executable, setup
from graxpert.version import version
import astropy
import sys
import os

libs_prefix = os.path.commonprefix([astropy.__file__, __file__])
astropy_path = os.path.join(
    "./", os.path.dirname(os.path.relpath(astropy.__file__, libs_prefix))
)

directory_table = [
    ("ProgramMenuFolder", "TARGETDIR", "."),
    ("GraXpert", "ProgramMenuFolder", "GraXpert"),
]

msi_data = {
    "Directory": directory_table,
    "ProgId": [
        ("Prog.Id", None, None, "GraXpert is an astronomical image processing program for extracting and removing gradients in the background of your astrophotos", "IconId", None),
    ],
    "Icon": [
        ("IconId", "./img/Icon.ico"),
    ],
}

bdist_msi_options = {
    "add_to_path": True,
    "data": msi_data,
    "upgrade_code": "{8887032b-9211-4752-8f88-6d29833bb001}",
    "target_name": "GraXpert",
    "install_icon": "./img/Icon.ico"
}

build_options = {
    # "packages": ["astropy"],
    "includes": [
        "astropy.constants.codata2018",
        "astropy.constants.iau2015",
        "imageio.plugins.pillow",
        "skimage.draw.draw",
        "skimage.exposure.exposure",
        "skimage.filters._gaussian",
    ],
    "include_files": [
        ["./img", "./lib/img"],
        ["./forest-dark.tcl", "./lib/forest-dark.tcl"],
        ["./forest-dark/", "./lib/forest-dark/"],
        ["./locales/", "./lib/locales/"],
        [
            os.path.join(astropy_path, "units", "format", "generic_parsetab.py"),
            "./lib/astropy/units/format/generic_parsetab.py",
        ],
        [
            os.path.join(astropy_path, "units", "format", "generic_lextab.py"),
            "./lib/astropy/units/format/generic_lextab.py",
        ],
    ],
    "excludes": [],
    "include_msvcr": True,
}

base = "Win32GUI" if sys.platform == "win32" else None

executables = [
    Executable(
        "./graxpert/main.py",
        base=base,
        icon="./img/Icon.ico",
        shortcut_name="GraXpert {}".format(version),
        shortcut_dir="GraXpert",
        target_name="GraXpert"
    )
]

setup(
    name="GraXpert",
    version=version,
    description="GraXpert is an astronomical image processing program for extracting and removing gradients in the background of your astrophotos",
    executables=executables,
    options={"build_exe": build_options, "bdist_msi": bdist_msi_options},
)
