import tkinter as tk
from tkinter import ttk
from localization import _

class Slider(tk.Frame):
    def __init__(self, frame, var, name, start, stop, precision, scale, command=None):
        super().__init__(frame)
        
        self.frame = frame
        self.var = var
        self.name = name
        self.start = start
        self.stop = stop
        self.precision = precision
        self.command = command
        
        self.var.set(round(self.var.get(), self.precision))
        
        self.text = tk.Label(self, text=_(self.name) + ":")
        
        # See https://stackoverflow.com/questions/4140437/interactively-validating-entry-widget-content-in-tkinter for explanation of validation
        vcmd = (self.register(self.on_entry), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        
        self.entry = ttk.Entry(self, textvariable = self.var, validate="focusout", validatecommand = vcmd, width = int(5*scale))
        self.slider = ttk.Scale(
            self,
            orient = tk.HORIZONTAL,
            from_= self.start,
            to = self.stop,
            var = self.var,
            command = self.on_slider,
            takefocus = False,
            length = 200*scale)
           
        if self.command:
            self.slider.bind("<ButtonRelease-1>", lambda event: self.command())
        
        self.entry.bind("<Up>", self.up)
        self.entry.bind("<Down>", self.down)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.text.grid(column=0, row=0, pady=0, padx=0, sticky="e")
        self.entry.grid(column=1, row=0, pady=0, padx=0, sticky="w")
        self.slider.grid(column=0, row=1, pady=5*scale, padx=0, sticky="news", columnspan=2)
        
    def on_slider(self, value):
        if self.precision == 0:    
            value = int(float(value))
        else:
            value = round(float(value), self.precision)

        self.var.set(value)
        
        
    def on_entry(self, d, i, P, s, S, v, V, W):   
        
        try:
            if self.precision == 0:
                value = int(float(P))
            else:
                value = round(float(P), self.precision)
            
            if value < self.start or value > self.stop:
                return False
            

            if self.command:
                self.command()
                
            return True
        
        except:
            return False
        
    def up(self, event):
        
       
        value = self.var.get() + 10**(-self.precision)
        
        if value > self.stop:
            return
        
        if self.precision == 0:
            value = int(float(value))
        else:
            value = round(float(value), self.precision)
            
        self.var.set(value)
        
    def down(self,event):
        value = self.var.get() - 10**(-self.precision)

        if value < self.start:
            return        
        
        if self.precision == 0:
            value = int(float(value))
        else:
            value = round(float(value), self.precision)
            
        self.var.set(value)