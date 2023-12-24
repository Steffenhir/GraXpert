import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk
from customtkinter import CTkFont, CTkImage, CTkLabel, CTkScrollableFrame, CTkTextbox
from packaging import version
from PIL import Image

from graxpert.ai_model_handling import list_local_versions, list_remote_versions
from graxpert.application.app import graxpert
from graxpert.application.app_events import AppEvents
from graxpert.application.eventbus import eventbus
from graxpert.localization import _, lang
from graxpert.resource_utils import resource_path
from graxpert.ui.widgets import ExtractionStep, GraXpertOptionMenu, ValueSlider, padx, pady


class HelpText(CTkTextbox):
    def __init__(self, master, text="", rows=1, font=None, **kwargs):
        super().__init__(master, width=250, fg_color="transparent", wrap="word", activate_scrollbars=False, **kwargs)
        self.configure(height=self._font.metrics("linespace") * rows + 4 * pady)
        self.insert("0.0", text)


class RightFrameBase(CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.row = 0
        self.heading_font = CTkFont(size=15, weight="bold")
        self.heading_font2 = CTkFont(size=13, weight="bold")

    def nrow(self):
        self.row += 1
        return self.row


class HelpFrame(RightFrameBase):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.create_and_place_children()
        self.setup_layout()

    def default_grid(self):
        return {"column": 0, "row": self.nrow(), "padx": padx, "pady": pady, "sticky": tk.EW}

    def create_and_place_children(self):
        logo = CTkImage(
            light_image=Image.open(resource_path("img/GraXpert_LOGO_Hauptvariante.png")),
            dark_image=Image.open(resource_path("img/GraXpert_LOGO_Hauptvariante.png")),
            size=(225, 111),
        )

        CTkLabel(self, image=logo, text="").grid(column=0, row=self.nrow(), padx=padx, pady=pady, sticky=tk.NSEW)
        CTkLabel(self, text=_("Instructions"), font=self.heading_font).grid(column=0, row=self.nrow(), pady=pady, sticky=tk.N)

        ExtractionStep(self, number=1, title=_(" Loading")).grid(**self.default_grid())
        HelpText(self, text=_("Load your image.")).grid(**self.default_grid())

        ExtractionStep(self, number=2, title=_(" Stretch Options")).grid(**self.default_grid())
        HelpText(self, rows=2, text=_("Stretch your image if necessary to reveal gradients.")).grid(**self.default_grid())

        ExtractionStep(self, number=3, title=_(" Sample Selection")).grid(**self.default_grid())
        HelpText(
            self,
            rows=5,
            text=_("Select background points\n  a) manually with left click\n  b) automatically via grid (grid selection)" "\nYou can remove already set points by right clicking on them."),
        ).grid(**self.default_grid())

        ExtractionStep(self, number=4, title=_(" Calculation")).grid(**self.default_grid())
        HelpText(self, rows=2, text=_("Click on Calculate Background to get the processed image.")).grid(**self.default_grid())

        ExtractionStep(self, number=5, title=_(" Saving")).grid(**self.default_grid())
        HelpText(self, text=_("Save the processed image.")).grid(**self.default_grid())

        CTkLabel(self, text=_("Keybindings"), font=self.heading_font).grid(column=0, row=self.nrow(), pady=pady, sticky=tk.N)

        HelpText(self, text=_("Left click on picture: Set sample point")).grid(**self.default_grid())
        HelpText(self, rows=2, text=_("Left click on picture + drag: Move picture")).grid(**self.default_grid())
        HelpText(self, rows=2, text=_("Left click on sample point + drag: Move sample point")).grid(**self.default_grid())
        HelpText(self, rows=2, text=_("Right click on sample point: Delete sample point")).grid(**self.default_grid())
        HelpText(self, text=_("Mouse wheel: Zoom")).grid(**self.default_grid())
        HelpText(self, rows=3, text=_("Ctrl+Z/Y: Undo/Redo sample point")).grid(**self.default_grid())

    def setup_layout(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)


class AdvancedFrame(RightFrameBase):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # sample points
        self.sample_size = tk.IntVar()
        self.sample_size.set(25)
        if "sample_size" in graxpert.prefs:
            self.sample_size.set(graxpert.prefs["sample_size"])
        self.sample_size.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.SAMPLE_SIZE_CHANGED, {"sample_size": self.sample_size.get()}))

        self.sample_color = tk.IntVar()
        self.sample_color.set(55)
        if "sample_color" in graxpert.prefs:
            self.sample_color.set(graxpert.prefs["sample_color"])
        self.sample_color.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.SAMPLE_COLOR_CHANGED, {"sample_color": self.sample_color.get()}))

        # interpolation
        self.rbf_kernels = ["thin_plate", "quintic", "cubic", "linear"]
        self.rbf_kernel = tk.StringVar()
        self.rbf_kernel.set(self.rbf_kernels[0])
        if "RBF_kernel" in graxpert.prefs:
            self.rbf_kernel.set(graxpert.prefs["RBF_kernel"])
        self.rbf_kernel.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.RBF_KERNEL_CHANGED, {"RBF_kernel": self.rbf_kernel.get()}))

        self.spline_orders = ["1", "2", "3", "4", "5"]
        self.spline_order = tk.StringVar()
        self.spline_order.set("3")
        if "spline_order" in graxpert.prefs:
            self.spline_order.set(graxpert.prefs["spline_order"])
        self.spline_order.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.SPLINE_ORDER_CHANGED, {"spline_order": self.spline_order.get()}))

        self.corr_types = ["Subtraction", "Division"]
        self.corr_type = tk.StringVar()
        self.corr_type.set(self.corr_types[0])
        if "corr_type" in graxpert.prefs:
            self.corr_type.set(graxpert.prefs["corr_type"])
        self.corr_type.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.CORRECTION_TYPE_CHANGED, {"corr_type": self.corr_type.get()}))

        # interface
        self.langs = ["English", "Deutsch"]
        self.lang = tk.StringVar()
        if "lang" in graxpert.prefs:
            self.lang.set(graxpert.prefs["lang"])
        self.lang.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.LANGUAGE_CHANGED, {"lang": self.lang.get()}))

        self.scaling = tk.DoubleVar()
        self.scaling.set(1.0)
        if "scaling" in graxpert.prefs:
            self.scaling.set(graxpert.prefs["scaling"])
        self.scaling.trace_add("write", lambda a, b, c: ctk.set_widget_scaling(self.scaling.get()))

        # ai model
        remote_versions = list_remote_versions()
        local_versions = list_local_versions()
        self.ai_options = set([])
        self.ai_options.update([rv["version"] for rv in remote_versions])
        self.ai_options.update([lv["version"] for lv in local_versions])
        self.ai_options = sorted(self.ai_options, key=lambda k: version.parse(k), reverse=True)

        self.ai_version = tk.StringVar(master)
        self.ai_version.set("None")  # default value
        if "ai_version" in graxpert.prefs:
            self.ai_version.set(graxpert.prefs["ai_version"])
        else:
            self.ai_options.insert(0, "None")
        self.ai_version.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.AI_VERSION_CHANGED, {"ai_version": self.ai_version.get()}))

        self.create_and_place_children()
        self.setup_layout()

    def create_and_place_children(self):
        CTkLabel(self, text=_("Advanced Settings"), font=self.heading_font).grid(column=0, row=self.nrow(), pady=pady, sticky=tk.N)

        # sample points
        CTkLabel(self, text=_("Sample Points"), font=self.heading_font2).grid(column=0, row=self.nrow(), pady=pady, sticky=tk.N)

        ValueSlider(self, variable=self.sample_size, variable_name=_("Sample size"), min_value=5, max_value=50, precision=0).grid(**self.default_grid())
        ValueSlider(self, variable=self.sample_color, variable_name=_("Sample color"), min_value=0, max_value=360, precision=0).grid(**self.default_grid())

        # interpolation
        CTkLabel(self, text=_("Interpolation"), font=self.heading_font2).grid(column=0, row=self.nrow(), pady=pady, sticky=tk.N)

        CTkLabel(self, text=_("RBF Kernel")).grid(column=0, row=self.nrow(), pady=pady, sticky=tk.N)
        GraXpertOptionMenu(self, variable=self.rbf_kernel, values=self.rbf_kernels).grid(**self.default_grid())

        CTkLabel(self, text=_("Spline order")).grid(column=0, row=self.nrow(), pady=pady, sticky=tk.N)
        GraXpertOptionMenu(self, variable=self.spline_order, values=self.spline_orders).grid(**self.default_grid())

        CTkLabel(self, text=_("Correction")).grid(column=0, row=self.nrow(), pady=pady, sticky=tk.N)
        GraXpertOptionMenu(self, variable=self.corr_type, values=self.corr_types).grid(**self.default_grid())

        # interface
        CTkLabel(self, text=_("Interface"), font=self.heading_font2).grid(column=0, row=self.nrow(), pady=pady, sticky=tk.N)

        def lang_change(lang):
            messagebox.showerror("", _("Please restart the program to change the language."))

        CTkLabel(self, text=_("Language")).grid(column=0, row=self.nrow(), pady=pady, sticky=tk.N)
        GraXpertOptionMenu(self, variable=self.lang, values=self.langs).grid(**self.default_grid())

        ValueSlider(self, variable=self.scaling, variable_name=_("Scaling"), min_value=1, max_value=2, precision=1).grid(**self.default_grid())

        # ai model
        CTkLabel(self, text=_("AI-Model"), font=self.heading_font2).grid(column=0, row=self.nrow(), pady=pady, sticky=tk.N)
        GraXpertOptionMenu(self, variable=self.ai_version, values=self.ai_options).grid(**self.default_grid())

    def setup_layout(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def default_grid(self):
        return {"column": 0, "row": self.nrow(), "padx": padx, "pady": pady}
