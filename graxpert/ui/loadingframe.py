import logging
import tkinter as tk
from os import path
from queue import Empty, Queue
from threading import Thread

from customtkinter import CTkButton, CTkFont, CTkFrame, CTkImage, CTkLabel, CTkProgressBar, DoubleVar, StringVar, ThemeManager

from graxpert.application.app_events import AppEvents
from graxpert.application.eventbus import eventbus
from graxpert.localization import _
from graxpert.resource_utils import resource_image


class LoadingFrame(CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.create_children()
        self.setup_layout()
        self.place_children()

    def create_children(self):
        font = CTkFont(size=15)
        self.text = CTkLabel(
            self,
            text=_("Calculating..."),
            image=CTkImage(light_image=resource_image("hourglass.png"), dark_image=resource_image("hourglass.png"), size=(30, 30)),
            font=font,
            compound=tk.LEFT,
        )

    def setup_layout(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def place_children(self):
        self.text.grid(column=0, row=0)


class DynamicProgressFrame(CTkFrame):
    def __init__(self, parent, label_lext=_("Progress:"), cancellable=False, **kwargs):
        super().__init__(parent, **kwargs)

        self.inner_frame = CTkFrame(self, fg_color="transparent")
        self.inner_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=10, pady=(5, 10))

        self.text = StringVar(self, value=label_lext)
        self.variable = DoubleVar(self, value=0.0)
        self.cancellable = cancellable

        self.create_children()
        self.setup_layout()
        self.place_children()

    def create_children(self):
        self.label = CTkLabel(
            self.inner_frame,
            textvariable=self.text,
            width=280,
        )
        self.pb = CTkProgressBar(self.inner_frame, variable=self.variable)
        self.pb.grid(column=0, row=0, sticky=tk.NSEW, pady=10)
        self.cancel_button = CTkButton(
            self.inner_frame,
            text=_("Cancel"),
            command=lambda: eventbus.emit(AppEvents.CANCEL_PROCESSING),
            fg_color=ThemeManager.theme["Accent.CTkButton"]["fg_color"],
            hover_color=ThemeManager.theme["Accent.CTkButton"]["hover_color"],
        )

    def setup_layout(self):
        self.inner_frame.columnconfigure(0, weight=1)
        self.inner_frame.rowconfigure(0, weight=1)

    def place_children(self):
        self.label.grid(column=0, row=0, sticky=tk.NSEW)
        self.pb.grid(column=0, row=1, sticky=tk.NSEW)
        if self.cancellable:
            self.cancel_button.grid(column=0, row=2)
        else:
            self.cancel_button.grid_forget()

    def close(self):
        self.pb.grid_forget()
        self.cancel_button.grid_forget()
        self.update()
        self.destroy()

    def update_progress(self, progress):
        self.variable.set(progress)  # * 100
        logging.info("Progress: {}%".format(int(self.variable.get() * 100)))
        self.pb.update()


class DynamicProgressThread(Thread):
    def __init__(self, interval=1, total=100, callback=None):
        Thread.__init__(self)
        self.daemon = True
        self.interval = interval
        self.callback = callback
        self.total = total
        self.current_progress = 0
        self.update_queue = Queue()
        self.start()

    def run(self):
        while True:
            try:
                # display every interval secs
                task = self.update_queue.get(timeout=self.interval)
            except Empty:
                continue

            current_progress, total = task
            self.update_queue.task_done()
            if current_progress == total:
                # once we have done uploading everything return
                self.done_progress()
                return

    # minio needs this method
    def set_meta(self, total_length, object_name=None):
        self.total = total_length

    def update(self, size):
        if not isinstance(size, int):
            raise ValueError(f"{type(size)} type can not be displayed. Please change it to Int.")

        self.current_progress += size
        self.update_queue.put((self.current_progress, self.total))

        if self.callback is not None:
            self.callback(self.progress())

    def done_progress(self):
        self.total = 0
        self.current_progress = 0

    def progress(self):
        if self.total == 0:
            return 0
        return float(self.current_progress) / float(self.total)
