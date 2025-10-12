import tkinter as tk
from colorsys import hls_to_rgb
from tkinter import messagebox

import numpy as np
from customtkinter import CTkButton, CTkCanvas, CTkFrame, CTkOptionMenu, StringVar, ThemeManager
from PIL import Image, ImageTk

from graxpert.application.app import graxpert
from graxpert.application.app_events import AppEvents
from graxpert.application.eventbus import eventbus
from graxpert.AstroImageRepository import ImageTypes
from graxpert.commands import ADD_POINT_HANDLER, ADD_POINTS_HANDLER, MOVE_POINT_HANDLER, Command
from graxpert.localization import _
from graxpert.resource_utils import resource_photoimage
from graxpert.ui.loadingframe import DynamicProgressFrame, LoadingFrame
from graxpert.ui.ui_events import UiEvents
from graxpert.ui.widgets import default_option_menu_height


class Canvas(CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.display_options = []
        self.display_type = StringVar()
        self.display_type.set(None)
        self.display_type.trace_add("write", lambda a, b, c: eventbus.emit(AppEvents.DISPLAY_TYPE_CHANGED, {"display_type": self.display_type.get()}))
        self.display_menu = None

        self.startx = 0
        self.starty = 0
        self.endx = 0
        self.endy = 0
        self.crop_mode = False
        self.clicked_inside_pt = False

        self.create_children()
        self.setup_layout()
        self.place_children()
        self.create_bindings()
        self.register_events()

    # widget setup
    def create_children(self):
        self.topbar = CTkFrame(self, height=default_option_menu_height)
        self.canvas = CTkCanvas(self, background="black", bd=0, highlightthickness=0)
        self.help_button = CTkButton(
            self.canvas,
            text=_("H\nE\nL\nP"),
            width=0,
            fg_color=ThemeManager.theme["Help.CTkButton"]["fg_color"],
            bg_color="transparent",
            hover_color=ThemeManager.theme["Help.CTkButton"]["hover_color"],
            command=lambda: eventbus.emit(UiEvents.HELP_FRAME_TOGGLED),
        )
        self.advanced_button = CTkButton(self.canvas, text=_("A\nD\nV\nA\nN\nC\nE\nD"), width=0, bg_color="transparent", command=lambda: eventbus.emit(UiEvents.ADVANCED_FRAME_TOGGLED))
        self.static_loading_frame = LoadingFrame(self.canvas, width=0, height=0)
        self.dynamic_progress_frame = DynamicProgressFrame(self.canvas)

    def setup_layout(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.canvas.columnconfigure(0, weight=1)
        self.canvas.rowconfigure(0, weight=1)
        self.canvas.rowconfigure(1, weight=1)

    def place_children(self):
        self.topbar.grid(column=0, row=0, sticky=tk.NSEW)
        self.canvas.grid(column=0, row=1, sticky=tk.NSEW)
        self.help_button.grid(column=0, row=0, sticky=tk.SE)
        self.advanced_button.grid(column=0, row=1, sticky=tk.NE)
        self.static_loading_frame.grid_forget()
        self.dynamic_progress_frame.grid_forget()

    def create_bindings(self):
        self.canvas.bind("<Button-1>", self.on_mouse_down_left)  # Left Mouse Button Down
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release_left)  # Left Mouse Button Released
        self.canvas.bind("<Button-2>", self.on_mouse_down_right)  # Middle Mouse Button (Right Mouse Button on macs)
        self.canvas.bind("<Button-3>", self.on_mouse_down_right)  # Right Mouse Button (Middle Mouse Button on macs)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move_left)  # Left Mouse Button Drag
        self.canvas.bind("<Motion>", self.on_mouse_move)  # Mouse move
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)  # Mouse Wheel
        self.canvas.bind("<Button-4>", self.on_mouse_wheel)  # Mouse Wheel Linux
        self.canvas.bind("<Button-5>", self.on_mouse_wheel)  # Mouse Wheel Linux

    def register_events(self):
        eventbus.add_listener(AppEvents.LOAD_IMAGE_BEGIN, self.on_load_image_begin)
        eventbus.add_listener(AppEvents.LOAD_IMAGE_END, self.on_load_image_end)
        eventbus.add_listener(AppEvents.LOAD_IMAGE_ERROR, self.on_load_image_error)
        eventbus.add_listener(AppEvents.STRETCH_IMAGE_BEGIN, self.on_stretch_image_begin)
        eventbus.add_listener(AppEvents.STRETCH_IMAGE_END, self.on_stretch_image_end)
        eventbus.add_listener(AppEvents.STRETCH_IMAGE_ERROR, self.on_stretch_image_error)
        eventbus.add_listener(AppEvents.CHANGE_SATURATION_BEGIN, self.on_change_saturation_begin)
        eventbus.add_listener(AppEvents.CHANGE_SATURATION_END, self.on_change_saturation_end)
        eventbus.add_listener(AppEvents.CREATE_GRID_BEGIN, self.on_create_grid_begin)
        eventbus.add_listener(AppEvents.CREATE_GRID_END, self.on_create_grid_end)
        eventbus.add_listener(AppEvents.REDRAW_POINTS_REQUEST, self.redraw_points)
        eventbus.add_listener(AppEvents.RESET_POITS_BEGIN, self.on_reset_points_begin)
        eventbus.add_listener(AppEvents.RESET_POITS_END, self.on_reset_points_end)
        eventbus.add_listener(AppEvents.CALCULATE_BEGIN, self.on_calculate_begin)
        eventbus.add_listener(AppEvents.CALCULATE_PROGRESS, self.on_calculate_progress)
        eventbus.add_listener(AppEvents.CALCULATE_END, self.on_calculate_end)
        eventbus.add_listener(AppEvents.CALCULATE_SUCCESS, self.on_calculate_success)
        eventbus.add_listener(AppEvents.CALCULATE_ERROR, self.on_calculate_end)
        eventbus.add_listener(AppEvents.DECONVOLUTION_BEGIN, self.on_deconvolution_begin)
        eventbus.add_listener(AppEvents.DECONVOLUTION_PROGRESS, self.on_deconvolution_progress)
        eventbus.add_listener(AppEvents.DECONVOLUTION_END, self.on_deconvolution_end)
        eventbus.add_listener(AppEvents.DECONVOLUTION_SUCCESS, self.on_deconvolution_success)
        eventbus.add_listener(AppEvents.DECONVOLUTION_ERROR, self.on_deconvolution_end)
        eventbus.add_listener(AppEvents.DENOISE_BEGIN, self.on_denoise_begin)
        eventbus.add_listener(AppEvents.DENOISE_PROGRESS, self.on_denoise_progress)
        eventbus.add_listener(AppEvents.DENOISE_END, self.on_denoise_end)
        eventbus.add_listener(AppEvents.DENOISE_SUCCESS, self.on_denoise_success)
        eventbus.add_listener(AppEvents.DENOISE_ERROR, self.on_denoise_end)
        eventbus.add_listener(AppEvents.SAVE_BEGIN, self.on_save_begin)
        eventbus.add_listener(AppEvents.SAVE_END, self.on_save_end)
        eventbus.add_listener(AppEvents.SAVE_ERROR, self.on_save_end)
        eventbus.add_listener(AppEvents.AI_DOWNLOAD_BEGIN, self.on_ai_download_begin)
        eventbus.add_listener(AppEvents.AI_DOWNLOAD_PROGRESS, self.on_ai_download_progress)
        eventbus.add_listener(AppEvents.AI_DOWNLOAD_END, self.on_ai_download_end)
        eventbus.add_listener(AppEvents.AI_DOWNLOAD_ERROR, self.on_ai_download_end)
        eventbus.add_listener(AppEvents.UPDATE_DISPLAY_TYPE_REEQUEST, lambda e: self.display_type.set(e["display_type"]))
        eventbus.add_listener(AppEvents.DISPLAY_TYPE_CHANGED, self.redraw_image)
        eventbus.add_listener(UiEvents.RESET_ZOOM_REQUEST, self.reset_zoom)
        eventbus.add_listener(UiEvents.DISPLAY_START_BADGE_REQUEST, self.on_display_start_badge_request)
        eventbus.add_listener(UiEvents.TURN_ON_CROP_MODE, self.on_turn_on_crop_mode)
        eventbus.add_listener(UiEvents.TURN_OFF_CROP_MODE, self.on_turn_off_crop_mode)
        eventbus.add_listener(UiEvents.APPLY_CROP_REQUEST, self.on_apply_crop_request)

    # event handling
    def on_ai_download_begin(self, event=None):
        self.dynamic_progress_frame.text.set(_("Downloading AI-Model"))
        self.show_progress_frame(True)

    def on_ai_download_progress(self, event=None):
        self.dynamic_progress_frame.update_progress(event["progress"])

    def on_ai_download_end(self, event=None):
        self.dynamic_progress_frame.text.set("")
        self.dynamic_progress_frame.variable.set(0.0)
        self.show_progress_frame(False)

    def on_apply_crop_request(self, event=None):
        self.show_progress_frame(True)

        if not self.crop_mode:
            return

        graxpert.images.crop_all(self.startx, self.endx, self.starty, self.endy)

        self.startx = 0
        self.starty = 0
        self.endx = graxpert.images.get(ImageTypes.Original).width
        self.endy = graxpert.images.get(ImageTypes.Original).height

        eventbus.emit(AppEvents.RESET_POITS_REQUEST)
        self.zoom_fit(graxpert.images.get(self.display_type.get()).width, graxpert.images.get(self.display_type.get()).height)

        self.redraw_points()
        self.redraw_image()
        self.show_progress_frame(False)

    def on_calculate_begin(self, event=None):
        self.dynamic_progress_frame.text.set(_("Extracting Background"))
        self.show_progress_frame(True)

    def on_calculate_progress(self, event=None):
        self.dynamic_progress_frame.update_progress(event["progress"])

    def on_calculate_success(self, event=None):
        if not "Gradient-Corrected" in self.display_options:
            self.display_options.append("Gradient-Corrected")
            self.display_menu.grid_forget()
            self.display_menu = CTkOptionMenu(self, variable=self.display_type, values=self.display_options)
            self.display_menu.grid(column=0, row=0, sticky=tk.N)
        if not "Background" in self.display_options:
            self.display_menu._values.append("Background")
            self.display_menu.grid_forget()
            self.display_menu = CTkOptionMenu(self, variable=self.display_type, values=self.display_options)
            self.display_menu.grid(column=0, row=0, sticky=tk.N)

    def on_calculate_end(self, event=None):
        self.dynamic_progress_frame.text.set("")
        self.dynamic_progress_frame.variable.set(0.0)
        self.show_progress_frame(False)
        self.redraw_image()

    def on_deconvolution_begin(self, event=None):
        self.dynamic_progress_frame.text.set(_("Deconvolving"))
        self.dynamic_progress_frame.cancellable = True
        self.show_progress_frame(True)

    def on_deconvolution_progress(self, event=None):
        self.dynamic_progress_frame.update_progress(event["progress"])

    def on_deconvolution_success(self, event=None):
        self.dynamic_progress_frame.cancellable = False
        if not event["deconvolution_type_option"] in self.display_options:
            self.display_options.append(event["deconvolution_type_option"])
            self.display_menu.grid_forget()
            self.display_menu = CTkOptionMenu(self, variable=self.display_type, values=self.display_options)
            self.display_menu.grid(column=0, row=0, sticky=tk.N)

    def on_deconvolution_end(self, event=None):
        self.dynamic_progress_frame.cancellable = False
        self.dynamic_progress_frame.text.set("")
        self.dynamic_progress_frame.variable.set(0.0)
        self.show_progress_frame(False)
        self.redraw_image()

    def on_denoise_begin(self, event=None):
        self.dynamic_progress_frame.text.set(_("Denoising"))
        self.dynamic_progress_frame.cancellable = True
        self.show_progress_frame(True)

    def on_denoise_progress(self, event=None):
        self.dynamic_progress_frame.update_progress(event["progress"])

    def on_denoise_success(self, event=None):
        self.dynamic_progress_frame.cancellable = False
        if not "Denoised" in self.display_options:
            self.display_options.append("Denoised")
            self.display_menu.grid_forget()
            self.display_menu = CTkOptionMenu(self, variable=self.display_type, values=self.display_options)
            self.display_menu.grid(column=0, row=0, sticky=tk.N)

    def on_denoise_end(self, event=None):
        self.dynamic_progress_frame.cancellable = False
        self.dynamic_progress_frame.text.set("")
        self.dynamic_progress_frame.variable.set(0.0)
        self.show_progress_frame(False)
        self.redraw_image()

    def on_change_saturation_begin(self, event=None):
        self.show_loading_frame(True)

    def on_change_saturation_end(self, event=None):
        self.redraw_image()
        self.show_loading_frame(False)

    def on_create_grid_begin(self, event=None):
        self.show_loading_frame(True)

    def on_create_grid_end(self, event=None):
        self.redraw_image()
        self.show_loading_frame(False)

    def on_display_start_badge_request(self, event=None):
        self.start_badge = resource_photoimage("graXpert_Startbadge_Umbriel.png")
        self.canvas.create_image(self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2, anchor=tk.CENTER, image=self.start_badge, tags="start_badge")
        self.canvas.after(5000, lambda: self.canvas.delete("start_badge"))

    def on_load_image_begin(self, event=None):
        self.canvas.delete("start_badge")
        self.show_loading_frame(True)

    def on_load_image_end(self, event=None):

        if self.display_menu is not None:
            self.display_menu.grid_forget()
        self.display_options = [ImageTypes.Original]
        self.display_type.set(self.display_options[0])
        self.display_menu = CTkOptionMenu(self, variable=self.display_type, values=self.display_options)
        self.display_menu.grid(column=0, row=0, sticky=tk.N)

        width = graxpert.images.get(ImageTypes.Original).img_display.width
        height = graxpert.images.get(ImageTypes.Original).img_display.height

        self.zoom_fit(width, height)
        self.redraw_image()

        self.show_loading_frame(False)

    def on_load_image_error(self, event=None):
        self.show_loading_frame(False)

    def on_mouse_down_left(self, event=None):
        self.left_drag_timer = -1
        if graxpert.images.get(ImageTypes.Original) is None:
            return

        self.clicked_inside_pt = False
        point_im = graxpert.to_image_point(event.x, event.y)

        if len(graxpert.cmd.app_state.background_points) != 0 and len(point_im) != 0 and graxpert.prefs.display_pts:
            eventx_im = point_im[0]
            eventy_im = point_im[1]

            background_points = graxpert.cmd.app_state.background_points

            min_idx = -1
            min_dist = -1

            for i in range(len(background_points)):
                x_im = background_points[i][0]
                y_im = background_points[i][1]

                dist = np.max(np.abs([x_im - eventx_im, y_im - eventy_im]))

                if min_idx == -1 or dist < min_dist:
                    min_dist = dist
                    min_idx = i

            if min_idx != -1 and min_dist <= graxpert.prefs.sample_size:
                self.clicked_inside_pt = True
                self.clicked_inside_pt_idx = min_idx
                self.clicked_inside_pt_coord = graxpert.cmd.app_state.background_points[min_idx]

        if self.crop_mode:
            # Check if inside circles to move crop corners
            corner1 = graxpert.to_canvas_point(self.startx, self.starty)
            corner2 = graxpert.to_canvas_point(self.endx, self.endy)
            if (event.x - corner1[0]) ** 2 + (event.y - corner1[1]) ** 2 < 15**2 or (event.x - corner2[0]) ** 2 + (event.y - corner2[1]) ** 2 < 15**2:
                self.clicked_inside_pt = True

        self.__old_event = event

    def on_mouse_down_right(self, event=None):
        if graxpert.images.get(ImageTypes.Original) is None or not graxpert.prefs.display_pts:
            return

        graxpert.remove_pt(event)
        self.redraw_points()
        self.__old_event = event

    def on_mouse_move(self, event=None):
        eventbus.emit(UiEvents.MOUSE_MOVED, {"mouse_event": event})

    def on_mouse_move_left(self, event=None):
        if graxpert.images.get(ImageTypes.Original) is None:
            return

        if graxpert.images.get(graxpert.display_type) is None:
            return

        if self.left_drag_timer == -1:
            self.left_drag_timer = event.time

        if self.clicked_inside_pt and graxpert.prefs.display_pts and not self.crop_mode:
            new_point = graxpert.to_image_point(event.x, event.y)
            if len(new_point) != 0:
                graxpert.cmd.app_state.background_points[self.clicked_inside_pt_idx] = new_point

            self.redraw_points()

        elif self.clicked_inside_pt and self.crop_mode:
            new_point = graxpert.to_image_point_pinned(event.x, event.y)
            corner1_canvas = graxpert.to_canvas_point(self.startx, self.starty)
            corner2_canvas = graxpert.to_canvas_point(self.endx, self.endy)

            dist1 = (event.x - corner1_canvas[0]) ** 2 + (event.y - corner1_canvas[1]) ** 2
            dist2 = (event.x - corner2_canvas[0]) ** 2 + (event.y - corner2_canvas[1]) ** 2
            if dist1 < dist2:
                self.startx = int(new_point[0])
                self.starty = int(new_point[1])
            else:
                self.endx = int(new_point[0])
                self.endy = int(new_point[1])

            self.redraw_points()

        else:
            if event.time - self.left_drag_timer >= 100:
                graxpert.translate(event.x - self.__old_event.x, event.y - self.__old_event.y)
                self.redraw_image()

        self.on_mouse_move(event)
        self.__old_event = event
        return

    def on_mouse_release_left(self, event=None):
        if graxpert.images.get(ImageTypes.Original) is None or not graxpert.prefs.display_pts:
            return

        if self.clicked_inside_pt and not self.crop_mode:
            new_point = graxpert.to_image_point(event.x, event.y)
            graxpert.cmd.app_state.background_points[self.clicked_inside_pt_idx] = self.clicked_inside_pt_coord
            graxpert.cmd = Command(MOVE_POINT_HANDLER, prev=graxpert.cmd, new_point=new_point, idx=self.clicked_inside_pt_idx)
            graxpert.cmd.execute()

        elif len(graxpert.to_image_point(event.x, event.y)) != 0 and (event.time - self.left_drag_timer < 100 or self.left_drag_timer == -1):
            point = graxpert.to_image_point(event.x, event.y)

            if not graxpert.prefs.bg_flood_selection_option:
                graxpert.cmd = Command(ADD_POINT_HANDLER, prev=graxpert.cmd, point=point)
            else:
                graxpert.cmd = Command(
                    ADD_POINTS_HANDLER,
                    prev=graxpert.cmd,
                    point=point,
                    tol=graxpert.prefs.bg_tol_option,
                    bg_pts=graxpert.prefs.bg_pts_option,
                    sample_size=graxpert.prefs.sample_size,
                    image=graxpert.images.get(ImageTypes.Original),
                )
            graxpert.cmd.execute()

        self.redraw_points()
        self.__old_event = event
        self.left_drag_timer = -1

    def on_mouse_wheel(self, event=None):
        if graxpert.images.get(self.display_type.get()) is None:
            return
        if event.delta > 0 or event.num == 4:
            graxpert.scale_at(6 / 5, event.x, event.y)
        else:
            graxpert.scale_at(5 / 6, event.x, event.y)
        self.redraw_image()

    def on_reset_points_begin(self, event=None):
        self.show_loading_frame(True)

    def on_reset_points_end(self, event=None):
        self.redraw_points()
        self.show_loading_frame(False)

    def on_save_begin(self, event=None):
        self.show_loading_frame(True)

    def on_save_end(self, event=None):
        self.show_loading_frame(False)

    def on_stretch_image_begin(self, event=None):
        self.show_loading_frame(True)

    def on_stretch_image_end(self, event=None):
        self.redraw_image()
        self.show_loading_frame(False)

    def on_stretch_image_error(self, event=None):
        self.show_loading_frame(False)

    def on_turn_on_crop_mode(self, event=None):
        if self.crop_mode:
            return

        if graxpert.images.get(ImageTypes.Original) is None:
            messagebox.showerror("Error", _("Please load your picture first."))
            return

        self.startx = 0
        self.starty = 0
        self.endx = graxpert.images.get(ImageTypes.Original).width
        self.endy = graxpert.images.get(ImageTypes.Original).height

        self.crop_mode = True
        self.redraw_points()

    def on_turn_off_crop_mode(self, event=None):
        if not self.crop_mode:
            return

        self.startx = 0
        self.starty = 0
        self.endx = graxpert.images.get(ImageTypes.Original).width
        self.endy = graxpert.images.get(ImageTypes.Original).height

        self.crop_mode = False
        self.redraw_points()

    # widget logic
    def draw_image(self, pil_image, tags=None):
        if pil_image is None:
            return
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        mat_inv = np.linalg.inv(graxpert.mat_affine)

        affine_inv = (mat_inv[0, 0], mat_inv[0, 1], mat_inv[0, 2], mat_inv[1, 0], mat_inv[1, 1], mat_inv[1, 2])

        dst = pil_image.transform((canvas_width, canvas_height), Image.AFFINE, affine_inv, Image.NEAREST)

        im = ImageTk.PhotoImage(image=dst)

        self.canvas.create_image(0, 0, anchor=tk.NW, image=im, tags=tags)

        self.image = im
        self.redraw_points()
        return

    def redraw_image(self, event=None):
        if graxpert.images.get(self.display_type.get()) is None:
            return
        self.draw_image(graxpert.images.get(self.display_type.get()).img_display_saturated)

    def redraw_points(self, event=None):
        if graxpert.images.get(ImageTypes.Original) is None:
            return

        color = hls_to_rgb(graxpert.prefs.sample_color / 360, 0.5, 1.0)
        color = (int(color[0] * 255), int(color[1] * 255), int(color[2] * 255))
        color = "#%02x%02x%02x" % color

        self.canvas.delete("sample")
        self.canvas.delete("crop")
        rectsize = graxpert.prefs.sample_size
        background_points = graxpert.cmd.app_state.background_points

        if graxpert.prefs.display_pts and not self.crop_mode:
            for point in background_points:
                corner1 = graxpert.to_canvas_point(point[0] - rectsize, point[1] - rectsize)
                corner2 = graxpert.to_canvas_point(point[0] + rectsize, point[1] + rectsize)
                self.canvas.create_rectangle(corner1[0], corner1[1], corner2[0], corner2[1], outline=color, width=2, tags="sample")

        if self.crop_mode:
            corner1 = graxpert.to_canvas_point(self.startx, self.starty)
            corner2 = graxpert.to_canvas_point(self.endx, self.endy)
            self.canvas.create_rectangle(corner1[0], corner1[1], corner2[0], corner2[1], outline=color, width=2, tags="crop")
            self.canvas.create_oval(corner1[0] - 15, corner1[1] - 15, corner1[0] + 15, corner1[1] + 15, outline=color, width=2, tags="crop")
            self.canvas.create_oval(corner2[0] - 15, corner2[1] - 15, corner2[0] + 15, corner2[1] + 15, outline=color, width=2, tags="crop")

    def reset_zoom(self, event=None):
        if graxpert.images.get(self.display_type.get()) is None:
            return
        self.zoom_fit(graxpert.images.get(self.display_type.get()).width, graxpert.images.get(self.display_type.get()).height)
        self.redraw_image()

    def show_loading_frame(self, show):
        if show:
            self.static_loading_frame.grid(column=0, row=0, rowspan=2)
        else:
            self.static_loading_frame.grid_forget()
        self.update()

    def show_progress_frame(self, show):
        if show:
            self.dynamic_progress_frame.place_children()
            self.dynamic_progress_frame.grid(column=0, row=0, rowspan=2)
        else:
            self.dynamic_progress_frame.grid_forget()
        self.update()

    def zoom_fit(self, image_width, image_height):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if (image_width * image_height <= 0) or (canvas_width * canvas_height <= 0):
            return

        graxpert.reset_transform()

        scale = 1.0
        offsetx = 0.0
        offsety = 0.0

        if (canvas_width * image_height) > (image_width * canvas_height):
            scale = canvas_height / image_height
            offsetx = (canvas_width - image_width * scale) / 2
        else:
            scale = canvas_width / image_width
            offsety = (canvas_height - image_height * scale) / 2

        graxpert.scale(scale)
        graxpert.translate(offsetx, offsety)
