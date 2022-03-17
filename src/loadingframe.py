# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 18:16:05 2022

@author: Steffen
"""

import tkinter as tk

class LoadingFrame():
    def __init__(self, widget, toplevel):
        

        bg_color = "#474747"
        text_color = "#F0F0F0"
        font = ('Segoe UI Semibold', 20, 'normal')
        relief = "raised"
        

        self.toplevel = toplevel
        self.text = tk.Message(widget, 
                               text="Calculating...", 
                               background=bg_color, 
                               font=font, 
                               fg=text_color, 
                               width=500, 
                               relief=relief)

        
    def start(self):
        
        self.text.pack(fill="none", expand=True)
        self.toplevel.update()

    def end(self):
        self.text.pack_forget()
        self.toplevel.update()