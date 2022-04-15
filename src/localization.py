import gettext
import sys
import locale

lang = None


    
lang, enc = locale.getdefaultlocale()
lang = gettext.translation('base', localedir='../locales', languages=[lang], fallback=True)
    


lang.install()

def _(text):
    return lang.gettext(text)

