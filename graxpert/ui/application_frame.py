import tkinter as tk

from customtkinter import CTkFrame

from graxpert.application.app import graxpert
from graxpert.application.app_events import AppEvents
from graxpert.application.eventbus import eventbus
from graxpert.commands import InitHandler
from graxpert.ui.canvas import Canvas
from graxpert.ui.left_menu import LeftMenu
from graxpert.ui.right_menu import AdvancedFrame, HelpFrame
from graxpert.ui.statusbar import StatusBar
from graxpert.ui.ui_events import UiEvents
from graxpert.ui.widgets import default_label_width, padx


class ApplicationFrame(CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.initial_title = master.title()
        self.show_help = False
        self.show_advanced = False

        self.create_children()
        self.setup_layout()
        self.place_children()
        self.create_bindings()
        self.register_events()

    def create_children(self):
        self.left_menu = LeftMenu(self, fg_color="transparent", width=default_label_width + padx + 16)
        self.canvas = Canvas(self)
        self.help_frame = HelpFrame(self, fg_color="transparent", width=300)
        self.advanced_frame = AdvancedFrame(self, fg_color="transparent", width=300)
        self.statusbar_frame = StatusBar(self, fg_color="transparent")

    def setup_layout(self):
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=100)
        self.columnconfigure(2, weight=0)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)

    def place_children(self):
        self.left_menu.grid(column=0, row=0, rowspan=2, ipadx=padx, sticky=tk.NS)
        self.canvas.grid(column=1, row=0, sticky=tk.NSEW)
        self.statusbar_frame.grid(column=1, row=1, sticky=tk.NSEW)

    def create_bindings(self):
        self.master.bind("<BackSpace>", lambda e: eventbus.emit(UiEvents.RESET_ZOOM_REQUEST))  # backspace -> reset zoom
        self.master.bind("<Control-Key-0>", lambda e: eventbus.emit(UiEvents.RESET_ZOOM_REQUEST))  # ctrl + 0 -> reset zoom (Windows)
        self.master.bind("<Command-Key-0>", lambda e: eventbus.emit(UiEvents.RESET_ZOOM_REQUEST))  # cmd  + 0 -> reset zoom (Mac)
        self.master.bind("<Control-Key-KP_0>", lambda e: eventbus.emit(UiEvents.RESET_ZOOM_REQUEST))  # ctrl + numpad 0 -> reset zoom (Windows)
        self.master.bind("<Command-Key-KP_0>", lambda e: eventbus.emit(UiEvents.RESET_ZOOM_REQUEST))  # cmd  + numpad 0 -> reset zoom (Mac)
        self.master.bind("<Control-l>", lambda e: eventbus.emit(AppEvents.OPEN_FILE_DIALOG_REQUEST))
        self.master.bind("<Command-l>", lambda e: eventbus.emit(AppEvents.OPEN_FILE_DIALOG_REQUEST))
        self.master.bind("<Control-c>", lambda e: eventbus.emit(AppEvents.CALCULATE_REQUEST))
        self.master.bind("<Command-c>", lambda e: eventbus.emit(AppEvents.CALCULATE_REQUEST))
        self.master.bind("<Control-d>", lambda e: eventbus.emit(AppEvents.DENOISE_REQUEST))
        self.master.bind("<Command-d>", lambda e: eventbus.emit(AppEvents.DENOISE_REQUEST))
        self.master.bind("<Control-s>", lambda e: eventbus.emit(AppEvents.SAVE_REQUEST))
        self.master.bind("<Command-s>", lambda e: eventbus.emit(AppEvents.SAVE_REQUEST))
        self.master.bind("<Control-z>", self.undo)  # undo
        self.master.bind("<Control-y>", self.redo)  # redo
        self.master.bind("<Command-z>", self.undo)  # undo on macs
        self.master.bind("<Command-y>", self.redo)  # redo on macs

    def register_events(self):
        eventbus.add_listener(UiEvents.HELP_FRAME_TOGGLED, self.toggle_help)
        eventbus.add_listener(UiEvents.ADVANCED_FRAME_TOGGLED, self.toggle_advanced)
        eventbus.add_listener(AppEvents.LOAD_IMAGE_END, self.on_load_image_end)

    def place_right_frame(self):
        self.help_frame.grid_forget()
        self.advanced_frame.grid_forget()

        if self.show_help:
            self.help_frame.grid(column=2, row=0, rowspan=2, sticky=tk.NSEW)

        if self.show_advanced:
            self.advanced_frame.grid(column=2, row=0, rowspan=2, sticky=tk.NSEW)

    # event handling
    def on_load_image_end(self, event):
        self.master.title(f'{self.initial_title} - {event["filename"]}')

    def redo(self, event):
        if graxpert.cmd.next is not None:
            redo = graxpert.cmd.redo()
            graxpert.cmd = redo
            eventbus.emit(AppEvents.REDRAW_POINTS_REQUEST)

    # widget logic
    def toggle_help(self, event):
        if self.show_help:
            self.show_help = False
        else:
            self.show_advanced = False
            self.show_help = True
        self.place_right_frame()

    def toggle_advanced(self, event):
        if self.show_advanced:
            self.show_advanced = False
        else:
            self.show_help = False
            self.show_advanced = True
        self.place_right_frame()

    def undo(self, event):
        if not type(graxpert.cmd.handler) is InitHandler:
            undo = graxpert.cmd.undo()
            graxpert.cmd = undo
            eventbus.emit(AppEvents.REDRAW_POINTS_REQUEST)
