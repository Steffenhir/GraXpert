import gettext
import sys
import locale

lang = None

if sys.platform.startswith("win"):
    
    lang, enc = locale.getdefaultlocale()
    lang = gettext.translation('base', localedir='../locales', languages=[lang], fallback=True)
    
else:
    lang = gettext.translation('base', localedir='../locales', fallback=True)

lang.install()

def _(text):
    return lang.gettext(text)

