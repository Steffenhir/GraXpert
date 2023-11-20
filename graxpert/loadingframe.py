import logging
import sys
import tkinter as tk
from os import path
from queue import Empty, Queue
from threading import Thread
from tkinter import LEFT, ttk

from PIL import ImageTk

from graxpert.localization import _


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_path = path.abspath(path.join(path.dirname(__file__), "../"))

    return path.join(base_path, relative_path)


class LoadingFrame:
    def __init__(self, widget, toplevel):
        font = ("Verdana", 20, "normal")

        self.toplevel = toplevel
        hourglass_pic = ImageTk.PhotoImage(
            file=resource_path("img/hourglass-scaled.png")
        )
        self.text = ttk.Label(
            widget,
            text=_("Calculating..."),
            image=hourglass_pic,
            font=font,
            compound=LEFT,
        )
        self.text.image = hourglass_pic

    def start(self):
        self.text.pack(fill="none", expand=True)
        self.toplevel.update()
        # force update of label to prevent white background on mac
        self.text.configure(background="#313131")
        self.text.update()

    def end(self):
        self.text.pack_forget()
        self.toplevel.update()


class DynamicProgressFrame(ttk.Frame):
    def __init__(self, master, label_lext=_("Progress:")):
        super().__init__(width=400, height=200)
        self.place(in_=master, anchor="c", relx=0.5, rely=0.5)
        label = tk.Message(
            self,
            text=label_lext,
            width=280,
            font="Verdana 11 bold",
            anchor="center",
        )
        label.pack()
        self.pb = ttk.Progressbar(
            self, orient="horizontal", mode="determinate", length=280
        )
        self.pb.pack()
        self.update()

    def close(self):
        self.pb.pack_forget()
        self.update()
        self.destroy()

    def update_progress(self, progress):
        self.pb["value"] = progress * 100
        logging.info("Progress: {}%".format(int(self.pb["value"])))
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
            raise ValueError(
                "{} type can not be displayed. "
                "Please change it to Int.".format(type(size))
            )

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
