import sys
import tkinter as tk
from cProfile import label
from os import path
from tkinter import CENTER, messagebox, ttk

from numpy import pad
from packaging import version
from PIL import Image, ImageTk

from graxpert.ai_model_handling import (list_local_versions,
                                        list_remote_versions)
from graxpert.localization import _, lang
from graxpert.slider import Slider
from graxpert.ui_scaling import get_scaling_factor


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
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
        
        scaling = get_scaling_factor()

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
            font=("Verdana","12","bold"),
            width=2
        )
        self.help_label.bind("<Button-1>", self.help)
        self.help_label.pack(
            ipady=int(20 * scaling),
        )

        self.help_button.grid(
            row=0,
            column=0,
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
            style="Advanced.TButton"
        )
        self.advanced_label = ttk.Label(
            self.advanced_button,
            text=_("A\nD\nV\nA\nN\nC\nE\nD"),
            style="Advanced.TLabel",
            font=("Verdana","12","bold"),
            width=2
        )
        self.advanced_label.bind("<Button-1>", self.advanced)
        self.advanced_label.pack(
            ipady=int(20 * scaling)
        )

        self.advanced_button.grid(
            row=1,
            column=0
        )
        
        
        self.button_frame.pack(side=tk.RIGHT)
        
        # ------------Help Panel-----------------
        heading_font = "Verdana 18 bold"
        heading_font2 = "Verdana 11 bold"
        
        
        self.help_panel = tk.Frame(self.canvas)
        self.help_canvas = tk.Canvas(self.help_panel, borderwidth=0,  bd=0, highlightthickness=0, name="help_canvas")
        self.help_canvas.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        self.help_scrollbar = ttk.Scrollbar(self.help_panel, orient=tk.VERTICAL, command=self.help_canvas.yview)
        self.help_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.help_panel_window = tk.Frame(self.help_canvas, borderwidth=0)
        
        logo = Image.open(resource_path("img/GraXpert_LOGO_Hauptvariante.png"))
        logo = logo.resize((
            int(logo.width/6 * scaling),
            int(logo.height/6 * scaling)
        ))
        
        self.help_panel_window.columnconfigure(0, weight=1)
        
        logo = ImageTk.PhotoImage(logo)
        self.label = tk.Label(self.help_panel_window, image=logo)
        self.label.image= logo
        self.label.grid(column=0, row=0, padx=(40,30), pady=50*scaling)

        # text = tk.Message(self.help_panel, text="Release: '{}' ({})".format(release, version), width=240 * scaling, anchor="center")
        # text.grid(column=0, row=1, padx=(40,30), pady=(0,25*scaling), sticky="ew")
        
        text = tk.Message(self.help_panel_window, text=_("Instructions"), width=240 * scaling, font=heading_font, anchor="center")
        text.grid(column=0, row=1, padx=(40,30), pady=(0,10*scaling), sticky="ew")
        
        num_pic = ImageTk.PhotoImage(file=resource_path("img/gfx_number_1-scaled.png"))
        text = tk.Label(self.help_panel_window, text=_(" Loading"), image=num_pic, compound="left", font=heading_font2)
        text.image = num_pic
        text.grid(column=0, row=2, padx=(40,30), pady=(5*scaling,0), sticky="w")
        text = tk.Message(self.help_panel_window, text=_("Load your image."), width=240 * scaling)
        text.grid(column=0, row=3, padx=(40,30), pady=(5*scaling,10*scaling), sticky="w")
        
        
        num_pic = ImageTk.PhotoImage(file=resource_path("img/gfx_number_2-scaled.png"))
        text = tk.Label(self.help_panel_window, text=_(" Stretch Options"), image=num_pic, compound="left", font=heading_font2)
        text.image = num_pic
        text.grid(column=0, row=4, padx=(40,30), pady=(5*scaling,0), sticky="w")
        text = tk.Message(self.help_panel_window, text=_("Stretch your image if necessary to reveal gradients."), width=240 * scaling)
        text.grid(column=0, row=5, padx=(40,30), pady=(5*scaling,10*scaling), sticky="w")
        
        
        num_pic = ImageTk.PhotoImage(file=resource_path("img/gfx_number_3-scaled.png"))
        text = tk.Label(self.help_panel_window, text=_(" Sample Selection"), image=num_pic, compound="left", font=heading_font2)
        text.image = num_pic
        text.grid(column=0, row=6, padx=(40,30), pady=(5*scaling,0), sticky="w")
        text = tk.Message(
            self.help_panel_window,
            text= _("Select background points\n  a) manually with left click\n  b) automatically via grid (grid selection)"
                "\nYou can remove already set points by right clicking on them."), 
            width=240 * scaling
        )
        text.grid(column=0, row=7, padx=(40,30), pady=(5*scaling,10*scaling), sticky="w")
        
        
        num_pic = ImageTk.PhotoImage(file=resource_path("img/gfx_number_4-scaled.png"))
        text = tk.Label(self.help_panel_window, text=_(" Calculation"), image=num_pic, compound="left", font=heading_font2)
        text.image = num_pic
        text.grid(column=0, row=8, padx=(40,30), pady=(5*scaling,0), sticky="w")
        text = tk.Message(self.help_panel_window, text=_("Click on Calculate Background to get the processed image."), width=240 * scaling)
        text.grid(column=0, row=9, padx=(40,30), pady=(5*scaling,10*scaling), sticky="w")
        
        
        num_pic = ImageTk.PhotoImage(file=resource_path("img/gfx_number_5-scaled.png"))
        text = tk.Label(self.help_panel_window, text=_(" Saving"), image=num_pic, compound="left", font=heading_font2)
        text.image = num_pic
        text.grid(column=0, row=10, padx=(40,30), pady=(5*scaling,0), sticky="w")
        text = tk.Message(self.help_panel_window, text=_("Save the processed image."), width=240 * scaling)
        text.grid(column=0, row=11, padx=(40,30), pady=(5*scaling,10*scaling), sticky="w")
    
        text = tk.Message(self.help_panel_window, text=_("Keybindings"), width=240 * scaling, font=heading_font, anchor="center")
        text.grid(column=0, row=12, padx=(40,30), pady=(20*scaling,10*scaling), sticky="ew")
        
        text = tk.Message(self.help_panel_window, text=_("Left click on picture: Set sample point"), width=240 * scaling)
        text.grid(column=0, row=13, padx=(40,30), pady=(0,10*scaling), sticky="w")
        
        text = tk.Message(self.help_panel_window, text=_("Left click on picture + drag: Move picture"), width=240 * scaling)
        text.grid(column=0, row=14, padx=(40,30), pady=(0,10*scaling), sticky="w")
        
        text = tk.Message(self.help_panel_window, text=_("Left click on sample point + drag:\nMove sample point"), width=240 * scaling)
        text.grid(column=0, row=15, padx=(40,30), pady=(0,10*scaling), sticky="w")
        
        text = tk.Message(self.help_panel_window, text=_("Right click on sample point:\nDelete sample point"), width=240 * scaling)
        text.grid(column=0, row=16, padx=(40,30), pady=(0,10*scaling), sticky="w")       
        
        text = tk.Message(self.help_panel_window, text=_("Mouse wheel: Zoom"), width=240 * scaling)
        text.grid(column=0, row=17, padx=(40,30), pady=(0,10*scaling), sticky="w")
        
        text = tk.Message(self.help_panel_window, text=_("Ctrl+Z/Y: Undo/Redo sample point"), width=240 * scaling)
        text.grid(column=0, row=18, padx=(40,30), pady=(0,10*scaling), sticky="w")
        
        self.help_canvas.create_window((0,0), window=self.help_panel_window)
        self.help_canvas.configure(yscrollcommand=self.help_scrollbar.set)
        self.help_canvas.bind('<Configure>', lambda e: self.help_canvas.configure(scrollregion=self.help_canvas.bbox("all")))
        self.help_panel_window.update()
        width = self.help_panel_window.winfo_width()
        self.help_canvas.configure(width=width)
        self.help_canvas.yview_moveto("0.0")
        
        # ------Advanced Panel-----------
        
        self.advanced_panel = tk.Frame(self.canvas)
        self.advanced_canvas = tk.Canvas(self.advanced_panel, borderwidth=0,  bd=0, highlightthickness=0, name="advanced_canvas")
        self.advanced_canvas.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        self.advanced_scrollbar = ttk.Scrollbar(self.advanced_panel, orient=tk.VERTICAL, command=self.advanced_canvas.yview)
        self.advanced_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.advanced_panel_window = tk.Frame(self.advanced_canvas, borderwidth=0)
        
        self.advanced_panel_window.columnconfigure(0, weight=1)
        
        text = tk.Message(self.advanced_panel_window, text=_("Advanced Settings"), width=240 * scaling, font=heading_font, anchor="center")
        text.grid(column=0, row=0, padx=(40,30), pady=(20*scaling,10*scaling), sticky="ew")
        
        text = tk.Message(self.advanced_panel_window, text=_("Sample Points"), width=240 * scaling, font=heading_font2, anchor="center")
        text.grid(column=0, row=1, padx=(40,30), pady=(20*scaling,10*scaling), sticky="ew")
        
        self.app.sample_size = tk.IntVar()
        self.app.sample_size.set(25)
        if "sample_size" in self.app.prefs:
            self.app.sample_size.set(self.app.prefs["sample_size"])
        
        
        self.sample_size_slider = Slider(self.advanced_panel_window, self.app.sample_size, "Sample size", 5, 50, 0, scaling, self.app.redraw_points)
        self.sample_size_slider.grid(column=0, row=3, pady=(0,10*scaling), padx=(40,30), sticky="ew")
        
        
        self.app.sample_color = tk.IntVar()
        self.app.sample_color.set(55)
        if "sample_color" in self.app.prefs:
            self.app.sample_color.set(self.app.prefs["sample_color"])
        
        self.sample_color_slider = Slider(self.advanced_panel_window, self.app.sample_color, "Sample color", 0, 360, 0, scaling, self.app.redraw_points)
        self.sample_color_slider.grid(column=0, row=5, pady=(0,10*scaling), padx=(40,30), sticky="ew")
        
        text = tk.Message(self.advanced_panel_window, text=_("Interpolation"), width=240 * scaling, font=heading_font2, anchor="center")
        text.grid(column=0, row=6, padx=(10*scaling,10*scaling), pady=(20*scaling,10*scaling), sticky="ew")
        
        text = tk.Message(self.advanced_panel_window, text=_("RBF Kernel"), width=240*scaling, anchor="center")
        text.grid(column=0, row=7, pady=(5*scaling,5*scaling), padx=(40,30), sticky="ews")
        
        self.app.RBF_kernels = ["thin_plate", "quintic", "cubic", "linear"]
        self.app.RBF_kernel = tk.StringVar()
        self.app.RBF_kernel.set(self.app.RBF_kernels[0])
        if "RBF_kernel" in self.app.prefs:
            self.app.RBF_kernel.set(self.app.prefs["RBF_kernel"])

        self.kernel_menu = ttk.OptionMenu(self.advanced_panel_window, self.app.RBF_kernel, self.app.RBF_kernel.get(), *self.app.RBF_kernels)
        self.kernel_menu.grid(column=0, row=8, pady=(5*scaling,5*scaling), padx=(40,30), sticky="ews")
        
        
        text = tk.Message(self.advanced_panel_window, text=_("Spline order"), width=240*scaling, anchor="center")
        text.grid(column=0, row=9, pady=(5*scaling,5*scaling), padx=(40,30), sticky="ews")
        
        self.app.spline_orders = [1,2,3,4,5]
        self.app.spline_order = tk.IntVar()
        self.app.spline_order.set(3)
        if "spline_order" in self.app.prefs:
            self.app.spline_order.set(self.app.prefs["spline_order"])

        self.spline_order_menu = ttk.OptionMenu(self.advanced_panel_window, self.app.spline_order, self.app.spline_order.get(), *self.app.spline_orders)
        self.spline_order_menu.grid(column=0, row=10, pady=(5*scaling,5*scaling), padx=(40,30), sticky="ews")
        
        text = tk.Message(self.advanced_panel_window, text=_("Correction"), width=240 * scaling, font=heading_font2, anchor="center")
        text.grid(column=0, row=11, padx=(10*scaling,10*scaling), pady=(20*scaling,10*scaling), sticky="ew")
        
        
        self.app.corr_types = ["Subtraction", "Division"]
        self.app.corr_type = tk.StringVar()
        self.app.corr_type.set(self.app.corr_types[0])
        if "corr_type" in self.app.prefs:
            self.app.corr_type.set(self.app.prefs["corr_type"])

        self.corr_menu = ttk.OptionMenu(self.advanced_panel_window, self.app.corr_type, self.app.corr_type.get(), *self.app.corr_types)
        self.corr_menu.grid(column=0, row=12, pady=(5*scaling,5*scaling), padx=(40,30), sticky="ews")
        
        
        text = tk.Message(self.advanced_panel_window, text=_("Interface"), width=240 * scaling, font=heading_font2, anchor="center")
        text.grid(column=0, row=13, padx=(40,30), pady=(20*scaling,10*scaling), sticky="ew")
        
        text = tk.Message(self.advanced_panel_window, text=_("Language"), width=240*scaling, anchor="center")
        text.grid(column=0, row=14, pady=(5*scaling,5*scaling), padx=(40,30), sticky="ews")
    
        def lang_change(lang):
            messagebox.showerror("", _("Please restart the program to change the language."))
        
        self.app.langs = ["English", "Deutsch"]
        self.app.lang = tk.StringVar()

        if lang == "de_DE":
            self.app.lang.set("Deutsch")
        else:
            self.app.lang.set("English")

        self.lang_menu = ttk.OptionMenu(self.advanced_panel_window, self.app.lang, self.app.lang.get(), *self.app.langs, command=lang_change)
        self.lang_menu.grid(column=0, row=15, pady=(5*scaling,5*scaling), padx=(40,30), sticky="ews")
        
        
        def scaling_change():
            messagebox.showerror("", _("Please restart the program to apply the changes to UI scaling."))
        
        self.app.scaling = tk.DoubleVar()
        self.app.scaling.set(1.0)
        if "scaling" in self.app.prefs:
            self.app.scaling.set(self.app.prefs["scaling"])
        
        
        self.scaling_slider = Slider(self.advanced_panel_window, self.app.scaling, "Scaling", 0.5, 2, 1, scaling, scaling_change)
        self.scaling_slider.grid(column=0, row=16, pady=(10*scaling,10*scaling), padx=(40,30), sticky="ew")

        # -- begin ai-model selection --
        text = tk.Message(self.advanced_panel_window, text=_("AI-Model"), width=240 * scaling, font=heading_font2, anchor="center")
        text.grid(column=0, row=17, padx=(40,30), pady=(20*scaling,10*scaling), sticky="ew")

        remote_versions = list_remote_versions()
        local_versions = list_local_versions()
        ai_options = set([])
        ai_options.update([rv["version"] for rv in remote_versions])
        ai_options.update(set([lv["version"] for lv in local_versions]))
        ai_options = sorted(ai_options, key=lambda k: version.parse(k), reverse=True)

        self.app.ai_version = tk.StringVar(master)
        self.app.ai_version.set("None") # default value
        if "ai_version" in self.app.prefs:
            self.app.ai_version.set(self.app.prefs["ai_version"])
        else:
            ai_options.insert(0, "None")

        try:
            default_idx = ai_options.index(self.app.ai_version.get())
        except ValueError:
            default_idx = 0
        
        self.app.ai_version_options = ttk.OptionMenu(self.advanced_panel_window, self.app.ai_version, ai_options[default_idx], *ai_options)
        self.app.ai_version_options.grid(column=0, row=18, pady=(10*scaling,10*scaling), padx=(40,30), sticky="ew")
        # -- end ai-model selection --

        
        self.advanced_canvas.create_window((0,0), window=self.advanced_panel_window)
        self.advanced_canvas.configure(yscrollcommand=self.advanced_scrollbar.set)
        self.advanced_canvas.bind('<Configure>', lambda e: self.advanced_canvas.configure(scrollregion=self.advanced_canvas.bbox("all")))
        self.advanced_panel_window.update()
        width = self.advanced_panel_window.winfo_width()
        self.advanced_canvas.configure(width=width)
        self.advanced_canvas.yview_moveto("0.0")
        
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
