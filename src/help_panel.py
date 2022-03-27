import tkinter as tk

class Help_Panel():
    def __init__(self, master, canvas):
        
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
        
        self.visible = True
        self.master = canvas
        self.canvas = canvas
        
        self.visible_panel = "None"
        
        self.button_frame = tk.Frame(self.canvas, bg=bg_color)
        
        self.help_pic = tk.PhotoImage(file="../img/HELP.png")
        
        self.toggle_button = tk.Button(self.button_frame, 
                         image=self.help_pic,
                         font=menu_font,
                         bg="black",
                         borderwidth=0,
                         activebackground="black",
                         command=self.help)
        
        self.toggle_button.grid(row=0,column=0)
        
        self.advanced_pic = tk.PhotoImage(file="../img/advanced.png")
        
        self.advanced_button = tk.Button(self.button_frame, 
                         image=self.advanced_pic,
                         font=menu_font,
                         bg="black",
                         borderwidth=0,
                         activebackground="black",
                         command=self.advanced)
        
        self.advanced_button.grid(row=1, column=0)
        
        
        self.button_frame.pack(side=tk.RIGHT)
        
        # Help Panel
        
        self.help_panel = tk.Frame(self.canvas, bg=bg_color, relief=relief, borderwidth=bdwidth)
        
        self.logo = tk.PhotoImage(file="../img/GraXpert_LOGO_Hauptvariante.png")
        self.logo = self.logo.subsample(6)
        self.label = tk.Label(self.help_panel, image=self.logo, bg=bg_color)
        self.label.image=self.logo
        self.label.grid(column=0, row=0, padx=10, pady=10)
        
        text = tk.Message(self.help_panel, text="Instructions", bg=bg_color, font=menu_font, fg=text_color, width=300)
        text.grid(column=0, row=1, padx=3, pady=3)
    
        # Advanced Panel
        
        self.advanced_panel = tk.Frame(self.canvas, bg=bg_color, relief=relief, borderwidth=bdwidth)
        text = tk.Message(self.advanced_panel, text="Advanced", bg=bg_color, font=menu_font, fg=text_color, width=300)
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
        


