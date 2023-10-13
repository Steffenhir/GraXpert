from graxpert.astroimage import AstroImage
from graxpert.background_extraction import extract_background
from graxpert.preferences import load_preferences
from appdirs import user_config_dir
import os

class CommandLineTool:
    def __init__(self, args):
        self.args = args
    
    def execute(self):
        astroImage = AstroImage(update_display = False)
        astroImage.set_from_file(self.args.filename)
        processedAstroImage = AstroImage(update_display = False)
        
        prefs_filename = os.path.join(user_config_dir(appname="GraXpert"), "preferences.json")
        prefs = load_preferences(prefs_filename)
        AIDir = prefs["AI_directory"] 
        
        processedAstroImage.set_from_array(
            extract_background(
            astroImage.img_array,[],
            "AI",0.0,
            1, 50,
            "RBF",0,
            "Subtraction", AIDir
            ))
        
        
        saveDir = os.path.splitext(self.args.filename)[0] + "_GraXpert.fits"
        
        
        astroImage.save(saveDir, "32 bit Fits")
        return