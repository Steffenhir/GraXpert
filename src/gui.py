# -*- coding: utf-8 -*-
"""
Created on Sun Feb 13 10:05:08 2022
@author: steff
"""

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk 
import math                   
import numpy as np            
import os       
import background_extraction
import background_selection
import stretch
import tooltip
from astropy.io import fits
from skimage import io,img_as_float32, img_as_uint, exposure
from skimage.util import img_as_ubyte



class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        self.master.geometry("1920x1080") 

        self.data_type = ""
        self.pil_image = None
        self.image_full = None
        self.image_full_processed = None
        self.background_model = None
        
        self.my_title = "Background Extraction"
        self.master.title(self.my_title)       
        
        self.background_points = []

        self.create_widget()

        self.reset_transform()
        
        

    def create_widget(self):

        frame_statusbar = tk.Frame(self.master, bd=1, relief = tk.SUNKEN)
        self.label_image_info = tk.Label(frame_statusbar, text="image info", anchor=tk.E, padx = 5)
        self.label_image_pixel = tk.Label(frame_statusbar, text="(x, y)", anchor=tk.W, padx = 5)
        self.label_image_info.pack(side=tk.RIGHT)
        self.label_image_pixel.pack(side=tk.LEFT)
        frame_statusbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Canvas
        self.canvas = tk.Canvas(self.master, background="black", name="picture")
        self.canvas.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)


        self.master.bind("<Button-1>", self.mouse_down_left)                   # Left Mouse Button
        self.master.bind("<Button-3>", self.mouse_down_right)                  # Right Mouse Button
        self.master.bind("<B1-Motion>", self.mouse_move_left)                  # Left Mouse Button Drag
        self.master.bind("<Motion>", self.mouse_move)                          # Mouse move
        self.master.bind("<Double-Button-1>", self.mouse_double_click_left)    # Left Button Double Click
        self.master.bind("<MouseWheel>", self.mouse_wheel)                     # Mouse Wheel
        self.master.bind("<Return>", self.enter_key)                           # Enter Key
        
        #Side menu
        
        border_color = "#171717"
        bg_color = "#474747"
        button_color = "#6a6a6a"
        text_color = "#F0F0F0"
        menu_font = ('Segoe UI Semibold', 12, 'normal')
        button_height = 2
        button_width = 16
        relief = "raised"
        bdwidth = 5
        
        self.side_menu = tk.Frame(self.master, bg=bg_color, relief=relief, borderwidth=bdwidth)
        self.side_menu.pack(side=tk.LEFT, fill=tk.Y)
        
        self.side_menu.grid_columnconfigure(0, weight=1)
        
        for i in range(17):
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
        self.stretch_text.grid(column=0, row=2, pady=(5,0), padx=15, sticky="news")
        
        self.stretch_options = ["No Stretch", "10% Bg, 3 sigma", "15% Bg, 3 sigma", "20% Bg, 3 sigma", "25% Bg, 1.25 sigma"]
        self.stretch_option_current = tk.StringVar()
        self.stretch_option_current.set(self.stretch_options[0])
        self.stretch_menu = tk.OptionMenu(self.side_menu, self.stretch_option_current, *self.stretch_options,command=self.stretch)
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
        
        self.bg_selection_text = tk.Message(self.side_menu, text="# of Points:", bg=bg_color)
        self.bg_selection_text.config(width=300, font=menu_font, fg=text_color)
        self.bg_selection_text.grid(column=0, row=5, pady=(5,0), padx=15, sticky="news")
        
        self.bg_pts = tk.IntVar()
        self.bg_pts.set(5.0)
        self.bg_pts_slider = tk.Scale(self.side_menu,orient=tk.HORIZONTAL,from_=0,to=100,tickinterval=50,resolution=1,
                                      var=self.bg_pts,width=12, bg=button_color, fg=text_color, relief=relief, 
                                      borderwidth=bdwidth, highlightbackground=bg_color)
        self.bg_pts_slider.grid(column=0, row=6, pady=(0,5), padx=15, sticky="news")
        tt_bg_points= tooltip.Tooltip(self.bg_pts_slider, text=tooltip.num_points_text)
        
        self.bg_selection_button = tk.Button(self.side_menu, 
                         text="Select Background",
                         font=menu_font,
                         bg=button_color,fg=text_color,
                         relief=relief, borderwidth=bdwidth,
                         command=self.select_background,
                         height=button_height,width=button_width)
        self.bg_selection_button.grid(column=0, row=7, pady=5, padx=15, sticky="news")
        tt_bg_select = tooltip.Tooltip(self.bg_selection_button, text= tooltip.bg_select_text)
        
        #---Calculation---
        
        self.intp_type_text = tk.Message(self.side_menu, text="Method:", bg=bg_color, font=menu_font)
        self.intp_type_text.config(width=200, font=menu_font, fg=text_color)
        self.intp_type_text.grid(column=0, row=8, pady=(5,0), padx=15, sticky="news")
        
        self.interpol_options = ["Splines", "RBF", "Kriging"]
        self.interpol_type = tk.StringVar()
        self.interpol_type.set(self.interpol_options[0])
        self.interpol_menu = tk.OptionMenu(self.side_menu, self.interpol_type, *self.interpol_options)
        self.interpol_menu.config(font=menu_font, bg=button_color, fg=text_color, relief=relief, 
                                  borderwidth=bdwidth, highlightbackground=bg_color)
        self.interpol_menu.grid(column=0, row=9, pady=(0,5), padx=15, sticky="news")
        tt_interpol_type= tooltip.Tooltip(self.interpol_menu, text=tooltip.interpol_type_text)
        
        self.smooth_text = tk.Message(self.side_menu, text="Smoothing:", bg=bg_color)
        self.smooth_text.config(width=200, font=menu_font, fg=text_color)
        self.smooth_text.grid(column=0, row=10, pady=(5,0), padx=15, sticky="news")
        
        self.smoothing = tk.DoubleVar()
        self.smoothing.set(5.0)
        self.smoothing_slider = tk.Scale(self.side_menu,orient=tk.HORIZONTAL,
                                         from_=-10,to=10,tickinterval=10.0,resolution=0.1,var=self.smoothing,
                                         width=12, bg=button_color, fg=text_color, relief=relief, 
                                         borderwidth=bdwidth, highlightbackground=bg_color)
        self.smoothing_slider.grid(column=0, row=11, pady=(0,5), padx=15, sticky="news")
        tt_smoothing= tooltip.Tooltip(self.smoothing_slider, text=tooltip.smoothing_text)
        
        self.calculate_button = tk.Button(self.side_menu, 
                         text="Calculate",
                         font=menu_font,
                         bg=button_color,fg=text_color,
                         relief=relief, borderwidth=bdwidth,
                         command=self.calculate,
                         height=button_height,width=button_width)
        self.calculate_button.grid(column=0, row=12, pady=5, padx=15, sticky="news")
        tt_calculate= tooltip.Tooltip(self.calculate_button, text=tooltip.calculate_text)
        
        #---Saving---  
        
        self.saveas_text = tk.Message(self.side_menu, text="Save as:", bg=bg_color, font=menu_font)
        self.saveas_text.config(width=200, font=menu_font, fg=text_color)
        self.saveas_text.grid(column=0, row=13, pady=(5,0), padx=15, sticky="news")
        
        self.saveas_options = ["16 bit Tiff", "32 bit Tiff"]
        self.saveas_type = tk.StringVar()
        self.saveas_type.set(self.saveas_options[0])
        self.saveas_menu = tk.OptionMenu(self.side_menu, self.saveas_type, *self.saveas_options)
        self.saveas_menu.config(font=menu_font, bg=button_color, fg=text_color, relief=relief, 
                                  borderwidth=bdwidth, highlightbackground=bg_color)
        self.saveas_menu.grid(column=0, row=14, pady=(0,5), padx=15, sticky="news")
        tt_interpol_type= tooltip.Tooltip(self.saveas_menu, text=tooltip.saveas_text)
        
        self.save_background_button = tk.Button(self.side_menu, 
                         text="Save Background",
                         font=menu_font,
                         bg=button_color,fg=text_color,
                         relief=relief, borderwidth=bdwidth,
                         command=self.save_background_image,
                         height=button_height,width=button_width)
        self.save_background_button.grid(column=0, row=15, pady=5, padx=15, sticky="news")
        tt_save_bg = tooltip.Tooltip(self.save_background_button, text=tooltip.save_bg_text)
              
        
        self.save_button = tk.Button(self.side_menu, 
                         text="Save Picture",
                         font=menu_font,
                         bg=button_color,fg=text_color,
                         relief=relief, borderwidth=bdwidth,
                         command=self.save_image,
                         height=button_height,width=button_width)
        self.save_button.grid(column=0, row=16, pady=5, padx=15, sticky="news")
        tt_save_pic= tooltip.Tooltip(self.save_button, text=tooltip.save_pic_text)
    
    
    def menu_open_clicked(self, event=None):

        filename = tk.filedialog.askopenfilename(
            filetypes = [("Image file", ".bmp .png .jpg .tif .tiff .fit .fits"), ("Bitmap", ".bmp"), ("PNG", ".png"), ("JPEG", ".jpg"), ("Tiff", ".tif .tiff"), ("Fits", ".fit .fits")],
            initialdir = os.getcwd()
            )

        self.data_type = os.path.splitext(filename)[1]
        self.set_image(filename)


    def select_background(self,event=None):
        self.background_points = background_selection.background_selection(self.image_full,self.bg_pts.get())
        for i in range(len(self.background_points)):
            self.background_points[i] = np.array([self.background_points[i][1],self.background_points[i][0],1.0])
        

        self.redraw_image()
        return

        
    def stretch(self,event=None):
        
        if(self.image_full is None):
            return
        
        if(self.stretch_option_current.get() == "10% Bg, 3 sigma"):
                bg, sigma = (0.1,3)
               
        if(self.stretch_option_current.get() == "15% Bg, 3 sigma"):
                bg, sigma = (0.15,3)
                
        if(self.stretch_option_current.get() == "20% Bg, 3 sigma"):
                bg, sigma = (0.2,3)
                
        if(self.stretch_option_current.get() == "25% Bg, 1.25 sigma"):
                bg, sigma = (0.25,1.25)
        
        
        
        if(self.image_full_processed is None):
            if(self.stretch_option_current.get() == "No Stretch"):
                if(self.image_full.shape[2] == 1):
                    self.pil_image = Image.fromarray(img_as_ubyte(self.image_full[:,:,0]))
                else:
                    self.pil_image = Image.fromarray(img_as_ubyte(self.image_full))
            else:
                if(self.image_full.shape[2] == 1):
                    self.pil_image = Image.fromarray(img_as_ubyte(stretch.stretch(self.image_full,bg,sigma))[:,:,0])
                else:
                    self.pil_image = Image.fromarray(img_as_ubyte(stretch.stretch(self.image_full,bg,sigma)))
        
        else:
            if(self.stretch_option_current.get() == "No Stretch"):
                if(self.image_full_processed.shape[2] == 1):
                    self.pil_image = Image.fromarray(img_as_ubyte(self.image_full_processed[:,:,0]))    
                else:
                    self.pil_image = Image.fromarray(img_as_ubyte(self.image_full_processed))    
            else:
                if(self.image_full_processed.shape[2] == 1):
                    self.pil_image = Image.fromarray(img_as_ubyte(stretch.stretch(self.image_full_processed,bg,sigma))[:,:,0])
                else:
                    self.pil_image = Image.fromarray(img_as_ubyte(stretch.stretch(self.image_full_processed,bg,sigma)))
        

        self.redraw_image()


    def set_image(self, filename):

        if not filename:
            return
        
        self.background_points = []
        self.image_full_processed = None
        
        
        if(self.data_type == ".fits" or self.data_type == ".fit"):
            self.image_full = fits.open(filename)[0].data
            if(len(self.image_full.shape) == 3):
               self.image_full = np.moveaxis(self.image_full,0,-1)           
        else:
            self.image_full = io.imread(filename)
        
        
        if(self.image_full.dtype == "float32" or self.image_full.dtype == ">f4"):
            self.saveas_type.set("32 bit Tiff")
        
        elif(self.image_full.dtype == "uint16" or self.image_full.dtype == ">i2"):
            self.saveas_type.set("16 bit Tiff")
            
        print(self.image_full.dtype)
       
        # Reshape greyscale picture to shape (y,x,1)
        if(len(self.image_full.shape) == 2):
            
            self.image_full = np.array([self.image_full])
            self.image_full = np.moveaxis(self.image_full,0,-1)
       
        # Use 32 bit float with range (0,1) for internal calculations
        self.image_full = img_as_float32(self.image_full)
        
        
        if(np.min(self.image_full) < 0):
            self.image_full = exposure.rescale_intensity(self.image_full, in_range=(-1,1), out_range=(0,1))

        
        self.stretch()
              
        self.zoom_fit(self.pil_image.width, self.pil_image.height)

        self.draw_image(self.pil_image)


        self.master.title(self.my_title + " - " + os.path.basename(filename))

        self.label_image_info["text"] = f"{self.data_type} : {self.pil_image.width} x {self.pil_image.height} {self.pil_image.mode}"

        os.chdir(os.path.dirname(filename))
    
   
    def save_image(self):
       
       if(self.image_full_processed is None):
           return
        
       dir = tk.filedialog.asksaveasfilename(
           initialfile = "out.tiff",
           filetypes = [("Tiff", ".tiff")],
           defaultextension = ".tiff",
           initialdir = os.getcwd()
           )
       
       if(self.saveas_type.get() == "16 bit Tiff"):
           image_converted = img_as_uint(self.image_full_processed)
       else:
           image_converted = self.image_full_processed
       
       io.imsave(dir, image_converted)

       
    def save_background_image(self):

        if(self.background_model is None):
            return
         
        dir = tk.filedialog.asksaveasfilename(
            initialfile = "background.tiff",
            filetypes = [("Tiff", ".tiff")],
            defaultextension = ".tiff",
            initialdir = os.getcwd()
            )
        
        if(self.saveas_type.get() == "16 bit Tiff"):
            background_model_converted = img_as_uint(self.background_model)
        else:
            background_model_converted = self.background_model

        io.imsave(dir, background_model_converted)
        
    
    def reset_backgroundpts(self):
        
        self.background_points = []
        self.redraw_image()
    
    def calculate(self):
        
        #Error messages if not enough points
        if(len(self.background_points) == 0):
            tk.messagebox.showerror("Error", "Please select background points with right click")
            return
        
        if(len(self.background_points) < 2 and self.interpol_type.get() == "Kriging"):
            tk.messagebox.showerror("Error", "Please select at least 2 background points with right click for the Kriging method")
            return
        
        if(len(self.background_points) < 16 and self.interpol_type.get() == "Splines"):
            tk.messagebox.showerror("Error", "Please select at least 16 background points with right click for the Splines method")
            return
        
        
        imarray = np.array(self.image_full)
        
        downscale_factor = 1
        
        if(self.interpol_type.get() == "Kriging" or self.interpol_type.get() == "RBF"):
            downscale_factor = 4

            
        self.background_model = background_extraction.extract_background(
            imarray,np.array(self.background_points),
            self.interpol_type.get(),10**self.smoothing.get(),
            downscale_factor
            )
        
        self.image_full_processed = imarray       
        

        self.stretch()
        return
    
    def enter_key(self,enter):
        
        self.calculate()
        
    
    def mouse_down_right(self,event):
        
        if(str(event.widget).split(".")[-1] != "picture"):
            return
        

        if(not self.remove_pt(event) and self.to_image_point(event.x,event.y) != []):
            self.background_points.append(self.to_image_point(event.x,event.y))

        self.redraw_image()
        self.__old_event = event
        
    def remove_pt(self,event):
        
        min_idx = -1
        min_dist = -1
        
        for i in range(len(self.background_points)):
            x_im = self.background_points[i][0]
            y_im = self.background_points[i][1]
            
            x = self.to_canvas_point(x_im, y_im)[0]
            y = self.to_canvas_point(x_im, y_im)[1]
            
            dist = np.sqrt((x-event.x)**2 + (y-event.y)**2)
            
            if(min_idx == -1 or dist < min_dist):
                min_dist = dist
                min_idx = i
        
        
        if(min_idx != -1 and min_dist <= 10):
            self.background_points.pop(min_idx)
            return True
        
        return False

            
        
    def mouse_down_left(self, event):
        
        if(str(event.widget).split(".")[-1] != "picture"):
            return
        
        self.__old_event = event


    def mouse_move_left(self, event):
        
        if(str(event.widget).split(".")[-1] != "picture"):
            return
        
        if (self.pil_image == None):
            return
        self.translate(event.x - self.__old_event.x, event.y - self.__old_event.y)
        self.redraw_image()
        self.__old_event = event

    def mouse_move(self, event):

        if (self.pil_image == None):
            return
        
        image_point = self.to_image_point(event.x, event.y)
        if image_point != []:
            self.label_image_pixel["text"] = "x=" + f"{image_point[0]:.2f}" + ",y=" + f"{image_point[1]:.2f}"
        else:
            self.label_image_pixel["text"] = ("(--, --)")


    def mouse_double_click_left(self, event):
        
        if(str(event.widget).split(".")[-1] != "picture"):
            return
        
        if self.pil_image == None:
            return
        self.zoom_fit(self.pil_image.width, self.pil_image.height)
        self.redraw_image()

    def mouse_wheel(self, event):

        if self.pil_image == None:
            return

        if event.state != 9:
            if (event.delta > 0):

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

        if self.pil_image == None:
            return []

        mat_inv = np.linalg.inv(self.mat_affine)
        image_point = np.dot(mat_inv, (x, y, 1.))
        if  image_point[0] < 0 or image_point[1] < 0 or image_point[0] > self.pil_image.width or image_point[1] > self.pil_image.height:
            return []

        return image_point

    def to_canvas_point(self, x, y):
        
        return np.dot(self.mat_affine,(x,y,1.))

    def draw_image(self, pil_image):

        if pil_image == None:
            return

        self.pil_image = pil_image


        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()


        mat_inv = np.linalg.inv(self.mat_affine)


        affine_inv = (
            mat_inv[0, 0], mat_inv[0, 1], mat_inv[0, 2],
            mat_inv[1, 0], mat_inv[1, 1], mat_inv[1, 2]
            )


        dst = self.pil_image.transform(
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
        
        self.canvas.delete("oval")
        ovalsize=10
        for point in self.background_points:
            canvas_point = self.to_canvas_point(point[0],point[1])
            x = canvas_point[0]
            y = canvas_point[1]
            self.canvas.create_oval(x-ovalsize,y-ovalsize, x+ovalsize,y+ovalsize,outline="red", tags="oval")
            
        return

    def redraw_image(self):

        if self.pil_image == None:
            return
        self.draw_image(self.pil_image)


if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()