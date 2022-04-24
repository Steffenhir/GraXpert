import sys
import tkinter as tk
from tkinter import CENTER, ttk
from cProfile import label
from os import path

from numpy import pad
from PIL import Image, ImageTk

from graxpert.ui_scaling import get_scaling_factor
from graxpert.localization import _

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_path = path.abspath(path.dirname(__file__))
    else:
        base_path = path.abspath(path.join(path.dirname(__file__), "../"))

    return path.join(base_path, relative_path)

class Help_Panel():
    def __init__(self, master, canvas):
        
        
        self.visible = True
        self.master = master
        self.canvas = canvas
        
        self.visible_panel = "None"
        
        self.button_frame = tk.Frame(self.canvas)
        
        scaling = get_scaling_factor(master)
        
        s = ttk.Style(master)
        s.configure("Help.TButton", 
            borderwidth=0
        )
        s.configure("Help.TLabel",
            foreground="#ffffff",
            background="#c46f1a",
            justify=CENTER,
            anchor=CENTER
        )
        self.toggle_button = ttk.Button(self.button_frame,
            style="Help.TButton"
        )
        self.toggle_label = ttk.Label(
            self.toggle_button,
            text=_("H\nE\nL\nP"),
            style="Help.TLabel",
            font=("Verdana","12","bold")
        )
        self.toggle_label.bind("<Button-1>", self.help)
        self.toggle_label.pack(
            ipadx=int(5 * scaling),
            ipady=int(20 * scaling)
        )

        self.toggle_button.grid(
            row=0,
            column=0
        )
        
        #self.advanced_pic = tk.PhotoImage(file=resource_path("img/advanced.png"))
        #self.advanced_button = tk.Button(self.button_frame, image=self.advanced_pic, command=self.advanced, borderwidth=0)
        #self.advanced_button.grid(row=1, column=0)
        
        self.button_frame.pack(side=tk.RIGHT)
        
        # Help Panel
        heading_font = "Verdana 18 bold"
        heading_font2 = "Verdana 10 bold"
        
        
        self.help_panel = tk.Frame(self.canvas)
        
        logo = Image.open(resource_path("img/GraXpert_LOGO_Hauptvariante.png"))
        logo = logo.resize((
            int(logo.width/6 * scaling),
            int(logo.height/6 * scaling)
        ))

        logo = ImageTk.PhotoImage(logo)
        self.label = tk.Label(self.help_panel, image=logo)
        self.label.image= logo
        self.label.grid(column=0, row=0, padx=(40,30), pady=50*scaling)
        
        text = tk.Message(self.help_panel, text=_("Instructions"), width=240 * scaling, font=heading_font, anchor="center")
        text.grid(column=0, row=1, padx=(40,30), pady=(0,10*scaling), sticky="ew")
        
        num_pic = ImageTk.PhotoImage(file=resource_path("img/gfx_number_1-scaled.png"))
        text = tk.Label(self.help_panel, text=_(" Loading"), image=num_pic, compound="left", font=heading_font2)
        text.image = num_pic
        text.grid(column=0, row=2, padx=(40,30), pady=(5*scaling,0), sticky="w")
        text = tk.Message(self.help_panel, text=_("Load your image."), width=240 * scaling)
        text.grid(column=0, row=3, padx=(40,30), pady=(5*scaling,10*scaling), sticky="w")
        
        
        num_pic = ImageTk.PhotoImage(file=resource_path("img/gfx_number_2-scaled.png"))
        text = tk.Label(self.help_panel, text=_(" Stretch Options"), image=num_pic, compound="left", font=heading_font2)
        text.image = num_pic
        text.grid(column=0, row=4, padx=(40,30), pady=(5*scaling,0), sticky="w")
        text = tk.Message(self.help_panel, text=_("Stretch your image if necessary to reveal gradients."), width=240 * scaling)
        text.grid(column=0, row=5, padx=(40,30), pady=(5*scaling,10*scaling), sticky="w")
        
        
        num_pic = ImageTk.PhotoImage(file=resource_path("img/gfx_number_3-scaled.png"))
        text = tk.Label(self.help_panel, text=_(" Sample Selection"), image=num_pic, compound="left", font=heading_font2)
        text.image = num_pic
        text.grid(column=0, row=6, padx=(40,30), pady=(5*scaling,0), sticky="w")
        text = tk.Message(
            self.help_panel,
            text= _("Select background points\n  a) manually with left click\n  b) automatically via grid (grid selection)"
                "\nYou can remove already set points by right clicking on them."), 
            width=240 * scaling
        )
        text.grid(column=0, row=7, padx=(40,30), pady=(5*scaling,10*scaling), sticky="w")
        
        
        num_pic = ImageTk.PhotoImage(file=resource_path("img/gfx_number_4-scaled.png"))
        text = tk.Label(self.help_panel, text=_(" Calculation"), image=num_pic, compound="left", font=heading_font2)
        text.image = num_pic
        text.grid(column=0, row=8, padx=(40,30), pady=(5*scaling,0), sticky="w")
        text = tk.Message(self.help_panel, text=_("Click on Calculate Background to get the processed image."), width=240 * scaling)
        text.grid(column=0, row=9, padx=(40,30), pady=(5*scaling,10*scaling), sticky="w")
        
        
        num_pic = ImageTk.PhotoImage(file=resource_path("img/gfx_number_5-scaled.png"))
        text = tk.Label(self.help_panel, text=_(" Saving"), image=num_pic, compound="left", font=heading_font2)
        text.image = num_pic
        text.grid(column=0, row=10, padx=(40,30), pady=(5*scaling,0), sticky="w")
        text = tk.Message(self.help_panel, text=_("Save the processed image."), width=240 * scaling)
        text.grid(column=0, row=11, padx=(40,30), pady=(5*scaling,10*scaling), sticky="w")
    
        # Advanced Panel
        
        self.advanced_panel = tk.Frame(self.canvas)
        text = tk.Message(self.advanced_panel, text="Advanced", width=240 * scaling)
        text.grid(column=0, row=0, padx=3, pady=3)
        
    def help(self, event):
        
        if self.visible_panel == "None":
            self.button_frame.pack_forget()
            self.help_panel.pack(side=tk.RIGHT, fill=tk.Y)
            self.button_frame.pack(side=tk.RIGHT)
            self.visible_panel = self.help_panel
        
        elif self.visible_panel == self.advanced_panel:
            self.advanced_panel.pack_forget()
            self.button_frame.pack_forget()
            self.help_panel.pack(side=tk.RIGHT, fill=tk.Y)
            self.button_frame.pack(side=tk.RIGHT)
            self.visible_panel = self.help_panel
        
        elif self.visible_panel == self.help_panel:
            self.help_panel.pack_forget()
            self.button_frame.pack_forget()
            self.button_frame.pack(side=tk.RIGHT)
            self.visible_panel="None"
            
        self.master.update()
        # force update of label to prevent white background on mac
        self.toggle_label.configure(background="#c46f1a")
            

    def advanced(self):
        
        if self.visible_panel == "None":
            self.button_frame.pack_forget()
            self.advanced_panel.pack(side=tk.RIGHT, fill=tk.Y)
            self.button_frame.pack(side=tk.RIGHT)
            self.visible_panel = self.advanced_panel
        
        elif self.visible_panel == self.help_panel:
            self.help_panel.pack_forget()
            self.button_frame.pack_forget()
            self.advanced_panel.pack(side=tk.RIGHT, fill=tk.Y)
            self.button_frame.pack(side=tk.RIGHT)
            self.visible_panel = self.advanced_panel
        
        elif self.visible_panel == self.advanced_panel:
            self.advanced_panel.pack_forget()
            self.button_frame.pack_forget()
            self.button_frame.pack(side=tk.RIGHT)
            self.visible_panel="None"
            
        self.master.update()
        


