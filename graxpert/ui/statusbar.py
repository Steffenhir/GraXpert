import tkinter as tk

from customtkinter import CTkFrame, CTkLabel, StringVar

import graxpert.ui.tooltip as tooltip
from graxpert.application.app import graxpert
from graxpert.application.app_events import AppEvents
from graxpert.application.eventbus import eventbus
from graxpert.AstroImageRepository import ImageTypes
from graxpert.localization import _
from graxpert.ui.ui_events import UiEvents
from graxpert.ui.widgets import GraXpertCheckbox, GraXpertOptionMenu, ProcessingStep, ValueSlider, default_label_width, padx, pady


class StatusBar(CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.stretch_options = ["No Stretch", "10% Bg, 3 sigma", "15% Bg, 3 sigma", "20% Bg, 3 sigma", "30% Bg, 2 sigma"]
        self.stretch_option_current = StringVar()
        self.stretch_option_current.set(graxpert.prefs.stretch_option)
        self.stretch_option_current.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.STRETCH_OPTION_CHANGED, {"stretch_option": self.stretch_option_current.get()}))

        self.saturation = tk.DoubleVar()
        self.saturation.set(graxpert.prefs.saturation)
        self.saturation.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.CHANGE_SATURATION_REQUEST, {"saturation": self.saturation.get()}))

        self.channels_linked = tk.BooleanVar()
        self.channels_linked.set(graxpert.prefs.channels_linked_option)
        self.channels_linked.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.CHANNELS_LINKED_CHANGED, {"channels_linked": self.channels_linked.get()}))

        self.create_children()
        self.setup_layout()
        self.place_children()
        self.register_events()

    # widget setup
    def create_children(self):
        self.label_image_info = CTkLabel(self, text="image info")
        self.label_image_pixel = CTkLabel(self, text="(x, y)")

        self.stretch_option_frame = CTkFrame(self)

        self.stretch_options_title = ProcessingStep(self.stretch_option_frame, number=0, indent=2, title=_(" Stretch Options"))
        self.stretch_menu = GraXpertOptionMenu(
            self.stretch_option_frame,
            variable=self.stretch_option_current,
            values=self.stretch_options,
        )
        tooltip.Tooltip(self.stretch_menu, text=tooltip.stretch_text)
        self.saturation_slider = ValueSlider(
            self.stretch_option_frame,
            width=default_label_width,
            variable_name=_("Saturation"),
            variable=self.saturation,
            min_value=0,
            max_value=3,
            precision=1,
        )
        self.channels_linked_switch = GraXpertCheckbox(self.stretch_option_frame, width=default_label_width, text=_("Channels linked"), variable=self.channels_linked)

    def setup_layout(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def place_children(self):
        self.stretch_option_frame.grid(column=0, row=0, sticky=tk.NS)
        self.label_image_info.grid(column=0, row=0, padx=padx, sticky=tk.W)
        self.label_image_pixel.grid(column=0, row=0, padx=padx, sticky=tk.E)

        self.stretch_menu.grid(column=0, row=0, padx=padx, pady=pady, sticky=tk.E)
        self.saturation_slider.grid(column=1, row=0, padx=padx, pady=pady, sticky=tk.EW)
        self.channels_linked_switch.grid(column=2, row=0, padx=padx, pady=pady, sticky=tk.W)

    def register_events(self):
        eventbus.add_listener(AppEvents.LOAD_IMAGE_END, self.on_load_image_end)
        eventbus.add_listener(UiEvents.MOUSE_MOVED, self.on_mouse_move)

    # event handling
    def on_load_image_end(self, event):
        self.label_image_info.configure(
            text=f"{graxpert.data_type} : {graxpert.images.get(ImageTypes.Original).img_display.width} x {graxpert.images.get(ImageTypes.Original).img_display.height} {graxpert.images.get(ImageTypes.Original).img_display.mode}"
        )

    def on_mouse_move(self, event):
        if graxpert.images.get(graxpert.display_type) is None:
            return

        image_point = graxpert.to_image_point(event["mouse_event"].x, event["mouse_event"].y)
        if len(image_point) != 0:
            text = "x=" + f"{image_point[0]:.2f}" + ",y=" + f"{image_point[1]:.2f}  "
            if graxpert.images.get(graxpert.display_type).img_array.shape[2] == 3:
                R, G, B = graxpert.images.get(graxpert.display_type).get_local_median(image_point)
                text = text + "RGB = (" + f"{R:.4f}," + f"{G:.4f}," + f"{B:.4f})"

            if graxpert.images.get(graxpert.display_type).img_array.shape[2] == 1:
                L = graxpert.images.get(graxpert.display_type).get_local_median(image_point)
                text = text + "L= " + f"{L:.4f}"

            self.label_image_pixel.configure(text=text)
        else:
            self.label_image_pixel.configure(text="(--, --)")
