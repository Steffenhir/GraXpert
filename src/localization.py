import gettext
import sys
import locale
import os
from appdirs import user_config_dir
import json
from preferences import DEFAULT_PREFS, Prefs, merge_json


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_path = os.path.abspath(os.path.dirname(__file__))
    else:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))

    return os.path.join(base_path, relative_path)

prefs_file = os.path.join(user_config_dir(), ".graxpert", "preferences.json")
prefs = DEFAULT_PREFS
if os.path.isfile(prefs_file):
    with open(prefs_file) as f:
        json_prefs: Prefs = json.load(f)
        prefs = merge_json(prefs, json_prefs)


lang = None
if prefs["lang"] is None:
    lang, enc = locale.getdefaultlocale()
    if lang.startswith("de") or lang.startswith("gsw"):
        lang = "de_DE"
    else:
        lang = "en_EN"

else:
    lang = prefs["lang"]
    if lang == "Deutsch":
        lang = "de_DE"      
    else:
        lang = "en_EN"




lang_gettext = gettext.translation('base', localedir=resource_path("locales"), languages=[lang], fallback=True)
lang_gettext.install()

def _(text):
    return lang_gettext.gettext(text)

