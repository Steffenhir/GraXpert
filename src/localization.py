import gettext
import sys
import locale
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_path = os.path.abspath(os.path.dirname(__file__))
    else:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))

    return os.path.join(base_path, relative_path)


lang = None
lang, enc = locale.getdefaultlocale()

if lang is None:
    lang = "en_EN"
if lang.startswith("de"):
    lang = "de_DE"

lang = gettext.translation('base', localedir=resource_path("locales"), languages=[lang], fallback=True)
lang.install()

def _(text):
    return lang.gettext(text)

