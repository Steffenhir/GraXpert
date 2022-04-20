# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 18:16:05 2022

@author: Steffen
"""

import tkinter as tk
from localization import _

class LoadingFrame():
    def __init__(self, widget, toplevel):

        font = ('Verdana', 20, 'normal')
      

        self.toplevel = toplevel
        self.text = tk.Message(widget, text=_("Calculating..."), width=500 ,font=font)

        
    def start(self):
        
        self.text.pack(fill="none", expand=True)
        self.toplevel.update()

    def end(self):
        self.text.pack_forget()
        self.toplevel.update()