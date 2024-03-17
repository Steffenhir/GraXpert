import os

from appdirs import user_config_dir

from graxpert.preferences import load_preferences


def get_scaling_factor():
    prefs_filename = os.path.join(user_config_dir(appname="GraXpert"), "preferences.json")
    prefs = load_preferences(prefs_filename)
    scaling_factor = prefs.scaling

    return scaling_factor
