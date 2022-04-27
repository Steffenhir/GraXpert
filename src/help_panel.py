import sys
import tkinter as tk
from cProfile import label
from os import path
from tkinter import CENTER, ttk

from numpy import pad
from PIL import Image, ImageTk

from localization import _
from ui_scaling import get_scaling_factor
# from version import release, version


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_path = path.abspath(path.dirname(__file__))
    else:
        base_path = path.abspath(path.join(path.dirname(__file__), "../"))

    return path.join(base_path, relative_path)

class Help_Panel():
    def __init__(self, master, canvas, app):
        
        
        self.visible = True
        self.master = master
        self.canvas = canvas
        self.app = app
        
        self.visible_panel = "None"
        
        self.button_frame = tk.Frame(self.canvas)
        
        scaling = get_scaling_factor(master)
        
        s = ttk.Style(master)
        
        # Help Button
        s.configure("Help.TButton", 
            borderwidth=0
        )
        s.configure("Help.TLabel",
            foreground="#ffffff",
            background="#c46f1a",
            justify=CENTER,
            anchor=CENTER
        )
        
        self.help_button = ttk.Button(self.button_frame,
            style="Help.TButton"
        )
        self.help_label = ttk.Label(
            self.help_button,
            text=_("H\nE\nL\nP"),
            style="Help.TLabel",
            font=("Verdana","12","bold")
        )
        self.help_label.bind("<Button-1>", self.help)
        self.help_label.pack(
            ipadx=int(5 * scaling),
            ipady=int(20 * scaling)
        )

        self.help_button.grid(
            row=0,
            column=0
        )
        
        # Advanced Button
        s.configure("Advanced.TButton", 
            borderwidth=0
        )
        s.configure("Advanced.TLabel",
            foreground="#ffffff",
            background="#254f69",
            justify=CENTER,
            anchor=CENTER
        )
        
        self.advanced_button = ttk.Button(self.button_frame,
            style="Advaned.TButton"
        )
        self.advanced_label = ttk.Label(
            self.advanced_button,
            text=_("A\nD\nV\nA\nN\nC\nE\nD"),
            style="Advanced.TLabel",
            font=("Verdana","12","bold")
        )
        self.advanced_label.bind("<Button-1>", self.advanced)
        self.advanced_label.pack(
            ipadx=int(5 * scaling),
            ipady=int(20 * scaling)
        )

        self.advanced_button.grid(
            row=1,
            column=0
        )
        
        
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

        # text = tk.Message(self.help_panel, text="Release: '{}' ({})".format(release, version), width=240 * scaling, anchor="center")
        # text.grid(column=0, row=1, padx=(40,30), pady=(0,25*scaling), sticky="ew")
        
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
        
        text = tk.Message(self.advanced_panel, text=_("Advanced Settings"), width=240 * scaling, font=heading_font, anchor="center")
        text.grid(column=0, row=0, padx=(40,30), pady=(20*scaling,10*scaling), sticky="ew")
        
        self.app.sample_size = tk.IntVar()
        self.app.sample_size.set(25)
        if "sample_size" in self.app.prefs:
            self.app.sample_size.set(self.app.prefs["sample_size"])
        
        self.sample_size_text = tk.Message(self.advanced_panel, text=_("Sample size: {}").format(self.app.sample_size.get()))
        self.sample_size_text.config(width=500 * scaling)
        self.sample_size_text.grid(column=0, row=1, pady=(5*scaling,5*scaling), padx=15*scaling, sticky="ews")
        
        def on_sample_size_slider(sample_size):
            self.app.sample_size.set(float("{:.2f}".format(float(sample_size))))
            self.sample_size_text.configure(text=_("Sample size: {}").format(self.app.sample_size.get()))
            self.app.redraw_points()
        
        self.sample_size_slider = ttk.Scale(
            self.advanced_panel,
            orient=tk.HORIZONTAL,
            from_=5,
            to=50,
            var=self.app.sample_size,
            command=on_sample_size_slider,
            length=150
            )
        self.sample_size_slider.grid(column=0, row=2, pady=(0,10*scaling), padx=15*scaling, sticky="ew")
        
        
        self.app.sample_color = tk.IntVar()
        self.app.sample_color.set(55)
        if "sample_color" in self.app.prefs:
            self.app.sample_color.set(self.app.prefs["sample_color"])
        
        self.sample_color_text = tk.Message(self.advanced_panel, text=_("Sample color: {}").format(self.app.sample_color.get()))
        self.sample_color_text.config(width=500 * scaling)
        self.sample_color_text.grid(column=0, row=3, pady=(5*scaling,5*scaling), padx=15*scaling, sticky="ews")
        
        def on_sample_color_slider(sample_color):
            self.app.sample_color.set(float("{:.2f}".format(float(sample_color))))
            self.sample_color_text.configure(text=_("Sample color: {}").format(self.app.sample_color.get()))
            self.app.redraw_points()
        
        self.sample_color_slider = ttk.Scale(
            self.advanced_panel,
            orient=tk.HORIZONTAL,
            from_=0,
            to=360,
            var=self.app.sample_color,
            command=on_sample_color_slider,
            length=150
            )
        self.sample_color_slider.grid(column=0, row=4, pady=(0,10*scaling), padx=15*scaling, sticky="ew")
        
        
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
        self.help_label.configure(background="#c46f1a")
            

    def advanced(self, event):
        
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
        # force update of label to prevent white background on mac
        self.advanced_label.configure(background="#254f69")
        


