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
from skimage import io,exposure,img_as_uint
from skimage.util import img_as_ubyte

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        self.master.geometry("1920x1080") 
 
        self.pil_image = None
        self.image_full = None
        self.image_full_processed = None
        self.background_model = None
        
        self.my_title = "Background Extraction"
        self.master.title(self.my_title)
        
        self.interpol_type = 'RBF'
        self.background_points = []

        self.create_menu()
        self.create_widget()

        self.reset_transform()
        
        
        
        

    def menu_open_clicked(self, event=None):

        filename = tk.filedialog.askopenfilename(
            filetypes = [("Image file", ".bmp .png .jpg .tif .tiff"), ("Bitmap", ".bmp"), ("PNG", ".png"), ("JPEG", ".jpg"), ("Tiff", ".tif .tiff") ],
            initialdir = os.getcwd()
            )


        self.set_image(filename)

    def menu_quit_clicked(self):

        self.master.destroy() 
        
    def menu_intp_RBF_clicked(self):
        
        self.interpol_type = 'RBF'
        self.intp_type_text.configure(text="Method: " + self.interpol_type)
        
    def menu_intp_Splines_clicked(self):
        
        self.interpol_type = 'Splines'
        self.intp_type_text.configure(text="Method: " + self.interpol_type)
    
    def menu_intp_Kriging_clicked(self):
         
         self.interpol_type = 'Kriging'
         self.intp_type_text.configure(text="Method: " + self.interpol_type)
         

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
        self.master.bind("<Return>", self.enter_key)                         # Enter Key
        
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
        self.intp_type_text.config(width=200,bg='lightgreen', font=('times', 18, 'normal'))
        self.intp_type_text.place(x=10, y=240)
        
        self.save_background_button = tk.Button(self.canvas, 
                         text="Calculate", fg="green",
                         command=self.calculate,
                         height=5,width=15)
        self.save_background_button.place(x=10,y=310)
        
        self.save_background_button = tk.Button(self.canvas, 
                         text="Save Background", fg="green",
                         command=self.save_background_image,
                         height=5,width=15)
        self.save_background_button.place(x=10,y=410)
        
              
        
        self.save_button = tk.Button(self.canvas, 
                         text="Save Picture", fg="green",
                         command=self.save_image,
                         height=5,width=15)
        self.save_button.place(x=10,y=510)
        
        


    def set_image(self, filename):

        if not filename:
            return

        self.pil_image = Image.open(filename)
        self.image_full = io.imread(filename)

        self.zoom_fit(self.pil_image.width, self.pil_image.height)

        self.draw_image(self.pil_image)


        self.master.title(self.my_title + " - " + os.path.basename(filename))

        self.label_image_info["text"] = f"{self.pil_image.format} : {self.pil_image.width} x {self.pil_image.height} {self.pil_image.mode}"

        os.chdir(os.path.dirname(filename))
    
   
    def save_image(self):
        
       io.imsave("out.tiff", self.image_full_processed)

       
    def save_background_image(self):

        io.imsave("background.tiff", self.background_model)
    
    def reset_backgroundpts(self):
        
        self.background_points = []
        self.redraw_image()
    
    def calculate(self):
        
        imarray = np.array(self.image_full)

        background = background_extraction.extract_background(imarray,np.array(self.background_points),self.interpol_type)
        
        self.image_full_processed = imarray
        
      
        background = exposure.rescale_intensity(background, out_range='float')
        self.background_model = img_as_uint(background)

        self.pil_image = Image.fromarray(img_as_ubyte(imarray))
        self.redraw_image()
        return
    
    def enter_key(self,enter):
        
        self.calculate()
        
    
    def mouse_down_right(self,event):
        
        if self.to_image_point(event.x,event.y) != []:
            self.background_points.append(self.to_image_point(event.x,event.y))
        
        self.redraw_image()
        self.__old_event = event
        
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
        
        ovalsize=10
        for point in self.background_points:
            canvas_point = self.to_canvas_point(point[0],point[1])
            x = canvas_point[0]
            y = canvas_point[1]
            self.canvas.create_oval(x-ovalsize,y-ovalsize, x+ovalsize,y+ovalsize,outline="red")

    def redraw_image(self):

        if self.pil_image == None:
            return
        self.draw_image(self.pil_image)


if __name__ == "__main__":
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()