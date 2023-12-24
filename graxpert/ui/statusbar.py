import tkinter as tk

from customtkinter import CTkFrame, CTkLabel

from graxpert.application.app import graxpert
from graxpert.application.app_events import AppEvents
from graxpert.application.eventbus import eventbus
from graxpert.ui.ui_events import UiEvents


class StatusBar(CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.create_children()
        self.setup_layout()
        self.place_children()
        self.register_events()

    # widget setup
    def create_children(self):
        self.label_image_info = CTkLabel(self, text="image info")
        self.label_image_pixel = CTkLabel(self, text="(x, y)")

    def setup_layout(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def place_children(self):
        self.label_image_info.grid(column=0, row=0, sticky=tk.W)
        self.label_image_pixel.grid(column=0, row=0, sticky=tk.E)

    def register_events(self):
        eventbus.add_listener(AppEvents.LOAD_IMAGE_END, self.on_load_image_end)
        eventbus.add_listener(UiEvents.MOUSE_MOVED, self.on_mouse_move)

    # event handling
    def on_load_image_end(self, event):
        self.label_image_info.configure(
            text=f'{graxpert.data_type} : {graxpert.images["Original"].img_display.width} x {graxpert.images["Original"].img_display.height} {graxpert.images["Original"].img_display.mode}'
        )

    def on_mouse_move(self, event):
        if graxpert.images[graxpert.display_type] is None:
            return

        image_point = graxpert.to_image_point(event["mouse_event"].x, event["mouse_event"].y)
        if len(image_point) != 0:
            text = "x=" + f"{image_point[0]:.2f}" + ",y=" + f"{image_point[1]:.2f}  "
            if graxpert.images[graxpert.display_type].img_array.shape[2] == 3:
                R, G, B = graxpert.images[graxpert.display_type].get_local_median(image_point)
                text = text + "RGB = (" + f"{R:.4f}," + f"{G:.4f}," + f"{B:.4f})"

            if graxpert.images[graxpert.display_type].img_array.shape[2] == 1:
                L = graxpert.images[graxpert.display_type].get_local_median(image_point)
                text = text + "L= " + f"{L:.4f}"

            self.label_image_pixel.configure(text=text)
        else:
            self.label_image_pixel.configure(text="(--, --)")
