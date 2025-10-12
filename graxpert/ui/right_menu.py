import tkinter as tk
import webbrowser
from tkinter import messagebox

import customtkinter as ctk
from customtkinter import CTkFont, CTkImage, CTkLabel, CTkSwitch, CTkTextbox
from packaging import version

from graxpert.ai_model_handling import bge_ai_models_dir, deconvolution_object_ai_models_dir, deconvolution_stars_ai_models_dir, denoise_ai_models_dir, list_local_versions, list_remote_versions
from graxpert.application.app import graxpert
from graxpert.application.app_events import AppEvents
from graxpert.application.eventbus import eventbus
from graxpert.localization import _, lang
from graxpert.resource_utils import resource_image
from graxpert.s3_secrets import bge_bucket_name, deconvolution_object_bucket_name, deconvolution_stars_bucket_name, denoise_bucket_name
from graxpert.ui.widgets import GraXpertOptionMenu, GraXpertScrollableFrame, ProcessingStep, ValueSlider, padx, pady


class HelpText(CTkTextbox):
    def __init__(self, master, text="", rows=1, font=None, **kwargs):
        super().__init__(master, width=250, fg_color="transparent", wrap="word", activate_scrollbars=False, **kwargs)
        self.configure(height=self._font.metrics("linespace") * rows + 4 * pady)
        self.insert("0.0", text)


class RightFrameBase(GraXpertScrollableFrame):
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

        self.img = resource_image("GraXpert_LOGO_Hauptvariante.png")
        self.create_and_place_children()
        self.setup_layout()

    def _on_destroy(self, event):
        """This method is called when the widget is destroyed."""
        if self.img:
            self.img.close()

    def default_grid(self):
        return {"column": 0, "row": self.nrow(), "padx": padx, "pady": pady, "sticky": tk.EW}

    def create_and_place_children(self):

        logo = CTkImage(
            light_image=self.img,
            dark_image=self.img,
            size=(225, 111),
        )

        CTkLabel(self, image=logo, text="").grid(column=0, row=self.nrow(), padx=padx, pady=pady, sticky=tk.NSEW)
        CTkLabel(self, text=_("Instructions"), font=self.heading_font).grid(column=0, row=self.nrow(), pady=pady, sticky=tk.N)

        ProcessingStep(self, number=1, indent=0, title=_(" Loading")).grid(**self.default_grid())
        HelpText(self, text=_("Load your image.")).grid(**self.default_grid())

        ProcessingStep(self, number=2, indent=0, title=_(" Stretch Options")).grid(**self.default_grid())
        HelpText(self, rows=2, text=_("Stretch your image if necessary to reveal gradients.")).grid(**self.default_grid())

        ProcessingStep(self, number=3, indent=0, title=_(" Sample Selection")).grid(**self.default_grid())
        HelpText(
            self,
            rows=5,
            text=_("Select background points\n  a) manually with left click\n  b) automatically via grid (grid selection)" "\nYou can remove already set points by right clicking on them."),
        ).grid(**self.default_grid())

        ProcessingStep(self, number=4, indent=0, title=_(" Calculation")).grid(**self.default_grid())
        HelpText(self, rows=2, text=_("Click on Calculate Background to get the processed image.")).grid(**self.default_grid())

        ProcessingStep(self, number=5, indent=0, title=_(" Saving")).grid(**self.default_grid())
        HelpText(self, text=_("Save the processed image.")).grid(**self.default_grid())

        CTkLabel(self, text=_("Keybindings"), font=self.heading_font).grid(column=0, row=self.nrow(), pady=pady, sticky=tk.N)

        HelpText(self, text=_("Left click on picture: Set sample point")).grid(**self.default_grid())
        HelpText(self, rows=2, text=_("Left click on picture + drag: Move picture")).grid(**self.default_grid())
        HelpText(self, rows=2, text=_("Left click on sample point + drag: Move sample point")).grid(**self.default_grid())
        HelpText(self, rows=2, text=_("Right click on sample point: Delete sample point")).grid(**self.default_grid())
        HelpText(self, text=_("Mouse wheel: Zoom")).grid(**self.default_grid())
        HelpText(self, rows=3, text=_("Ctrl+Z/Y: Undo/Redo sample point")).grid(**self.default_grid())

        CTkLabel(self, text=_("Licenses"), font=self.heading_font).grid(column=0, row=self.nrow(), pady=pady, sticky=tk.N)

        def callback(url):
            webbrowser.open_new(url)

        row = self.nrow()
        HelpText(self, text=_("GraXpert is licensed under GPL-3:")).grid(column=0, row=row, padx=padx, pady=pady, sticky=tk.W)
        url_link_1 = "https://raw.githubusercontent.com/Steffenhir/GraXpert/main/License.md"
        url_label_1 = CTkLabel(self, text="<Link>", text_color="dodger blue")
        url_label_1.grid(column=0, row=row, padx=padx, sticky=tk.E)
        url_label_1.bind("<Button-1>", lambda e: callback(url_link_1))

        row = self.nrow()
        HelpText(self, rows=2, text=_("Background Extraction AI models are licensed under CC BY-NC-SA:")).grid(column=0, row=row, padx=padx, pady=pady, sticky=tk.W)
        url_link_2 = "https://raw.githubusercontent.com/Steffenhir/GraXpert/main/licenses/BGE-Model-LICENSE.html"
        url_label_2 = CTkLabel(self, text="<Link>", text_color="dodger blue")
        url_label_2.grid(column=0, row=row, padx=padx, sticky=tk.E)
        url_label_2.bind("<Button-1>", lambda e: callback(url_link_2))

        row = self.nrow()
        HelpText(self, rows=2, text=_("Deconvolution AI models are licensed under CC BY-NC-SA:")).grid(column=0, row=row, padx=padx, pady=pady, sticky=tk.W)
        url_link_3 = "https://raw.githubusercontent.com/Steffenhir/GraXpert/main/licenses/Deconvolution-Model-LICENSE.html"
        url_label_3 = CTkLabel(self, text="<Link>", text_color="dodger blue")
        url_label_3.grid(column=0, row=row, padx=padx, sticky=tk.E)
        url_label_3.bind("<Button-1>", lambda e: callback(url_link_3))

        row = self.nrow()
        HelpText(self, rows=2, text=_("Denoising AI models are licensed under CC BY-NC-SA:")).grid(column=0, row=row, padx=padx, pady=pady, sticky=tk.W)
        url_link_3 = "https://raw.githubusercontent.com/Steffenhir/GraXpert/main/licenses/Denoise-Model-LICENSE.html"
        url_label_3 = CTkLabel(self, text="<Link>", text_color="dodger blue")
        url_label_3.grid(column=0, row=row, padx=padx, sticky=tk.E)
        url_label_3.bind("<Button-1>", lambda e: callback(url_link_3))

    def setup_layout(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)


class AdvancedFrame(RightFrameBase):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # sample points
        self.sample_size = tk.IntVar()
        self.sample_size.set(graxpert.prefs.sample_size)
        self.sample_size.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.SAMPLE_SIZE_CHANGED, {"sample_size": self.sample_size.get()}))

        self.sample_color = tk.IntVar()
        self.sample_color.set(graxpert.prefs.sample_color)
        self.sample_color.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.SAMPLE_COLOR_CHANGED, {"sample_color": self.sample_color.get()}))

        # interpolation
        self.rbf_kernels = ["thin_plate", "quintic", "cubic", "linear"]
        self.rbf_kernel = tk.StringVar()
        self.rbf_kernel.set(graxpert.prefs.RBF_kernel)
        self.rbf_kernel.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.RBF_KERNEL_CHANGED, {"RBF_kernel": self.rbf_kernel.get()}))

        self.spline_orders = ["1", "2", "3", "4", "5"]
        self.spline_order = tk.StringVar()
        self.spline_order.set(str(graxpert.prefs.spline_order))
        self.spline_order.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.SPLINE_ORDER_CHANGED, {"spline_order": int(self.spline_order.get())}))

        self.corr_types = ["Subtraction", "Division"]
        self.corr_type = tk.StringVar()
        self.corr_type.set(graxpert.prefs.corr_type)
        self.corr_type.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.CORRECTION_TYPE_CHANGED, {"corr_type": self.corr_type.get()}))

        # interface
        self.langs = ["English", "Deutsch"]
        self.lang = tk.StringVar()
        self.lang.set(graxpert.prefs.lang)
        self.lang.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.LANGUAGE_CHANGED, {"lang": self.lang.get()}))

        self.scaling = tk.DoubleVar()
        self.scaling.set(graxpert.prefs.scaling)
        self.scaling.trace_add("write", self.on_scaling_change)

        # bge ai model
        bge_remote_versions = list_remote_versions(bge_bucket_name)
        bge_local_versions = list_local_versions(bge_ai_models_dir)
        self.bge_ai_options = set([])
        self.bge_ai_options.update([rv["version"] for rv in bge_remote_versions])
        self.bge_ai_options.update([lv["version"] for lv in bge_local_versions])
        self.bge_ai_options = sorted(self.bge_ai_options, key=lambda k: version.parse(k), reverse=True)

        self.bge_ai_version = tk.StringVar(master)
        self.bge_ai_version.set("None")  # default value
        if graxpert.prefs.bge_ai_version is not None:
            self.bge_ai_version.set(graxpert.prefs.bge_ai_version)
        else:
            self.bge_ai_options.insert(0, "None")
        self.bge_ai_version.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.BGE_AI_VERSION_CHANGED, {"bge_ai_version": self.bge_ai_version.get()}))

        # object deconvolution ai models
        deconvolution_object_ai_remote_versions = list_remote_versions(deconvolution_object_bucket_name)
        deconvolution_object_ai_local_versions = list_local_versions(deconvolution_object_ai_models_dir)
        self.deconvolution_object_ai_options = set([])
        self.deconvolution_object_ai_options.update([rv["version"] for rv in deconvolution_object_ai_remote_versions])
        self.deconvolution_object_ai_options.update([lv["version"] for lv in deconvolution_object_ai_local_versions])
        self.deconvolution_object_ai_options = sorted(self.deconvolution_object_ai_options, key=lambda k: version.parse(k), reverse=True)

        self.deconvolution_object_ai_version = tk.StringVar(master)
        self.deconvolution_object_ai_version.set("None")  # default value
        if graxpert.prefs.deconvolution_object_ai_version is not None:
            self.deconvolution_object_ai_version.set(graxpert.prefs.deconvolution_object_ai_version)
        else:
            self.deconvolution_object_ai_options.insert(0, "None")
        self.deconvolution_object_ai_version.trace_add(
            "write", lambda a, b, c: eventbus.emit(AppEvents.DECONVOLUTION_OBJECT_AI_VERSION_CHANGED, {"deconvolution_object_ai_version": self.deconvolution_object_ai_version.get()})
        )

        # stars deconvolution ai models
        deconvolution_stars_ai_remote_versions = list_remote_versions(deconvolution_stars_bucket_name)
        deconvolution_stars_ai_local_versions = list_local_versions(deconvolution_stars_ai_models_dir)
        self.deconvolution_stars_ai_options = set([])
        self.deconvolution_stars_ai_options.update([rv["version"] for rv in deconvolution_stars_ai_remote_versions])
        self.deconvolution_stars_ai_options.update([lv["version"] for lv in deconvolution_stars_ai_local_versions])
        self.deconvolution_stars_ai_options = sorted(self.deconvolution_stars_ai_options, key=lambda k: version.parse(k), reverse=True)

        self.deconvolution_stars_ai_version = tk.StringVar(master)
        self.deconvolution_stars_ai_version.set("None")  # default value
        if graxpert.prefs.deconvolution_stars_ai_version is not None:
            self.deconvolution_stars_ai_version.set(graxpert.prefs.deconvolution_stars_ai_version)
        else:
            self.deconvolution_stars_ai_options.insert(0, "None")
        self.deconvolution_stars_ai_version.trace_add(
            "write", lambda a, b, c: eventbus.emit(AppEvents.DECONVOLUTION_STARS_AI_VERSION_CHANGED, {"deconvolution_stars_ai_version": self.deconvolution_stars_ai_version.get()})
        )

        # denoise ai model
        denoise_remote_versions = list_remote_versions(denoise_bucket_name)
        denoise_local_versions = list_local_versions(denoise_ai_models_dir)
        self.denoise_ai_options = set([])
        self.denoise_ai_options.update([rv["version"] for rv in denoise_remote_versions])
        self.denoise_ai_options.update([lv["version"] for lv in denoise_local_versions])
        self.denoise_ai_options = sorted(self.denoise_ai_options, key=lambda k: version.parse(k), reverse=True)

        self.denoise_ai_version = tk.StringVar(master)
        self.denoise_ai_version.set("None")  # default value
        if graxpert.prefs.denoise_ai_version is not None:
            self.denoise_ai_version.set(graxpert.prefs.denoise_ai_version)
        else:
            self.denoise_ai_options.insert(0, "None")
        self.denoise_ai_version.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.DENOISE_AI_VERSION_CHANGED, {"denoise_ai_version": self.denoise_ai_version.get()}))

        # ai settings
        self.ai_batch_size_options = ["1", "2", "4", "8", "16", "32"]
        self.ai_batch_size = tk.IntVar()
        self.ai_batch_size.set(graxpert.prefs.ai_batch_size)
        self.ai_batch_size.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.AI_BATCH_SIZE_CHANGED, {"ai_batch_size": self.ai_batch_size.get()}))

        self.ai_gpu_acceleration = tk.BooleanVar()
        self.ai_gpu_acceleration.set(graxpert.prefs.ai_gpu_acceleration)
        self.ai_gpu_acceleration.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.AI_GPU_ACCELERATION_CHANGED, {"ai_gpu_acceleration": self.ai_gpu_acceleration.get()}))

        self.create_and_place_children()
        self.setup_layout()

    def on_scaling_change(self, a, b, c):
        eventbus.emit(AppEvents.SCALING_CHANGED, {"scaling": self.scaling.get()})
        ctk.set_widget_scaling(self.scaling.get())

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

        # bge ai model
        CTkLabel(self, text=_("Background Extraction AI-Model"), font=self.heading_font2).grid(column=0, row=self.nrow(), pady=pady, sticky=tk.N)
        GraXpertOptionMenu(self, variable=self.bge_ai_version, values=self.bge_ai_options).grid(**self.default_grid())

        # object-deconvolution ai model
        CTkLabel(self, text=_("Object Deconvolution AI-Model"), font=self.heading_font2).grid(column=0, row=self.nrow(), pady=pady, sticky=tk.N)
        GraXpertOptionMenu(self, variable=self.deconvolution_object_ai_version, values=self.deconvolution_object_ai_options).grid(**self.default_grid())

        # stars-deconvolution ai model
        CTkLabel(self, text=_("Stars Deconvolution AI-Model"), font=self.heading_font2).grid(column=0, row=self.nrow(), pady=pady, sticky=tk.N)
        GraXpertOptionMenu(self, variable=self.deconvolution_stars_ai_version, values=self.deconvolution_stars_ai_options).grid(**self.default_grid())

        # denoise ai model
        CTkLabel(self, text=_("Denoising AI-Model"), font=self.heading_font2).grid(column=0, row=self.nrow(), pady=pady, sticky=tk.N)
        GraXpertOptionMenu(self, variable=self.denoise_ai_version, values=self.denoise_ai_options).grid(**self.default_grid())

        # ai settings
        CTkLabel(self, text=_("AI inference batch size"), font=self.heading_font2).grid(column=0, row=self.nrow(), pady=pady, sticky=tk.N)
        GraXpertOptionMenu(self, variable=self.ai_batch_size, values=self.ai_batch_size_options).grid(**self.default_grid())

        CTkLabel(self, text=_("AI Hardware Acceleration"), font=self.heading_font2).grid(column=0, row=self.nrow(), pady=pady, sticky=tk.N)
        CTkSwitch(self, text=_("Enable Acceleration"), variable=self.ai_gpu_acceleration).grid(column=0, row=self.nrow(), pady=pady, sticky=tk.N)

    def setup_layout(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def default_grid(self):
        return {"column": 0, "row": self.nrow(), "padx": padx, "pady": pady}
