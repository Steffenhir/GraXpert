import logging
import os
import sys

from appdirs import user_config_dir

from graxpert.ai_model_handling import (ai_model_path_from_version,
                                        download_version, latest_version,
                                        list_local_versions)
from graxpert.astroimage import AstroImage
from graxpert.background_extraction import extract_background
from graxpert.preferences import load_preferences, save_preferences


class CommandLineTool:
    def __init__(self, args):
        self.args = args

    def execute(self):
        astroImage = AstroImage(do_update_display=False)
        astroImage.set_from_file(self.args.filename)
        processedAstroImage = AstroImage(do_update_display=False)

        prefs_filename = os.path.join(
            user_config_dir(appname="GraXpert"), "preferences.json"
        )
        prefs = load_preferences(prefs_filename)

        ai_version = None
        if self.args.ai_version:
            ai_version = self.args.ai_version
        else:
            ai_version = prefs["ai_version"]

        if ai_version is None:
            ai_version = latest_version()

        logging.info(
            "using AI version {}. you can change this by providing the argument '-ai_version'".format(
                ai_version
            )
        )

        if not ai_version in [v["version"] for v in list_local_versions()]:
            try:
                logging.info(
                    "AI version {} not found locally, downloading...".format(ai_version)
                )
                download_version(ai_version)
                logging.info("download successful".format(ai_version))
            except Exception as e:
                logging.exception(e)
                sys.exit(1)

        prefs["ai_version"] = ai_version
        save_preferences(prefs_filename, prefs)

        processedAstroImage.set_from_array(
            extract_background(
                astroImage.img_array,
                [],
                "AI",
                self.args.smoothing,
                1,
                50,
                "RBF",
                0,
                self.args.correction,
                ai_model_path_from_version(ai_version),
            )
        )

        saveDir = os.path.splitext(self.args.filename)[0] + "_GraXpert.fits"

        astroImage.save(saveDir, "32 bit Fits")
        return
