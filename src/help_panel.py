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
        self.help_panel = tk.Frame(self.canvas, bg=bg_color, relief=relief, borderwidth=bdwidth)
        self.help_panel.pack(side=tk.RIGHT, fill=tk.Y)
        
        
        self.help_pic = tk.PhotoImage(file="../img/HELP.png")
        
        self.toggle_button = tk.Button(self.canvas, 
                         image=self.help_pic,
                         font=menu_font,
                         bg="black",
                         borderwidth=0,
                         command=self.toggle)
        
        self.toggle_button.pack(side=tk.RIGHT)
        
        # Content of help panel
        
        self.logo = tk.PhotoImage(file="../img/GraXpert_LOGO_Hauptvariante.png")
        self.logo = self.logo.subsample(6)
        self.label = tk.Label(self.help_panel, image=self.logo, bg=bg_color)
        self.label.image=self.logo
        self.label.grid(column=0, row=0, padx=10, pady=10)
        
        text = tk.Message(self.help_panel, text="Instructions", bg=bg_color, font=menu_font, fg=text_color, width=300)
        text.grid(column=0, row=1, padx=3, pady=3)
    
        self.toggle()
        
    def show(self):
        
        self.toggle_button.pack_forget()
        self.help_panel.pack(side=tk.RIGHT, fill=tk.Y)
        self.toggle_button.pack(side=tk.RIGHT)

        
    def forget(self):

        self.help_panel.pack_forget()

        
    def toggle(self):
        
        if self.visible:
            self.forget()
            self.master.update()
            self.visible = False
        
        else:
            self.show()
            self.master.update()
            self.visible = True