# -*- coding: utf-8 -*-
"""
Created on Sun Feb 13 10:05:08 2022
@author: steff
"""

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk 
import math                   
import numpy as np            
import os
from app_state import INITIAL_STATE
import background_extraction
from commands import ADD_POINT_HANDLER, INIT_HANDLER, RESET_POINTS_HANDLER, RM_POINT_HANDLER, Command, SEL_POINTS_HANDLER, InitHandler
from preferences import DEFAULT_PREFS, Prefs, app_state_2_prefs, merge_json, prefs_2_app_state
import tooltip
from loadingframe import LoadingFrame
from help_panel import Help_Panel
from astroimage import AstroImage
import json
from appdirs import user_config_dir

root = tk.Tk()

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        self.master.geometry("1920x1080")
        
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
        
        self.my_title = "GraXpert"
        self.master.title(self.my_title)

        self.prefs: Prefs = DEFAULT_PREFS
        prefs_file = os.path.join(user_config_dir(), ".graxpert", "preferences.json")
        if os.path.isfile(prefs_file):
            with open(prefs_file) as f:
                json_prefs: Prefs = json.load(f)
                self.prefs = merge_json(self.prefs, json_prefs)

        tmp_state = prefs_2_app_state(self.prefs, INITIAL_STATE)
        
        self.cmd: Command = Command(INIT_HANDLER, background_points=tmp_state["background_points"])
        self.cmd.execute()

        self.create_widget()

        self.reset_transform()
        

    def create_widget(self):
        
        #Style    
        border_color = "#171717"
        bg_color = "#474747"
        button_color = "#6a6a6a"
        text_color = "#F0F0F0"
        menu_font = ('Segoe UI Semibold', 12, 'normal')
        button_height = 2
        button_width = 16
        relief = "raised"
        bdwidth = 5

        frame_statusbar = tk.Frame(self.master, bd=1, relief = tk.SUNKEN)
        self.label_image_info = tk.Label(frame_statusbar, text="image info", anchor=tk.E, padx = 5)
        self.label_image_pixel = tk.Label(frame_statusbar, text="(x, y)", anchor=tk.W, padx = 5)
        self.label_image_info.pack(side=tk.RIGHT)
        self.label_image_pixel.pack(side=tk.LEFT)
        frame_statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        
        self.master.grid_columnconfigure(3)
        #Right help panel
        
        self.canvas = tk.Canvas(self.master, background="black", name="picture")
        self.help_panel = Help_Panel(self.master, self.canvas)
        
       
        # Canvas
        
        self.canvas.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        
        
        self.display_options = ["Original","Processed","Background"]
        self.display_type = tk.StringVar()
        self.display_type.set(self.display_options[0])
        self.display_menu = tk.OptionMenu(self.canvas, self.display_type, *self.display_options, command=self.switch_display)
        self.display_menu.config(font=menu_font, bg=button_color, fg=text_color, relief=relief, 
                                  borderwidth=bdwidth, highlightbackground=bg_color)
        self.display_menu.place(relx=0.5, rely=0.01)
        tt_display_type = tooltip.Tooltip(self.display_menu, text=tooltip.display_text, wraplength=500)
        
        self.loading_frame = LoadingFrame(self.canvas, self.master)


        self.master.bind("<Button-1>", self.mouse_down_left)                   # Left Mouse Button
        self.master.bind("<Button-3>", self.mouse_down_right)                  # Right Mouse Button
        self.master.bind("<B1-Motion>", self.mouse_move_left)                  # Left Mouse Button Drag
        self.master.bind("<Motion>", self.mouse_move)                          # Mouse move
        self.master.bind("<Double-Button-1>", self.mouse_double_click_left)    # Left Button Double Click
        self.master.bind("<MouseWheel>", self.mouse_wheel)                     # Mouse Wheel
        self.master.bind("<Button-4>", self.mouse_wheel)                       # Mouse Wheel Linux
        self.master.bind("<Button-5>", self.mouse_wheel)                       # Mouse Wheel Linux
        self.master.bind("<Return>", self.enter_key)                           # Enter Key
        self.master.bind("<Control-z>", self.undo)                             # undo
        self.master.bind("<Control-y>", self.redo)                             # redo
        
        
        #Side menu
        
        self.side_menu = tk.Frame(self.master, bg=bg_color, relief=relief, borderwidth=0)
        self.side_menu.pack(side=tk.LEFT, fill=tk.Y)
        
        self.side_menu.grid_columnconfigure(0, weight=1)
        
        for i in range(19):
            self.side_menu.grid_rowconfigure(i, weight=1)
        
        #---Display---
        
        self.load_image_button = tk.Button(self.side_menu, 
                         text="Load",
                         font=menu_font,
                         bg=button_color,fg=text_color,
                         relief=relief, borderwidth=bdwidth,
                         command=self.menu_open_clicked,
                         height=button_height,width=button_width)
        tt_load = tooltip.Tooltip(self.load_image_button, text=tooltip.load_text)
        self.load_image_button.grid(column=0, row=1, pady=(15,5), padx=15, sticky="news")
        
        self.stretch_text = tk.Message(self.side_menu, text="Stretch Options:", bg=bg_color, font=menu_font, fg=text_color)
        self.stretch_text.config(width=200)
        self.stretch_text.grid(column=0, row=2, pady=(5,0), padx=15, sticky="ews")
        
        self.stretch_options = ["No Stretch", "10% Bg, 3 sigma", "15% Bg, 3 sigma", "20% Bg, 3 sigma", "25% Bg, 1.25 sigma"]
        self.stretch_option_current = tk.StringVar()
        self.stretch_option_current.set(self.stretch_options[0])
        if "stretch_option" in self.prefs:
            self.stretch_option_current.set(self.prefs["stretch_option"])
        self.stretch_menu = tk.OptionMenu(self.side_menu, self.stretch_option_current, *self.stretch_options,command=self.change_stretch)
        self.stretch_menu.config(font=menu_font, bg=button_color, fg=text_color, relief=relief, borderwidth=bdwidth, highlightbackground=bg_color)
        self.stretch_menu.grid(column=0, row=3, pady=(0,5), padx=15, sticky="news")
        tt_stretch= tooltip.Tooltip(self.stretch_menu, text=tooltip.stretch_text)
        
      
        #---Selection---
        
        self.reset_button = tk.Button(self.side_menu, 
                         text="Reset Points",
                         font=menu_font,
                         bg=button_color,fg=text_color,
                         relief=relief, borderwidth=bdwidth,
                         command=self.reset_backgroundpts,
                         height=button_height,width=button_width)
        self.reset_button.grid(column=0, row=4, pady=5, padx=15, sticky="news")
        tt_reset= tooltip.Tooltip(self.reset_button, text=tooltip.reset_text)
        
        self.bg_selection_text = tk.Message(self.side_menu, text="Points per row:", bg=bg_color)
        self.bg_selection_text.config(width=300, font=menu_font, fg=text_color)
        self.bg_selection_text.grid(column=0, row=5, pady=(5,0), padx=15, sticky="ews")
        
        self.bg_pts = tk.IntVar()
        self.bg_pts.set(15)
        if "bg_pts_option" in self.prefs:
            self.bg_pts.set(self.prefs["bg_pts_option"])
        self.bg_pts_slider = tk.Scale(self.side_menu,orient=tk.HORIZONTAL,from_=4,to=20,tickinterval=16,resolution=1,
                                      var=self.bg_pts, width=12, bg=button_color, fg=text_color, relief=relief, 
                                      borderwidth=bdwidth, highlightbackground=bg_color)
        self.bg_pts_slider.grid(column=0, row=6, pady=(0,0), padx=15, sticky="news")
        tt_bg_points= tooltip.Tooltip(self.bg_pts_slider, text=tooltip.num_points_text)
        
        self.bg_selection_tol = tk.Message(self.side_menu, text="Grid Tolerance:", bg=bg_color)
        self.bg_selection_tol.config(width=300, font=menu_font, fg=text_color)
        self.bg_selection_tol.grid(column=0, row=7, pady=(0,0), padx=15, sticky="ews")
        
        self.bg_tol = tk.DoubleVar()
        self.bg_tol.set(1)
        if "bg_tol_option" in self.prefs:
            self.bg_tol.set(self.prefs["bg_tol_option"])
        self.bg_tol_slider = tk.Scale(self.side_menu,orient=tk.HORIZONTAL,from_=-10,to=10,tickinterval=20,resolution=0.1,
                                      var=self.bg_tol, width=12, bg=button_color, fg=text_color, relief=relief, 
                                      borderwidth=bdwidth, highlightbackground=bg_color)
        self.bg_tol_slider.grid(column=0, row=8, pady=(0,0), padx=15, sticky="news")
        tt_tol_points= tooltip.Tooltip(self.bg_tol_slider, text=tooltip.bg_tol_text)
        
        self.bg_selection_button = tk.Button(self.side_menu, 
                         text="Grid Selection",
                         font=menu_font,
                         bg=button_color,fg=text_color,
                         relief=relief, borderwidth=bdwidth,
                         command=self.select_background,
                         height=button_height,width=button_width)
        self.bg_selection_button.grid(column=0, row=9, pady=5, padx=15, sticky="news")
        tt_bg_select = tooltip.Tooltip(self.bg_selection_button, text= tooltip.bg_select_text)
        
        #---Calculation---
        
        self.intp_type_text = tk.Message(self.side_menu, text="Method:", bg=bg_color, font=menu_font)
        self.intp_type_text.config(width=200, font=menu_font, fg=text_color)
        self.intp_type_text.grid(column=0, row=10, pady=(5,0), padx=15, sticky="ews")
        
        self.interpol_options = ["RBF", "Splines", "Kriging"]
        self.interpol_type = tk.StringVar()
        self.interpol_type.set(self.interpol_options[0])
        if "interpol_type_option" in self.prefs:
            self.interpol_type.set(self.prefs["interpol_type_option"])
        self.interpol_menu = tk.OptionMenu(self.side_menu, self.interpol_type, *self.interpol_options)
        self.interpol_menu.config(font=menu_font, bg=button_color, fg=text_color, relief=relief, 
                                  borderwidth=bdwidth, highlightbackground=bg_color)
        self.interpol_menu.grid(column=0, row=11, pady=(0,5), padx=15, sticky="news")
        tt_interpol_type= tooltip.Tooltip(self.interpol_menu, text=tooltip.interpol_type_text)
        
        self.smooth_text = tk.Message(self.side_menu, text="Smoothing:", bg=bg_color)
        self.smooth_text.config(width=200, font=menu_font, fg=text_color)
        self.smooth_text.grid(column=0, row=12, pady=(5,0), padx=15, sticky="ews")
        
        self.smoothing = tk.DoubleVar()
        self.smoothing.set(1.0)
        if "smoothing_option" in self.prefs:
            self.smoothing.set(self.prefs["smoothing_option"])
        self.smoothing_slider = tk.Scale(self.side_menu,orient=tk.HORIZONTAL,
                                         from_=0,to=1,tickinterval=1.0,resolution=0.05,var=self.smoothing,
                                         width=12, bg=button_color, fg=text_color, relief=relief, 
                                         borderwidth=bdwidth, highlightbackground=bg_color)
        self.smoothing_slider.grid(column=0, row=13, pady=(0,5), padx=15, sticky="news")
        tt_smoothing= tooltip.Tooltip(self.smoothing_slider, text=tooltip.smoothing_text)
        
        self.calculate_button = tk.Button(self.side_menu, 
                         text="Calculate",
                         font=menu_font,
                         bg=button_color,fg=text_color,
                         relief=relief, borderwidth=bdwidth,
                         command=self.calculate,
                         height=button_height,width=button_width)
        self.calculate_button.grid(column=0, row=14, pady=5, padx=15, sticky="news")
        tt_calculate= tooltip.Tooltip(self.calculate_button, text=tooltip.calculate_text)
        
        #---Saving---  
        
        self.saveas_text = tk.Message(self.side_menu, text="Save as:", bg=bg_color, font=menu_font)
        self.saveas_text.config(width=200, font=menu_font, fg=text_color)
        self.saveas_text.grid(column=0, row=15, pady=(5,0), padx=15, sticky="ews")
        
        self.saveas_options = ["16 bit Tiff", "32 bit Tiff", "16 bit Fits", "32 bit Fits"]
        self.saveas_type = tk.StringVar()
        self.saveas_type.set(self.saveas_options[0])
        if "saveas_option" in self.prefs:
            self.saveas_type.set(self.prefs["saveas_option"])
        self.saveas_menu = tk.OptionMenu(self.side_menu, self.saveas_type, *self.saveas_options)
        self.saveas_menu.config(font=menu_font, bg=button_color, fg=text_color, relief=relief, 
                                  borderwidth=bdwidth, highlightbackground=bg_color)
        self.saveas_menu.grid(column=0, row=16, pady=(0,5), padx=15, sticky="news")
        tt_interpol_type= tooltip.Tooltip(self.saveas_menu, text=tooltip.saveas_text)
        
        self.save_background_button = tk.Button(self.side_menu, 
                         text="Save Background",
                         font=menu_font,
                         bg=button_color,fg=text_color,
                         relief=relief, borderwidth=bdwidth,
                         command=self.save_background_image,
                         height=button_height,width=button_width)
        self.save_background_button.grid(column=0, row=17, pady=5, padx=15, sticky="news")
        tt_save_bg = tooltip.Tooltip(self.save_background_button, text=tooltip.save_bg_text)
              
        
        self.save_button = tk.Button(self.side_menu, 
                         text="Save Picture",
                         font=menu_font,
                         bg=button_color,fg=text_color,
                         relief=relief, borderwidth=bdwidth,
                         command=self.save_image,
                         height=button_height,width=button_width)
        self.save_button.grid(column=0, row=18, pady=5, padx=15, sticky="news")
        tt_save_pic= tooltip.Tooltip(self.save_button, text=tooltip.save_pic_text)
    
    
    def menu_open_clicked(self, event=None):

        if self.prefs["working_dir"] != "" and os.path.exists(self.prefs["working_dir"]):
            initialdir = self.prefs["working_dir"]
        else:
            initialdir = os.getcwd()
        
        filename = tk.filedialog.askopenfilename(
            filetypes = [("Image file", ".bmp .png .jpg .tif .tiff .fit .fits"), ("Bitmap", ".bmp"), ("PNG", ".png"), ("JPEG", ".jpg"), ("Tiff", ".tif .tiff"), ("Fits", ".fit .fits")],
            initialdir = initialdir
            )
        
        self.loading_frame.start()
        self.data_type = os.path.splitext(filename)[1]
        
        try:
            image = AstroImage(self.stretch_option_current)
            image.set_from_file(filename)
            self.images["Original"] = image
            self.prefs["working_dir"] = os.path.dirname(filename)
        except:
            messagebox.showerror("Error", "An error occurred while loading your picture.")
        
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
        
        self.zoom_fit(width, height)
        self.redraw_image()
        self.loading_frame.end()
        return
    
    def select_background(self,event=None):
        
        if self.images["Original"] is None:
            messagebox.showerror("Error", "Please load your picture first.")
            return
        
        self.loading_frame.start()
        self.cmd = Command(SEL_POINTS_HANDLER, self.cmd, data=self.images["Original"].img_array, num_pts=self.bg_pts.get(), tol=self.bg_tol.get())
        self.cmd.execute()
        self.redraw_image()
        self.loading_frame.end()
        return

    def change_stretch(self,event=None):
        self.loading_frame.start()
        for key, img in self.images.items():
            if(img is not None):
                img.update_display()
        self.loading_frame.end()
        
        self.redraw_image()
        return

    
   
    def save_image(self):
       
       
       if(self.saveas_type.get() == "16 bit Tiff" or self.saveas_type.get() == "32 bit Tiff"):
           dir = tk.filedialog.asksaveasfilename(
               initialfile = self.filename + "_GraXpert.tiff",
               filetypes = [("Tiff", ".tiff")],
               defaultextension = ".tiff",
               initialdir = self.prefs["working_dir"]
               )           
       else:
           dir = tk.filedialog.asksaveasfilename(
               initialfile = self.filename + "_GraXpert.fits",
               filetypes = [("Fits", ".fits")],
               defaultextension = ".fits",
               initialdir = self.prefs["working_dir"]
               )
       
       self.loading_frame.start()
       
       try:
           self.images["Processed"].save(dir, self.saveas_type.get(), self.images["Original"].fits_header)
       except:
           messagebox.showerror("Error", "Error occured when saving the image.")
           
       self.loading_frame.end()
       
    def save_background_image(self):

         
        if(self.saveas_type.get() == "16 bit Tiff" or self.saveas_type.get() == "32 bit Tiff"):
            dir = tk.filedialog.asksaveasfilename(
                initialfile = self.filename + "_background.tiff",
                filetypes = [("Tiff", ".tiff")],
                defaultextension = ".tiff",
                initialdir = self.prefs["working_dir"]
                )           
        else:
            dir = tk.filedialog.asksaveasfilename(
                initialfile = self.filename + "_background.fits",
                filetypes = [("Fits", ".fits")],
                defaultextension = ".fits",
                initialdir = os.getcwd()
                )
        
        self.loading_frame.start()
        
        try:
            self.images["Background"].save(dir, self.saveas_type.get(), self.images["Original"].fits_header)
        except:
            messagebox.showerror("Error", "Error occured when saving the image.")
            
        self.loading_frame.end()
        
    
    def reset_backgroundpts(self):
        
        if len(self.cmd.app_state["background_points"]) > 0:
            self.cmd = Command(RESET_POINTS_HANDLER, self.cmd)
            self.cmd.execute()
            self.redraw_image()
    
    def calculate(self):
        
        background_points = self.cmd.app_state["background_points"]
        
        #Error messages if not enough points
        if(len(background_points) == 0):
            messagebox.showerror("Error", "Please load your picture and select background points with right click.")
            return
        
        if(len(background_points) < 2 and self.interpol_type.get() == "Kriging"):
            messagebox.showerror("Error", "Please select at least 2 background points with right click for the Kriging method.")
            return
        
        if(len(background_points) < 16 and self.interpol_type.get() == "Splines"):
            messagebox.showerror("Error", "Please select at least 16 background points with right click for the Splines method.")
            return
        
        self.loading_frame.start()
        
        imarray = np.copy(self.images["Original"].img_array)
        
        downscale_factor = 1
        
        if(self.interpol_type.get() == "Kriging" or self.interpol_type.get() == "RBF"):
            downscale_factor = 4

        self.images["Background"] = AstroImage(self.stretch_option_current)
        self.images["Background"].set_from_array(background_extraction.extract_background(
            imarray,np.array(background_points),
            self.interpol_type.get(),self.smoothing.get(),
            downscale_factor
            ))

        self.images["Processed"] = AstroImage(self.stretch_option_current)
        self.images["Processed"].set_from_array(imarray)       
        
        self.display_type.set("Processed")
        self.redraw_image()
        
        self.loading_frame.end()
        return
    
    def enter_key(self,enter):
        
        self.calculate()
        
    
    def mouse_down_right(self,event):
        
        if(str(event.widget).split(".")[-1] != "picture"):
            return
        

        if(not self.remove_pt(event) and self.to_image_point(event.x,event.y) != []):
            point = self.to_image_point(event.x,event.y)
            self.cmd = Command(ADD_POINT_HANDLER, prev=self.cmd, point=point)
            self.cmd.execute()

        self.redraw_image()
        self.__old_event = event
        
    def remove_pt(self,event):
        
        if len(self.cmd.app_state["background_points"]) == 0:
            return False
        
        background_points = self.cmd.app_state["background_points"]
        
        min_idx = -1
        min_dist = -1
        
        for i in range(len(background_points)):
            x_im = background_points[i][0]
            y_im = background_points[i][1]
            
            eventx_im = self.to_image_point(event.x, event.y)[0]
            eventy_im = self.to_image_point(event.x, event.y)[1]
            
            dist = np.max(np.abs([x_im-eventx_im, y_im-eventy_im]))
            
            if(min_idx == -1 or dist < min_dist):
                min_dist = dist
                min_idx = i
        
        
        if(min_idx != -1 and min_dist <= 25):
            point = background_points[min_idx]
            self.cmd = Command(RM_POINT_HANDLER, self.cmd, idx=min_idx, point=point)
            self.cmd.execute()
            return True
        else:
            return False
            
        
    def mouse_down_left(self, event):
        
        if(str(event.widget).split(".")[-1] != "picture"):
            return
        
        self.__old_event = event


    def mouse_move_left(self, event):
        
        if(str(event.widget).split(".")[-1] != "picture"):
            return
        
        if (self.images[self.display_type.get()] is None):
            return
        self.translate(event.x - self.__old_event.x, event.y - self.__old_event.y)
        self.redraw_image()
        self.__old_event = event

    def mouse_move(self, event):

        if (self.images[self.display_type.get()] is None):
            return
        
        image_point = self.to_image_point(event.x, event.y)
        if image_point != []:
            self.label_image_pixel["text"] = "x=" + f"{image_point[0]:.2f}" + ",y=" + f"{image_point[1]:.2f}"
        else:
            self.label_image_pixel["text"] = ("(--, --)")


    def mouse_double_click_left(self, event):
        
        if(str(event.widget).split(".")[-1] != "picture"):
            return
        
        if self.images[self.display_type.get()] is None:
            return
        self.zoom_fit(self.images[self.display_type.get()].width, self.images[self.display_type.get()].height)
        self.redraw_image()

    def mouse_wheel(self, event):

        if self.images[self.display_type.get()] is None:
            return

        if event.state != 9:
            if (event.delta > 0 or event.num == 4):

                self.scale_at(6/5, event.x, event.y)
            else:

                self.scale_at(5/6, event.x, event.y)
        else:
            if (event.delta < 0):

                self.rotate_at(-5, event.x, event.y)
            else:

                self.rotate_at(5, event.x, event.y)     
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

    def rotate(self, deg:float):

        mat = np.eye(3)
        mat[0, 0] = math.cos(math.pi * deg / 180)
        mat[1, 0] = math.sin(math.pi * deg / 180)
        mat[0, 1] = -mat[1, 0]
        mat[1, 1] = mat[0, 0]

        self.mat_affine = np.dot(mat, self.mat_affine)

    def rotate_at(self, deg:float, cx:float, cy:float):


        self.translate(-cx, -cy)
        self.rotate(deg)
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
                    Image.NEAREST   
                    )

        im = ImageTk.PhotoImage(image=dst)


        item = self.canvas.create_image(
                0, 0,           
                anchor='nw',    
                image=im        
                )

        self.image = im
        
        self.canvas.delete("rectangle")
        
        rectsize=25
        background_points = self.cmd.app_state["background_points"]

        for point in background_points:        
            corner1 = self.to_canvas_point(point[0]-rectsize,point[1]-rectsize)
            corner2 = self.to_canvas_point(point[0]+rectsize,point[1]+rectsize)
            self.canvas.create_rectangle(corner1[0],corner1[1], corner2[0],corner2[1],outline="red", tags="rectangle")
            
        return

    def redraw_image(self):

        if self.images[self.display_type.get()] is None:
            return
        self.draw_image(self.images[self.display_type.get()].img_display)

    def undo(self, event):
        if not type(self.cmd.handler) is InitHandler:
            undo = self.cmd.undo()
            self.cmd = undo
            self.redraw_image()
    
    def redo(self, event):
        if self.cmd.next is not None:
            redo = self.cmd.redo()
            self.cmd = redo
            self.redraw_image()
            
    def switch_display(self, event):
        if(self.images["Processed"] is None and self.display_type.get() != "Original"):
            self.display_type.set("Original")
            messagebox.showerror("Error", "Please select background points and press the Calculate button first")         
            return
        
        self.loading_frame.start()
        self.redraw_image()
        self.loading_frame.end()
    
    def on_closing(self):
        prefs_file = os.path.join(user_config_dir(), ".graxpert", "preferences.json")
        try:
            os.makedirs(os.path.dirname(prefs_file), exist_ok=True)
            with open(prefs_file, "w") as f:
                self.prefs = app_state_2_prefs(self.prefs, self.cmd.app_state)
                self.prefs["bg_pts_option"] = self.bg_pts.get()
                self.prefs["stretch_option"] = self.stretch_option_current.get()
                self.prefs["bg_tol_option"] = self.bg_tol.get()
                self.prefs["interpol_type_option"] = self.interpol_type.get()
                self.prefs["smoothing_option"] = self.smoothing.get()
                self.prefs["saveas_option"] = self.saveas_type.get()
                json.dump(self.prefs, f)
        except OSError as err:
            print("error serializing preferences: {0}".format(err))
        root.destroy()

if __name__ == "__main__":
    app = Application(master=root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()