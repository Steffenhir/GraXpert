# -*- coding: utf-8 -*-
"""
Created on Sun Feb 13 10:05:08 2022
@author: steff
"""

import multiprocessing

multiprocessing.freeze_support()

from mp_logging import configure_logging, initialize_logging, shutdown_logging

configure_logging()

import importlib
import logging
import os
import sys
import tkinter as tk
from colorsys import hls_to_rgb
from tkinter import filedialog, messagebox, ttk

import hdpitkinter as hdpitk
import numpy as np
from appdirs import user_config_dir
from PIL import Image, ImageTk
from skimage import io
from skimage.transform import resize

import background_extraction
import tooltip
from app_state import INITIAL_STATE
from astroimage import AstroImage
from collapsible_frame import CollapsibleFrame
from commands import (ADD_POINT_HANDLER, ADD_POINTS_HANDLER, INIT_HANDLER,
                      MOVE_POINT_HANDLER, RESET_POINTS_HANDLER,
                      RM_POINT_HANDLER, SEL_POINTS_HANDLER, Command,
                      InitHandler)
from help_panel import Help_Panel
from loadingframe import LoadingFrame
from localization import _
from parallel_processing import executor
from preferences import (app_state_2_prefs, load_preferences,
                         prefs_2_app_state, save_preferences,
                         app_state_2_fitsheader, fitsheader_2_app_state)
from stretch import stretch_all
from ui_scaling import get_scaling_factor
from version import release, version


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_path = os.path.abspath(os.path.dirname(__file__))
    else:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))

    return os.path.join(base_path, relative_path)



class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        self.master.geometry("1920x1080")
        self.master.minsize(height=768 ,width=1024)
        
        try:
            self.master.state("zoomed")
        except:
            self.master.state("normal")
        
        self.filename = ""
        self.data_type = ""

        self.images = {
            "Original": None,
            "Background": None,
            "Processed": None
            }
        
        self.my_title = "GraXpert | Release: '{}' ({})".format(release, version)
        self.master.title(self.my_title)

        prefs_filename = os.path.join(user_config_dir(appname="GraXpert"), "preferences.json")
        self.prefs = load_preferences(prefs_filename)

        tmp_state = prefs_2_app_state(self.prefs, INITIAL_STATE)
        
        self.cmd: Command = Command(INIT_HANDLER, background_points=tmp_state["background_points"])
        self.cmd.execute()

        self.create_widget()
        self.bgextr_menu.show.set(1)
        self.bgextr_menu.toggle()

        self.reset_transform()
        
        if len(sys.argv) > 1 and sys.argv[1].endswith((".bmp", ".png", ".jpg", ".tif", ".tiff", ".fit", ".fits", ".fts", ".xisf")):
            filename = sys.argv[1]
            self.menu_open_clicked(None, filename)
        

    def create_widget(self):
        

        frame_statusbar = tk.Frame(self.master, bd=1, relief = tk.SUNKEN)
        self.label_image_info = ttk.Label(frame_statusbar, text="image info", anchor=tk.E)
        self.label_image_pixel = ttk.Label(frame_statusbar, text="(x, y)", anchor=tk.W)
        self.label_image_info.pack(side=tk.RIGHT)
        self.label_image_pixel.pack(side=tk.LEFT)
        frame_statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        
        self.master.grid_columnconfigure(3)
        #Right help panel
        
        self.canvas = tk.Canvas(self.master, background="black", name="picture")
        self.help_panel = Help_Panel(self.master, self.canvas, self)
        
       
        # Canvas
        
        self.canvas.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        
        
        self.display_options = ["Original","Processed","Background"]
        self.display_type = tk.StringVar()
        self.display_type.set(self.display_options[0])
        self.display_menu = ttk.OptionMenu(self.canvas, self.display_type, self.display_type.get(), *self.display_options, command=self.switch_display)
        self.display_menu.place(relx=0.5, rely=0.01)
        tt_display_type = tooltip.Tooltip(self.display_menu, text=tooltip.display_text, wraplength=500)
        
        self.loading_frame = LoadingFrame(self.canvas, self.master)

        self.left_drag_timer = -1 
        self.clicked_inside_pt = False
        self.clicked_inside_pt_idx = 0
        self.clicked_inside_pt_coord = None
        
        self.crop_mode = False
        
        self.master.bind("<Button-1>", self.mouse_down_left)  
        self.master.bind("<ButtonRelease-1>", self.mouse_release_left) # Left Mouse Button
        self.master.bind("<Button-2>", self.mouse_down_right)          # Middle Mouse Button (Right Mouse Button on macs)
        self.master.bind("<Button-3>", self.mouse_down_right)          # Right Mouse Button (Middle Mouse Button on macs)
        self.master.bind("<B1-Motion>", self.mouse_move_left)          # Left Mouse Button Drag
        self.master.bind("<Motion>", self.mouse_move)                  # Mouse move
        self.master.bind("<BackSpace>", self.reset_zoom)               # backspace -> reset zoom
        self.master.bind("<Control-Key-0>", self.reset_zoom)           # ctrl + 0 -> reset zoom (Windows)
        self.master.bind("<Command-Key-0>", self.reset_zoom)           # cmd  + 0 -> reset zoom (Mac)
        self.master.bind("<Control-Key-KP_0>", self.reset_zoom)        # ctrl + numpad 0 -> reset zoom (Windows)
        self.master.bind("<Command-Key-KP_0>", self.reset_zoom)        # cmd  + numpad 0 -> reset zoom (Mac)
        self.master.bind("<MouseWheel>", self.mouse_wheel)             # Mouse Wheel
        self.master.bind("<Button-4>", self.mouse_wheel)               # Mouse Wheel Linux
        self.master.bind("<Button-5>", self.mouse_wheel)               # Mouse Wheel Linux
        self.master.bind("<Return>", self.enter_key)                   # Enter Key
        self.master.bind("<Control-z>", self.undo)                     # undo
        self.master.bind("<Control-y>", self.redo)                     # redo
        self.master.bind("<Command-z>", self.undo)                     # undo on macs
        self.master.bind("<Command-y>", self.redo)                     # redo on macs
        
        
        #Side menu
        heading_font = "Verdana 10 bold"
        
        self.side_canvas = tk.Canvas(self.master, borderwidth=0,  bd=0, highlightthickness=0, name="left_panel")
        self.side_canvas.pack(side=tk.TOP, fill=tk.Y, expand=True)
        
        self.scrollbar = ttk.Scrollbar(self.canvas, orient=tk.VERTICAL, command=self.side_canvas.yview)
        self.scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        
        scal = get_scaling_factor()*0.75
        self.side_menu = tk.Frame(self.side_canvas, borderwidth=0)
        
        #Crop menu
        self.crop_menu = CollapsibleFrame(self.side_menu, text=_("Crop") + " ")
        self.crop_menu.grid(column=0, row=0, pady=(20*scal,5*scal), padx=15*scal, sticky="news")
        self.crop_menu.sub_frame.grid_columnconfigure(0, weight=1)
        
        for i in range(2):
            self.crop_menu.sub_frame.grid_rowconfigure(i, weight=1)
            
        self.cropmode_button = ttk.Button(self.crop_menu.sub_frame, 
                          text=_("Crop mode on/off"),
                          command=self.toggle_crop_mode,
        )
        self.cropmode_button.grid(column=0, row=0, pady=(20*scal,5*scal), padx=15*scal, sticky="news")
        
        self.cropapply_button = ttk.Button(self.crop_menu.sub_frame, 
                          text=_("Apply crop"),
                          command=self.crop_apply,
        )
        self.cropapply_button.grid(column=0, row=1, pady=(5*scal,20*scal), padx=15*scal, sticky="news")

        
        #Background extraction menu
        self.bgextr_menu = CollapsibleFrame(self.side_menu, text=_("Background Extraction") + " ")
        self.bgextr_menu.grid(column=0, row=1, pady=(5*scal,20*scal), padx=15*scal, sticky="news")
        self.bgextr_menu.sub_frame.grid_columnconfigure(0, weight=1)
        
        for i in range(26):
            self.bgextr_menu.sub_frame.grid_rowconfigure(i, weight=1)
        
        #---Open Image---
        num_pic = ImageTk.PhotoImage(file=resource_path("img/gfx_number_1-scaled.png"))
        text = tk.Label(self.bgextr_menu.sub_frame, text=_(" Loading"), image=num_pic, font=heading_font, compound="left")
        text.image = num_pic
        text.grid(column=0, row=0, pady=(20*scal,5*scal), padx=0, sticky="w")
        
        self.load_image_button = ttk.Button(self.bgextr_menu.sub_frame, 
                         text=_("Load Image"),
                         command=self.menu_open_clicked,
        )
        tt_load = tooltip.Tooltip(self.load_image_button, text=tooltip.load_text)
        self.load_image_button.grid(column=0, row=1, pady=(5*scal,30*scal), padx=15*scal, sticky="news")
        
        #--Stretch Options--
        num_pic = ImageTk.PhotoImage(file=resource_path("img/gfx_number_2-scaled.png"))
        text = tk.Label(self.bgextr_menu.sub_frame, text=_(" Stretch Options"), image=num_pic, font=heading_font, compound="left")
        text.image = num_pic
        text.grid(column=0, row=2, pady=5*scal, padx=0, sticky="w")
        
        self.stretch_options = ["No Stretch", "10% Bg, 3 sigma", "15% Bg, 3 sigma", "20% Bg, 3 sigma", "30% Bg, 2 sigma"]
        self.stretch_option_current = tk.StringVar()
        self.stretch_option_current.set(self.stretch_options[0])
        if "stretch_option" in self.prefs:
            self.stretch_option_current.set(self.prefs["stretch_option"])
        self.stretch_menu = ttk.OptionMenu(self.bgextr_menu.sub_frame, self.stretch_option_current, self.stretch_option_current.get(), *self.stretch_options, command=self.change_stretch)
        self.stretch_menu.grid(column=0, row=3, pady=(5*scal,5*scal), padx=15*scal, sticky="news")
        tt_stretch= tooltip.Tooltip(self.stretch_menu, text=tooltip.stretch_text)
        
        self.saturation = tk.DoubleVar()
        self.saturation.set(1.0)
        if "saturation" in self.prefs:
            self.saturation.set(self.prefs["saturation"])
        
        self.saturation_text = tk.Message(self.bgextr_menu.sub_frame, text=_("Saturation") + ": {:.1f}".format(self.saturation.get()))
        self.saturation_text.config(width=500 * scal)
        self.saturation_text.grid(column=0, row=4, pady=(5*scal,5*scal), padx=15*scal, sticky="ews")
        
        def on_saturation_slider(saturation):
            self.saturation.set(saturation)
            self.saturation_text.configure(text=_("Saturation") + ": {:.1f}".format(self.saturation.get()))
                

        self.saturation_slider = ttk.Scale(
            self.bgextr_menu.sub_frame,
            orient=tk.HORIZONTAL,
            from_=0,
            to=3,
            var=self.saturation,
            command=on_saturation_slider,
            length=150
            )
        
        self.saturation_slider.bind("<ButtonRelease-1>", self.update_saturation)
        self.saturation_slider.grid(column=0, row=5, pady=(0,30*scal), padx=15*scal, sticky="ew")
      
        #---Sample Selection---
        num_pic = ImageTk.PhotoImage(file=resource_path("img/gfx_number_3-scaled.png"))
        text = tk.Label(self.bgextr_menu.sub_frame, text=_(" Sample Selection"), image=num_pic, font=heading_font, compound="left")
        text.image = num_pic
        text.grid(column=0, row=6, pady=5*scal, padx=0, sticky="w")
        
        self.display_pts = tk.BooleanVar()
        self.display_pts.set(True)
        self.display_pts_switch = ttk.Checkbutton(self.bgextr_menu.sub_frame, text="  "+_("Display points"), compound=tk.LEFT, var=self.display_pts, command=self.redraw_points)
        self.display_pts_switch.grid(column=0, row=7, pady=(5*scal,5*scal), padx=15*scal, sticky="ews")
        
        self.flood_select_pts = tk.BooleanVar()
        self.flood_select_pts.set(False)
        if "bg_flood_selection_option" in self.prefs:
            self.flood_select_pts.set(self.prefs["bg_flood_selection_option"])
        self.flood_select_pts_switch = ttk.Checkbutton(self.bgextr_menu.sub_frame, text="  "+_("Flooded generation"), compound=tk.LEFT, var=self.flood_select_pts)
        tt_load = tooltip.Tooltip(self.flood_select_pts_switch, text=tooltip.bg_flood_text)
        self.flood_select_pts_switch.grid(column=0, row=8, pady=(5*scal,5*scal), padx=15*scal, sticky="ews")
        
        self.bg_pts = tk.IntVar()
        self.bg_pts.set(10)
        if "bg_pts_option" in self.prefs:
            self.bg_pts.set(self.prefs["bg_pts_option"])
        
        self.bg_selection_text = tk.Message(self.bgextr_menu.sub_frame, text=_("Points per row: {}").format(self.bg_pts.get()))
        self.bg_selection_text.config(width=500 * scal)
        self.bg_selection_text.grid(column=0, row=9, pady=(5*scal,5*scal), padx=15*scal, sticky="ews")
        
        def on_bg_pts_slider(bgs_points):
            self.bg_pts.set(int(float(bgs_points)))
            self.bg_selection_text.configure(text=_("Points per row: {}").format(self.bg_pts.get()))

        self.bg_pts_slider = ttk.Scale(
            self.bgextr_menu.sub_frame,
            orient=tk.HORIZONTAL,
            from_=4,
            to=25,
            var=self.bg_pts,
            command=on_bg_pts_slider,
            length=150
            )
        
        self.bg_pts_slider.grid(column=0, row=10, pady=(0,0), padx=15*scal, sticky="ew")
        tt_bg_points= tooltip.Tooltip(self.bg_pts_slider, text=tooltip.num_points_text)
        
        self.bg_tol = tk.DoubleVar()
        self.bg_tol.set(1)
        if "bg_tol_option" in self.prefs:
            self.bg_tol.set(self.prefs["bg_tol_option"])
        
        self.bg_selection_tol = tk.Message(self.bgextr_menu.sub_frame, text=_("Grid Tolerance: {}").format(self.bg_tol.get()))
        self.bg_selection_tol.config(width=500)
        self.bg_selection_tol.grid(column=0, row=11, pady=(5*scal,5*scal), padx=15*scal, sticky="ews")
        
        def on_bg_tol_slider(bg_tol):
            self.bg_tol.set(float("{:.1f}".format(float(bg_tol))))
            self.bg_selection_tol.configure(text=_("Grid Tolerance: {}").format(self.bg_tol.get()))
        
        self.bg_tol_slider = ttk.Scale(
            self.bgextr_menu.sub_frame,
            orient=tk.HORIZONTAL,
            from_=-2,
            to=10,
            var=self.bg_tol,
            command=on_bg_tol_slider,
            length=150
            )
        self.bg_tol_slider.grid(column=0, row=12, pady=(0,10*scal), padx=15*scal, sticky="ew")
        tt_tol_points= tooltip.Tooltip(self.bg_tol_slider, text=tooltip.bg_tol_text)
        
        self.bg_selection_button = ttk.Button(self.bgextr_menu.sub_frame, 
                         text=_("Create Grid"),
                         command=self.select_background)
        self.bg_selection_button.grid(column=0, row=13, pady=5*scal, padx=15*scal, sticky="news")
        tt_bg_select = tooltip.Tooltip(self.bg_selection_button, text= tooltip.bg_select_text)
        
        self.reset_button = ttk.Button(self.bgextr_menu.sub_frame, 
                         text=_("Reset Sample Points"),
                         command=self.reset_backgroundpts)
        self.reset_button.grid(column=0, row=14, pady=(5*scal,30*scal), padx=15*scal, sticky="news")
        tt_reset= tooltip.Tooltip(self.reset_button, text=tooltip.reset_text)
        
        #---Calculation---
        num_pic = ImageTk.PhotoImage(file=resource_path("img/gfx_number_4-scaled.png"))
        text = tk.Label(self.bgextr_menu.sub_frame, text=_(" Calculation"), image=num_pic, font=heading_font, compound="left")
        text.image = num_pic
        text.grid(column=0, row=15, pady=5*scal, padx=0, sticky="w")
        
        self.intp_type_text = tk.Message(self.bgextr_menu.sub_frame, text=_("Interpolation Method:"))
        self.intp_type_text.config(width=500)
        self.intp_type_text.grid(column=0, row=16, pady=(5*scal,5*scal), padx=15*scal, sticky="ews")
        
        self.interpol_options = ["RBF", "Splines", "Kriging"]
        self.interpol_type = tk.StringVar()
        self.interpol_type.set(self.interpol_options[0])
        if "interpol_type_option" in self.prefs:
            self.interpol_type.set(self.prefs["interpol_type_option"])
        self.interpol_menu = ttk.OptionMenu(self.bgextr_menu.sub_frame, self.interpol_type, self.interpol_type.get(), *self.interpol_options)
        self.interpol_menu.grid(column=0, row=17, pady=(0,5*scal), padx=15*scal, sticky="news")
        tt_interpol_type= tooltip.Tooltip(self.interpol_menu, text=tooltip.interpol_type_text)
        
        self.smoothing = tk.DoubleVar()
        self.smoothing.set(1.0)
        if "smoothing_option" in self.prefs:
            self.smoothing.set(self.prefs["smoothing_option"])
        
        self.smooth_text = tk.Message(self.bgextr_menu.sub_frame, text="Smoothing: {}".format(self.smoothing.get()))
        self.smooth_text.config(width=500)
        self.smooth_text.grid(column=0, row=18, pady=(5*scal,5*scal), padx=15*scal, sticky="ews")
        
        def on_smoothing_slider(smoothing):
            self.smoothing.set(float("{:.2f}".format(float(smoothing))))
            self.smooth_text.configure(text="Smoothing: {}".format(self.smoothing.get()))
        
        self.smoothing_slider = ttk.Scale(
            self.bgextr_menu.sub_frame,
            orient=tk.HORIZONTAL,
            from_=0,
            to=1,
            var=self.smoothing,
            command=on_smoothing_slider,
            length=150
            )
        self.smoothing_slider.grid(column=0, row=19, pady=(0,10*scal), padx=15*scal, sticky="ew")
        tt_smoothing= tooltip.Tooltip(self.smoothing_slider, text=tooltip.smoothing_text)
        
        self.calculate_button = ttk.Button(self.bgextr_menu.sub_frame, 
                         text=_("Calculate Background"),
                         command=self.calculate)
        self.calculate_button.grid(column=0, row=20, pady=(5*scal,30*scal), padx=15*scal, sticky="news")
        tt_calculate= tooltip.Tooltip(self.calculate_button, text=tooltip.calculate_text)
        
        #---Saving---  
        num_pic = ImageTk.PhotoImage(file=resource_path("img/gfx_number_5-scaled.png"))
        self.saveas_text = tk.Label(self.bgextr_menu.sub_frame, text=_(" Saving"), image=num_pic, font=heading_font, compound="left")
        self.saveas_text.image = num_pic
        self.saveas_text.grid(column=0, row=21, pady=5*scal, padx=0, sticky="w")
        
        self.saveas_options = ["16 bit Tiff", "32 bit Tiff", "16 bit Fits", "32 bit Fits", "16 bit XISF", "32 bit XISF"]
        self.saveas_type = tk.StringVar()
        self.saveas_type.set(self.saveas_options[0])
        if "saveas_option" in self.prefs:
            self.saveas_type.set(self.prefs["saveas_option"])
        self.saveas_menu = ttk.OptionMenu(self.bgextr_menu.sub_frame, self.saveas_type, self.saveas_type.get(), *self.saveas_options)
        self.saveas_menu.grid(column=0, row=22, pady=(5*scal,20*scal), padx=15*scal, sticky="news")
        tt_interpol_type= tooltip.Tooltip(self.saveas_menu, text=tooltip.saveas_text)
        
        self.save_background_button = ttk.Button(self.bgextr_menu.sub_frame, 
                         text=_("Save Background"),
                         command=self.save_background_image)
        self.save_background_button.grid(column=0, row=23, pady=5*scal, padx=15*scal, sticky="news")
        tt_save_bg = tooltip.Tooltip(self.save_background_button, text=tooltip.save_bg_text)
              
        
        self.save_button = ttk.Button(self.bgextr_menu.sub_frame, 
                         text=_("Save Processed"),
                         command=self.save_image)
        self.save_button.grid(column=0, row=24, pady=5*scal, padx=15*scal, sticky="news")
        tt_save_pic= tooltip.Tooltip(self.save_button, text=tooltip.save_pic_text)

        self.save_stretched_button = ttk.Button(self.bgextr_menu.sub_frame, 
                         text=_("Save Stretched & Processed"),
                         command=self.save_stretched_image)
        self.save_stretched_button.grid(column=0, row=25, pady=(5*scal,10*scal), padx=15*scal, sticky="news")
        tt_save_pic= tooltip.Tooltip(self.save_stretched_button, text=tooltip.save_stretched_pic_text)
        

        self.side_canvas.create_window((0,0), window=self.side_menu)
        self.side_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.side_canvas.bind('<Configure>', lambda e: self.side_canvas.configure(scrollregion=self.side_canvas.bbox("all")))
        self.side_menu.update()
        width = self.side_menu.winfo_width()
        self.side_canvas.configure(width=width)
        self.side_canvas.yview_moveto("0.0")

    
    def menu_open_clicked(self, event=None, filename=None):

        if self.prefs["working_dir"] != "" and os.path.exists(self.prefs["working_dir"]):
            initialdir = self.prefs["working_dir"]
        else:
            initialdir = os.getcwd()
        
        if filename is None:
            filename = tk.filedialog.askopenfilename(
                filetypes = [("Image file", ".bmp .png .jpg .tif .tiff .fit .fits .fts .xisf"),
                            ("Bitmap", ".bmp"), ("PNG", ".png"), ("JPEG", ".jpg"), ("Tiff", ".tif .tiff"), ("Fits", ".fit .fits .fts"), ("XISF", ".xisf")],
                initialdir = initialdir
                )
        
        if filename == "":
            return
        
        self.loading_frame.start()
        self.data_type = os.path.splitext(filename)[1]
        
        try:
            image = AstroImage(self.stretch_option_current, self.saturation)
            image.set_from_file(filename)
            self.images["Original"] = image
            self.prefs["working_dir"] = os.path.dirname(filename)
            
        except Exception as e:
            msg = _("An error occurred while loading your picture.")
            logging.exception(msg)
            messagebox.showerror("Error", _(msg))

        
        self.display_type.set("Original")
        self.images["Processed"] = None
        self.images["Background"] = None
        
        self.master.title(self.my_title + " - " + os.path.basename(filename))
        self.filename = os.path.splitext(os.path.basename(filename))[0]
        
        width = self.images["Original"].img_display.width
        height = self.images["Original"].img_display.height
        mode = self.images["Original"].img_display.mode
        self.label_image_info["text"] = f"{self.data_type} : {width} x {height} {mode}"

        os.chdir(os.path.dirname(filename))

        if self.prefs["width"] != width or self.prefs["height"] != height:
            self.reset_backgroundpts()

        self.prefs["width"] = width
        self.prefs["height"] = height
        
        tmp_state = fitsheader_2_app_state(self, self.cmd.app_state, self.images["Original"].fits_header)
        self.cmd: Command = Command(INIT_HANDLER, background_points=tmp_state["background_points"])
        self.cmd.execute()
        
        self.zoom_fit(width, height)
        self.redraw_image()
        self.loading_frame.end()
        return
    
    def toggle_crop_mode(self):
        
        if self.images["Original"] is None:
            messagebox.showerror("Error", _("Please load your picture first."))
            return
        
        self.startx = 0
        self.starty = 0
        self.endx = self.images["Original"].width
        self.endy = self.images["Original"].height

        if(self.crop_mode):
            self.crop_mode = False
        else:
            self.crop_mode = True
        
        self.redraw_points()
        
    def crop_apply(self):
        
        if (not self.crop_mode):
            return
        
        for astroimg in self.images.values():
            if(astroimg is not None):
                astroimg.crop(self.startx, self.endx, self.starty, self.endy)

        self.reset_backgroundpts()
        self.crop_mode = False
        self.zoom_fit(self.images[self.display_type.get()].width, self.images[self.display_type.get()].height)
        self.redraw_image()
        self.redraw_points()
        return
        
        
        
    def select_background(self,event=None):
        
        if self.images["Original"] is None:
            messagebox.showerror("Error", _("Please load your picture first."))
            return
        
        self.loading_frame.start()
        self.cmd = Command(SEL_POINTS_HANDLER, self.cmd, data=self.images["Original"].img_array, 
                           num_pts=self.bg_pts.get(), tol=self.bg_tol.get(), sample_size=self.sample_size.get())
        self.cmd.execute()
        self.redraw_image()
        self.loading_frame.end()
        return

    def change_stretch(self,event=None):
        self.loading_frame.start()
        
        all_images = []
        stretches = []
        for img in self.images.values():    
            if(img is not None):
                all_images.append(img.img_array)
        if len(all_images) > 0:
            stretch_params = self.images["Original"].get_stretch()
            stretches = stretch_all(all_images, stretch_params)
        for idx, img in enumerate(self.images.values()):
            if(img is not None):
                img.update_display_from_array(stretches[idx])
        self.loading_frame.end()
        
        self.redraw_image()
        return


    def update_saturation(self, event=None):
        for img in self.images.values():
            if img is not None:
                img.update_saturation()
        
        self.redraw_image()

   
    def save_image(self):
       
       
       if(self.saveas_type.get() == "16 bit Tiff" or self.saveas_type.get() == "32 bit Tiff"):
           dir = tk.filedialog.asksaveasfilename(
               initialfile = self.filename + "_GraXpert.tiff",
               filetypes = [("Tiff", ".tiff")],
               defaultextension = ".tiff",
               initialdir = self.prefs["working_dir"]
               )         
       elif(self.saveas_type.get() == "16 bit XISF" or self.saveas_type.get() == "32 bit XISF"):       
            dir = tk.filedialog.asksaveasfilename(
                initialfile = self.filename + "_GraXpert.xisf",
                filetypes = [("XISF", ".xisf")],
                defaultextension = ".xisf",
                initialdir = self.prefs["working_dir"]
                )           
       else:
           dir = tk.filedialog.asksaveasfilename(
               initialfile = self.filename + "_GraXpert.fits",
               filetypes = [("Fits", ".fits")],
               defaultextension = ".fits",
               initialdir = self.prefs["working_dir"]
               )
                           
       if(dir == ""):
           return
        
       self.loading_frame.start()
       
       try:
           self.images["Processed"].save(dir, self.saveas_type.get())
       except:
           messagebox.showerror("Error", _("Error occured when saving the image."))
           
       self.loading_frame.end()

    def save_stretched_image(self):
       
       
       if(self.saveas_type.get() == "16 bit Tiff" or self.saveas_type.get() == "32 bit Tiff"):
           dir = tk.filedialog.asksaveasfilename(
               initialfile = self.filename + "_stretched_GraXpert.tiff",
               filetypes = [("Tiff", ".tiff")],
               defaultextension = ".tiff",
               initialdir = self.prefs["working_dir"]
               )         
       elif(self.saveas_type.get() == "16 bit XISF" or self.saveas_type.get() == "32 bit XISF"):       
            dir = tk.filedialog.asksaveasfilename(
                initialfile = self.filename + "_stretched_GraXpert.xisf",
                filetypes = [("XISF", ".xisf")],
                defaultextension = ".xisf",
                initialdir = self.prefs["working_dir"]
                )           
       else:
           dir = tk.filedialog.asksaveasfilename(
               initialfile = self.filename + "_stretched_GraXpert.fits",
               filetypes = [("Fits", ".fits")],
               defaultextension = ".fits",
               initialdir = self.prefs["working_dir"]
               )
                           
       if(dir == ""):
           return
        
       self.loading_frame.start()
       
       try:
           if self.images["Processed"] is None:
               self.images["Original"].save_stretched(dir, self.saveas_type.get())
           else:
               self.images["Processed"].save_stretched(dir, self.saveas_type.get())
       except:
           messagebox.showerror("Error", _("Error occured when saving the image."))
           
       self.loading_frame.end()
       
    def save_background_image(self):

         
        if(self.saveas_type.get() == "16 bit Tiff" or self.saveas_type.get() == "32 bit Tiff"):
            dir = tk.filedialog.asksaveasfilename(
                initialfile = self.filename + "_background.tiff",
                filetypes = [("Tiff", ".tiff")],
                defaultextension = ".tiff",
                initialdir = self.prefs["working_dir"]
                )
        elif(self.saveas_type.get() == "16 bit XISF" or self.saveas_type.get() == "32 bit XISF"):
            dir = tk.filedialog.asksaveasfilename(
                initialfile = self.filename + "_background.xisf",
                filetypes = [("XISF", ".xisf")],
                defaultextension = ".xisf",
                initialdir = self.prefs["working_dir"]
                ) 
        else:
            dir = tk.filedialog.asksaveasfilename(
                initialfile = self.filename + "_background.fits",
                filetypes = [("Fits", ".fits")],
                defaultextension = ".fits",
                initialdir = os.getcwd()
                )
        
        if(dir == ""):
            return
        
        self.loading_frame.start()
        
        try:
            self.images["Background"].save(dir, self.saveas_type.get())
        except:
            messagebox.showerror("Error", _("Error occured when saving the image."))
            
        self.loading_frame.end()
        
    
    def reset_backgroundpts(self):
        
        if len(self.cmd.app_state["background_points"]) > 0:
            self.cmd = Command(RESET_POINTS_HANDLER, self.cmd)
            self.cmd.execute()
            self.redraw_image()
    
    def calculate(self):

        if self.images["Original"] is None:
            messagebox.showerror("Error", _("Please load your picture first."))
            return

        background_points = self.cmd.app_state["background_points"]
        
        #Error messages if not enough points
        if(len(background_points) == 0):
            messagebox.showerror("Error", _("Please select background points with left click."))
            return
        
        if(len(background_points) < 2 and self.interpol_type.get() == "Kriging"):
            messagebox.showerror("Error", _("Please select at least 2 background points with left click for the Kriging method."))
            return
        
        if(len(background_points) < 16 and self.interpol_type.get() == "Splines"):
            messagebox.showerror("Error", _("Please select at least 16 background points with left click for the Splines method."))
            return
        
        self.loading_frame.start()
        
        imarray = np.copy(self.images["Original"].img_array)
        
        downscale_factor = 1
        
        if(self.interpol_type.get() == "Kriging" or self.interpol_type.get() == "RBF"):
            downscale_factor = 4

        self.images["Background"] = AstroImage(self.stretch_option_current, self.saturation)
        self.images["Background"].set_from_array(background_extraction.extract_background(
            imarray,np.array(background_points),
            self.interpol_type.get(),self.smoothing.get(),
            downscale_factor, self.sample_size.get(),
            self.RBF_kernel.get(),self.spline_order.get(),
            self.corr_type.get()
            ))

        self.images["Processed"] = AstroImage(self.stretch_option_current, self.saturation)
        self.images["Processed"].set_from_array(imarray)
        
        # Update fits header and metadata
        background_mean = np.mean(self.images["Background"].img_array)
        self.images["Processed"].update_fits_header(self.images["Original"].fits_header, background_mean, self, self.cmd.app_state)
        self.images["Background"].update_fits_header(self.images["Original"].fits_header, background_mean, self, self.cmd.app_state)
        
        self.images["Processed"].copy_metadata(self.images["Original"])
        self.images["Background"].copy_metadata(self.images["Original"])

        all_images = [self.images["Original"].img_array, self.images["Processed"].img_array, self.images["Background"].img_array]
        stretches = stretch_all(all_images, self.images["Original"].get_stretch())
        self.images["Original"].update_display_from_array(stretches[0])
        self.images["Processed"].update_display_from_array(stretches[1])
        self.images["Background"].update_display_from_array(stretches[2])
        
        self.display_type.set("Processed")
        self.redraw_image()
        
        self.loading_frame.end()

        return
    
    def enter_key(self,enter):
        
        self.calculate()
        
    
    def mouse_down_left(self,event):
        
        self.left_drag_timer = -1
        if(str(event.widget).split(".")[-1] != "picture" or self.images["Original"] is None):
            return
        
        self.clicked_inside_pt = False       
        point_im = self.to_image_point(event.x,event.y)
        
        if len(self.cmd.app_state["background_points"]) != 0 and len(point_im) != 0 and self.display_pts.get():
            
            eventx_im = point_im[0]
            eventy_im = point_im[1]
            
            background_points = self.cmd.app_state["background_points"]
            
            min_idx = -1
            min_dist = -1
            
            for i in range(len(background_points)):
                x_im = background_points[i][0]
                y_im = background_points[i][1]
                            
                dist = np.max(np.abs([x_im-eventx_im, y_im-eventy_im]))
                
                if(min_idx == -1 or dist < min_dist):
                    min_dist = dist
                    min_idx = i
            
            
            if(min_idx != -1 and min_dist <= self.sample_size.get()):
                self.clicked_inside_pt = True
                self.clicked_inside_pt_idx = min_idx
                self.clicked_inside_pt_coord = self.cmd.app_state["background_points"][min_idx]
        
        if(self.crop_mode):
            #Check if inside circles to move crop corners
            corner1 = self.to_canvas_point(self.startx, self.starty)
            corner2 = self.to_canvas_point(self.endx, self.endy)
            if((event.x - corner1[0])**2 + (event.y - corner1[1])**2 < 15**2 or (event.x - corner2[0])**2 + (event.y - corner2[1])**2 < 15**2):
                self.clicked_inside_pt = True
                
        self.__old_event = event

        
    def mouse_release_left(self,event):
        
        if(str(event.widget).split(".")[-1] != "picture" or self.images["Original"] is None or not self.display_pts.get()):
            return
        

        if self.clicked_inside_pt and not self.crop_mode:            
            new_point = self.to_image_point(event.x,event.y)
            self.cmd.app_state["background_points"][self.clicked_inside_pt_idx] = self.clicked_inside_pt_coord
            self.cmd = Command(MOVE_POINT_HANDLER, prev=self.cmd, new_point=new_point, idx=self.clicked_inside_pt_idx)
            self.cmd.execute()
               
            
        elif(len(self.to_image_point(event.x,event.y)) != 0 and (event.time - self.left_drag_timer < 100 or self.left_drag_timer == -1)):

            point = self.to_image_point(event.x,event.y)
            
            if not self.flood_select_pts.get():
                self.cmd = Command(ADD_POINT_HANDLER, prev=self.cmd, point=point)
            else:
                self.cmd = Command(
                    ADD_POINTS_HANDLER,
                    prev=self.cmd,
                    point=point,
                    tol=self.bg_tol.get(),
                    bg_pts=self.bg_pts.get(),
                    sample_size=self.sample_size.get(),
                    image=self.images["Original"]
                )
            self.cmd.execute()
            

        self.redraw_points()
        self.__old_event = event
        self.left_drag_timer = -1
        
    def mouse_move_left(self, event):
        
        if(str(event.widget).split(".")[-1] != "picture" or self.images["Original"] is None):
            return
        
        if (self.images[self.display_type.get()] is None):
            return
        
        if(self.left_drag_timer == -1):
            self.left_drag_timer = event.time
        
        if(self.clicked_inside_pt and self.display_pts.get() and not self.crop_mode):         
            new_point = self.to_image_point(event.x, event.y)
            if len(new_point) != 0:
                self.cmd.app_state["background_points"][self.clicked_inside_pt_idx] = new_point
                
            self.redraw_points()
            
        elif(self.clicked_inside_pt and self.crop_mode):
            new_point = self.to_image_point_pinned(event.x, event.y)
            corner1_canvas = self.to_canvas_point(self.startx, self.starty)
            corner2_canvas = self.to_canvas_point(self.endx, self.endy)
            
            dist1 = (event.x - corner1_canvas[0])**2 + (event.y - corner1_canvas[1])**2
            dist2 = (event.x - corner2_canvas[0])**2 + (event.y - corner2_canvas[1])**2
            if(dist1 < dist2):
                self.startx = int(new_point[0])
                self.starty = int(new_point[1])
            else:
                self.endx = int(new_point[0])
                self.endy = int(new_point[1])
                
            self.redraw_points()
                
        else:
            if(event.time - self.left_drag_timer >= 100):            
                self.translate(event.x - self.__old_event.x, event.y - self.__old_event.y)
                self.redraw_image()
        
        
        self.mouse_move(event)
        self.__old_event = event
        return        

        
    def remove_pt(self,event):
        
        if len(self.cmd.app_state["background_points"]) == 0 or not self.display_pts.get():
            return False
            
        point_im = self.to_image_point(event.x,event.y)
        if len(point_im) == 0:
            return False
            
        eventx_im = point_im[0]
        eventy_im = point_im[1]
        
        background_points = self.cmd.app_state["background_points"]
        
        min_idx = -1
        min_dist = -1
        
        for i in range(len(background_points)):
            x_im = background_points[i][0]
            y_im = background_points[i][1]
                        
            dist = np.max(np.abs([x_im-eventx_im, y_im-eventy_im]))
            
            if(min_idx == -1 or dist < min_dist):
                min_dist = dist
                min_idx = i
        
        
        if(min_idx != -1 and min_dist <= self.sample_size.get()):
            point = background_points[min_idx]
            self.cmd = Command(RM_POINT_HANDLER, self.cmd, idx=min_idx, point=point)
            self.cmd.execute()
            return True
        else:
            return False
            
        
    def mouse_down_right(self, event):
        
        if(str(event.widget).split(".")[-1] != "picture" or self.images["Original"] is None or not self.display_pts.get()):
            return
        
        self.remove_pt(event)
        self.redraw_points()
        self.__old_event = event




    def mouse_move(self, event):

        if (self.images[self.display_type.get()] is None):
            return
        
        image_point = self.to_image_point(event.x, event.y)
        if len(image_point) != 0:
            text = "x=" + f"{image_point[0]:.2f}" + ",y=" + f"{image_point[1]:.2f}  "
            if(self.images[self.display_type.get()].img_array.shape[2] == 3):
                R, G, B = self.images[self.display_type.get()].get_local_median(image_point)            
                text = text + "RGB = (" + f"{R:.4f}," + f"{G:.4f}," + f"{B:.4f})"
            
            if(self.images[self.display_type.get()].img_array.shape[2] == 1):
                L = self.images[self.display_type.get()].get_local_median(image_point)
                text = text + "L= " + f"{L:.4f}"
            
            self.label_image_pixel["text"] = text
        else:
            self.label_image_pixel["text"] = ("(--, --)")


    def reset_zoom(self, event):
        
        if self.images[self.display_type.get()] is None:
            return
        self.zoom_fit(self.images[self.display_type.get()].width, self.images[self.display_type.get()].height)
        self.redraw_image()


    def mouse_wheel(self, event):

        if "help_canvas" in str(event.widget):
            if self.help_panel.help_canvas.yview() == (0.0,1.0):
                return
            
            if (event.delta > 0 or event.num == 4):
                self.help_panel.help_canvas.yview_scroll(-1, "units")
            else:
                self.help_panel.help_canvas.yview_scroll(1, "units")       
                
        elif "advanced_canvas" in str(event.widget):
            if self.help_panel.advanced_canvas.yview() == (0.0,1.0):
                return
            
            if (event.delta > 0 or event.num == 4):
                self.help_panel.advanced_canvas.yview_scroll(-1, "units")
            else:
                self.help_panel.advanced_canvas.yview_scroll(1, "units") 
        
        elif "left_panel" in str(event.widget):
            if self.side_canvas.yview() == (0.0,1.0):
                return
            
            if (event.delta > 0 or event.num == 4):
                self.side_canvas.yview_scroll(-1, "units")
            else:
                self.side_canvas.yview_scroll(1, "units")
                
        elif "picture" in str(event.widget):
            if self.images[self.display_type.get()] is None:
                return    
    
            if (event.delta > 0 or event.num == 4):
    
                self.scale_at(6/5, event.x, event.y)
            else:
    
                self.scale_at(5/6, event.x, event.y)
       
            self.redraw_image()

        

    def reset_transform(self):

        self.mat_affine = np.eye(3)

    def translate(self, offset_x, offset_y):

        mat = np.eye(3)
        mat[0, 2] = float(offset_x)
        mat[1, 2] = float(offset_y)

        self.mat_affine = np.dot(mat, self.mat_affine)

    def scale(self, scale:float):

        mat = np.eye(3)
        mat[0, 0] = scale
        mat[1, 1] = scale

        self.mat_affine = np.dot(mat, self.mat_affine)

    def scale_at(self, scale:float, cx:float, cy:float):



        self.translate(-cx, -cy)
        self.scale(scale)
        self.translate(cx, cy)



    def zoom_fit(self, image_width, image_height):


        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if (image_width * image_height <= 0) or (canvas_width * canvas_height <= 0):
            return


        self.reset_transform()

        scale = 1.0
        offsetx = 0.0
        offsety = 0.0

        if (canvas_width * image_height) > (image_width * canvas_height):

            scale = canvas_height / image_height
            offsetx = (canvas_width - image_width * scale) / 2
        else:

            scale = canvas_width / image_width
            offsety = (canvas_height - image_height * scale) / 2


        self.scale(scale)
        self.translate(offsetx, offsety)

    def to_image_point(self, x, y):

        if self.images[self.display_type.get()] is None:
            return []

        mat_inv = np.linalg.inv(self.mat_affine)
        image_point = np.dot(mat_inv, (x, y, 1.))
        
        width = self.images[self.display_type.get()].width
        height = self.images[self.display_type.get()].height
        
        if  image_point[0] < 0 or image_point[1] < 0 or image_point[0] > width or image_point[1] > height:
            return []

        return image_point

    def to_image_point_pinned(self, x, y):
        
        if self.images[self.display_type.get()] is None:
            return []

        mat_inv = np.linalg.inv(self.mat_affine)
        image_point = np.dot(mat_inv, (x, y, 1.))
        
        width = self.images[self.display_type.get()].width
        height = self.images[self.display_type.get()].height
        
        if image_point[0] < 0:
            image_point[0] = 0
        if image_point[1] < 0:
            image_point[1] = 0
        if image_point[0] > width:
            image_point[0] = width
        if image_point[1] > height:
            image_point[1] = height

        return image_point
    
    def to_canvas_point(self, x, y):
        
        return np.dot(self.mat_affine,(x,y,1.))

    def draw_image(self, pil_image):

        if pil_image is None:
            return


        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()


        mat_inv = np.linalg.inv(self.mat_affine)


        affine_inv = (
            mat_inv[0, 0], mat_inv[0, 1], mat_inv[0, 2],
            mat_inv[1, 0], mat_inv[1, 1], mat_inv[1, 2]
            )


        dst = pil_image.transform(
                    (canvas_width, canvas_height),
                    Image.AFFINE,
                    affine_inv,
                    Image.BILINEAR  
                    )

        im = ImageTk.PhotoImage(image=dst)


        item = self.canvas.create_image(
                0, 0,           
                anchor='nw',    
                image=im        
                )

        self.image = im
        self.redraw_points()
        return
    
    def redraw_points(self):
        
        if self.images["Original"] is None:
            return
    
        color = hls_to_rgb(self.sample_color.get()/360, 0.5, 1.0)
        color = (int(color[0]*255), int(color[1]*255), int(color[2]*255))
        color = '#%02x%02x%02x' % color
        
        self.canvas.delete("sample")
        self.canvas.delete("crop")  
        rectsize = self.sample_size.get()
        background_points = self.cmd.app_state["background_points"]
        
        if self.display_pts.get() and not self.crop_mode:
            for point in background_points:        
                corner1 = self.to_canvas_point(point[0]-rectsize,point[1]-rectsize)
                corner2 = self.to_canvas_point(point[0]+rectsize,point[1]+rectsize)
                self.canvas.create_rectangle(corner1[0],corner1[1], corner2[0],corner2[1],outline=color, width=2, tags="sample")
        
        if self.crop_mode:
            corner1 = self.to_canvas_point(self.startx, self.starty)
            corner2 = self.to_canvas_point(self.endx, self.endy)
            self.canvas.create_rectangle(corner1[0],corner1[1], corner2[0],corner2[1], outline=color, width=2, tags="crop")
            self.canvas.create_oval(corner1[0]-15,corner1[1]-15, corner1[0]+15,corner1[1]+15, outline=color, width=2, tags="crop")
            self.canvas.create_oval(corner2[0]-15,corner2[1]-15, corner2[0]+15,corner2[1]+15, outline=color, width=2, tags="crop")
        return

    def redraw_image(self):

        if self.images[self.display_type.get()] is None:
            return
        self.draw_image(self.images[self.display_type.get()].img_display_saturated)

    def undo(self, event):
        if not type(self.cmd.handler) is InitHandler:
            undo = self.cmd.undo()
            self.cmd = undo
            self.redraw_points()
    
    def redo(self, event):
        if self.cmd.next is not None:
            redo = self.cmd.redo()
            self.cmd = redo
            self.redraw_points()
            
    def switch_display(self, event):
        if(self.images["Processed"] is None and self.display_type.get() != "Original"):
            self.display_type.set("Original")
            messagebox.showerror("Error", _("Please select background points and press the Calculate button first"))         
            return
        
        self.loading_frame.start()
        self.redraw_image()
        self.loading_frame.end()
    
    def on_closing(self, logging_thread):
        

        self.prefs = app_state_2_prefs(self.prefs, self.cmd.app_state, self)

        prefs_filename = os.path.join(user_config_dir(appname="GraXpert"), "preferences.json")
        save_preferences(prefs_filename, self.prefs)
        try:
            executor.shutdown(cancel_futures=True)
        except Exception as e:
            logging.exception("error shutting down ProcessPoolExecutor")
        shutdown_logging(logging_thread)
        root.destroy()

def scale_img(path, scaling, shape):
    img = io.imread(resource_path(path))
    img = resize(img, (int(shape[0]*scaling),int(shape[1]*scaling)))
    img = img*255
    img = img.astype(dtype=np.uint8)
    io.imsave(resource_path(resource_path(path.replace('.png', '-scaled.png'))), img, check_contrast=False)

if __name__ == "__main__":

    logging_thread = initialize_logging()

    root = hdpitk.HdpiTk()
    scaling = get_scaling_factor()
    
    scale_img("./forest-dark/vert-hover.png", scaling*0.9, (20,10))
    scale_img("./forest-dark/vert-basic.png", scaling*0.9, (20,10))
    
    scale_img("./forest-dark/thumb-hor-accent.png", scaling*0.9, (20,8))
    scale_img("./forest-dark/thumb-hor-hover.png", scaling*0.9, (20,8))
    scale_img("./forest-dark/thumb-hor-basic.png", scaling*0.9, (20,8))
    scale_img("./forest-dark/scale-hor.png", scaling, (20,20))
    
    scale_img("./forest-dark/check-accent.png", scaling*0.8, (20,20))
    scale_img("./forest-dark/check-basic.png", scaling*0.8, (20,20))
    scale_img("./forest-dark/check-hover.png", scaling*0.8, (20,20))
    scale_img("./forest-dark/check-unsel-accent.png", scaling*0.8, (20,20))
    scale_img("./forest-dark/check-unsel-basic.png", scaling*0.8, (20,20))
    scale_img("./forest-dark/check-unsel-hover.png", scaling*0.8, (20,20))
    scale_img("./forest-dark/check-unsel-pressed.png", scaling*0.8, (20,20))
    
    scale_img("./img/gfx_number_1.png", scaling*0.7, (25,25))
    scale_img("./img/gfx_number_2.png", scaling*0.7, (25,25))
    scale_img("./img/gfx_number_3.png", scaling*0.7, (25,25))
    scale_img("./img/gfx_number_4.png", scaling*0.7, (25,25))
    scale_img("./img/gfx_number_5.png", scaling*0.7, (25,25))
    scale_img("./img/hourglass.png", scaling, (25,25))
    
    root.tk.call("source", resource_path("forest-dark.tcl"))   
    style = ttk.Style(root)
    style.theme_use("forest-dark")
    style.configure("TButton", padding=(8*scaling, 12*scaling, 8*scaling, 12*scaling))
    style.configure("TMenubutton", padding=(8*scaling, 4*scaling, 4*scaling, 4*scaling))
    root.tk.call("wm", "iconphoto", root._w, tk.PhotoImage(file=resource_path("img/Icon.png")))
    root.tk.call('tk', 'scaling', scaling)
    root.option_add("*TkFDialog*foreground", "black")
    app = Application(master=root)
    root.protocol("WM_DELETE_WINDOW", lambda: app.on_closing(logging_thread))
    root.createcommand("::tk::mac::Quit", lambda: app.on_closing(logging_thread))

    if '_PYIBoot_SPLASH' in os.environ and importlib.util.find_spec("pyi_splash"):
        import pyi_splash
        pyi_splash.close()

    app.mainloop()
    