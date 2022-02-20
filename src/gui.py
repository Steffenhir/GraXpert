# -*- coding: utf-8 -*-
"""
Created on Sun Feb 13 10:05:08 2022
@author: steff
"""

import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk 
import math                   
import numpy as np            
import os       
import background_extraction
import background_selection
import stretch
from astropy.io import fits
from skimage import io,img_as_float32
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
        
        self.interpol_type = 'Splines'
        self.downscale_factor = 1
        
        self.background_points = []

        self.create_menu()
        self.create_widget()

        self.reset_transform()
        
        
        
        

    def menu_open_clicked(self, event=None):

        filename = tk.filedialog.askopenfilename(
            filetypes = [("Image file", ".bmp .png .jpg .tif .tiff .fits"), ("Bitmap", ".bmp"), ("PNG", ".png"), ("JPEG", ".jpg"), ("Tiff", ".tif .tiff"), ("Fits", ".fits")],
            initialdir = os.getcwd()
            )

        self.data_type = os.path.splitext(filename)[1]
        self.set_image(filename)

    def menu_quit_clicked(self):

        self.master.destroy() 
        
    def menu_intp_RBF_clicked(self):
        
        self.interpol_type = 'RBF'
        self.intp_type_text.configure(text="Method: " + self.interpol_type)
        self.downscale_factor = 4
        
    def menu_intp_Splines_clicked(self):
        
        self.interpol_type = 'Splines'
        self.intp_type_text.configure(text="Method: " + self.interpol_type)
        self.downscale_factor = 1
    
    def menu_intp_Kriging_clicked(self):
         
         self.interpol_type = 'Kriging'
         self.intp_type_text.configure(text="Method: " + self.interpol_type)
         self.downscale_factor = 4

    
    def menu_intp_GPR_CUDA_clicked(self):
         
         self.interpol_type = 'GPR_CUDA'
         self.intp_type_text.configure(text="Method: " + self.interpol_type)
         self.downscale_factor = 1 
         

    def create_menu(self):
        self.menu_bar = tk.Menu(self)
 
    
        #File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff = tk.OFF)
        
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        self.file_menu.add_command(label="Open", command = self.menu_open_clicked)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command = self.menu_quit_clicked)
        
        #Interpolation menu
        
        self.interpolation_menu = tk.Menu(self.menu_bar, tearoff = tk.OFF)   
        self.menu_bar.add_cascade(label="Interpolation Type", menu=self.interpolation_menu)
        
        self.interpolation_menu.add_command(label="RBF", command = self.menu_intp_RBF_clicked)
        self.interpolation_menu.add_command(label="Splines", command = self.menu_intp_Splines_clicked)
        self.interpolation_menu.add_command(label="Kriging", command = self.menu_intp_Kriging_clicked)
        self.interpolation_menu.add_command(label="GPR-CUDA", command = self.menu_intp_GPR_CUDA_clicked)
           

        self.master.config(menu=self.menu_bar)
        
 

    def create_widget(self):

        frame_statusbar = tk.Frame(self.master, bd=1, relief = tk.SUNKEN)
        self.label_image_info = tk.Label(frame_statusbar, text="image info", anchor=tk.E, padx = 5)
        self.label_image_pixel = tk.Label(frame_statusbar, text="(x, y)", anchor=tk.W, padx = 5)
        self.label_image_info.pack(side=tk.RIGHT)
        self.label_image_pixel.pack(side=tk.LEFT)
        frame_statusbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Canvas
        self.canvas = tk.Canvas(self.master, background="black")
        self.canvas.pack(expand=True,  fill=tk.BOTH)


        self.master.bind("<Button-1>", self.mouse_down_left)                   # Left Mouse Button
        self.master.bind("<Button-3>", self.mouse_down_right)                  # Right Mouse Button
        self.master.bind("<B1-Motion>", self.mouse_move_left)                  # Left Mouse Button Drag
        self.master.bind("<Motion>", self.mouse_move)                          # Mouse move
        self.master.bind("<Double-Button-1>", self.mouse_double_click_left)    # Left Button Double Click
        self.master.bind("<MouseWheel>", self.mouse_wheel)                     # Mouse Wheel
        self.master.bind("<Return>", self.enter_key)                           # Enter Key
        
        #Side buttons
        
        self.load_image_button = tk.Button(self.canvas, 
                         text="Load", fg="green",
                         command=self.menu_open_clicked,
                         height=5,width=15)
        self.load_image_button.place(x=10,y=10)
        
        self.save_background_button = tk.Button(self.canvas, 
                         text="Reset Points", fg="green",
                         command=self.reset_backgroundpts,
                         height=5,width=15)
        self.save_background_button.place(x=10,y=110)
        

        self.intp_type_text = tk.Message(self.canvas, text="Method: " + self.interpol_type)
        self.intp_type_text.config(width=200,bg='lightgreen', font=('times', 16, 'normal'))
        self.intp_type_text.place(x=10, y=200)
        
        self.smooth_text = tk.Message(self.canvas, text="Smoothing ")
        self.smooth_text.config(width=200,bg='lightgreen', font=('times', 12, 'normal'))
        self.smooth_text.place(x=10, y=240)
        
        self.smoothing = tk.DoubleVar()
        self.smoothing.set(5.0)
        self.smoothing_slider = tk.Scale(self.canvas,orient=tk.HORIZONTAL,from_=-10,to=10,tickinterval=20.0,resolution=0.1,var=self.smoothing,width=10)
        self.smoothing_slider.place(x=10,y=270)
        
        self.save_background_button = tk.Button(self.canvas, 
                         text="Calculate", fg="green",
                         command=self.calculate,
                         height=5,width=15)
        self.save_background_button.place(x=10,y=330)
        
        self.save_background_button = tk.Button(self.canvas, 
                         text="Save Background", fg="green",
                         command=self.save_background_image,
                         height=5,width=15)
        self.save_background_button.place(x=10,y=430)
        
              
        
        self.save_button = tk.Button(self.canvas, 
                         text="Save Picture", fg="green",
                         command=self.save_image,
                         height=5,width=15)
        self.save_button.place(x=10,y=530)
        
        self.stretch_text = tk.Message(self.canvas, text="Stretch Options:")
        self.stretch_text.config(width=200,bg='lightgreen', font=('times', 16, 'normal'))
        self.stretch_text.place(x=10, y=630)
        
        self.stretch_options = ["No Stretch", "10% Bg, 3 sigma", "15% Bg, 3 sigma", "20% Bg, 3 sigma", "25% Bg, 1.25 sigma"]
        self.stretch_option_current = tk.StringVar()
        self.stretch_option_current.set(self.stretch_options[0])
        self.stretch_menu = tk.OptionMenu(self.canvas, self.stretch_option_current, *self.stretch_options,command=self.stretch)
        self.stretch_menu.place(x=10,y=680)
        
        self.bg_selection_text = tk.Message(self.canvas, text="Automatic Background Selection")
        self.bg_selection_text.config(width=300,bg='lightgreen', font=('times', 16, 'normal'))
        self.bg_selection_text.place(x=10, y=780)
        
        self.bg_selection_text = tk.Message(self.canvas, text="# of Points")
        self.bg_selection_text.config(width=300,bg='lightgreen', font=('times', 12, 'normal'))
        self.bg_selection_text.place(x=10, y=820)
        
        self.bg_pts = tk.IntVar()
        self.bg_pts.set(5.0)
        self.bg_pts_slider = tk.Scale(self.canvas,orient=tk.HORIZONTAL,from_=0,to=100,tickinterval=20,resolution=1,var=self.bg_pts,width=10)
        self.bg_pts_slider.place(x=10,y=850)
        
        self.bg_selection_button = tk.Button(self.canvas, 
                         text="Select Background", fg="green",
                         command=self.select_background,
                         height=5,width=15)
        self.bg_selection_button.place(x=10,y=920)
        
    
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
                self.pil_image = Image.fromarray(img_as_ubyte(self.image_full))
            else:
                self.pil_image = Image.fromarray(img_as_ubyte(stretch.stretch(self.image_full,bg,sigma)))
        
        else:
            if(self.stretch_option_current.get() == "No Stretch"):
                self.pil_image = Image.fromarray(img_as_ubyte(self.image_full_processed))    
            else:
                self.pil_image = Image.fromarray(img_as_ubyte(stretch.stretch(self.image_full_processed,bg,sigma)))
        

        self.redraw_image()

    def set_image(self, filename):

        if not filename:
            return
        
        self.background_points = []
        self.image_full_processed = None
        
        
        if self.data_type == ".fits":
            self.image_full = np.moveaxis(fits.open(filename)[0].data,0,-1)           
        else:
            self.image_full = io.imread(filename)
        
        # Use 32 bit float with range (0,1) for internal calculations
        self.image_full = img_as_float32(self.image_full)
        
        self.stretch()
              

        self.zoom_fit(self.pil_image.width, self.pil_image.height)

        self.draw_image(self.pil_image)


        self.master.title(self.my_title + " - " + os.path.basename(filename))

        self.label_image_info["text"] = f"{self.pil_image.format} : {self.pil_image.width} x {self.pil_image.height} {self.pil_image.mode}"

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
       
       io.imsave(dir, self.image_full_processed)

       
    def save_background_image(self):

        if(self.background_model is None):
            return
         
        dir = tk.filedialog.asksaveasfilename(
            initialfile = "background.tiff",
            filetypes = [("Tiff", ".tiff")],
            defaultextension = ".tiff",
            initialdir = os.getcwd()
            )
        

        io.imsave(dir, self.background_model)
        
    
    def reset_backgroundpts(self):
        
        self.background_points = []
        self.redraw_image()
    
    def calculate(self):
        
        imarray = np.array(self.image_full)

        self.background_model = background_extraction.extract_background(
            imarray,np.array(self.background_points),
            self.interpol_type,10**self.smoothing.get(),
            self.downscale_factor
            )
        
        self.image_full_processed = imarray       
        

        self.stretch()
        return
    
    def enter_key(self,enter):
        
        self.calculate()
        
    
    def mouse_down_right(self,event):
        
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

        self.__old_event = event

    def mouse_move_left(self, event):

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
            self.label_image_pixel["text"] = (f"({image_point[0]:.2f}, {image_point[1]:.2f})")
        else:
            self.label_image_pixel["text"] = ("(--, --)")


    def mouse_double_click_left(self, event):

        if self.pil_image == None:
            return
        self.zoom_fit(self.pil_image.width, self.pil_image.height)
        self.redraw_image() # 再描画

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