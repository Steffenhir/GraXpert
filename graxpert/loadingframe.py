# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 18:16:05 2022

@author: Steffen
"""

import sys
from os import path
from tkinter import LEFT, ttk

from PIL import ImageTk

from graxpert.localization import _


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_path = path.abspath(path.dirname(__file__))
    else:
        base_path = path.abspath(path.join(path.dirname(__file__), "../"))

    return path.join(base_path, relative_path)

class LoadingFrame():
    def __init__(self, widget, toplevel):

        font = ('Verdana', 20, 'normal')

        self.toplevel = toplevel
        hourglass_pic = ImageTk.PhotoImage(file=resource_path("img/hourglass-scaled.png"))
        self.text = ttk.Label(
            widget, 
            text=_("Calculating..."), 
            image=hourglass_pic,
            font=font,
            compound=LEFT
        )
        self.text.image=hourglass_pic
        
    def start(self):
        
        self.text.pack(fill="none", expand=True)
        self.toplevel.update()
        # force update of label to prevent white background on mac
        self.text.configure(background="#313131")
        self.text.update()

    def end(self):
        self.text.pack_forget()
        self.toplevel.update()