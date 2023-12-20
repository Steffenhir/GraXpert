import tkinter as tk

from customtkinter import CTkButton, CTkCheckBox, CTkEntry, CTkFrame, CTkImage, CTkLabel, CTkOptionMenu, CTkSlider, DoubleVar, StringVar, ThemeManager
from icecream import ic
from PIL import Image

from graxpert.localization import _
from graxpert.resource_utils import resource_path
from graxpert.ui_scaling import get_scaling_factor

default_button_width = 200
default_label_width = 200

padx = 5 * get_scaling_factor()
pady = 5 * get_scaling_factor()


class GraXpertButton(CTkButton):
    def __init__(self, parent, width=default_button_width, **kwargs):
        super().__init__(parent, width=width, **kwargs)


class GraXpertLabel(CTkLabel):
    def __init__(self, parent, width=default_label_width, **kwargs):
        super().__init__(parent, width=width, **kwargs)


class GraXpertOptionMenu(CTkOptionMenu):
    def __init__(self, parent, width=default_label_width, **kwargs):
        super().__init__(parent, width=width, **kwargs)


class GraXpertCheckbox(CTkCheckBox):
    def __init__(self, parent, width=default_label_width, **kwargs):
        super().__init__(parent, width=width, checkbox_width=20, checkbox_height=20, **kwargs)


class ExtractionStep(CTkFrame):
    def __init__(self, parent, number=0, title="", **kwargs):
        super().__init__(parent, **kwargs)
        self.number = number
        self.title = title
        self.create_children()
        self.setup_layout()
        self.place_children()

    def create_children(self):
        num_pic = CTkImage(
            light_image=Image.open(resource_path(f"img/gfx_number_{self.number}.png")),
            dark_image=Image.open(resource_path(f"img/gfx_number_{self.number}.png")),
            size=(20, 20),
        )
        self.title = GraXpertLabel(self, text=self.title, image=num_pic, anchor=tk.W, compound=tk.LEFT)

    def setup_layout(self):
        self.columnconfigure(0, weight=0)
        self.rowconfigure(0, weight=1)

    def place_children(self):
        self.title.grid(column=0, row=0)


class ValueSlider(CTkFrame):
    def __init__(
        self,
        parent,
        width=default_label_width,
        variable_name="",
        variable=None,
        default_value=0.5,
        min_value=0,
        max_value=1,
        number_of_steps=None,
        precision=1,
        **kwargs,
    ):
        super().__init__(parent, width=width, **kwargs)
        self.variable_name = variable_name
        self.min_value = min_value
        self.max_value = max_value
        self.number_of_steps = number_of_steps
        self.precision = precision

        if variable:
            self.variable = variable
        else:
            self.variable = DoubleVar(value=default_value)

        self.variable.set(round(self.variable.get(), self.precision))
        self.entry_variable = StringVar(value=str(self.variable.get()))
        self.slider_variable = DoubleVar(value=self.entry_variable.get())

        self.create_children()
        self.setup_layout()
        self.place_children()
        self.create_bindings()

    def create_children(self):
        self.variable_label = CTkLabel(self, width=0, text=self.variable_name)
        self.entry = CTkEntry(self, width=35, textvariable=self.entry_variable, validate="focusout")
        self.entry_variable.trace_add("write", lambda a, b, c: self.format_entry())
        self.slider = CTkSlider(
            self,
            width=default_label_width,
            command=self.on_slider,
            variable=self.slider_variable,
            from_=self.min_value,
            to=self.max_value,
            number_of_steps=self.number_of_steps,
        )

    def setup_layout(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

    def place_children(self):
        self.variable_label.grid(column=0, row=0, pady=pady, sticky=tk.E)
        self.entry.grid(column=1, row=0, padx=padx, pady=pady, sticky=tk.W)
        self.slider.grid(column=0, row=1, columnspan=2, pady=pady, sticky=tk.NSEW)

    def create_bindings(self):
        self.entry.bind("<FocusOut>", lambda event: self.on_entry(event))
        self.entry.bind("<Return>", lambda event: self.on_entry(event))
        self.slider.bind("<ButtonRelease-1>", lambda event: self.on_slider_release(event))

        self.entry.bind("<Up>", self.up)
        self.entry.bind("<Down>", self.down)
        self.entry.bind("<Left>", self.down)
        self.entry.bind("<Right>", self.up)

        self.slider.bind("<Up>", self.up)
        self.slider.bind("<Down>", self.down)
        self.slider.bind("<Left>", self.down)
        self.slider.bind("<Right>", self.up)

    def transform_value(self, value):
        if self.precision == 0:
            value = int(value)
        else:
            value = round(value, self.precision)
        return value

    def validate_entry(self):
        try:
            value = self.transform_value(float(self.entry_variable.get()))
            if value < self.min_value or value > self.max_value:
                return False
            return True
        except:
            return False

    def format_entry(self):
        if not self.validate_entry():
            self.entry.configure(fg_color="darkred")
        else:
            self.entry.configure(fg_color=ThemeManager.theme["CTkEntry"]["fg_color"])

    def on_entry(self, event):
        if not self.validate_entry():
            self.entry_variable.set(self.variable.get())
        else:
            value = self.transform_value(float(self.entry_variable.get()))
            self.entry_variable.set(str(value))
            self.slider_variable.set(value)
            if self.variable.get() != value:
                self.variable.set(value)

    def on_slider(self, value):
        value = self.transform_value(value)
        self.entry_variable.set(str(value))

    def on_slider_release(self, event):
        value = self.slider_variable.get()
        if self.precision == 0:
            value = int(float(value))
        else:
            value = round(float(value), self.precision)

        if self.variable.get() != value:
            self.variable.set(value)

    def up(self, event):
        value = float(self.entry_variable.get()) + 10 ** (-self.precision)
        if value > self.max_value:
            return "break"
        if self.precision == 0:
            value = int(float(value))
        else:
            value = round(float(value), self.precision)
        self.slider_variable.set(value)
        self.variable.set(value)
        return "break"

    def down(self, event):
        value = float(self.entry_variable.get()) - 10 ** (-self.precision)
        if value < self.min_value:
            return "break"
        if self.precision == 0:
            value = int(float(value))
        else:
            value = round(float(value), self.precision)
        self.slider_variable.set(value)
        self.variable.set(value)
        return "break"


class CollapsibleMenuFrame(CTkFrame):
    def __init__(self, parent, title="", show=True, **kwargs):
        super().__init__(parent, **kwargs)

        self.title = title
        self.show = show

    def create_children(self):
        self.title_label = GraXpertLabel(
            self,
            width=default_button_width + padx,
            text=self.title,
            pady=pady,
        )
        self.toggle_button = GraXpertButton(self, width=25, text="+", command=self.toggle)

        self.sub_frame = CTkFrame(self, fg_color="transparent")

    def setup_layout(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.sub_frame.columnconfigure(0, minsize=padx, weight=0)
        self.sub_frame.columnconfigure(1, weight=1)
        self.sub_frame.rowconfigure(0, weight=0)

    def place_children(self):
        self.title_label.grid(column=0, row=0, pady=pady, sticky=tk.W)
        self.toggle_button.grid(column=0, row=0, pady=pady, sticky=tk.E)
        self.place_sub_frame(self.show)

    def place_sub_frame(self, show):
        if show:
            self.sub_frame.grid(column=0, row=1, sticky=tk.NS)
            self.toggle_button.configure(text="-")
        else:
            self.sub_frame.grid_forget()
            self.toggle_button.configure(text="+")

    def toggle(self):
        self.show = not self.show
        self.place_sub_frame(self.show)
        self.sub_frame.update()
