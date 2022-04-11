import tkinter as tk
from PIL import ImageTk, Image
from os import path
import sys

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
        self.master = canvas
        self.canvas = canvas
        
        self.visible_panel = "None"
        
        self.button_frame = tk.Frame(self.canvas)
        
        

        self.help_pic = tk.PhotoImage(file=resource_path("img/HELP.png"))
        
        self.toggle_button = tk.Button(self.button_frame, 
                         image=self.help_pic,
                         borderwidth=0,
                         command=self.help)
        
        self.toggle_button.grid(row=0,column=0)
        
        #self.advanced_pic = tk.PhotoImage(file=resource_path("advanced.png"))
        
        #self.advanced_button = tk.Button(self.button_frame, 
                         #image=self.advanced_pic,
                         #font=menu_font,
                         #bg="black",
                         #borderwidth=0,
                         #activebackground="black",
                         #command=self.advanced)
        
        #self.advanced_button.grid(row=1, column=0)
        
        
        self.button_frame.pack(side=tk.RIGHT)
        
        # Help Panel
        
        self.help_panel = tk.Frame(self.canvas)
        
        logo = Image.open(resource_path("img/GraXpert_LOGO_Hauptvariante.png"))
        logo = logo.reduce(6)
        logo = ImageTk.PhotoImage(logo)
        self.label = tk.Label(self.help_panel, image=logo)
        self.label.image= logo
        self.label.grid(column=0, row=0, padx=(40,30), pady=60)
        
        text = tk.Message(self.help_panel, text="Instructions", width=240)
        text.grid(column=0, row=1, padx=(40,30), pady=(0,5), sticky="w")
        
        text = tk.Message(self.help_panel, text="1. Load your image",width=240)
        text.grid(column=0, row=2, padx=(40,30), pady=5, sticky="w")
        
        
        text = tk.Message(self.help_panel, text="2. Stretch your image if necessary to reveal gradients",width=240)
        text.grid(column=0, row=3, padx=(40,30), pady=5, sticky="w")
        
        
        text = tk.Message(self.help_panel
                          ,text="3. Select background points \n a) manually with right click \n b) automatically via grid (grid selection) \n"
                          "You can remove already set points by right clicking on them."
                          ,width=240)
        text.grid(column=0, row=4, padx=(40,30), pady=5, sticky="w")
        
        text = tk.Message(self.help_panel, text="4. Click on Calculate to get the processed image.",width=240)
        text.grid(column=0, row=5, padx=(40,30), pady=5, sticky="w")
        
        text = tk.Message(self.help_panel, text="5. Save the processed image.",width=240)
        text.grid(column=0, row=6, padx=(40,30), pady=5, sticky="w")
    
        # Advanced Panel
        
        self.advanced_panel = tk.Frame(self.canvas)
        text = tk.Message(self.advanced_panel, text="Advanced",width=240)
        text.grid(column=0, row=0, padx=3, pady=3)
        
    def help(self):
        
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
        


