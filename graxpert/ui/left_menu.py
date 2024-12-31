import tkinter as tk

from customtkinter import ThemeManager

import graxpert.ui.tooltip as tooltip
from graxpert.application.app import graxpert
from graxpert.application.app_events import AppEvents
from graxpert.application.eventbus import eventbus
from graxpert.localization import _
from graxpert.ui.ui_events import UiEvents
from graxpert.ui.widgets import CollapsibleMenuFrame, GraXpertButton, GraXpertCheckbox, GraXpertOptionMenu, GraXpertScrollableFrame, ProcessingStep, ValueSlider, default_label_width, padx, pady


class LoadMenu(CollapsibleMenuFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, title=_("Loading"), show=True, number=1, **kwargs)

        self.create_children()
        self.setup_layout()
        self.place_children()

        eventbus.add_listener(UiEvents.SHOW_MENU_REQUEST, lambda e: self.hide() if not e == "LOAD" else None)

    def create_children(self):
        super().create_children()

        # image loading
        self.load_image_button = GraXpertButton(
            self.sub_frame,
            text=_("Load Image"),
            fg_color=ThemeManager.theme["Accent.CTkButton"]["fg_color"],
            hover_color=ThemeManager.theme["Accent.CTkButton"]["hover_color"],
            command=self.menu_open_clicked,
        )
        self.tt_load = tooltip.Tooltip(self.load_image_button, text=tooltip.load_text)

    def setup_layout(self):
        super().setup_layout()

    def place_children(self):
        super().place_children()

        row = -1

        def next_row():
            nonlocal row
            row += 1
            return row

        # image loading
        self.load_image_button.grid(column=1, row=next_row(), pady=pady, sticky=tk.EW)

    def toggle(self):
        super().toggle()
        if self.show:
            eventbus.emit(UiEvents.SHOW_MENU_REQUEST, "LOAD")

    def menu_open_clicked(self, event=None):
        eventbus.emit(AppEvents.OPEN_FILE_DIALOG_REQUEST)


class CropMenu(CollapsibleMenuFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, title=_("Crop"), show=False, number=2, **kwargs)
        self.create_children()
        self.setup_layout()
        self.place_children()

        eventbus.add_listener(UiEvents.SHOW_MENU_REQUEST, lambda e: self.hide() if not e == "CROP" else None)
        eventbus.add_listener(UiEvents.SHOW_MENU_REQUEST, lambda e: eventbus.emit(UiEvents.TURN_OFF_CROP_MODE) if not e == "CROP" else None)

    def create_children(self):
        super().create_children()
        self.cropapply_button = GraXpertButton(
            self.sub_frame,
            text=_("Apply crop"),
            fg_color=ThemeManager.theme["Accent.CTkButton"]["fg_color"],
            hover_color=ThemeManager.theme["Accent.CTkButton"]["hover_color"],
            command=lambda: eventbus.emit(UiEvents.APPLY_CROP_REQUEST),
        )

    def setup_layout(self):
        super().setup_layout()

    def place_children(self):
        super().place_children()
        self.cropapply_button.grid(column=1, row=0, pady=pady, sticky=tk.NSEW)

    def toggle(self):
        super().toggle()
        if self.show:
            eventbus.emit(UiEvents.SHOW_MENU_REQUEST, "CROP")
            eventbus.emit(UiEvents.TURN_ON_CROP_MODE)
        else:
            eventbus.emit(UiEvents.TURN_OFF_CROP_MODE)


class ExtractionMenu(CollapsibleMenuFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, title=_("Background Extraction"), show=False, number=3, **kwargs)

        # method selection
        self.interpol_options = ["RBF", "Splines", "Kriging", "AI"]
        self.interpol_type = tk.StringVar()
        self.interpol_type.set(graxpert.prefs.interpol_type_option)
        self.interpol_type.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.INTERPOL_TYPE_CHANGED, {"interpol_type_option": self.interpol_type.get()}))

        # sample selection
        self.display_pts = tk.BooleanVar()
        self.display_pts.set(graxpert.prefs.display_pts)
        self.display_pts.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.DISPLAY_PTS_CHANGED, {"display_pts": self.display_pts.get()}))

        self.flood_select_pts = tk.BooleanVar()
        self.flood_select_pts.set(graxpert.prefs.bg_flood_selection_option)
        self.flood_select_pts.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.BG_FLOOD_SELECTION_CHANGED, {"bg_flood_selection_option": self.flood_select_pts.get()}))

        self.bg_pts = tk.IntVar()
        self.bg_pts.set(graxpert.prefs.bg_pts_option)
        self.bg_pts.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.BG_PTS_CHANGED, {"bg_pts_option": self.bg_pts.get()}))

        self.bg_tol = tk.DoubleVar()
        self.bg_tol.set(graxpert.prefs.bg_tol_option)
        self.bg_tol.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.BG_TOL_CHANGED, {"bg_tol_option": self.bg_tol.get()}))

        # calculation
        self.smoothing = tk.DoubleVar()
        self.smoothing.set(graxpert.prefs.smoothing_option)
        self.smoothing.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.SMOTTHING_CHANGED, {"smoothing_option": self.smoothing.get()}))

        self.create_children()
        self.setup_layout()
        self.place_children()

        eventbus.add_listener(AppEvents.INTERPOL_TYPE_CHANGED, self.place_children)
        eventbus.add_listener(UiEvents.SHOW_MENU_REQUEST, lambda e: self.hide() if not e == "BGE" else None)

    def create_children(self):
        super().create_children()

        # method selection
        self.intp_type_title = ProcessingStep(self.sub_frame, number=0, title=_("Interpolation Method:"))
        self.interpol_menu = GraXpertOptionMenu(self.sub_frame, variable=self.interpol_type, values=self.interpol_options)
        tooltip.Tooltip(self.interpol_menu, text=tooltip.interpol_type_text)

        # sample selection
        self.sample_selection_title = ProcessingStep(self.sub_frame, number=0, title=_(" Sample Selection"))
        self.display_pts_switch = GraXpertCheckbox(self.sub_frame, width=default_label_width, text=_("Display points"), variable=self.display_pts)
        self.flood_select_pts_switch = GraXpertCheckbox(self.sub_frame, width=default_label_width, text=_("Flooded generation"), variable=self.flood_select_pts)
        tooltip.Tooltip(self.flood_select_pts_switch, text=tooltip.bg_flood_text)
        self.bg_pts_slider = ValueSlider(self.sub_frame, width=default_label_width, variable_name=_("Points per row"), variable=self.bg_pts, min_value=4, max_value=25, precision=0)
        tooltip.Tooltip(self.bg_pts_slider, text=tooltip.num_points_text)
        self.bg_tol_slider = ValueSlider(self.sub_frame, width=default_label_width, variable_name=_("Grid Tolerance"), variable=self.bg_tol, min_value=-2, max_value=10, precision=1)
        tooltip.Tooltip(self.bg_tol_slider, text=tooltip.bg_tol_text)
        self.bg_selection_button = GraXpertButton(self.sub_frame, text=_("Create Grid"), command=lambda: eventbus.emit(AppEvents.CREATE_GRID_REQUEST))
        tooltip.Tooltip(self.bg_selection_button, text=tooltip.bg_select_text)
        self.reset_button = GraXpertButton(self.sub_frame, text=_("Reset Sample Points"), command=lambda: eventbus.emit(AppEvents.RESET_POITS_REQUEST))
        tooltip.Tooltip(self.reset_button, text=tooltip.reset_text)

        # calculation
        self.calculation_title = ProcessingStep(self.sub_frame, number=0, title=_(" Calculation"))
        self.smoothing_slider = ValueSlider(self.sub_frame, width=default_label_width, variable_name=_("Smoothing"), variable=self.smoothing, min_value=0, max_value=1, precision=1)
        tooltip.Tooltip(self.smoothing_slider, text=tooltip.smoothing_text)
        self.calculate_button = GraXpertButton(
            self.sub_frame,
            text=_("Calculate Background"),
            fg_color=ThemeManager.theme["Accent.CTkButton"]["fg_color"],
            hover_color=ThemeManager.theme["Accent.CTkButton"]["hover_color"],
            command=lambda: eventbus.emit(AppEvents.CALCULATE_REQUEST),
        )
        tooltip.Tooltip(self.calculate_button, text=tooltip.calculate_text)

    def setup_layout(self):
        super().setup_layout()

    def place_children(self, event=None):
        super().place_children()

        row = -1

        def next_row():
            nonlocal row
            row += 1
            return row

        # method selection
        self.intp_type_title.grid(column=1, row=next_row(), pady=pady, sticky=tk.EW)
        self.interpol_menu.grid(column=1, row=next_row(), pady=pady, sticky=tk.EW)

        # sample selection
        self.sample_selection_title.grid_forget()
        self.display_pts_switch.grid_forget()
        self.flood_select_pts_switch.grid_forget()
        self.bg_pts_slider.grid_forget()
        self.bg_tol_slider.grid_forget()
        self.bg_selection_button.grid_forget()
        self.reset_button.grid_forget()
        if not self.interpol_type.get() == "AI":
            self.sample_selection_title.grid(column=0, row=next_row(), columnspan=2, pady=pady, sticky=tk.EW)
            self.display_pts_switch.grid(column=1, row=next_row(), pady=pady, sticky=tk.EW)
            self.flood_select_pts_switch.grid(column=1, row=next_row(), pady=pady, sticky=tk.EW)
            self.bg_pts_slider.grid(column=1, row=next_row(), pady=pady, sticky=tk.EW)
            self.bg_tol_slider.grid(column=1, row=next_row(), pady=pady, sticky=tk.EW)
            self.bg_selection_button.grid(column=1, row=next_row(), pady=pady, sticky=tk.EW)
            self.reset_button.grid(column=1, row=next_row(), pady=pady, sticky=tk.EW)

        # calculation
        self.calculation_title.grid_forget()
        self.smoothing_slider.grid_forget()
        self.calculate_button.grid_forget()
        self.calculation_title.grid(column=0, row=next_row(), pady=pady, columnspan=2, sticky=tk.EW)
        self.smoothing_slider.grid(column=1, row=next_row(), pady=pady, sticky=tk.EW)
        self.calculate_button.grid(column=1, row=next_row(), pady=pady, sticky=tk.EW)

    def toggle(self):
        super().toggle()
        if self.show:
            eventbus.emit(UiEvents.SHOW_MENU_REQUEST, "BGE")


class DeconvolutionMenu(CollapsibleMenuFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, title=_("Deconvolution"), show=False, number=4, **kwargs)

        # method selection
        self.deconvolution_options = ["Object-only", "Stars-only"]
        self.deconvolution_type = tk.StringVar()
        self.deconvolution_type.set(graxpert.prefs.deconvolution_type_option)
        self.deconvolution_type.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.DECONVOLUTION_TYPE_CHANGED, {"deconvolution_type_option": self.deconvolution_type.get()}))

        self.deconvolution_strength = tk.DoubleVar()
        self.deconvolution_strength.set(graxpert.prefs.deconvolution_strength)
        self.deconvolution_strength.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.DECONVOLUTION_STRENGTH_CHANGED, {"deconvolution_strength": self.deconvolution_strength.get()}))

        self.deconvolution_psfsize = tk.DoubleVar()
        self.deconvolution_psfsize.set(graxpert.prefs.deconvolution_psfsize)
        self.deconvolution_psfsize.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.DECONVOLUTION_PSFSIZE_CHANGED, {"deconvolution_psfsize": self.deconvolution_psfsize.get()}))

        self.create_children()
        self.setup_layout()
        self.place_children()

        eventbus.add_listener(UiEvents.SHOW_MENU_REQUEST, lambda e: self.hide() if not e == "DECONVOLUTION" else None)

    def create_children(self):
        super().create_children()

        # method selection
        self.deconvolution_type_title = ProcessingStep(self.sub_frame, number=0, title=_("Deconvolution Method:"))
        self.deconvolution_menu = GraXpertOptionMenu(self.sub_frame, variable=self.deconvolution_type, values=self.deconvolution_options)
        tooltip.Tooltip(self.deconvolution_menu, text=tooltip.deconvolution_type_text)

        self.deconvolution_button = GraXpertButton(
            self.sub_frame,
            text=_("Deconvolve Image"),
            fg_color=ThemeManager.theme["Accent.CTkButton"]["fg_color"],
            hover_color=ThemeManager.theme["Accent.CTkButton"]["hover_color"],
            command=lambda: eventbus.emit(AppEvents.DECONVOLUTION_REQUEST),
        )
        self.tt_load = tooltip.Tooltip(self.deconvolution_button, text=tooltip.deconvolution_text)

        self.deconvolution_strength_slider = ValueSlider(
            self.sub_frame, width=default_label_width, variable_name=_("Deconvolution Strength"), variable=self.deconvolution_strength, min_value=0.0, max_value=1.0, precision=1
        )
        tooltip.Tooltip(self.deconvolution_strength_slider, text=tooltip.deconvolution_strength_text)

        self.deconvolution_psfsize_slider = ValueSlider(
            self.sub_frame, width=default_label_width, variable_name=_("Image FWHM (in pixels)"), variable=self.deconvolution_psfsize, min_value=0.0, max_value=14.0, precision=1
        )
        tooltip.Tooltip(self.deconvolution_psfsize_slider, text=tooltip.deconvolution_psfsize_text)

    def setup_layout(self):
        super().setup_layout()

    def place_children(self):
        super().place_children()

        row = -1

        def next_row():
            nonlocal row
            row += 1
            return row

        # method selection
        self.deconvolution_type_title.grid(column=1, row=next_row(), pady=pady, sticky=tk.EW)
        self.deconvolution_menu.grid(column=1, row=next_row(), pady=pady, sticky=tk.EW)

        self.deconvolution_strength_slider.grid(column=1, row=next_row(), pady=pady, sticky=tk.EW)
        self.deconvolution_psfsize_slider.grid(column=1, row=next_row(), pady=pady, sticky=tk.EW)
        self.deconvolution_button.grid(column=1, row=next_row(), pady=pady, sticky=tk.EW)

    def toggle(self):
        super().toggle()
        if self.show:
            eventbus.emit(UiEvents.SHOW_MENU_REQUEST, "DECONVOLUTION")


class DenoiseMenu(CollapsibleMenuFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, title=_("Denoising"), show=False, number=5, **kwargs)

        self.denoise_strength = tk.DoubleVar()
        self.denoise_strength.set(graxpert.prefs.denoise_strength)
        self.denoise_strength.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.DENOISE_STRENGTH_CHANGED, {"denoise_strength": self.denoise_strength.get()}))

        self.create_children()
        self.setup_layout()
        self.place_children()

        eventbus.add_listener(UiEvents.SHOW_MENU_REQUEST, lambda e: self.hide() if not e == "DENOISE" else None)

    def create_children(self):
        super().create_children()

        self.denoise_button = GraXpertButton(
            self.sub_frame,
            text=_("Denoise Image"),
            fg_color=ThemeManager.theme["Accent.CTkButton"]["fg_color"],
            hover_color=ThemeManager.theme["Accent.CTkButton"]["hover_color"],
            command=lambda: eventbus.emit(AppEvents.DENOISE_REQUEST),
        )
        self.tt_load = tooltip.Tooltip(self.denoise_button, text=tooltip.denoise_text)

        self.denoise_strength_slider = ValueSlider(
            self.sub_frame, width=default_label_width, variable_name=_("Denoise Strength"), variable=self.denoise_strength, min_value=0.0, max_value=1.0, precision=2
        )
        tooltip.Tooltip(self.denoise_strength_slider, text=tooltip.denoise_strength_text)

    def setup_layout(self):
        super().setup_layout()

    def place_children(self):
        super().place_children()

        self.denoise_strength_slider.grid(column=1, row=0, pady=pady, sticky=tk.EW)
        self.denoise_button.grid(column=1, row=2, pady=pady, sticky=tk.EW)

    def toggle(self):
        super().toggle()
        if self.show:
            eventbus.emit(UiEvents.SHOW_MENU_REQUEST, "DENOISE")


class SaveMenu(CollapsibleMenuFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, title=_("Saving"), show=False, number=6, **kwargs)

        # saving
        self.saveas_options = ["16 bit Tiff", "32 bit Tiff", "16 bit Fits", "32 bit Fits", "16 bit XISF", "32 bit XISF"]
        self.saveas_type = tk.StringVar()
        self.saveas_type.set(graxpert.prefs.saveas_option)
        self.saveas_type.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.SAVE_AS_CHANGED, {"saveas_option": self.saveas_type.get()}))
        self.saveas_stretched = tk.BooleanVar()
        self.saveas_stretched.set(graxpert.prefs.saveas_stretched)
        self.saveas_stretched.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.SAVE_STRETCHED_CHANGED, {"saveas_stretched": self.saveas_stretched.get()}))

        self.create_children()
        self.setup_layout()
        self.place_children()

        eventbus.add_listener(UiEvents.SHOW_MENU_REQUEST, lambda e: self.hide() if not e == "SAVE" else None)

    def create_children(self):
        super().create_children()

        # saving
        self.saveas_menu = GraXpertOptionMenu(self.sub_frame, variable=self.saveas_type, values=self.saveas_options)
        tooltip.Tooltip(self.saveas_menu, text=tooltip.saveas_text)
        self.save_button = GraXpertButton(
            self.sub_frame,
            text=_("Save Selected"),
            fg_color=ThemeManager.theme["Accent.CTkButton"]["fg_color"],
            hover_color=ThemeManager.theme["Accent.CTkButton"]["hover_color"],
            command=lambda: eventbus.emit(AppEvents.SAVE_REQUEST),
        )
        tooltip.Tooltip(self.save_button, text=tooltip.save_pic_text)
        self.saveas_stretched_checkbox = GraXpertCheckbox(self.sub_frame, width=default_label_width, text=_("Save Stretched"), variable=self.saveas_stretched)
        tooltip.Tooltip(self.saveas_stretched_checkbox, text=tooltip.saveas_stretched_text)

    def setup_layout(self):
        super().setup_layout()

    def place_children(self):
        super().place_children()

        row = -1

        def next_row():
            nonlocal row
            row += 1
            return row

        # saving
        self.saveas_menu.grid(column=1, row=next_row(), pady=pady, sticky=tk.EW)
        self.save_button.grid(column=1, row=next_row(), pady=pady, sticky=tk.EW)
        self.saveas_stretched_checkbox.grid(column=1, row=next_row(), pady=pady, sticky=tk.EW)

    def toggle(self):
        super().toggle()
        if self.show:
            eventbus.emit(UiEvents.SHOW_MENU_REQUEST, "SAVE")


class LeftMenu(GraXpertScrollableFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.create_children()
        self.setup_layout()
        self.place_children()

    def create_children(self):
        self.load_menu = LoadMenu(self, fg_color="transparent")
        self.crop_menu = CropMenu(self, fg_color="transparent")
        self.extraction_menu = ExtractionMenu(self, fg_color="transparent")
        self.deconvolution_menu = DeconvolutionMenu(self, fg_color="transparent")
        self.denoise_menu = DenoiseMenu(self, fg_color="transparent")
        self.save_menu = SaveMenu(self, fg_color="transparent")

    def setup_layout(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def place_children(self):

        row = -1

        def next_row():
            nonlocal row
            row += 1
            return row

        self.load_menu.grid(column=0, row=next_row(), ipadx=padx, sticky=tk.N)
        self.crop_menu.grid(column=0, row=next_row(), ipadx=padx, sticky=tk.N)
        self.extraction_menu.grid(column=0, row=next_row(), ipadx=padx, sticky=tk.N)
        self.deconvolution_menu.grid(column=0, row=next_row(), ipadx=padx, sticky=tk.N)
        self.denoise_menu.grid(column=0, row=next_row(), ipadx=padx, sticky=tk.N)
        self.save_menu.grid(column=0, row=next_row(), ipadx=padx, sticky=tk.N)
